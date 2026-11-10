#!/usr/bin/env python3
"""Generate a Tableau workbook (.twb) with one Map Layer per layer of an ArcGIS MapServer.

For every feature layer (tables are skipped) it writes:
  * a one-row .hyper extract (columns/types from the layer's REST metadata, values from one
    GeoJSON feature) so Tableau can open the workbook; use Extract > Refresh to populate it
  * a federated Esri-connector datasource + one map-layer pane in a single worksheet

Usage:
  python gen_workbook.py https://host/arcgis/rest/services/Folder/Name/MapServer \
      --out out --name Book2 [--layers 0,4,6]

Requires: pip install tableauhyperapi
"""
import argparse, datetime as dt, json, os, random, re, string, sys, time, urllib.parse, urllib.request, uuid
from xml.sax.saxutils import escape


def quoteattr(v):
    """Single-quoted XML attribute value, the way Tableau writes them."""
    return "'" + escape(str(v), {"'": "&apos;", '"': "&quot;"}) + "'"

from tableauhyperapi import (Connection, CreateMode, HyperProcess, Inserter, SqlType,
                             TableDefinition, TableName, Telemetry, escape_string_literal)

# esriFieldType -> (connector remote-type, extract remote-type, local-type, aggregation, hyper type)
TYPES = {
    "esriFieldTypeOID":          (3,   20,  "integer", "Sum",   SqlType.big_int),
    "esriFieldTypeInteger":      (3,   20,  "integer", "Sum",   SqlType.big_int),
    "esriFieldTypeSmallInteger": (2,   20,  "integer", "Sum",   SqlType.big_int),
    "esriFieldTypeDouble":       (5,   5,   "real",    "Sum",   SqlType.double),
    "esriFieldTypeString":       (129, 129, "string",  "Count", SqlType.text),
    "esriFieldTypeGeometry":     (132, 128, "spatial", "Count", SqlType.tabgeography),
    # --- UNVERIFIED guesses: no sample in a real workbook yet. Replace with Tableau's actual output. ---
    "esriFieldTypeDate":         (135, 135, "datetime", "Year", SqlType.timestamp),  # GeoJSON: epoch ms
    "esriFieldTypeBigInteger":   (20,  20,  "integer", "Sum",   SqlType.big_int),
    "esriFieldTypeSingle":       (5,   5,   "real",    "Sum",   SqlType.double),
    "esriFieldTypeGlobalID":     (129, 129, "string",  "Count", SqlType.text),
    "esriFieldTypeGUID":         (129, 129, "string",  "Count", SqlType.text),
}
# Tableau 10 palette, in the order Tableau hands out colors (blue is the implicit default)
PALETTE = ["f28e2b", "e15759", "76b7b2", "59a14f", "edc948", "b07aa1", "ff9da7", "9c755f", "bab0ab"]
DRAW_ORDER = {"esriGeometryPolygon": 0, "esriGeometryPolyline": 1, "esriGeometryPoint": 2}


# Some servers (WAFs) reject urllib's default "Python-urllib" User-Agent with a 403.
HEADERS = {"User-Agent": "Mozilla/5.0 (tableau-maps gen_workbook)"}


# Characters Windows does not allow in file names, plus path separators and control characters.
BAD_NAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def check_name(name):
    """Refuse a --name that could escape the output folder or is not a valid file name."""
    if not name.strip() or name.strip(" .") != name.strip() or ".." in name or BAD_NAME.search(name):
        sys.exit(f"invalid --name {name!r}: use letters, digits, spaces, '-', '_' or parentheses, "
                 "with no slashes, '..', or any of <>:\"|?*")


def check_scheme(url, what="service URL"):
    """Only http(s) URLs are fetched; urllib would otherwise also open file:// or ftp:// URLs."""
    if urllib.parse.urlparse(url).scheme.lower() not in ("http", "https"):
        sys.exit(f"{what} must start with https:// or http://: {url}")


def check_service_error(d, url):
    """Stop with a clear message when the server answers with an error instead of service JSON."""
    if not (isinstance(d, dict) and "error" in d):
        return
    err = d["error"] if isinstance(d["error"], dict) else {"message": str(d["error"])}
    code, msg = err.get("code"), str(err.get("message", "service error"))
    if code in (401, 403, 498, 499) or "token" in msg.lower():
        sys.exit(f"{url} needs sign-in ({code}: {msg}). This skill supports public services only.")
    sys.exit(f"{url} returned an error ({code}: {msg}).")


def get_json(url, _timeout=60, _retries=1, **params):
    """GET and parse JSON; a timeout or connection error is retried once (busy servers often answer the second time)."""
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}", headers=HEADERS)
    for attempt in range(_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=_timeout) as r:
                return json.load(r)
        except (OSError, ValueError):
            if attempt == _retries:
                raise
            time.sleep(1)


def sample_feature(layer_url, timeout=60):
    """One GeoJSON feature for the placeholder row, or {}.

    Some layers reject resultRecordCount ("Pagination is not supported."); then ask for the ids and
    fetch the lowest one by where clause.
    """
    q = dict(where="1=1", outFields="*", returnGeometry="true", f="geojson")
    gj = get_json(f"{layer_url}/query", _timeout=timeout, resultRecordCount=1, **q)
    if gj.get("features"):
        f = gj["features"][0]
        if f.get("geometry") is None:
            # Some layers hold features without shapes; look at a few more for one that has a shape.
            more = get_json(f"{layer_url}/query", _timeout=timeout, resultRecordCount=50, **q)
            f = next((x for x in more.get("features") or [] if x.get("geometry")), f)
        return f
    if "error" not in gj:
        return {}
    time.sleep(1)
    ids = get_json(f"{layer_url}/query", _timeout=timeout, where="1=1", returnIdsOnly="true", f="json")
    if "error" in ids:
        raise ValueError(f"query refused: {ids['error']}")
    if not ids.get("objectIds"):
        return {}
    q["where"] = f"{ids['objectIdFieldName']}={min(ids['objectIds'])}"
    one = get_json(f"{layer_url}/query", _timeout=timeout, **q)
    if "error" in one:
        raise ValueError(f"query refused: {one['error']}")
    return (one.get("features") or [{}])[0]


def wmts_url(service_url):
    """MapServer URL -> its WMTS capabilities URL (only cached services answer it)."""
    return service_url.rstrip("/") + "/WMTS/1.0.0/WMTSCapabilities.xml"


def discover_basemaps(rest_root):
    """Walk <host>/arcgis/rest/services and list cached MapServers that serve WMTS."""
    found = []
    top = get_json(rest_root, f="json")
    for folder in [""] + top.get("folders", []):
        listing = top if not folder else get_json(f"{rest_root}/{folder}", f="json")
        for svc in listing.get("services", []):
            if svc["type"] != "MapServer":
                continue
            url = f"{rest_root}/{svc['name']}/MapServer"
            try:
                meta = get_json(url, f="json")
                if not meta.get("singleFusedMapCache"):
                    continue
                req = urllib.request.Request(wmts_url(url), method="HEAD", headers=HEADERS)
                with urllib.request.urlopen(req, timeout=30) as r:
                    if r.status == 200:
                        found.append((svc["name"], wmts_url(url)))
            except Exception:
                continue
    return found


def service_labels(maps):
    """{service name: short label} for the services in one workbook: drop a trailing _v1 and any leading
    words every service shares (NDFD_SnowFall_v1, NDFD_Ice_v1 -> SnowFall, Ice)."""
    toks = {m: re.sub(r"[_ ]v\d+$", "", m, flags=re.I).replace(" ", "_").split("_") for m in maps}
    common = 0
    if len(toks) > 1:
        for col in zip(*toks.values()):
            if len(set(t.lower() for t in col)) != 1:
                break
            common += 1
    return {m: " ".join(t[common:] if t[common:] else t) for m, t in toks.items()}


def mapsource_xml(url, name):
    q = quoteattr
    u = urllib.parse.urlparse(url)
    port = u.port or (443 if u.scheme == "https" else 80)
    return f"""    <mapsource inline='true' name={q(name)} source-platform='mac' version='18.1'>
      <connection class='OGC-WMTS' description={q(url)} full-url={q(url)} implicit-base='true' inline='true' offline='' port='{port}' server={q(u.hostname)} service={q(u.scheme)} tileset='US/normal' url={q(u.path)} />
      <languages />
      <properties />
      <map-styles />
      <mapsource-defaults version='18.1'>
        <style>
          <style-rule element='map-layer'>
            <format attr='enabled' id='implicit' value='true' />
          </style-rule>
        </style>
      </mapsource-defaults>
      <map-attribution copyright-string={q('© ' + u.hostname)} copyright-url={q(f'{u.scheme}://{u.hostname}')} short-copyright-string='' />
    </mapsource>"""


def tab_id(n=28):
    return "".join(random.choices(string.digits + string.ascii_lowercase, k=n))


def wkt(g):
    """GeoJSON geometry -> WKT (WGS84 lon/lat)."""
    if g is None or not g.get("coordinates"):  # null or empty geometry: the placeholder row gets a NULL
        return None
    t, c = g["type"], g["coordinates"]
    pt = lambda p: f"{p[0]} {p[1]}"
    line = lambda l: "(" + ",".join(pt(p) for p in l) + ")"
    poly = lambda p: "(" + ",".join(line(r) for r in p) + ")"
    if t == "Point":           return f"POINT({pt(c)})"
    if t == "MultiPoint":      return "MULTIPOINT(" + ",".join(f"({pt(p)})" for p in c) + ")"
    if t == "LineString":      return f"LINESTRING{line(c)}"
    if t == "MultiLineString": return "MULTILINESTRING(" + ",".join(line(l) for l in c) + ")"
    if t == "Polygon":         return f"POLYGON{poly(c)}"
    if t == "MultiPolygon":    return "MULTIPOLYGON(" + ",".join(poly(p) for p in c) + ")"
    raise ValueError(f"unsupported geometry {t}")


class Col:
    def __init__(self, f, ordinal):
        self.esri_type = f["type"]
        self.is_geom = self.esri_type == "esriFieldTypeGeometry"
        # Tableau always calls the geometry column "Shape", even for joined layers (xxx.SHAPE)
        self.name = "Shape" if self.is_geom else f["name"]
        self.src_name = f["name"]
        self.length = f.get("length")
        self.ordinal = ordinal  # 0-based
        (self.rt_conn, self.rt_ext, self.local_type, self.agg, self.hyper) = TYPES[self.esri_type]


def ident(name):
    """Quote a column name as a SQL identifier (field names come from the remote service)."""
    return '"' + name.replace('"', '""') + '"'


def build_hyper(path, cols, props, geom, hp):
    if os.path.exists(path):
        os.remove(path)
    with Connection(hp.endpoint, path, CreateMode.CREATE) as c:
        c.catalog.create_schema("Extract")
        td = TableDefinition(TableName("Extract", "Extract"),
                             [TableDefinition.Column(k.name, k.hyper()) for k in cols])
        c.catalog.create_table(td)
        # The geometry goes in as WKT text through a staging table and is converted by Hyper
        # (Tableau rejects raw WKT bytes, and big polygons exceed the max SQL literal length).
        stage = TableDefinition(TableName("Extract", "Stage"),
                                [TableDefinition.Column(k.name, SqlType.text() if k.is_geom else k.hyper())
                                 for k in cols])
        c.catalog.create_table(stage)
        row = []
        for k in cols:
            if k.local_type == "datetime":
                ms = props.get(k.src_name)
                v = (dt.datetime(1970, 1, 1) + dt.timedelta(milliseconds=ms)) if isinstance(ms, (int, float)) else None
            elif k.is_geom:
                v = wkt(geom) if geom else None
            else:
                v = props.get(k.src_name)
            row.append(v)
        with Inserter(c, stage) as ins:
            ins.add_row(row)
            ins.execute()
        sel = ", ".join(f'{ident(k.name)}::geography' if k.is_geom else ident(k.name) for k in cols)
        c.execute_command(f'INSERT INTO "Extract"."Extract" SELECT {sel} FROM "Extract"."Stage"')
        c.execute_command('DROP TABLE "Extract"."Stage"')


def conn_record(k, layer, objid, ordinal):
    x = [f"<remote-name>{escape(k.name)}</remote-name>", f"<remote-type>{k.rt_conn}</remote-type>",
         f"<local-name>[{escape(k.name)}]</local-name>", f"<parent-name>[{escape(layer)}]</parent-name>",
         f"<remote-alias>{escape(k.name)}</remote-alias>", f"<ordinal>{ordinal}</ordinal>",
         f"<local-type>{k.local_type}</local-type>", f"<aggregation>{k.agg}</aggregation>"]
    if k.local_type == "string":
        if k.length:
            x.append(f"<width>{k.length}</width>")
        x.append("<contains-null>true</contains-null>")
        x.append("<attributes><attribute datatype='string' name='TypeIsVarchar'>&quot;true&quot;</attribute></attributes>")
    else:
        x.append("<contains-null>true</contains-null>")
    x.append(f"<object-id>[{escape(layer)}_{objid}]</object-id>")
    return "<metadata-record class='column'>" + "".join(x) + "</metadata-record>"


def ext_record(k, layer, objid):
    x = [f"<remote-name>{escape(k.name)}</remote-name>", f"<remote-type>{k.rt_ext}</remote-type>",
         f"<local-name>[{escape(k.name)}]</local-name>", "<parent-name>[Extract]</parent-name>",
         f"<remote-alias>{escape(k.name)}</remote-alias>", f"<ordinal>{k.ordinal}</ordinal>",
         f"<family>{escape(layer)}</family>", f"<local-type>{k.local_type}</local-type>",
         f"<aggregation>{'Collect' if k.is_geom else k.agg}</aggregation>",
         "<approx-count>1</approx-count>", "<contains-null>true</contains-null>"]
    if k.local_type == "string":
        x.append("<collation flag='0' name='LROOT' />")
    x.append(f"<object-id>[{escape(layer)}_{objid}]</object-id>")
    return "<metadata-record class='column'>" + "".join(x) + "</metadata-record>"


def datasource_xml(ds, now):
    layer, cols, objid = ds["layer"], ds["cols"], ds["objid"]  # layer = the real name the connector looks up
    q = quoteattr
    table = f"[{ds['map']}].[{layer}]"
    rel = f"<relation connection={q(ds['conn'])} name={q(layer)} table={q(table)} type='table' />"
    caption = ds["caption"]
    conn_recs = "\n".join(conn_record(k, layer, objid, i + 1) for i, k in enumerate(cols))
    ext_recs = "\n".join(ext_record(k, layer, objid) for k in cols)
    shape_cap = f"{ds['display']} (Shape)"
    shape_col = "" if ds["table"] else f"      <column caption={q(shape_cap)} datatype='spatial' name='[Shape]' role='measure' type='nominal' />\n"
    ts = now.strftime("%Y-%m-%d %H:%M:%S.000")
    upd = now.strftime("%m/%d/%Y %I:%M:%S %p")
    return f"""    <datasource caption={q(caption)} inline='true' name={q(ds['name'])} version='18.1'>
      <connection class='federated'>
        <named-connections>
          <named-connection caption={q(ds['server'])} name={q(ds['conn'])}>
            <connection authentication='auth-none' class='esri' one-time-sql='' server={q(ds['server'])} />
          </named-connection>
        </named-connections>
        {rel}
        <metadata-records>
{conn_recs}
        </metadata-records>
      </connection>
      <aliases enabled='yes' />
      <column caption='Measure Names' datatype='string' name='[:Measure Names]' role='dimension' type='nominal' />
      <column caption='Measure Values' datatype='real' name='[Multiple Values]' role='measure' type='quantitative' />
{shape_col}      <column caption={q(layer)} datatype='table' name={q(f'[__tableau_internal_object_id__].[{layer}_{objid}]')} role='measure' type='quantitative' />
      <extract count='-1' enabled='true' object-id='' units='records' user-specific='false'>
        <connection access_mode='readonly' authentication='auth-none' author-locale='en_US' class='hyper' dbname={q(ds['hyper'])} default-settings='yes' schema='Extract' sslmode='' tablename='Extract' update-time={q(upd)} username='tableau_internal_user'>
          <relation name='Extract' table='[Extract].[Extract]' type='table' />
          <refresh>
            <refresh-event add-from-file-path={q(caption)} increment-value='%null%' refresh-type='create' rows-inserted='1' timestamp-start={q(ts)} />
          </refresh>
          <metadata-records>
{ext_recs}
          </metadata-records>
        </connection>
      </extract>
      <layout dim-ordering='alphabetic' measure-ordering='alphabetic' show-structure='true' />
      <semantic-values>
        <semantic-value key='[Country].[Name]' value='&quot;United States&quot;' />
      </semantic-values>
      <object-graph>
        <objects>
          <object caption={q(layer)} id={q(f'{layer}_{objid}')}>
            <properties context=''>
              {rel}
            </properties>
            <properties context='extract'>
              <relation name='Extract' table='[Extract].[Extract]' type='table' />
            </properties>
          </object>
        </objects>
      </object-graph>
    </datasource>"""


def worksheet_xml(dss, sheet, basemap=None):
    q = quoteattr
    lst = "\n".join(f"            <datasource caption={q(d['caption'])} name={q(d['name'])} />" for d in dss)
    deps = "\n".join(f"""          <datasource-dependencies datasource={q(d['name'])}>
            <column caption={q(f"{d['display']} (Shape)")} datatype='spatial' name='[Shape]' role='measure' type='nominal' />
            <column-instance column='[Shape]' derivation='Collect' name='[clct:Shape:nk]' pivot='key' type='nominal' />
          </datasource-dependencies>""" for d in dss)
    panes = ["""          <pane id='1' selection-relaxation-option='selection-relaxation-allow'>
            <view>
              <breakdown value='auto' />
            </view>
            <mark class='Automatic' />
          </pane>"""]
    pid = 0
    for i, d in enumerate(dss):
        if pid == 1:
            pid = 2
        col = f"[{d['name']}].[clct:Shape:nk]"
        style = ""
        if i > 0:
            style = f"""
            <style>
              <style-rule element='mark'>
                <format attr='mark-color' value='#{PALETTE[(i - 1) % len(PALETTE)]}' />
              </style-rule>
            </style>"""
        hidden = "" if d.get("visible", True) else " hidden='true'"
        panes.append(f"""          <pane generated-title={q(f"{d['display']} (Shape)")}{hidden} id='{pid}' selection-relaxation-option='selection-relaxation-allow'>
            <view>
              <breakdown value='auto' />
            </view>
            <mark class='Automatic' />
            <encodings>
              <lod column={q(col)} />
              <geometry column={q(col)} />
            </encodings>
            <customized-tooltip>
              <formatted-text>
                <run bold='true'>&lt;Layer Name&gt;</run>
                <run>Æ&#10;</run>
                <run>&lt;All Fields&gt;</run>
              </formatted-text>
            </customized-tooltip>{style}
          </pane>""")
        pid += 1
    p = dss[0]["name"]
    maplayer_rule = ("\n          <style-rule element='map-layer'>\n"
                     "            <format attr='enabled' id='implicit' value='true' />\n"
                     "          </style-rule>") if basemap else ""
    return f"""    <worksheet name={q(sheet)}>
      <table>
        <view>
          <datasources>
{lst}
          </datasources>
          <mapsources>
            <mapsource name={q(basemap or 'Tableau')} />
          </mapsources>
{deps}
          <aggregation value='true' />
        </view>
        <style>{maplayer_rule}
          <style-rule element='map'>
            <format attr='washout' value='0' />
          </style-rule>
        </style>
        <panes customization-axis='layer'>
{chr(10).join(panes)}
        </panes>
        <rows>[{p}].[Latitude (generated)]</rows>
        <cols>[{p}].[Longitude (generated)]</cols>
      </table>
      <simple-id uuid='{{{str(uuid.uuid4()).upper()}}}' />
    </worksheet>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("server", nargs="+", metavar="SERVICE_URL[#ID,ID]",
                    help="MapServer or FeatureServer URL, e.g. https://host/arcgis/rest/services/F/N/MapServer. "
                         "Give several to combine services in one workbook (first = bottom of the map); a "
                         "'#0,4,6' suffix picks layer ids of that service, no suffix = all its feature layers")
    ap.add_argument("--out", default="out")
    ap.add_argument("--name", default="Book2")
    ap.add_argument("--layers", help="comma-separated layer ids (default: all feature layers)")
    ap.add_argument("--group", action="append", metavar="ID|NAME|PATH",
                    help="only layers under this group layer (any depth); repeatable. A group id, a name, or a "
                         "path such as 'Heat Exposure (deg F)/Atlanta' when a name is ambiguous")
    ap.add_argument("--twb-dir", help="where the .twb goes (default: <out>); refuses to overwrite an existing file")
    ap.add_argument("--hyper-dir", help="where .hyper files go (default: <out>/Datasources)")
    ap.add_argument("--basemap", metavar="WMTS_URL",
                    help="WMTS capabilities URL for the background map. Tableau only keeps the "
                         "map source the sheet uses, so only one is written")
    ap.add_argument("--probe-timeout", type=float, default=20,
                    help="seconds allowed for a layer's metadata and one-row probe; a layer that fails or is "
                         "slower is skipped (public-looking servers often restrict some layers)")
    ap.add_argument("--order", choices=["esri", "geometry"], default="esri",
                    help="layer stacking, bottom to top: esri = service layer order (default), "
                         "geometry = polygons, then lines, then points")
    ap.add_argument("--visibility", choices=["esri", "all"], default="esri",
                    help="esri = hide (pane hidden='true') layers the service hides by default, "
                         "including layers under a hidden group; all = show every layer")
    ap.add_argument("--sheet-name", metavar="TEXT",
                    help="name of the sheet, shown on its tab and as the view title (default: '<service or --name> - "
                         "refresh extracts to load data'; pass a translation when the user does not speak English)")
    ap.add_argument("--label-service", choices=["dups", "all", "none"], default="dups",
                    help="prefix layer display names with a short service label (NDFD_SnowFall_v1 -> SnowFall): "
                         "dups = only layers whose name occurs in more than one service (default), all, none")
    ap.add_argument("--discover-basemaps", action="store_true",
                    help="list cached MapServers serving WMTS on the same host, then exit")
    a = ap.parse_args()
    check_name(a.name)
    if a.basemap:
        check_scheme(a.basemap, "--basemap URL")

    servers = []  # [(service url, layer ids picked with '#' or None)]
    for arg in a.server:
        url, _, picked = arg.partition("#")
        check_scheme(url)
        # service names can contain spaces; encode once (also if the caller already did) so every layer URL is valid
        url = urllib.parse.quote(urllib.parse.unquote(url), safe=":/")
        servers.append((url.rstrip("/"), {int(x) for x in picked.split(",")} if picked else None))
    multi = len(servers) > 1
    if multi and (a.layers or a.group):
        sys.exit("with several services, pick layers per service with URL#0,4,6; --layers and --group need a single service")
    server = servers[0][0]
    if a.discover_basemaps:
        root_url = server.split("/rest/services")[0] + "/rest/services"
        for name, url in discover_basemaps(root_url):
            print(f"{name}\n  --basemap {url}")
        return
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)  # also holds hyperd.log
    hdir = os.path.abspath(a.hyper_dir or os.path.join(out, "Datasources"))
    os.makedirs(hdir, exist_ok=True)
    dropped = []  # layers that were selected but could not be imported, reported in the final summary

    want = {int(x) for x in a.layers.split(",")} if a.layers else None

    def collect_layers(service_url, want):
        """Feature layers of one MapServer/FeatureServer, with _server/_map/_visible filled in."""
        root = get_json(service_url, f="json")
        check_service_error(root, service_url)
        # The relation is [<service name>].[<layer>]; the Esri connector looks the service up by the
        # last path segment before /MapServer (no folder). root["mapName"] can differ (e.g. "Layers").
        map_name = urllib.parse.unquote(service_url.rsplit("/", 2)[-2])
        by_id = {l["id"]: l for l in root["layers"]}

        def visible(lid):
            """Esri shows a layer only if it and every parent group are on by default."""
            while lid is not None and lid in by_id:
                if not by_id[lid].get("defaultVisibility", True):
                    return False
                lid = by_id[lid].get("parentLayerId", -1)
                lid = None if lid == -1 else lid
            return True

        def path(lid):
            names = []
            while lid in by_id:
                names.append(by_id[lid]["name"].strip())
                lid = by_id[lid].get("parentLayerId", -1)
            return names[::-1]

        in_group = None
        if a.group:
            in_group = set()
            for spec in a.group:
                if spec.isdigit() and int(spec) in by_id:
                    roots = [int(spec)]
                else:
                    parts = [x.strip().lower() for x in spec.split("/")]
                    roots = [g["id"] for g in root["layers"] if g.get("subLayerIds")
                             and [x.lower() for x in path(g["id"])][-len(parts):] == parts]
                if not roots:
                    sys.exit(f"no group layer matches --group {spec!r}")
                if len(roots) > 1:
                    sys.exit(f"--group {spec!r} is ambiguous; use an id or a longer path. Matches: "
                             + "; ".join(f"{r} = {'/'.join(path(r))}" for r in roots))
                stack = [roots[0]]
                while stack:
                    g = by_id[stack.pop()]
                    in_group.add(g["id"])
                    stack.extend(g.get("subLayerIds") or [])

        found, skipped = [], {}
        for l in root["layers"] + root.get("tables", []):
            if want is not None and l["id"] not in want:
                continue
            if in_group is not None and l["id"] not in in_group:
                continue
            if l.get("subLayerIds"):  # a group layer holds no features itself
                continue
            try:
                m = get_json(f"{service_url}/{l['id']}", _timeout=a.probe_timeout, f="json")
            except (OSError, ValueError) as e:
                print(f"  SKIP {map_name} layer {l['id']} {l['name']}: metadata failed ({e})")
                dropped.append(l["name"])
                continue
            if m.get("type") not in ("Feature Layer", "Table"):
                skipped[m.get("type")] = skipped.get(m.get("type"), 0) + 1
                continue
            # A table is a layer without geometry: it becomes a datasource but not a map layer.
            m["_table"] = m["type"] == "Table" or not m.get("geometryType")
            # Hosted (ArcGIS Online) layers leave the geometry out of fields[]; MapServer layers list it.
            if not m["_table"] and not any(f["type"] == "esriFieldTypeGeometry" for f in m["fields"]):
                m["fields"] = [{"name": "Shape", "type": "esriFieldTypeGeometry", "alias": "Shape"}] + m["fields"]
            # A service can mislabel an ordinary field (e.g. a date) as geometry; keep only the real one,
            # which is named like "shape" / "SHAPE" / "xxx.SHAPE".
            geoms = [f for f in m["fields"] if f["type"] == "esriFieldTypeGeometry"]
            if len(geoms) > 1:
                real = next((f for f in geoms if f["name"].lower().rsplit(".", 1)[-1] == "shape"), geoms[0])
                for f in geoms:
                    if f is not real:
                        print(f"  WARNING {map_name} layer {l['id']}: ignoring extra geometry-typed field {f['name']}")
                m["fields"] = [f for f in m["fields"] if f is real or f["type"] != "esriFieldTypeGeometry"]
            m.update(_visible=a.visibility == "all" or visible(l["id"]), _server=service_url, _map=map_name)
            found.append(m)
        if skipped:
            print(f"  NOTE {map_name}: not importable, skipped " + ", ".join(f"{n} x {t}" for t, n in skipped.items()))
        return found

    metas = []
    for si, (service_url, picked) in enumerate(servers):
        for m in collect_layers(service_url, picked if picked is not None else want):
            m["_service_index"] = si
            metas.append(m)
    # <pane> order in the worksheet is the draw order, first = bottom. ArcGIS draws a higher layer id
    # underneath a lower one, so descending id reproduces the Esri map. Services keep the order given.
    if a.order == "esri":
        metas.sort(key=lambda m: (m["_service_index"], -m["id"]))
    else:
        metas.sort(key=lambda m: (DRAW_ORDER.get(m.get("geometryType"), 9), m["_service_index"], -m["id"]))
    if not metas:
        sys.exit("no feature layers selected")

    by_map = {}
    for m in metas:
        by_map.setdefault(m["_map"], set()).add(m["_server"])
    for svc, urls in sorted(by_map.items()):
        if len(urls) > 1:
            print(f"  WARNING {len(urls)} services are named {svc!r}: {', '.join(sorted(urls))}; "
                  "the Esri connector finds a service by that name alone, so only one of them will refresh correctly")
    names = [(m["_map"], m["name"]) for m in metas]
    for svc, n in sorted({k for k in names if names.count(k) > 1}):
        ids = [m["id"] for m in metas if (m["_map"], m["name"]) == (svc, n)]
        print(f'  WARNING {svc} layers {ids} are all named "{n}"; the Esri connector looks layers up by name')
    # Display names (captions, pane titles, tooltip) can carry the service; the relation name never does.
    labels = service_labels({m["_map"] for m in metas})
    dup_names = {n for n in {m["name"] for m in metas}
                 if len({x["_map"] for x in metas if x["name"] == n}) > 1}

    def display_name(m):
        if a.label_service == "all" or (a.label_service == "dups" and m["name"] in dup_names):
            return f"{labels[m['_map']]} - {m['name']}"
        return m["name"]

    now = dt.datetime.now(dt.timezone.utc)
    dss = []

    def hyper_path(m):
        base = f"{m['id']:02d}_{re.sub(r'[^A-Za-z0-9]+', '-', m['name']).strip('-')[:60]}"
        if multi:  # layer ids repeat across services
            base = f"s{m['_service_index']}_{re.sub(r'[^A-Za-z0-9]+', '-', m['_map']).strip('-')[:40]}_{base}"
        return os.path.join(hdir, base + ".hyper")

    # The placeholder extracts would overwrite the data of an earlier import (refreshed, full-size) that
    # lives in the same folder, leaving that workbook with one-row extracts.
    planned = [hyper_path(m) for m in metas]
    if len(set(planned)) != len(planned):
        sys.exit("two layers would write the same extract file; rerun with fewer layers or a different --name")
    clash = [p for p in planned if os.path.exists(p)]
    if clash:
        sys.exit(f"{len(clash)} extract(s) already exist, e.g. {clash[0]}\n"
                 "An earlier import uses this folder; pass a different --hyper-dir (or --name) so it is not overwritten")
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
                      parameters={"log_dir": out}) as hp:
        for m in metas:
            try:
                feat = sample_feature(f"{m['_server']}/{m['id']}", a.probe_timeout)
            except (OSError, ValueError) as e:
                print(f"  SKIP layer {m['id']} {m['name']}: one-row probe failed ({e})")
                dropped.append(m["name"])
                continue
            if feat and not m["_table"] and feat.get("geometry") is None:
                # A layer typed as polygon/line/point whose features have no shapes would show a red
                # error on the map, so treat it as a table.
                print(f"  NOTE layer {m['id']} {m['name']}: sampled features have no geometry; adding it as a table")
                m["_table"] = True
                m["fields"] = [f for f in m["fields"] if f["type"] != "esriFieldTypeGeometry"]
            usable = [f for f in m["fields"] if f["type"] in TYPES]
            for f in m["fields"]:
                if f["type"] not in TYPES:
                    print(f"  WARNING layer {m['id']}: skipping field {f['name']} (unsupported {f['type']})")
            cols = [Col(f, i) for i, f in enumerate(usable)]
            name = f"federated.{tab_id()}"
            hyper = hyper_path(m)
            build_hyper(hyper, cols, feat.get("properties") or {}, feat.get("geometry"), hp)
            # Tableau rejects two datasources with the same caption, and ArcGIS allows duplicate layer names
            label = f"{display_name(m)} [layer {m['id']}]" if names.count((m["_map"], m["name"])) > 1 else display_name(m)
            dss.append(dict(layer=m["name"], display=display_name(m), caption=f"{label} ({m['_server'].split('://', 1)[1]})", cols=cols, name=name, conn=f"esri.{tab_id()}", hyper=hyper,
                            objid=uuid.uuid4().hex.upper(), server=m["_server"], map=m["_map"],
                            visible=m["_visible"], table=m["_table"]))
            print(f"  layer {m['id']:>2} {m['name']}: {len(cols)} cols, feature={'yes' if feat else 'NO ROWS'}")

    if not dss:
        sys.exit("every selected layer was skipped; nothing to write")
    maps = [d for d in dss if not d["table"]]
    if not maps:
        sys.exit("no layers with geometry; nothing to put on a map")
    if not any(d["visible"] for d in maps):
        # panes are listed bottom to top; the last one is the top-drawn (lowest id) layer
        maps[-1]["visible"] = True
        print(f"  NOTE every layer is hidden by default in the service; showing {maps[-1]['display']!r} so the map is not blank")
    # The extracts are one-row placeholders until the user refreshes them, so say so on the tab and the view title.
    sheet = a.sheet_name or f"{a.name if multi else maps[0]['map']} - refresh extracts to load data"
    bm_name = a.basemap.rstrip("/").split("/MapServer/WMTS")[0].rsplit("/", 1)[-1] if a.basemap else None
    bm_xml = mapsource_xml(a.basemap, bm_name) if a.basemap else "    <mapsource name='Tableau' />"
    xml = f"""<?xml version='1.0' encoding='utf-8' ?>

<workbook original-version='18.1' source-build='2026.3.0 (20263.26.0927.0033)' source-platform='mac' version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <document-format-change-manifest>
    <AnimationOnByDefault />
    <EsriConnectorCanBeFederated />
    <Layers />
    <LayersPerPaneSpecPrimaryDS />
    <MarkAnimation />
    <ObjectModelEncapsulateLegacy />
    <ObjectModelExtractV2 />
    <ObjectModelTableType />
    <SchemaViewerObjectModel />
    <SheetIdentifierTracking />
    <VConnDownstreamExtractsWithWarnings />
    <WindowsPersistSimpleIdentifiers />
  </document-format-change-manifest>
  <preferences>
    <preference name='ui.encoding.shelf.height' value='24' />
    <preference name='ui.shelf.height' value='26' />
  </preferences>
  <datasources>
{chr(10).join(datasource_xml(d, now) for d in dss)}
  </datasources>
  <mapsources>
{bm_xml}
  </mapsources>
  <worksheets>
{worksheet_xml(maps, sheet, bm_name)}
  </worksheets>
  <windows source-height='93'>
    <window class='worksheet' maximized='true' name={quoteattr(sheet)}>
      <cards>
        <edge name='left'>
          <strip size='160'>
            <card type='pages' />
            <card type='filters' />
            <card type='marks' />
          </strip>
        </edge>
        <edge name='top'>
          <strip size='2147483647'>
            <card type='columns' />
          </strip>
          <strip size='2147483647'>
            <card type='rows' />
          </strip>
          <strip size='2147483647'>
            <card type='title' />
          </strip>
        </edge>
      </cards>
      <viewpoint>
        <default-map-tool-selection tool='1' />
      </viewpoint>
      <simple-id uuid='{{{str(uuid.uuid4()).upper()}}}' />
    </window>
  </windows>
</workbook>
"""
    twb_dir = os.path.abspath(a.twb_dir or out)
    os.makedirs(twb_dir, exist_ok=True)
    twb = os.path.join(twb_dir, f"{a.name}.twb")
    if os.path.exists(twb):
        sys.exit(f"{twb} already exists (it may be open in Tableau); choose another --name")
    with open(twb, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"wrote {twb} ({len(maps)} map layers, {len(dss) - len(maps)} tables); hyper files in {hdir}")
    if dropped:
        print(f"WARNING: {len(dropped)} layer(s) NOT imported: {', '.join(dropped)}. Re-run, or raise --probe-timeout.")
    else:
        print(f"All {len(dss)} selected layers imported.")


if __name__ == "__main__":
    main()
