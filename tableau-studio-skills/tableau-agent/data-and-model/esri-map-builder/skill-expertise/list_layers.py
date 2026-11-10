#!/usr/bin/env python3
"""List the layers of ArcGIS REST services so layers can be chosen by meaning, before generating.

Standard library only (Python 3.9+), read-only, no venv needed.

  python3 list_layers.py URL [URL ...] [--max-services 12] [--open REGEX] [--timeout 20]

URL is a MapServer/FeatureServer, or a services folder / root (".../rest/services[/Folder]").
A folder with at most --max-services services (default 12) has every service opened. A bigger one
(an ArcGIS Online org can hold hundreds) is not opened: you get an index of service names with
name prefix clusters; rerun with --open REGEX to open the services whose names match (at most
--open-limit). A root also lists its folder names.

Per service: one line per layer "id<TAB>name<TAB>geometry<TAB>group path<TAB>flags" (geometry only
when the service lists it; flags: hidden = off by default, table, group), then "name prefix
clusters": 3+ layers whose names start with the same word (EPL_Parks, EPL_Trails, ...). ArcGIS
Online services are flat, and prefixes are how their owners organize layers.
"""
import argparse, collections, http.client, json, re, sys, urllib.parse, urllib.request

FAILED = []  # URLs that could not be read; main() exits 1 if any
HEADERS = {"User-Agent": "Mozilla/5.0 (tableau-maps list_layers)"}
SPLIT = re.compile(r"\s*[_:|/]+\s*|\s+-\s+|[-]")


def norm(url):
    """Percent-encode spaces etc. in a service URL, whether or not it already is encoded."""
    return urllib.parse.quote(urllib.parse.unquote(url), safe=":/")


def get_json(url, timeout):
    with urllib.request.urlopen(urllib.request.Request(norm(url) + "?f=json", headers=HEADERS), timeout=timeout) as r:
        d = json.load(r)
    if isinstance(d, dict) and "error" in d:
        raise ValueError(d["error"].get("message", "service error"))
    return d


def group_path(by_id, lid):
    names = []
    lid = by_id[lid].get("parentLayerId", -1)
    while lid in by_id:
        names.append(by_id[lid]["name"].strip())
        lid = by_id[lid].get("parentLayerId", -1)
    return "/".join(names[::-1])


def prefixes(names):
    """{prefix: [names]} for first words shared by 3+ layers, unless one word covers every layer."""
    firsts = collections.defaultdict(list)
    for n in names:
        parts = [p for p in SPLIT.split(n.strip()) if p]
        if len(parts) > 1 and len(parts[0]) >= 2:
            firsts[parts[0].lower()].append(n)
    return {k: v for k, v in firsts.items() if len(v) >= 3 and len(v) < len(names)}


def show_service(url, timeout):
    try:
        root = get_json(url, timeout)
    except (OSError, ValueError, http.client.HTTPException) as e:
        print(f"# {url}\n  FAILED: {e}\n")
        FAILED.append(url)
        return
    layers = root.get("layers", []) + root.get("tables", [])
    by_id = {l["id"]: l for l in root.get("layers", [])}
    print(f"# {url}  ({len(layers)} layers/tables)")
    for l in layers:
        flags = []
        if l.get("subLayerIds"):
            flags.append("group")
        if l.get("defaultVisibility") is False:
            flags.append("hidden")
        if l in root.get("tables", []):
            flags.append("table")
        gp = group_path(by_id, l["id"]) if l["id"] in by_id else ""
        print("\t".join([str(l["id"]), l["name"].strip(), l.get("geometryType", "").replace("esriGeometry", ""),
                         gp, ",".join(flags)]))
    leafs = [l["name"] for l in layers if not l.get("subLayerIds")]
    clusters = prefixes(leafs)
    if clusters:
        print("name prefix clusters:")
        for k, v in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
            print(f"  {k}: {len(v)} layers, e.g. {', '.join(v[:3])}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--max-services", type=int, default=12,
                    help="open every service of a folder only if it has at most this many (default 12)")
    ap.add_argument("--open", metavar="REGEX", help="open the folder's services whose name matches (case-insensitive)")
    ap.add_argument("--open-limit", type=int, default=40, help="most services --open will open (default 40)")
    ap.add_argument("--timeout", type=float, default=20)
    a = ap.parse_args()
    for url in (norm(u.rstrip("/")) for u in a.urls):
        if urllib.parse.urlparse(url).scheme.lower() not in ("http", "https"):
            print(f"# {url}\n  FAILED: only https:// or http:// URLs are supported\n")
            FAILED.append(url)
            continue
        if re.search(r"/(MapServer|FeatureServer)$", url):
            show_service(url, a.timeout)
            continue
        try:
            d = get_json(url, a.timeout)
        except (OSError, ValueError) as e:
            print(f"# {url}\n  FAILED: {e}\n")
            FAILED.append(url)
            continue
        root = url.split("/rest/services")[0] + "/rest/services"
        svcs = [s for s in d.get("services", []) if s["type"] in ("MapServer", "FeatureServer")]
        if d.get("folders"):
            print(f"# {url}\nfolders (rerun with one of these): " + ", ".join(d["folders"]) + "\n")
        names = [x["name"] for x in svcs]
        if a.open:
            hit = [x for x in svcs if re.search(a.open, x["name"], re.I)]
        elif len(svcs) <= a.max_services:
            hit = svcs
        else:
            hit = []
            print(f"# {url}: {len(svcs)} services, not opened. Rerun with --open REGEX (e.g. a cluster name).")
            clusters = prefixes(names)
            if clusters:
                print("service name prefix clusters:")
                for k, v in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
                    print(f"  {k}: {len(v)} services, e.g. {', '.join(v[:3])}")
            clustered = {n for v in clusters.values() for n in v}
            print("other services: " + ", ".join(n for n in names if n not in clustered) + "\n")
        for x in hit[:a.open_limit]:
            show_service(norm(f"{root}/{x['name']}/{x['type']}"), a.timeout)
        if len(hit) > a.open_limit:
            print(f"{len(hit) - a.open_limit} more matched; narrow --open or raise --open-limit")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
