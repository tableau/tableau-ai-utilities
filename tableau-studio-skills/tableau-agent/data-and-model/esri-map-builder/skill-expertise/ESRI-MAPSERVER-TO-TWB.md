# ArcGIS MapServer -> Tableau workbook (Map Layers): reference

Read this only when debugging a failed import or editing the generated XML. Verified end to end in Tableau
Desktop and Tableau Studio: the generated workbook opens with no errors, and **Extract > Refresh All Extracts**
fills every layer on the map.

## Run it

```
python3 skill-expertise/check_driver.py                       # Esri JDBC driver installed? (stdlib only)
python3 skill-expertise/list_layers.py <service|folder|root URL> [--open REGEX]   # what is there (stdlib only)
python3 skill-expertise/gen_workbook.py <MapServer URL>[#0,4,6] [<2nd service URL>[#ids] ...] --out out --name Book2 \
    [--layers 0,4,6] [--basemap <WMTSCapabilities.xml URL>] [--hyper-dir DIR]
python3 skill-expertise/gen_workbook.py <MapServer URL> --discover-basemaps
```

`check_driver.py` and `list_layers.py` use only the standard library. `gen_workbook.py` needs `tableauhyperapi`;
follow SKILL.md step 3 and 4 to find an interpreter that has it, and ask the user before creating a venv or
installing anything. Hyper writes `hyperd.log` into `--out`.

## The approach

Per feature layer the generator writes:

1. **A federated Esri datasource**: `<connection class='federated'>` with a named-connection
   `class='esri' server='<MapServer URL>'`, relation `[<service name>].[<layer name>]`, connector-side
   `metadata-records`, an `<extract>` block with extract-side `metadata-records`, and an `object-graph`.
2. **A one-row `.hyper` extract** at the path in `<extract><connection dbname=...>`. Tableau needs the file to
   exist at open; the single row is replaced by Refresh. (A missing file gives an error plus a file picker.)
3. **A map-layer pane** in one worksheet: `<pane>` with `lod` + `geometry` encodings on
   `[<ds>].[clct:Shape:nk]`, `customization-axis='layer'`. Rows/cols are the first datasource's
   `Latitude (generated)` / `Longitude (generated)`.

Sources of truth:

| Need | REST call |
|---|---|
| Layer list, geometry type, default visibility | `MapServer?f=pjson` (no fields here) |
| Field names/types/lengths | `MapServer/{id}?f=pjson` |
| One sample row incl. geometry (WGS84) | `MapServer/{id}/query?where=1=1&outFields=*&returnGeometry=true&resultRecordCount=1&f=geojson` |
| Feature count | `MapServer/{id}/query?where=1=1&returnCountOnly=true&f=json` |

## Type mapping (esriFieldType -> Tableau)

| Esri | connector remote-type | extract remote-type | local-type | agg | Hyper type |
|---|---|---|---|---|---|
| OID, Integer | 3 | 20 | integer | Sum | BIG_INT |
| SmallInteger | 2 | 20 | integer | Sum | BIG_INT |
| Double | 5 | 5 | real | Sum | DOUBLE |
| String | 129 | 129 | string | Count | TEXT |
| Geometry | 132 | 128 | spatial | Count (conn) / Collect (extract) | TABLEAU.TABGEOGRAPHY |
| Date | 135 | 135 | datetime | Year | TIMESTAMP |

- Strings: connector record gets `<width>` = field length and `TypeIsVarchar`; extract record gets
  `<collation flag='0' name='LROOT' />`.
- Ordinals: connector 1-based, extract 0-based. Field order follows the REST `fields[]` order.
- Date and GlobalID refresh fine. BigInteger, Single, and GUID are mapped but unverified. Blob, Raster, and XML
  fields are skipped with a warning.
- Take types from `fields[]`, never from the sample row: the first row can be mostly NULL.

## XML details that matter

- **Schema errors on open** (`'user-specific' is not declared for element 'extract'`, `simple-id` not allowed in
  `window`): Tableau validates against a schema gated by `<document-format-change-manifest>`. Keep the full
  flag list from a real workbook (`AnimationOnByDefault`, `EsriConnectorCanBeFederated`, `Layers`,
  `LayersPerPaneSpecPrimaryDS`, `MarkAnimation`, `ObjectModel*`, `SchemaViewerObjectModel`,
  `SheetIdentifierTracking`, `VConnDownstreamExtractsWithWarnings`, `WindowsPersistSimpleIdentifiers`).
- **`invalid geography format: not a spatial stream`** (on open and on Refresh): Hyper's Inserter accepts raw
  WKT bytes for `TABGEOGRAPHY` without validating, but Tableau rejects them. Let Hyper encode with
  `'<WKT>'::geography`. Large polygons exceed the maximum SQL literal length, so load WKT as TEXT into a staging
  table via the Inserter, then `INSERT ... SELECT "Shape"::geography`.
- **Relation schema is the service name, not `mapName`.** Use the URL segment before `/MapServer` (folder
  dropped). Using `root["mapName"]` can fail with `"selectedService" is null` when the two differ.
- **Geometry column name** is always `Shape` in Tableau metadata, even when Esri names it something like
  `library.recreation.PARK_area.SHAPE` (joined layers). Each layer's `[Shape]` column is captioned
  `<layer name> (Shape)` so layers are distinguishable on the map.
- **One geometry column only.** Some services label an ordinary field as geometry, giving
  `column 'Shape' specified more than once`. The generator keeps one geometry field (prefers a name whose last
  dotted part is `shape`) and warns about the rest.
- **Hosted (FeatureServer) layers have no geometry field in `fields[]`; MapServer layers do.** The generator adds a
  synthetic `Shape` field when none is listed; otherwise Tableau reports "(Shape) does not exist in the database"
  until the first refresh.
- **Joined layers** carry prefixed field names (`schema.table.Field`). The joins are server-side; keep the names
  verbatim. GeoJSON `properties` use the same prefixed keys.
- **Attribute quoting**: Tableau writes single-quoted attributes; the generator matches that.
- **Duplicate layer names.** Tableau rejects two datasources with the same caption, so captions are
  `<layer> (<host/path>)`, with ` [layer N]` added for duplicates. The Esri connector resolves layers by name only,
  so a duplicate-named layer can receive the first match's data.

## Layer order and visibility

- The order of `<pane>` elements inside `<panes customization-axis='layer'>` **is the draw order, first =
  bottom** (after the empty `id='1'` "All" pane). The bottom pane's datasource drives the lat/long axes.
- Esri draws a higher layer id underneath a lower one, so the default `--order esri` sorts by descending id.
  `--order geometry` puts polygons, then lines, then points. Users can reorder on the Marks card.
- A hidden layer is `hidden='true'` on its `<pane>`; datasource, columns, and encodings stay so the user can switch
  it back on. The generator maps Esri `defaultVisibility` (a layer is hidden if it or any parent group is hidden).
  If every layer is hidden by default, the top-drawn layer is shown so the map isn't blank.
- Do not confuse this with `map-layer` / `map-data-layer` style rules; those are Tableau's built-in background
  and demographic layers.

## Basemaps (WMTS)

- A basemap is one inline `<mapsource>` with `<connection class='OGC-WMTS' ...>`, plus `mapsource-defaults` with a
  `map-layer` style rule; the worksheet references it by `<mapsource name=.../>`.
- **Tableau saves only the mapsource the sheet uses**, so the generator writes one. One basemap per sheet.
- WMTS exists only for **cached** MapServers (`singleFusedMapCache: true`). `--discover-basemaps` walks
  `/rest/services` and its folders and keeps cached services whose `.../MapServer/WMTS/1.0.0/WMTSCapabilities.xml`
  returns 200.
- Attribution defaults to `© <host>`.

## Service and server behavior

- **MapServer and FeatureServer URLs both work.** ArcGIS Online (`services*.arcgis.com/<orgid>/arcgis/rest/services`)
  is flat: every FeatureServer is a service with one or many layers, and the root reports no folders. Give the
  generator the FeatureServer, not the org root. Path case doesn't matter.
- **Group layers** (no geometry, `subLayerIds` lists children) are organizers; the generator skips them and imports
  their sublayers. Group nesting is not carried into the workbook.
- **Tables** (layers without geometry) become datasources with no `Shape` column and are left off the map. A layer
  typed polygon/line/point whose sampled features all lack geometry is also added as a table.
- **Raster and image layers** cannot be imported and are skipped with a `NOTE`.
- **Spatial reference:** `f=geojson` returns WGS84, so no reprojection is needed for the placeholders.
- **Some servers block Python's default User-Agent** (HTTP 403); the scripts send a browser-style one.
- **Some layers reject `resultRecordCount`** ("Pagination is not supported"). The sample-row fetch falls back to
  `returnIdsOnly` plus `where OBJECTID=<min id>`.
- **Restricted or slow layers** on public-looking servers fail or time out. Probes use `--probe-timeout`, retry
  once, then `SKIP` the layer; the run ends with `All N selected layers imported.` or `WARNING: N layer(s) NOT
  imported: ...`.
- **Names with spaces or parentheses** are percent-encoded once in both scripts; the relation keeps the decoded name.
- Two selected services with the same last path segment print a WARNING, because the connector finds a service by
  that name alone.

## Files, extracts, and refresh

- The skill writes `<Repository>/Workbooks/<name>.twb` and `<Repository>/Datasources/<name>/NN_<layer>.hyper`
  (`<service>_NN_<layer>.hyper` with several services). One subfolder per import keeps names from colliding.
- The script refuses to overwrite an existing `.twb` or any existing `.hyper` it would write, because an earlier
  import's refreshed extracts would be replaced by one-row placeholders. Use a new `--name` / `--hyper-dir`.
- Placeholders stay at one row on purpose, so users don't think they already have the data. The final message must
  say: placeholder, run Extract > Refresh All Extracts, then Save.
- **Refreshed data is not on disk until you save.** While the workbook is open, refreshed extracts live in Tableau's
  temp storage. Saving writes them to the absolute `dbname` paths, so a plain `.twb` works. Never delete or rewrite
  the output folder of an open workbook.
- Hyper files have a 64 KB minimum, so small refreshed layers look the same size as placeholders.
- **Big or slow layers** (hundreds of thousands of features, slow servers) should be refreshed individually; small
  municipalities can Refresh All. A 50-layer service can take about 20 minutes and a few hundred MB.
- **Canceling during a refresh** can leave a bad session ("Missing connection name in relation"). Reopen the saved
  file.
- **Features with no geometry** can crash Tableau Studio on Refresh with Esri driver 3.2.0. Detect them by comparing
  `returnCountOnly` with and without a whole-world envelope filter (`geometry=-180,-90,180,90`). Refresh such a
  layer on its own, or skip it.

## Choosing layers (list_layers.py) and several services

- ArcGIS Online owners organize by name prefix (`NDFD_...`, `Tax_Parcels_...`); on-prem servers also have folders
  and group layers (`--group`). Layer descriptions and web maps (Portal API) are not used.
- `list_layers.py` prints, per service, `id, name, geometry, group path, flags` (`hidden`, `table`, `group`) and
  name-prefix clusters. A folder with more than `--max-services` (12) services prints only a name index; `--open
  REGEX` opens matches (up to `--open-limit`, 40). Clusters are hints; read the whole name list.
- `gen_workbook.py` takes several `SERVICE_URL[#id,id]` arguments (first = bottom of the map). `--layers` and
  `--group` work only with a single service.
- **Display names vs relation names.** The relation must keep the real layer name. Only display text changes:
  `--label-service dups` (default) prefixes `<service label> - ` when a layer name occurs in more than one selected
  service; `all` always; `none` never.
- The sheet is named `<service> - refresh extracts to load data` (or after `--name` with several services);
  `--sheet-name` overrides it, for example with a translation.
- Each pane's tooltip is a bold `<Layer Name>`, a line break, and `<All Fields>`, so dragged fields appear at once.

## Esri driver

The connector needs the Esri JDBC driver jar in the Tableau Drivers folder (macOS `~/Library/Tableau/Drivers`;
Windows `%ProgramFiles%\Tableau\Drivers`; Linux `/opt/tableau/tableau_driver/jdbc`, unverified). Tableau scans
every jar there, so the filename doesn't matter; `check_driver.py` recognizes it by
`Implementation-Title: esri-jdbc-driver` and otherwise prints the download page and target folder. The skill never
downloads, copies, or bundles the jar; the user installs it and the agent checks again. No restart is needed.

## Known limits

- Esri renderer colors and scale ranges are not applied (layers cycle the Tableau 10 palette).
- Output is a `.twb` with absolute `.hyper` paths; `.twbx` packaging is not implemented.
- Sign-in services (`auth-none` only), MultiPoint, and ImageServer URLs are not supported or untested.
- Probing is serial, so a service with very many layers is slow before the refresh starts.
- The generator must stay compatible with Python 3.9.
