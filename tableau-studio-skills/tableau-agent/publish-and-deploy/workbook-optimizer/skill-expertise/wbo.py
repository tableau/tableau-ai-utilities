#!/usr/bin/env python3
"""Workbook-optimizer CLI: stats, check, and mechanical fix.
Uses argparse. check --format human|markdown|json (default human). --json is
an alias for --format json. Never overwrite the original unless --in-place.
"""
from __future__ import annotations

import argparse
import errno
import html
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path


# --- workbook I/O (.twb is XML; .twbx is a ZIP with one .twb) ---------------
def is_twbx(path: str) -> bool:
    """A workbook is packaged if it's a ZIP (regardless of extension)."""
    return zipfile.is_zipfile(path)


def twb_name_in_archive(zf: zipfile.ZipFile) -> str:
    """Return the archive-relative name of the single `.twb` entry."""
    twbs = [n for n in zf.namelist() if n.lower().endswith(".twb")]
    if not twbs:
        raise ValueError("no .twb entry found inside the .twbx archive")
    if len(twbs) > 1:
        root = [n for n in twbs if "/" not in n]
        if root:
            return root[0]
    return twbs[0]


def read_twb(path: str) -> str:
    """Return the `.twb` XML as text, whether `path` is a .twb or a .twbx.

    Newlines are kept as they are on disk (newline="") so a fix changes only
    the intended edit.
    """
    if is_twbx(path):
        with zipfile.ZipFile(path) as zf:
            with zf.open(twb_name_in_archive(zf)) as f:
                return f.read().decode("utf-8")
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def _dest_dir(path: str) -> str:
    """Directory for tempfile.mkstemp / makedirs. Bare filenames use cwd."""
    return os.path.dirname(path) or "."


def repack_twbx(
    orig_twbx: str, new_twbx: str, edited_twb: str, *, in_place: bool = False
) -> str:
    """Write new_twbx = orig_twbx with its `.twb` entry replaced by edited_twb.

    Every other entry (Data/, images, ...) is copied through byte-for-byte.
    """
    if not is_twbx(orig_twbx):
        raise ValueError(f"{orig_twbx} is not a .twbx archive")
    overwrite = in_place or os.path.abspath(orig_twbx) == os.path.abspath(new_twbx)
    with open(edited_twb, encoding="utf-8", newline="") as f:
        twb_bytes = f.read().encode("utf-8")
    dest = os.path.abspath(orig_twbx if overwrite else new_twbx)
    os.makedirs(_dest_dir(dest), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(suffix=".twbx", dir=_dest_dir(dest))
    os.close(fd)
    try:
        with zipfile.ZipFile(orig_twbx) as zin:
            twb_entry = twb_name_in_archive(zin)
            with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename == twb_entry:
                        zout.writestr(item, twb_bytes)
                    else:
                        zout.writestr(item, zin.read(item.filename))
        os.replace(tmp_path, dest)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
    return dest


def write_fixed(
    orig: str, new: str | None, edited_twb: str, *, in_place: bool = False
) -> str:
    """Write a fixed workbook (copy by default; `--in-place` overwrites orig)."""
    if is_twbx(orig):
        return repack_twbx(
            orig, orig if in_place else new, edited_twb, in_place=in_place
        )
    dest = os.path.abspath(orig if in_place else new)
    os.makedirs(_dest_dir(dest), exist_ok=True)
    if in_place:
        fd, tmp_path = tempfile.mkstemp(suffix=".twb", dir=_dest_dir(dest))
        os.close(fd)
        shutil.copy2(edited_twb, tmp_path)
        os.replace(tmp_path, dest)
    else:
        shutil.copy2(edited_twb, dest)
    return dest


SCHEMA_VERSION = 3
SIZE_WARNING_BYTES = 200 * 1024 * 1024
OBJECT_COUNT_THRESHOLD = 500
_EXCLUDED_DS = {"Parameters"}
_INTERNAL_PREFIX = "[__tableau_internal_object_id__]"
TABLEAU_LINKS = {
    "Checklist": "https://help.tableau.com/current/pro/desktop/en-us/perf_checklist.htm",
    "Streamline": "https://help.tableau.com/current/pro/desktop/en-us/wbo_streamline.htm",
    "Extracts": "https://help.tableau.com/current/pro/desktop/en-us/perf_extracts.htm",
    "Visualizations": "https://help.tableau.com/current/pro/desktop/en-us/perf_visualization.htm",
    "Dashboards": "https://help.tableau.com/current/pro/desktop/en-us/dashboards_best_practices.htm",
}
PLAIN_SOURCES = {
    "InterWorks": "InterWorks",
    "Practitioner": "practitioner pattern",
    "Tableau docs": "Tableau docs",
}


def _sources(*labels: str) -> list[dict]:
    out = []
    for lab in labels:
        url = TABLEAU_LINKS.get(lab)
        label = PLAIN_SOURCES[lab] if lab in PLAIN_SOURCES else lab
        out.append({"label": label, "url": url})
    return out


def _cat(
    cid: str,
    summary: str,
    *,
    title: str,
    detail: str | None = None,
    det: str = "S",
    impact: str = "medium",
    priority: str = "MEDIUM",
    sources: tuple[str, ...] = (),
    programmable: bool = True,
    fix: str = "author-only",
) -> dict:
    return {
        "id": cid,
        "title": title,
        "summary": summary,
        "detail": detail or summary,
        "detectability": det,
        "programmable": programmable,
        "impact": impact,
        "priority": priority,
        "fixMethod": fix,
        "sources": _sources(*sources),
        "source_keys": sources,
    }


CATALOG: list[dict] = [
    _cat("extracts-over-live", "Prefer extracts over live connections unless you need real-time data.",
         title="Use an extract instead of a live connection",
         detail="Extracts load in memory; live pays network + DB. Try extracts unless real-time or billions of rows.",
         impact="big", priority="CRITICAL", sources=("Checklist", "Streamline", "Extracts")),
    _cat("hide-unused-fields", "Hide unused fields so extracts and queries drop them.",
         title="Hide unused fields",
         detail="Hidden fields drop from extracts and queries. Hide unused before creating an extract. Non-semantic: add hidden='true' on unused columns (regex). Copy unless --in-place.",
         impact="medium", priority="CLEANUP", sources=("Streamline", "Extracts"), fix="mechanical"),
    _cat("close-unused-datasources", "Close datasources no worksheet uses; extra sources add queries.",
         title="Close unused data sources",
         detail="Extra sources add queries; close unused ones. Big if the unused source is live.",
         impact="big", priority="HIGH", sources=("Streamline", "Visualizations")),
    _cat("minimize-data-volume", "Limit rows with data-source or extract filters; volume dominates load time.",
         title="Reduce data volume with source filters",
         detail="Python hits when XML has neither datasource-filters nor extract filters. Worksheet cards do not clear this id.",
         impact="big", priority="CRITICAL", sources=("Streamline", "Checklist")),
    _cat("avoid-custom-sql", "Avoid custom SQL; Tableau wraps it in a subquery many databases handle poorly.",
         title="Avoid custom SQL",
         detail="Avoid custom SQL; an extract runs it once if you must. Bigger on live than extract.",
         impact="big", priority="CRITICAL", sources=("Checklist", "Extracts")),
    _cat("avoid-params-in-custom-sql", "Parameters in custom SQL force a subquery wrap.",
         title="Avoid parameters in custom SQL",
         sources=("InterWorks",)),
    _cat("remove-sql-order-by", "ORDER BY in custom SQL is wasted; Tableau re-sorts after load.",
         title="Remove ORDER BY from custom SQL",
         impact="small", sources=("InterWorks",)),
    _cat("prefer-relationships", "Relationships query only tables a viz needs; keep physical joins limited.",
         title="Use relationships instead of joins",
         impact="big", sources=("Checklist",)),
    _cat("referential-integrity", "Enable referential integrity so Tableau can simplify joins.",
         title="Enable referential integrity",
         sources=("Checklist",)),
    _cat("limit-data-blending", "Blends query each source then combine; aggregate before blending when possible.",
         title="Limit data blending",
         impact="big", priority="HIGH", sources=("Checklist",)),
    _cat("prefer-numbers-booleans", "String and date calcs are slower than numbers and Booleans; flag IF/CASE/STR on those types.",
         title="Prefer numeric and Boolean calculations",
         sources=("Checklist",)),
    _cat("count-over-countd", "COUNTD is slow; prefer COUNT when distinctness is not required.",
         title="Use COUNT instead of COUNTD",
         detail="COUNTD is one of the slowest function types. Prefer COUNT when distinctness is not required. MEDIUM; never rank above filter-heavy dashboards.",
         sources=("Checklist",)),
    _cat("min-max-over-avg-attr", "MIN and MAX typically outperform AVG and ATTR.",
         title="Use MIN/MAX instead of AVG/ATTR",
         sources=("Checklist",)),
    _cat("limit-calc-fields", "Fewer calculated fields means less to parse and manage.",
         title="Reduce the number of calculated fields",
         impact="small", sources=("InterWorks",)),
    _cat("avoid-row-level-param-calcs", "Row-level parameter calcs recompute per row; prefer aggregating first.",
         title="Avoid row-level parameter calculations",
         sources=("InterWorks",)),
    _cat("limit-cross-source-calcs", "Cross-source calculations query sequentially.",
         title="Limit cross-data-source calculations",
         sources=("InterWorks",)),
    _cat("minimize-lod", "LOD expressions add compile cost; keep them only when they earn their keep.",
         title="Minimize LOD expressions",
         sources=("Checklist",)),
    _cat("avoid-nested-calcs", "Deep calc nesting slows query compilation.",
         title="Avoid deeply nested calculations",
         sources=("Tableau docs",)),
    _cat("limit-table-calcs", "Table calcs run in the local engine; prefer an LOD when cheaper.",
         title="Limit table calculations",
         sources=("Checklist",)),
    _cat("prefer-native-over-calcs", "Groups, bins, sets, custom dates, and combined fields beat equivalent calculations.",
         title="Use native features instead of calculations",
         sources=("Checklist",)),
    _cat("avoid-hierarchies", "Hierarchies add local compute; drop unused drill paths.",
         title="Drop unused hierarchies",
         impact="unknown", sources=("InterWorks",)),
    _cat("consolidate-duplicate-calcs", "Same formula under two captions; suggest consolidating for cognitive load. Does not rewrite XML.",
         title="Consolidate duplicate calculations",
         detail="Flag identical or wrapper formulas with different captions. Keep the calc used on the most sheets. Do not rewrite XML; the author must consolidate in Desktop.",
         sources=("Practitioner",)),
    _cat("binary-string-branches", "IF/CASE with exactly two string literals looks like a Boolean. Grey area; does not rewrite XML.",
         title="Convert two-value string logic to Boolean",
         detail="Row-level IF/CASE with exactly two string literals is binary logic as a string. Should be a Boolean. Do not rewrite XML; the author decides in Desktop.",
         sources=("Practitioner",)),
    _cat("minimize-quick-filters", "Each shown filter card needs an option query; prefer actions on busy dashboards.",
         title="Reduce the number of shown filter cards",
         impact="big", priority="HIGH", sources=("Visualizations", "Checklist")),
    _cat("avoid-only-relevant-values", "Only Relevant Values re-queries when other filters change.",
         title="Avoid 'Only Relevant Values' on filters",
         priority="HIGH", sources=("Visualizations", "Checklist")),
    _cat("avoid-high-cardinality-filters", "Enumerated filters on likely high-cardinality strings (customer, city, product) load slowly.",
         title="Avoid filters on high-cardinality fields",
         sources=("InterWorks",)),
    _cat("context-filters-not-query-lever", "Context filters no longer help query speed. Never fail a workbook for missing them.",
         title="Don't rely on context filters for speed",
         detail="Context filters force order of operations but no longer help query performance. Never hit for missing ones; never add them for load time.",
         impact="none", sources=("Checklist",)),
    _cat("prefer-range-over-huge-discrete", "A range filter is cheaper than a long itemized member list.",
         title="Use a range filter instead of a long member list",
         sources=("Checklist",)),
    _cat("filter-actions-over-quick-filters", "Filter actions avoid per-card option queries for guided drill-down.",
         title="Use filter actions instead of filter cards",
         impact="big", priority="HIGH", sources=("Visualizations", "Checklist")),
    _cat("avoid-user-filters", "USERNAME() / user filters prevent shared query cache.",
         title="Avoid user filters",
         impact="big", priority="HIGH", sources=("InterWorks",)),
    _cat("limit-filter-count", "Filters compound query complexity across worksheets.",
         title="Limit the total number of filters",
         sources=("Checklist",)),
    _cat("apply-button", "Show Apply Button batches multi-select filter changes.",
         title="Add an Apply button to filters",
         impact="big", priority="HIGH", sources=("Checklist",)),
    _cat("avoid-keep-only-exclude", "Keep Only / Exclude on discrete items can be expensive.",
         title="Avoid Keep Only / Exclude on many items",
         sources=("Checklist",)),
    _cat("filter-at-higher-grain", "Filter a parent grain (state) instead of every child (city) when both are filtered.",
         title="Filter at a higher grain",
         sources=("Checklist",)),
    _cat("limit-worksheets-per-dashboard", "Tableau guideline is two or three views per dashboard.",
         title="Limit worksheets per dashboard",
         impact="big", priority="HIGH", sources=("Dashboards", "Checklist", "Visualizations")),
    _cat("fixed-dashboard-size", "Fixed-size dashboards can be cached; automatic size re-renders per request.",
         title="Set a fixed dashboard size",
         detail="Fixed size can be cached; automatic re-renders per request. Non-semantic: set dashboard sizing-mode from automatic to fixed (regex). Copy unless --in-place.",
         impact="big", priority="HIGH", sources=("Checklist", "Streamline"), fix="mechanical"),
    _cat("limit-viz-in-tooltip", "Keep Viz-in-Tooltip targets simple.",
         title="Keep Viz in Tooltip simple",
         sources=("Tableau docs",)),
    _cat("minimize-image-sizes", "Packaged images over 50kb render more slowly.",
         title="Shrink large packaged images",
         impact="small", priority="CLEANUP", sources=("InterWorks",)),
    _cat("prefer-transparent-pngs", "Prefer PNG (with transparency) over JPEG/BMP/GIF for shapes and images.",
         title="Use transparent PNGs for images",
         impact="small", priority="CLEANUP", sources=("InterWorks",)),
    _cat("limit-dashboard-actions", "Actions run sequentially; excess compounds latency.",
         title="Limit dashboard actions",
         sources=("Tableau docs",)),
    _cat("prefer-tiled-over-floating", "Floating works best on fixed-size dashboards.",
         title="Prefer a tiled layout over floating",
         impact="indirect", priority="CLEANUP", sources=("Tableau docs",)),
    _cat("sets-for-top-n", "Prefer native sets / top-N over equivalent calculations.",
         title="Use sets for top-N instead of calculations",
         sources=("Checklist",)),
    _cat("limit-heavy-text-tables", "Crosstabs and text tables with many pills are a common mark-count trap.",
         title="Limit heavy text tables",
         priority="HIGH", sources=("Visualizations",)),
    _cat("guided-drill-down", "Crowded dashboards without actions show everything at once; spread detail across views.",
         title="Guide drill-down across views",
         impact="big", priority="HIGH", sources=("Checklist", "Visualizations")),
    _cat("keep-tooltips-simple", "Heavy tooltips add hover render cost.",
         title="Keep tooltips simple",
         impact="small", priority="CLEANUP", sources=("InterWorks",)),
    _cat("default-field-properties", "Set number formats and colors on the field once instead of repeating per sheet.",
         title="Set default field properties once",
         impact="indirect", priority="CLEANUP", sources=("InterWorks",)),
    _cat("avoid-excessive-formatting", "Mark transparency and animation add render cost.",
         title="Reduce excessive formatting",
         sources=("Checklist",)),
    _cat("upgrade-tableau-version", "Reports workbook version only; never auto-fails a supported version.",
         title="Consider upgrading the Tableau version",
         impact="variable", priority="CLEANUP", sources=("Checklist", "Streamline")),
    _cat("test-anchor-table", "Different anchoring changes query efficiency; confirm at runtime.",
         title="Test the join anchor table",
         det="S/R", programmable=False, sources=("InterWorks",)),
    _cat("publish-shared-sources", "Governance and consistency, not raw speed.",
         title="Publish shared data sources",
         det="P", impact="indirect", programmable=False, sources=("InterWorks",)),
    _cat("materialize-calcs-in-extract", "Compute Calculations Now precomputes expensive calcs at extract generation.",
         title="Materialize calculations in the extract",
         det="R", programmable=False, sources=("Tableau docs",)),
    _cat("reduce-mark-count", "More marks means more render CPU and memory. Status bar shows count; it is not in the XML.",
         title="Reduce the mark count",
         det="P", impact="big", priority="HIGH", programmable=False, sources=("Visualizations",)),
    _cat("performance-recorder", "Start here: long queries vs many queries vs slow calcs vs complex render.",
         title="Run the Performance Recorder",
         det="R", impact="none", programmable=False, sources=("Checklist",)),
    _cat("fix-source-bottlenecks", "Slow in the source means slow in Desktop and almost always on Server.",
         title="Fix data-source bottlenecks",
         det="R", impact="none", programmable=False, sources=("Checklist",)),
    _cat("clean-structured-data", "Cleaner, better-shaped data runs faster.",
         title="Use clean, well-structured data",
         det="P/R", impact="none", programmable=False, sources=("Checklist",)),
]

CATALOG_BY_ID = {r["id"]: r for r in CATALOG}
CHECK_IDS = tuple(r["id"] for r in CATALOG if r["programmable"])
MECHANICAL_FIX_IDS = tuple(r["id"] for r in CATALOG if r["fixMethod"] == "mechanical")
CHECK_SUMMARIES = {r["id"]: r["summary"] for r in CATALOG}
CHECK_SOURCES = {r["id"]: r["source_keys"] for r in CATALOG if r["source_keys"]}
_PRIORITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "CLEANUP": 3}

_TOKEN_RE = re.compile(r"\[[^\[\]]+\]")
_STRING_LIT_RE = re.compile(r'"([^"]*)"')


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _iter(el: ET.Element, name: str):
    for child in el.iter():
        if _local(child.tag) == name:
            yield child


def _is_real_datasource(ds: ET.Element) -> bool:
    if ds.get("caption") in _EXCLUDED_DS or ds.get("name") == "Parameters":
        return False
    if ds.get("hasconnection") == "false":
        return False
    return True


# Connection-class taxonomy for the live-database qualifier. A live *database*
# server (SQL Server, Snowflake, …) carries a far bigger load-time cost than a
# live *file* source (Excel/CSV), so we classify the two distinctly rather than
# lumping every non-extract source together as "live".
_EXTRACT_CLASSES = {"hyper", "dataengine", "tde"}
_FILE_CLASSES = {
    "excel-direct", "excel", "textscan", "csv", "msaccess", "access",
    "jsonfile", "json", "pdf", "statfile", "spatial", "parquet",
    "googlesheets",
}
_LIVE_DB_CLASSES = {
    "sqlserver", "sqlazure", "synapse", "postgres", "redshift", "snowflake",
    "oracle", "mysql", "mariadb", "maria", "teradata", "bigquery", "vertica",
    "netezza", "databricks", "athena", "awsathena", "presto", "trino", "hive",
    "impala", "db2", "saphana", "hana", "sapbw", "greenplum", "exasol",
    "memsql", "aurora", "spanner", "clickhouse", "denodo", "dremio", "firebolt",
    "mongodb", "spark", "cloudera-hadoop", "hortonworks-hadoop",
}


def _classify_connection(
    conn_class: str | None,
    is_extract: bool,
    server: str | None,
    dbname: str | None,
    filename: str | None,
) -> str:
    """Bucket a datasource connection: extract / live-database / file / unknown."""
    cls = (conn_class or "").lower()
    if is_extract or cls in _EXTRACT_CLASSES:
        return "extract"
    if cls in _FILE_CLASSES or filename:
        return "file"
    if cls in _LIVE_DB_CLASSES or server or dbname:
        return "live-database"
    return "unknown"


def _connection_class(ds: ET.Element) -> tuple[str | None, bool, str]:
    conn_class = None
    resolved = ds.find(".//named-connection/connection")
    if resolved is None:
        resolved = ds.find("connection")
    if resolved is not None:
        conn_class = resolved.get("class")
    is_extract = False
    for extract in ds.iter():
        if _local(extract.tag) == "extract" and extract.get("enabled") == "true":
            is_extract = True
            break
    server = resolved.get("server") if resolved is not None else None
    dbname = resolved.get("dbname") if resolved is not None else None
    filename = resolved.get("filename") if resolved is not None else None
    conn_type = _classify_connection(conn_class, is_extract, server, dbname, filename)
    # A direct extract file (class hyper/tde) is an extract even without an
    # <extract enabled='true'> element.
    return conn_class, is_extract or conn_type == "extract", conn_type


def normalize_formula(formula: str | None) -> str:
    text = formula or ""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", text).strip()


def _mermaid_id(label: str, prefix: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", label).strip("_")[:40] or "x"
    return f"{prefix}_{slug}"


def _mermaid_label(text: str) -> str:
    cleaned = (
        text.replace('"', "'")
        .replace("`", "'")
        .replace("[", " ")
        .replace("]", " ")
        .replace("{", " ")
        .replace("}", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("/", " ")
        .replace("\\", " ")
    )
    return re.sub(r"\s+", " ", cleaned).strip()[:60]


def _mermaid_node(kind: str, nid: str, label: str) -> str:
    text = _mermaid_label(label)
    shapes = {
        "workbook": ("([", "])"),
        "dashboard": ("[[", "]]"),
        "worksheet": ("[", "]"),
        "datasource": ("[(", ")]"),
        "filter": ("[/", "/]"),
        "parameter": ("{{", "}}"),
        "calculation": ("{", "}"),
    }
    left, right = shapes.get(kind, ("[", "]"))
    return f"  {nid}{left}{text}{right}:::{kind}"


def _dedupe_labels(labels: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in labels:
        label = (raw or "").strip()
        if not label:
            continue
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(label)
    return out


def _field_token(ref: str) -> str:
    tokens = re.findall(r"\[([^\]]+)\]", ref or "")
    inner = tokens[-1] if tokens else (ref or "").strip("[]")
    parts = inner.split(":")
    return parts[-2] if len(parts) >= 2 else inner


def _label_for_column_ref(
    ref: str,
    columns: list[dict],
    parameters: list[dict] | None = None,
) -> str:
    if not ref:
        return ""
    by_name = {c["name"]: c for c in columns}
    if ref in by_name:
        return (by_name[ref].get("caption") or ref).strip("[]")
    token = _field_token(ref)
    bracketed = f"[{token}]"
    if bracketed in by_name:
        return (by_name[bracketed].get("caption") or token).strip("[]")
    for c in columns:
        if (c.get("name") or "").strip("[]") == token:
            return (c.get("caption") or token).strip("[]")
    for p in parameters or []:
        pname = p.get("name") or ""
        if pname in (ref, bracketed) or pname.strip("[]") == token:
            return (p.get("caption") or pname).strip("[]")
    pretty = _caption_from_field_ref(ref)
    if pretty and pretty != "Calculation":
        return pretty
    if token and not _looks_internal(token) and not token.startswith("Calculation"):
        return token.replace("_", " ")
    return ""


def _result(
    cid: str,
    status: str,
    findings: list | None = None,
    suggestion: str = "",
    skip_reason: str | None = None,
) -> dict:
    rec = CATALOG_BY_ID[cid]
    return {
        "id": cid,
        "title": rec["title"],
        "status": status,
        "skipReason": skip_reason,
        "findings": findings or [],
        "suggestion": suggestion if status != "clear" else "",
        "summary": rec["summary"],
        "detail": rec["detail"],
        "detectability": rec["detectability"],
        "programmable": rec["programmable"],
        "impact": rec["impact"],
        "priority": rec["priority"],
        "fixMethod": rec["fixMethod"],
        "sources": rec["sources"],
    }


def envelope(
    command: str,
    path: str,
    *,
    ok: bool = True,
    version: str | None = None,
    error: dict | None = None,
    **extra,
) -> dict:
    out = {
        "schemaVersion": SCHEMA_VERSION,
        "command": command,
        "ok": ok,
        "workbook": {"path": path, "version": version},
        "error": error,
    }
    out.update(extra)
    return out


def fail_envelope(command: str, path: str, err_type: str, message: str) -> dict:
    return envelope(
        command,
        path,
        ok=False,
        error={"type": err_type, "message": message},
    )


def size_warning(path: str) -> dict | None:
    """Warn when the packaged file is 200+ MB. Not a hard stop.

    A `.twbx` is often large because of `Data/` extracts; this tool parses the
    `.twb` entry, not the whole ZIP.
    """
    try:
        nbytes = os.path.getsize(path)
    except OSError:
        return None
    if nbytes < SIZE_WARNING_BYTES:
        return None
    return {
        "id": "large-file",
        "bytes": nbytes,
        "thresholdBytes": SIZE_WARNING_BYTES,
        "message": (
            f"Packaged file is {nbytes} bytes (threshold {SIZE_WARNING_BYTES}). "
            "A .twbx is often large because of Data/ extracts, not XML. "
            "wbo.py parses the .twb entry, not the whole ZIP. "
            "Do not refuse a full catalog walk solely because of zip size."
        ),
    }


def object_count_warning(summary: dict) -> dict | None:
    """Warn when worksheets + dashboards + fields is 500+."""
    worksheets = int(summary.get("worksheets") or 0)
    dashboards = int(summary.get("dashboards") or 0)
    fields = int(summary.get("fields") or 0)
    objects = worksheets + dashboards + fields
    if objects < OBJECT_COUNT_THRESHOLD:
        return None
    return {
        "id": "large-object-count",
        "objects": objects,
        "threshold": OBJECT_COUNT_THRESHOLD,
        "worksheets": worksheets,
        "dashboards": dashboards,
        "fields": fields,
        "message": (
            f"Workbook has {objects} worksheets+dashboards+fields "
            f"(threshold {OBJECT_COUNT_THRESHOLD}). Ask once: full walk, "
            "one dashboard or datasource, skip a category, or stop after stats."
        ),
    }


def collect_warnings(path: str, summary: dict | None = None) -> list[dict]:
    out: list[dict] = []
    file_warn = size_warning(path)
    if file_warn:
        out.append(file_warn)
    if summary is not None:
        count_warn = object_count_warning(summary)
        if count_warn:
            out.append(count_warn)
    return out


def _format_warnings(warnings: list[dict]) -> str:
    if not warnings:
        return ""
    return "".join(f"warning: {w['id']}: {w['message']}\n" for w in warnings)


def under_training_data(path: str | Path) -> bool:
    try:
        parts = Path(path).resolve().parts
    except OSError:
        parts = Path(path).parts
    return any(part.casefold() == "training-data" for part in parts)


def _same_path(left: str | Path, right: str | Path) -> bool:
    a = Path(left)
    b = Path(right)
    try:
        if a.exists() and b.exists():
            return a.resolve().samefile(b.resolve())
    except OSError:
        pass
    try:
        return os.path.normcase(str(a.resolve())) == os.path.normcase(str(b.resolve()))
    except OSError:
        return os.path.normcase(str(a)) == os.path.normcase(str(b))


def _usage_view(usage: dict) -> dict:
    keys = ("datasources", "columns", "worksheets", "dashboards", "parameters")
    return {k: usage[k] for k in keys if k in usage}


# --- graph -----------------------------------------------------------------
def build_usage(xml: str) -> dict:
    root = ET.fromstring(xml)
    datasources = []
    columns = []
    worksheets = []
    dashboards = []
    ds_container = root.find("datasources")
    ds_elems = ds_container.findall("datasource") if ds_container is not None else []
    parameters: list[dict] = []
    for ds in ds_elems:
        if ds.get("caption") not in _EXCLUDED_DS and ds.get("name") != "Parameters":
            continue
        for col in ds.findall("column"):
            name = col.get("name")
            if not name:
                continue
            parameters.append(
                {"name": name, "caption": col.get("caption") or name}
            )
    for ds in ds_elems:
        if not _is_real_datasource(ds):
            continue
        conn_class, is_extract, conn_type = _connection_class(ds)
        ds_name = ds.get("name") or ""
        caption = ds.get("caption") or ds_name
        col_records = []
        for col in ds.findall("column"):
            name = col.get("name")
            if not name:
                continue
            calc = col.find("calculation")
            rec = {
                "datasource": ds_name,
                "datasourceCaption": caption,
                "name": name,
                "caption": col.get("caption") or name,
                "kind": "calculation" if calc is not None else "field",
                "datatype": col.get("datatype"),
                "hidden": col.get("hidden") == "true",
                "formula": calc.get("formula") if calc is not None else None,
                "formulaNormalized": normalize_formula(
                    calc.get("formula") if calc is not None else None
                ),
                "usedOnWorksheets": [],
                "usedOnDashboards": [],
                "referencedByCalcs": [],
                "references": [],
            }
            col_records.append(rec)
            columns.append(rec)
        datasources.append(
            {
                "name": ds_name,
                "caption": caption,
                "connectionClass": conn_class,
                "connectionType": conn_type,
                "isLiveDatabase": conn_type == "live-database",
                "isExtract": is_extract,
                "columns": [c["name"] for c in col_records],
            }
        )
    by_key: dict[tuple[str, str], dict] = {
        (c["datasource"], c["name"]): c for c in columns
    }
    for col in columns:
        if not col["formula"]:
            continue
        refs = [
            t
            for t in _TOKEN_RE.findall(col["formula"])
            if (col["datasource"], t) in by_key
        ]
        col["references"] = refs
        for token in refs:
            target = by_key[(col["datasource"], token)]
            if col["name"] not in target["referencedByCalcs"]:
                target["referencedByCalcs"].append(col["name"])
    ws_container = root.find("worksheets")
    ws_elems = ws_container.findall("worksheet") if ws_container is not None else []
    for ws in ws_elems:
        used = sorted(
            {
                col.get("name")
                for col in ws.iter()
                if _local(col.tag) == "column" and col.get("name")
            }
        )
        ds_refs = sorted(
            {
                d.get("caption")
                for d in ws.iter()
                if _local(d.tag) == "datasource" and d.get("caption")
            }
        )
        if not ds_refs:
            dep_names = {
                d.get("datasource")
                for d in ws.iter()
                if _local(d.tag) == "datasource-dependencies" and d.get("datasource")
            }
            ds_refs = [
                ds["caption"]
                for ds in datasources
                if ds["name"] in dep_names
            ]
        ws_filters = _dedupe_labels(
            [
                _label_for_column_ref(f.get("column") or "", columns, parameters)
                or _filter_display_name(f.get("column") or "", i)
                for i, f in enumerate(_iter(ws, "filter"))
                if f.get("column")
            ]
        )
        worksheets.append(
            {
                "name": ws.get("name") or "",
                "datasources": ds_refs,
                "fields": used,
                "filters": ws_filters,
            }
        )
        ws_name = ws.get("name") or ""
        marked = False
        for dep in ws.iter():
            if _local(dep.tag) != "datasource-dependencies":
                continue
            ds_name = dep.get("datasource") or ""
            for child in dep:
                if _local(child.tag) != "column" or not child.get("name"):
                    continue
                rec = by_key.get((ds_name, child.get("name") or ""))
                if rec is None:
                    continue
                marked = True
                if ws_name not in rec["usedOnWorksheets"]:
                    rec["usedOnWorksheets"].append(ws_name)
        if not marked:
            for fname in used:
                matches = [c for c in columns if c["name"] == fname]
                if len(matches) != 1:
                    continue
                rec = matches[0]
                if ws_name not in rec["usedOnWorksheets"]:
                    rec["usedOnWorksheets"].append(ws_name)
    db_container = root.find("dashboards")
    db_elems = db_container.findall("dashboard") if db_container is not None else []
    ws_names = {w["name"] for w in worksheets}
    for db in db_elems:
        size = db.find("size")
        zones = sorted(
            {
                z.get("name")
                for z in db.iter()
                if _local(z.tag) == "zone"
                and z.get("name") in ws_names
                and z.get("type-v2") != "filter"
            }
        )
        filter_zones = [
            z
            for z in db.iter()
            if _local(z.tag) == "zone" and z.get("type-v2") == "filter"
        ]
        filter_names = _dedupe_labels(
            [
                _label_for_column_ref(z.get("param") or "", columns, parameters)
                or _filter_display_name(z.get("param") or z.get("name") or "", i)
                for i, z in enumerate(filter_zones)
            ]
        )
        floating = any(
            z.get("fixed-size") is None
            and z.get("type-v2") not in (None, "layout-basic", "layout-flow", "filter")
            or z.get("param") == "floating"
            for z in db.iter()
            if _local(z.tag) == "zone" and z.get("floating") == "true"
        )
        dashboards.append(
            {
                "name": db.get("name") or "",
                "sizingMode": size.get("sizing-mode") if size is not None else None,
                "worksheetZones": zones,
                "filterZoneCount": len(filter_zones),
                "filters": filter_names,
                "hasFloating": floating
                or any(
                    z.get("floating") == "true"
                    for z in db.iter()
                    if _local(z.tag) == "zone"
                ),
            }
        )
        for zname in zones:
            for col in columns:
                if zname in col["usedOnWorksheets"]:
                    dname = db.get("name") or ""
                    if dname not in col["usedOnDashboards"]:
                        col["usedOnDashboards"].append(dname)
    used_keys: set[tuple[str, str]] = {
        (c["datasource"], c["name"]) for c in columns if c["usedOnWorksheets"]
    }
    changed = True
    while changed:
        changed = False
        for col in columns:
            key = (col["datasource"], col["name"])
            if key in used_keys:
                continue
            if any(
                (col["datasource"], ref) in used_keys for ref in col["referencedByCalcs"]
            ):
                used_keys.add(key)
                changed = True
    for col in columns:
        col["isUnused"] = (
            (col["datasource"], col["name"]) not in used_keys
            and not col["name"].startswith(_INTERNAL_PREFIX)
        )
    return {
        "version": root.get("version"),
        "datasources": datasources,
        "columns": columns,
        "worksheets": worksheets,
        "dashboards": dashboards,
        "parameters": parameters,
        "xml": xml,
        "root": root,
    }


def unused_columns(usage: dict) -> list[dict]:
    return [
        c
        for c in usage["columns"]
        if c.get("isUnused") and not c.get("hidden")
    ]


def unused_column_names(usage: dict) -> list[str]:
    return [c["name"] for c in unused_columns(usage)]


def unused_column_labels(usage: dict) -> list[str]:
    labels: list[str] = []
    for c in unused_columns(usage):
        cap = (c.get("caption") or "").strip()
        if cap and not _looks_internal(cap):
            labels.append(cap)
        else:
            inner = (c.get("name") or "").strip("[]")
            labels.append(inner or cap)
    return labels


def summarize_usage(usage: dict) -> dict:
    datasources = usage["datasources"]
    worksheets = usage["worksheets"]
    dashboards = usage["dashboards"]
    columns = usage["columns"]
    used_ws = {w for db in dashboards for w in db["worksheetZones"]}
    return {
        "version": usage["version"],
        "datasources": len(datasources),
        "worksheets": len(worksheets),
        "dashboards": len(dashboards),
        "fields": len(columns),
        "calculations": sum(1 for c in columns if c["kind"] == "calculation"),
        "hiddenFields": sum(1 for c in columns if c["hidden"]),
        "orphanWorksheets": [w["name"] for w in worksheets if w["name"] not in used_ws],
        "parameters": len(usage.get("parameters") or []),
        "connections": [
            {
                "name": d["name"],
                "caption": d["caption"],
                "connectionClass": d["connectionClass"],
                "isExtract": d["isExtract"],
            }
            for d in datasources
        ],
        "unusedFields": unused_column_names(usage),
        "unusedFieldLabels": unused_column_labels(usage),
    }


def check_priority(cid: str) -> str:
    rec = CATALOG_BY_ID.get(cid)
    return rec["priority"] if rec else "MEDIUM"


def _hits_by_priority(checks: list[dict]) -> list[tuple[str, list[dict]]]:
    grouped: dict[str, list[dict]] = {
        "CRITICAL": [],
        "HIGH": [],
        "MEDIUM": [],
        "CLEANUP": [],
    }
    for chk in checks:
        if chk["status"] != "hit":
            continue
        band = chk.get("priority") or check_priority(chk["id"])
        grouped.setdefault(band, []).append(chk)
    order = ("CRITICAL", "HIGH", "MEDIUM", "CLEANUP")
    extra = [b for b in grouped if b not in order and grouped[b]]
    return [(band, grouped[band]) for band in (*order, *extra) if grouped[band]]


def _looks_internal(text: str) -> bool:
    sl = text.lower()
    if "federated." in sl or "usr:calculation" in sl:
        return True
    if text.startswith("[") and ":" in text:
        return True
    return False


def _display_names(finding: dict) -> list[str]:
    members = finding.get("members")
    if isinstance(members, list) and members:
        names: list[str] = []
        for mem in members:
            if isinstance(mem, dict):
                names.extend(_display_names(mem))
        return names
    caption = (finding.get("caption") or "").strip()
    if caption and not _looks_internal(caption):
        return [caption]
    for key in ("name", "column"):
        raw = finding.get(key)
        if not raw:
            continue
        text = str(raw).strip()
        if not _looks_internal(text):
            if text.startswith("[") and text.endswith("]") and ":" not in text:
                return [text[1:-1]]
            return [text]
    field = finding.get("field")
    if field:
        pretty = _caption_from_field_ref(str(field))
        if pretty:
            return [pretty]
    kind = finding.get("kind")
    if kind:
        return [str(kind)]
    return []


def _caption_from_field_ref(field: str) -> str:
    match = re.findall(r"\[([^\]]+)\]", field)
    if not match:
        return ""
    inner = match[-1]
    parts = inner.split(":")
    token = parts[-2] if len(parts) >= 2 else inner
    if token.startswith("Calculation"):
        return "Calculation"
    if _looks_internal(token) or _looks_internal(inner):
        return ""
    return token.replace("_", " ")


def _names_for_check(chk: dict) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for finding in chk.get("findings") or []:
        if not isinstance(finding, dict):
            continue
        for name in _display_names(finding):
            if name not in seen:
                seen.add(name)
                names.append(name)
    return names


def _human_check(
    path: str,
    version: str | None,
    checks: list[dict],
    warnings: list[dict] | None = None,
) -> str:
    hits = [c for c in checks if c["status"] == "hit"]
    bands = _hits_by_priority(checks)
    lines = [
        f"{Path(path).name}  (version {version or '?'})",
        f"{len(hits)} hit",
        "",
    ]
    if not hits:
        lines.append("No programmable hits.")
        return _format_warnings(warnings or []) + "\n".join(lines).rstrip() + "\n"
    for band, group in bands:
        lines.append(f"{band} ({len(group)})")
        lines.append("")
        for chk in group:
            names = _names_for_check(chk)
            extra = f"  ({len(names)})" if names else ""
            title = chk.get("title") or chk["id"]
            lines.append(f"  {title} [{chk['id']}]{extra}")
            for name in names:
                lines.append(f"    {name}")
            lines.append("")
    return _format_warnings(warnings or []) + "\n".join(lines).rstrip() + "\n"


def _connection_kind(usage: dict) -> str:
    ds = usage.get("datasources") or []
    if not ds:
        return "unknown"
    extracts = sum(1 for d in ds if d.get("isExtract"))
    if extracts == len(ds):
        return "extract"
    if extracts == 0:
        return "live"
    return "mixed"


def _markdown_check(
    path: str,
    usage: dict,
    checks: list[dict],
    warnings: list[dict] | None = None,
) -> str:
    summary = summarize_usage(usage)
    hits = [c for c in checks if c["status"] == "hit"]
    bands = _hits_by_priority(checks)
    kind = _connection_kind(usage)
    counts = {band: len(group) for band, group in bands}
    high_titles = [
        c.get("title") or c["id"]
        for band, group in bands if band == "HIGH" for c in group
    ]
    crit_titles = [
        c.get("title") or c["id"]
        for band, group in bands if band == "CRITICAL" for c in group
    ]
    tldr_bits = [f"{len(hits)} hit"]
    if counts.get("CRITICAL"):
        tldr_bits.append(f"{counts['CRITICAL']} CRITICAL")
    if counts.get("HIGH"):
        tldr_bits.append(f"{counts['HIGH']} HIGH")
    if counts.get("MEDIUM"):
        tldr_bits.append(f"{counts['MEDIUM']} MEDIUM")
    if counts.get("CLEANUP"):
        tldr_bits.append(f"{counts['CLEANUP']} CLEANUP")
    lead = "; ".join(crit_titles + high_titles) if (crit_titles or high_titles) else "none"
    name = Path(path).name
    lines = [
        f"# Check report — {name}",
        "",
        f"**TL;DR:** {kind} connection. {'; '.join(tldr_bits)}. "
        f"Top issues: {lead}.",
        "",
        f"- Workbook: `{path}`",
        f"- Version: {usage.get('version') or '?'}",
        f"- Datasources: {summary['datasources']}; worksheets: {summary['worksheets']}; "
        f"dashboards: {summary['dashboards']}",
        "",
    ]
    if warnings:
        lines.extend(["## Warnings", ""])
        for w in warnings:
            lines.append(f"- **`{w['id']}`:** {w['message']}")
            lines.append("")
    lines.extend(
        [
        "## Workbook graph",
        "",
        "```mermaid",
        diagrams_workbook(usage, detailed=True),
        "```",
        "",
        "Legend: stadium = workbook, subroutine = dashboard, rectangle = worksheet, "
        "cylinder = datasource, parallelogram = filter, hexagon = parameter, "
        "diamond = calculation.",
        "",
        "### Nodes",
        "",
        "| Kind | Name | Detail |",
        "|---|---|---|",
        f"| workbook | {name} | version {usage.get('version') or '?'} |",
        ]
    )
    for ds in usage["datasources"]:
        conn = "extract" if ds.get("isExtract") else (ds.get("connectionClass") or "live")
        n = len(ds.get("columns") or [])
        lines.append(
            f"| datasource | {ds.get('caption') or ds.get('name')} | {conn}, {n} fields |"
        )
    for ws in usage["worksheets"]:
        src = ", ".join(ws.get("datasources") or []) or "-"
        lines.append(f"| worksheet | {ws['name']} | sources: {src} |")
    for db in usage["dashboards"]:
        zones = ", ".join(db.get("worksheetZones") or []) or "-"
        size = db.get("sizingMode") or "?"
        lines.append(f"| dashboard | {db['name']} | {size}; sheets: {zones} |")
    for p in usage.get("parameters") or []:
        lines.append(
            f"| parameter | {p.get('caption') or p.get('name')} | |"
        )
    for label in _graph_filter_labels(usage):
        lines.append(f"| filter | {label} | |")
    for calc in _graph_calcs(usage):
        used = ", ".join(calc.get("usedOnWorksheets") or []) or "unused"
        lines.append(
            f"| calculation | {calc['label']} | {calc.get('datasourceCaption') or '-'}; {used} |"
        )
    used_on_dash = {w for db in usage["dashboards"] for w in db.get("worksheetZones") or []}
    lines.extend(["", "### Edges", ""])
    edge_n = 0
    for db in usage["dashboards"]:
        lines.append(f"- {name} → {db['name']}")
        edge_n += 1
        for z in db.get("worksheetZones") or []:
            lines.append(f"- {db['name']} → {z}")
            edge_n += 1
        for flabel in db.get("filters") or []:
            lines.append(f"- {db['name']} → {flabel}")
            edge_n += 1
    for ws in usage["worksheets"]:
        if ws["name"] not in used_on_dash:
            lines.append(f"- {name} → {ws['name']}")
            edge_n += 1
        for cap in ws.get("datasources") or []:
            lines.append(f"- {ws['name']} → {cap}")
            edge_n += 1
        for flabel in ws.get("filters") or []:
            lines.append(f"- {ws['name']} → {flabel}")
            edge_n += 1
        used_calcs = [
            c["label"]
            for c in _graph_calcs(usage)
            if ws["name"] in (c.get("usedOnWorksheets") or [])
        ]
        for clabel in used_calcs:
            lines.append(f"- {ws['name']} → {clabel}")
            edge_n += 1
    for p in usage.get("parameters") or []:
        lines.append(f"- {name} → {p.get('caption') or p.get('name')}")
        edge_n += 1
    for calc in _graph_calcs(usage):
        ds_cap = calc.get("datasourceCaption")
        if ds_cap:
            lines.append(f"- {ds_cap} → {calc['label']}")
            edge_n += 1
    if edge_n == 0:
        lines.append("- (no graph edges)")
    lines.extend(["", "## Hits", ""])
    if not hits:
        lines.append("No programmable hits.")
        lines.append("")
    for band, group in bands:
        lines.append(f"### {band}")
        lines.append("")
        for chk in group:
            title = chk.get("title") or chk["id"]
            lines.append(f"#### {title}")
            lines.append("")
            names = _names_for_check(chk)
            if names:
                for n in names:
                    lines.append(f"- {n}")
                lines.append("")
            suggestion = (chk.get("suggestion") or chk.get("summary") or "").strip()
            if suggestion:
                refs = _source_links(chk["id"])
                if refs:
                    lines.append(f"**Suggestion:** {suggestion} ({refs})")
                else:
                    lines.append(f"**Suggestion:** {suggestion}")
                lines.append("")
            if chk.get("fixMethod") == "mechanical":
                lines.append(
                    "_Automatic fix available — the optimizer can apply this to a copy "
                    "of the workbook for you (your original is left untouched)._"
                )
                lines.append("")
    med = counts.get("MEDIUM", 0)
    high_n = counts.get("HIGH", 0)
    crit_n = counts.get("CRITICAL", 0)
    clean_n = counts.get("CLEANUP", 0)
    lines.extend(
        [
            "## Summary",
            "",
            f"{len(hits)} hit ({crit_n} CRITICAL, {high_n} HIGH, {med} MEDIUM, {clean_n} CLEANUP). "
            "These are known risk patterns, not measured load times. "
            "Use Tableau Performance Recorder if you need query vs render evidence.",
            "",
        ]
    )
    return "\n".join(lines)


_SEVERITY_LABEL = {"Warning": "warning", "Note": "note", "Info": "info"}


# Severity table. Mirrors the table in SKILL.md "Severity framework"; keep the
# two in sync (test_catalog_consistency.py pins the SKILL.md rows to this dict).
SEVERITY_TABLE = {
    #             live-database  live-file  extract
    "CRITICAL": ("Warning", "Note", "Warning"),
    "HIGH": ("Warning", "Note", "Note"),
    "MEDIUM": ("Note", "Info", "Info"),
    "CLEANUP": ("Note", "Info", "Info"),
}
_SEVERITY_COLUMNS = ("live-database", "live-file", "extract")


def _severity_column(usage: dict) -> str:
    """Strictest connection column across datasources.

    live database (or unknown / no datasources) > live file > extract.
    """
    ds = usage.get("datasources") or []
    if not ds:
        return "live-database"
    types = {d.get("connectionType", "unknown") for d in ds}
    if types & {"live-database", "unknown"} or not types <= {"file", "extract"}:
        return "live-database"
    if "file" in types:
        return "live-file"
    return "extract"


def _severity_for(band: str, column: str) -> str:
    """Warning / Note / Info from priority band + severity column."""
    row = SEVERITY_TABLE.get(band, SEVERITY_TABLE["CLEANUP"])
    return row[_SEVERITY_COLUMNS.index(column)]


def stamp_severity(usage: dict, checks: list[dict]) -> None:
    """Add `severity` to every hit, per the SKILL.md severity table."""
    column = _severity_column(usage)
    for chk in checks:
        if chk.get("status") == "hit":
            band = chk.get("priority") or check_priority(chk["id"])
            chk["severity"] = _severity_for(band, column)


def _source_links_html(cid: str) -> str:
    rec = CATALOG_BY_ID.get(cid)
    if not rec:
        return ""
    parts = []
    for src in rec["sources"]:
        label = html.escape(src.get("label") or "")
        if src.get("url"):
            url = html.escape(src["url"], quote=True)
            parts.append(f'<a href="{url}">{label}</a>')
        elif label:
            parts.append(label)
    return "; ".join(parts)


def _html_issue_card(chk: dict, column: str) -> list[str]:
    band = chk.get("priority") or check_priority(chk["id"])
    sev = chk.get("severity") or _severity_for(band, column)
    title = html.escape(chk.get("title") or chk["id"])
    out = [
        '      <li class="issue">',
        f'        <div class="issue-head">'
        f'<span class="sev sev-{_SEVERITY_LABEL[sev]}">{sev}</span>'
        f'<span class="issue-title">{title}</span></div>',
    ]
    names = _names_for_check(chk)
    if names:
        shown = ", ".join(html.escape(n) for n in names)
        out.append(f'        <p class="evidence">Found in: {shown}</p>')
    suggestion = (chk.get("suggestion") or chk.get("summary") or "").strip()
    if suggestion:
        refs = _source_links_html(chk["id"])
        tail = f' <span class="sources">({refs})</span>' if refs else ""
        out.append(f'        <p class="suggestion">{html.escape(suggestion)}{tail}</p>')
    out.append("      </li>")
    return out


def _html_check(
    path: str,
    usage: dict,
    checks: list[dict],
    warnings: list[dict] | None = None,
) -> str:
    summary = summarize_usage(usage)
    hits = [c for c in checks if c["status"] == "hit"]
    bands = _hits_by_priority(checks)
    kind = _connection_kind(usage)
    column = _severity_column(usage)
    counts = {band: len(group) for band, group in bands}
    # Group hits by fixability, preserving priority order within each group.
    fixable = [c for band, group in bands for c in group if c.get("fixMethod") == "mechanical"]
    author_only = [c for band, group in bands for c in group if c.get("fixMethod") != "mechanical"]
    crit_titles = [
        c.get("title") or c["id"]
        for band, group in bands if band == "CRITICAL" for c in group
    ]
    high_titles = [
        c.get("title") or c["id"]
        for band, group in bands if band == "HIGH" for c in group
    ]
    lead = ", ".join(crit_titles + high_titles) if (crit_titles or high_titles) else "none"
    name = html.escape(Path(path).name)

    style = """
    :root { color-scheme: light dark; }
    body { font: 15px/1.5 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
           margin: 0; padding: 2rem; max-width: 60rem; margin-inline: auto; color: #1b1b1f; background: #fff; }
    h1 { font-size: 1.6rem; margin: 0 0 .25rem; }
    h2 { font-size: 1.2rem; margin: 2rem 0 .5rem; border-bottom: 2px solid #ececef; padding-bottom: .25rem; }
    .tldr { background: #f5f7fa; border-left: 4px solid #4b6bfb; padding: .75rem 1rem; border-radius: 4px; }
    .meta { color: #5b5b66; font-size: .9rem; margin: .5rem 0 0; }
    ul.issues { list-style: none; padding: 0; margin: .5rem 0; }
    li.issue { border: 1px solid #e4e4ea; border-radius: 6px; padding: .75rem 1rem; margin: .5rem 0; }
    .issue-head { display: flex; align-items: center; gap: .6rem; }
    .issue-title { font-weight: 600; }
    .sev { font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .03em;
           padding: .12rem .5rem; border-radius: 999px; color: #fff; white-space: nowrap; }
    .sev-warning { background: #c0392b; }
    .sev-note { background: #b9770e; }
    .sev-info { background: #5b6673; }
    .evidence { color: #5b5b66; font-size: .9rem; margin: .4rem 0 0; }
    .suggestion { margin: .4rem 0 0; }
    .sources a { color: #4b6bfb; }
    .fix-note { font-size: .85rem; color: #2d7a3a; margin: .25rem 0 .75rem; }
    table.graph { border-collapse: collapse; width: 100%; font-size: .88rem; }
    table.graph th, table.graph td { border: 1px solid #e4e4ea; padding: .35rem .55rem; text-align: left; }
    table.graph th { background: #f5f7fa; }
    .empty { color: #5b5b66; font-style: italic; }
    footer { margin-top: 2rem; color: #5b5b66; font-size: .85rem; }
    """

    L: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta http-equiv="Content-Security-Policy" '
        'content="default-src \'none\'; style-src \'unsafe-inline\'">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f"  <title>Performance report — {name}</title>",
        f"  <style>{style}  </style>",
        "</head>",
        "<body>",
        f"  <h1>Performance report — {name}</h1>",
        f'  <p class="tldr"><strong>Summary:</strong> {kind} connection. '
        f"{len(hits)} issue(s) found"
        + (f" ({counts.get('CRITICAL', 0)} critical, {counts.get('HIGH', 0)} high)." if hits else ".")
        + f" Top issues: {html.escape(lead)}.</p>",
        f'  <p class="meta">Workbook version {html.escape(str(usage.get("version") or "?"))} · '
        f"{summary['datasources']} datasource(s) · {summary['worksheets']} worksheet(s) · "
        f"{summary['dashboards']} dashboard(s)</p>",
    ]

    if warnings:
        L.append("  <h2>Warnings</h2>")
        L.append('  <ul class="issues">')
        for w in warnings:
            L.append(
                f'    <li class="issue"><p class="suggestion">{html.escape(w["message"])}</p></li>'
            )
        L.append("  </ul>")

    # --- Issues grouped by fixability (item 3) ---
    L.append("  <h2>Issues the optimizer can fix for you</h2>")
    if fixable:
        L.append(
            '  <p class="fix-note">These are applied to a copy of your workbook — '
            "your original is never changed.</p>"
        )
        L.append('  <ul class="issues">')
        for chk in fixable:
            L.extend(_html_issue_card(chk, column))
        L.append("  </ul>")
    else:
        L.append('  <p class="empty">No auto-fixable issues found.</p>')

    L.append("  <h2>Issues to fix yourself in Tableau Studio</h2>")
    if author_only:
        L.append('  <ul class="issues">')
        for chk in author_only:
            L.extend(_html_issue_card(chk, column))
        L.append("  </ul>")
    else:
        L.append('  <p class="empty">No author-only issues found.</p>')

    # --- Workbook structure (graph as a table, no external JS) ---
    L.append("  <h2>Workbook structure</h2>")
    L.append('  <table class="graph">')
    L.append("    <thead><tr><th>Kind</th><th>Name</th><th>Detail</th></tr></thead>")
    L.append("    <tbody>")
    L.append(
        f'      <tr><td>workbook</td><td>{name}</td>'
        f'<td>version {html.escape(str(usage.get("version") or "?"))}</td></tr>'
    )
    for ds in usage["datasources"]:
        conn = "extract" if ds.get("isExtract") else (ds.get("connectionClass") or "live")
        n = len(ds.get("columns") or [])
        label = html.escape(str(ds.get("caption") or ds.get("name")))
        L.append(f"      <tr><td>datasource</td><td>{label}</td><td>{html.escape(conn)}, {n} fields</td></tr>")
    for ws in usage["worksheets"]:
        src = html.escape(", ".join(ws.get("datasources") or []) or "-")
        L.append(f'      <tr><td>worksheet</td><td>{html.escape(ws["name"])}</td><td>sources: {src}</td></tr>')
    for db in usage["dashboards"]:
        zones = html.escape(", ".join(db.get("worksheetZones") or []) or "-")
        size = html.escape(str(db.get("sizingMode") or "?"))
        L.append(f'      <tr><td>dashboard</td><td>{html.escape(db["name"])}</td><td>{size}; sheets: {zones}</td></tr>')
    for p in usage.get("parameters") or []:
        L.append(f'      <tr><td>parameter</td><td>{html.escape(str(p.get("caption") or p.get("name")))}</td><td></td></tr>')
    for label in _graph_filter_labels(usage):
        L.append(f"      <tr><td>filter</td><td>{html.escape(label)}</td><td></td></tr>")
    for calc in _graph_calcs(usage):
        used = html.escape(", ".join(calc.get("usedOnWorksheets") or []) or "unused")
        dsc = html.escape(str(calc.get("datasourceCaption") or "-"))
        L.append(f'      <tr><td>calculation</td><td>{html.escape(calc["label"])}</td><td>{dsc}; {used}</td></tr>')
    L.append("    </tbody>")
    L.append("  </table>")

    L.append(
        "  <footer>These are known risk patterns, not measured load times. "
        "Use Tableau Performance Recorder if you need query-vs-render evidence.</footer>"
    )
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L) + "\n"


def _print_fail(command: str, path: str, err_type: str, message: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps(fail_envelope(command, path, err_type, message), indent=2))
    else:
        print(f"error: {message}")
    return 1


def _human(summary: dict) -> str:
    lines = [
        f"Workbook (version {summary['version']})",
        f"  datasources : {summary['datasources']}",
        f"  worksheets  : {summary['worksheets']}",
        f"  dashboards  : {summary['dashboards']}",
        f"  fields      : {summary['fields']} ({summary['calculations']} calcs, "
        f"{summary['hiddenFields']} hidden)",
    ]
    if summary["orphanWorksheets"]:
        lines.append(f"  orphan sheets: {', '.join(summary['orphanWorksheets'])}")
    nparam = summary.get("parameters") or 0
    if nparam:
        lines.append(f"  parameters  : {nparam}")
    for c in summary["connections"]:
        kind = "extract" if c["isExtract"] else (c["connectionClass"] or "?")
        lines.append(f"  ds '{c['caption']}' -> {kind}")
    unused = summary.get("unusedFieldLabels") or summary.get("unusedFields") or []
    if unused:
        lines.append(f"  unused fields: {len(unused)}")
        for f in unused:
            lines.append(f"      {f}")
    return "\n".join(lines)


def _source_links(cid: str) -> str:
    rec = CATALOG_BY_ID.get(cid)
    if not rec:
        return ""
    parts = []
    for src in rec["sources"]:
        if src.get("url"):
            parts.append(f"[{src['label']}]({src['url']})")
        elif src.get("label"):
            parts.append(src["label"])
    return "; ".join(parts)


def _filter_display_name(raw: str, index: int) -> str:
    text = (raw or "").strip()
    if not text or _looks_internal(text):
        return f"Filter {index + 1}"
    pretty = _caption_from_field_ref(text)
    if pretty and pretty != "Calculation":
        return pretty
    return text.strip("[]")


def _graph_calcs(usage: dict) -> list[dict]:
    out: list[dict] = []
    for c in usage.get("columns") or []:
        if c.get("kind") != "calculation":
            continue
        name = c.get("name") or ""
        if name.startswith("[__tableau_internal"):
            continue
        if c.get("hidden") and not c.get("usedOnWorksheets"):
            continue
        cap = (c.get("caption") or "").strip()
        if cap and not _looks_internal(cap):
            label = cap
        else:
            label = _caption_from_field_ref(name) or cap or name
            if label == "Calculation":
                label = cap or name.strip("[]")
        if _looks_internal(label):
            continue
        row = dict(c)
        row["label"] = label.strip("[]")
        out.append(row)
    return out


def _graph_filter_labels(usage: dict) -> list[str]:
    labels: list[str] = []
    for db in usage.get("dashboards") or []:
        labels.extend(db.get("filters") or [])
    for ws in usage.get("worksheets") or []:
        labels.extend(ws.get("filters") or [])
    return _dedupe_labels(labels)


def _param_label(p: dict) -> str:
    return p.get("caption") or p.get("name") or "Parameter"


def diagrams_workbook(usage: dict, *, detailed: bool = False, title: str | None = None) -> str:
    wb_name = title or Path(usage.get("_path") or "workbook").name
    used_on_dash = {w for db in usage["dashboards"] for w in db["worksheetZones"]}
    calcs = _graph_calcs(usage)
    params = usage.get("parameters") or []
    filter_labels = _graph_filter_labels(usage)
    lines = [
        "flowchart TB",
        _mermaid_node("workbook", "wb", wb_name),
    ]
    declared: set[str] = {"wb"}

    def emit(kind: str, nid: str, label: str) -> str:
        if nid not in declared:
            declared.add(nid)
            lines.append(_mermaid_node(kind, nid, label))
        return nid

    large = not detailed and (
        len(usage["worksheets"]) >= 25
        or sum(1 for c in usage["columns"] if c["kind"] == "calculation") >= 100
    )
    if large:
        for ds in usage["datasources"]:
            n = len(ds["columns"])
            did = _mermaid_id(ds["caption"] or ds["name"], "ds")
            extra = f" · {n} fields"
            label = f"{ds['caption'] or ds['name']}{extra}"
            emit("datasource", did, label)
            lines.append(f"  wb --> {did}")
        n_ws = len(usage["worksheets"])
        n_db = len(usage["dashboards"])
        emit("worksheet", "ws_all", f"{n_ws} worksheets")
        emit("dashboard", "db_all", f"{n_db} dashboards")
        lines.append("  wb --> ws_all")
        lines.append("  wb --> db_all")
        if filter_labels:
            emit("filter", "fl_all", f"{len(filter_labels)} filters")
            lines.append("  wb --> fl_all")
        if params:
            emit("parameter", "pm_all", f"{len(params)} parameters")
            lines.append("  wb --> pm_all")
        if calcs:
            emit("calculation", "calc_all", f"{len(calcs)} calculations")
            lines.append("  wb --> calc_all")
        lines.extend(_mermaid_classdefs())
        return "\n".join(lines)
    for ds in usage["datasources"]:
        did = _mermaid_id(ds["caption"] or ds["name"], "ds")
        label = ds["caption"] or ds["name"]
        if detailed:
            kind = "extract" if ds.get("isExtract") else (ds.get("connectionClass") or "live")
            n = len(ds.get("columns") or [])
            label = f"{label} · {kind} · {n} fields"
        emit("datasource", did, label)
    used_ds = {cap for ws in usage["worksheets"] for cap in (ws.get("datasources") or [])}
    for ds in usage["datasources"]:
        caption = ds["caption"] or ds["name"]
        if caption not in used_ds:
            lines.append(f"  wb --> {_mermaid_id(caption, 'ds')}")
    named_calcs = calcs if detailed else calcs[:30]
    for calc in named_calcs:
        cid = _mermaid_id(calc["name"], "calc")
        emit("calculation", cid, calc["label"])
        ds_cap = calc.get("datasourceCaption")
        if ds_cap:
            did = _mermaid_id(ds_cap, "ds")
            lines.append(f"  {did} --> {cid}")
    if not detailed and len(calcs) > 30:
        emit("calculation", "calc_more", f"{len(calcs) - 30} more calculations")
        lines.append("  wb --> calc_more")
    for ws in usage["worksheets"]:
        wid = _mermaid_id(ws["name"], "ws")
        emit("worksheet", wid, ws["name"])
        if ws["name"] not in used_on_dash:
            lines.append(f"  wb --> {wid}")
        for caption in ws["datasources"]:
            did = _mermaid_id(caption, "ds")
            lines.append(f"  {wid} --> {did}")
        for flabel in ws.get("filters") or []:
            fid = _mermaid_id(flabel, "fl")
            emit("filter", fid, flabel)
            lines.append(f"  {wid} --> {fid}")
        for calc in named_calcs:
            if ws["name"] in (calc.get("usedOnWorksheets") or []):
                cid = _mermaid_id(calc["name"], "calc")
                lines.append(f"  {wid} --> {cid}")
    for db in usage["dashboards"]:
        bid = _mermaid_id(db["name"], "db")
        label = db["name"]
        if detailed:
            n = len(db.get("worksheetZones") or [])
            size = db.get("sizingMode") or "?"
            label = f"{label} · {n} views · {size}"
        emit("dashboard", bid, label)
        lines.append(f"  wb --> {bid}")
        for z in db["worksheetZones"]:
            wid = _mermaid_id(z, "ws")
            lines.append(f"  {bid} --> {wid}")
        for flabel in db.get("filters") or []:
            fid = _mermaid_id(flabel, "fl")
            emit("filter", fid, flabel)
            lines.append(f"  {bid} --> {fid}")
    for p in params:
        pid = _mermaid_id(p.get("name") or _param_label(p), "pm")
        emit("parameter", pid, _param_label(p))
        lines.append(f"  wb --> {pid}")
    lines.extend(_mermaid_classdefs())
    return "\n".join(lines)


def _mermaid_classdefs() -> list[str]:
    return [
        "  classDef workbook fill:#1f4e79,color:#ffffff,stroke:#0d2b4a",
        "  classDef dashboard fill:#2e7d32,color:#ffffff,stroke:#1b5e20",
        "  classDef worksheet fill:#1565c0,color:#ffffff,stroke:#0d47a1",
        "  classDef datasource fill:#6a1b9a,color:#ffffff,stroke:#4a148c",
        "  classDef filter fill:#ef6c00,color:#ffffff,stroke:#e65100",
        "  classDef parameter fill:#00838f,color:#ffffff,stroke:#006064",
        "  classDef calculation fill:#f9a825,color:#212121,stroke:#f57f17",
    ]


def diagrams_findings(checks: list[dict]) -> list[dict]:
    out = []
    for chk in checks:
        if chk["status"] != "hit" or not chk["findings"]:
            continue
        lines = ["flowchart LR"]
        drew = False
        if chk["id"] == "consolidate-duplicate-calcs":
            for group in chk["findings"]:
                for mem in group.get("members", []):
                    cid = _mermaid_id(mem.get("caption") or mem.get("name", "c"), "c")
                    lines.append(
                        f'  {cid}["{_mermaid_label(mem.get("caption") or mem.get("name", ""))}"]'
                    )
                    for sheet in mem.get("usedOnWorksheets") or []:
                        sid = _mermaid_id(sheet, "s")
                        lines.append(f'  {sid}["{_mermaid_label(sheet)}"]')
                        lines.append(f"  {cid} --> {sid}")
                        drew = True
                    for dash in mem.get("usedOnDashboards") or []:
                        did = _mermaid_id(dash, "d")
                        lines.append(f'  {did}["{_mermaid_label(dash)}"]')
                        for sheet in mem.get("usedOnWorksheets") or []:
                            lines.append(f"  {_mermaid_id(sheet, 's')} --> {did}")
                            drew = True
        else:
            finding = chk["findings"][0]
            label = finding.get("caption") or finding.get("name") or chk["id"]
            lines.append(f'  n["{_mermaid_label(str(label))}"]')
            drew = True
        if drew:
            out.append({"id": chk["id"], "mermaid": "\n".join(lines)})
    return out


# --- checks ----------------------------------------------------------------
def _calcs(usage: dict) -> list[dict]:
    return [c for c in usage["columns"] if c["kind"] == "calculation"]


def _xml(usage: dict) -> str:
    return usage["xml"]


def check_extracts_over_live(usage: dict) -> dict:
    live = [d for d in usage["datasources"] if not d["isExtract"]]
    if not usage["datasources"]:
        return _result("extracts-over-live", "skipped", skip_reason="no datasources")
    if live:
        findings = [
            {
                "caption": d["caption"],
                "connectionClass": d["connectionClass"],
                "connectionType": d.get("connectionType", "unknown"),
                "isLiveDatabase": d.get("isLiveDatabase", False),
            }
            for d in live
        ]
        has_live_db = any(f["isLiveDatabase"] for f in findings)
        suggestion = (
            "Live database connection(s) found — an extract usually loads much faster "
            "unless you need real-time data."
            if has_live_db
            else "Consider an extract unless you need real-time data."
        )
        return _result("extracts-over-live", "hit", findings, suggestion)
    return _result("extracts-over-live", "clear")


def check_hide_unused_fields(usage: dict) -> dict:
    names = unused_column_names(usage)
    if not names:
        return _result("hide-unused-fields", "clear")
    findings = [
        {
            "name": c["name"],
            "caption": c["caption"],
            "usedOnWorksheets": c["usedOnWorksheets"],
            "usedOnDashboards": c["usedOnDashboards"],
        }
        for c in usage["columns"]
        if c["name"] in names
    ]
    return _result(
        "hide-unused-fields",
        "hit",
        findings,
        f"Hide {len(names)} unused field(s) before extracting.",
    )


def check_close_unused_datasources(usage: dict) -> dict:
    used_caps = {cap for ws in usage["worksheets"] for cap in ws["datasources"]}
    unused = [
        d
        for d in usage["datasources"]
        if d["caption"] not in used_caps and d["name"] not in used_caps
    ]
    if not unused:
        return _result("close-unused-datasources", "clear")
    return _result(
        "close-unused-datasources",
        "hit",
        [{"caption": d["caption"], "name": d["name"]} for d in unused],
        "Close datasources that no worksheet uses.",
    )


def check_minimize_data_volume(usage: dict) -> dict:
    xml = _xml(usage)
    has_ds_filter = bool(re.search(r"<datasource-filters\b", xml, re.I))
    has_extract_filter = bool(
        re.search(
            r"<extract\b[^>]*enabled=['\"]true['\"][^>]*>.*?<filters\b",
            xml,
            re.I | re.DOTALL,
        )
    ) or bool(
        re.search(
            r"<extract\b[^>]*>.*?<filters\b[^>]*>\s*<filter\b",
            xml,
            re.I | re.DOTALL,
        )
    )
    if has_ds_filter or has_extract_filter:
        return _result("minimize-data-volume", "clear")
    return _result(
        "minimize-data-volume",
        "hit",
        [],
        "No data-source or extract filter detected; data volume may be unbounded.",
    )


def _custom_sql_blocks(xml: str) -> list[str]:
    return re.findall(r"<relation\b[^>]*\btype=['\"]text['\"][^>]*>.*?</relation>", xml, re.DOTALL)


def check_avoid_custom_sql(usage: dict) -> dict:
    blocks = _custom_sql_blocks(_xml(usage))
    if not blocks:
        return _result("avoid-custom-sql", "skipped", skip_reason="no custom SQL relation")
    return _result(
        "avoid-custom-sql",
        "hit",
        [{"excerpt": b[:200]} for b in blocks],
        "Avoid custom SQL; prefer native tables/relations, or extract if you must keep it.",
    )


def check_avoid_params_in_custom_sql(usage: dict) -> dict:
    blocks = _custom_sql_blocks(_xml(usage))
    if not blocks:
        return _result(
            "avoid-params-in-custom-sql", "skipped", skip_reason="no custom SQL relation"
        )
    hits = [b for b in blocks if "Parameters" in b or "<parameter" in b.lower()]
    if not hits:
        return _result("avoid-params-in-custom-sql", "clear")
    return _result(
        "avoid-params-in-custom-sql",
        "hit",
        [],
        "Parameter references in custom SQL force a subquery wrap.",
    )


def check_remove_sql_order_by(usage: dict) -> dict:
    blocks = _custom_sql_blocks(_xml(usage))
    if not blocks:
        return _result("remove-sql-order-by", "skipped", skip_reason="no custom SQL relation")
    hits = [b for b in blocks if re.search(r"\bORDER\s+BY\b", b, re.I)]
    if not hits:
        return _result("remove-sql-order-by", "clear")
    return _result(
        "remove-sql-order-by",
        "hit",
        [],
        "ORDER BY in custom SQL is wasted; Tableau re-sorts after load.",
    )


def check_prefer_relationships(usage: dict) -> dict:
    xml = _xml(usage)
    joins = re.findall(r"<relation\b[^>]*\btype=['\"]join['\"]", xml)
    collections = re.findall(r"<relation\b[^>]*\btype=['\"]collection['\"]", xml)
    if not joins and not collections:
        return _result("prefer-relationships", "skipped", skip_reason="single-table or no joins")
    if joins and not collections:
        return _result(
            "prefer-relationships",
            "hit",
            [],
            "Physical joins found; relationships query only tables a viz needs.",
        )
    return _result("prefer-relationships", "clear")


def check_referential_integrity(usage: dict) -> dict:
    xml = _xml(usage)
    joins = re.findall(r"<relation\b[^>]*\btype=['\"]join['\"]", xml)
    if not joins:
        return _result("referential-integrity", "skipped", skip_reason="no joins")
    if "assume-referential-integrity" in xml or "referential-integrity" in xml:
        return _result("referential-integrity", "clear")
    return _result(
        "referential-integrity",
        "hit",
        [],
        "Enable referential integrity so Tableau can simplify joins.",
    )


def check_limit_data_blending(usage: dict) -> dict:
    multi = [w for w in usage["worksheets"] if len(w["datasources"]) > 1]
    if not multi:
        return _result("limit-data-blending", "clear")
    return _result(
        "limit-data-blending",
        "hit",
        [{"name": w["name"], "datasources": w["datasources"]} for w in multi],
        "Worksheets blend multiple sources; consider aggregating before blending.",
    )


def check_count_over_countd(usage: dict) -> dict:
    hits = [c for c in _calcs(usage) if re.search(r"\bCOUNTD\s*\(", c["formula"] or "", re.I)]
    if not hits:
        return _result("count-over-countd", "clear")
    return _result(
        "count-over-countd",
        "hit",
        [_col_finding(c) for c in hits],
        "COUNTD is slow; prefer COUNT when distinctness is not required.",
    )


def check_min_max_over_avg_attr(usage: dict) -> dict:
    hits = [
        c
        for c in _calcs(usage)
        if re.search(r"\b(AVG|ATTR)\s*\(", c["formula"] or "", re.I)
    ]
    if not hits:
        return _result("min-max-over-avg-attr", "clear")
    return _result(
        "min-max-over-avg-attr",
        "hit",
        [_col_finding(c) for c in hits],
        "MIN/MAX often outperform AVG and ATTR.",
    )


def check_limit_calc_fields(usage: dict) -> dict:
    n = len(_calcs(usage))
    if n < 15:
        return _result("limit-calc-fields", "clear")
    return _result(
        "limit-calc-fields",
        "hit",
        [{"count": n}],
        f"{n} calculated fields; fewer fields means less to parse.",
    )


def check_limit_cross_source_calcs(usage: dict) -> dict:
    # Cross-source: formula mentions a second datasource caption/name.
    caps = [d["caption"] for d in usage["datasources"] if d["caption"]]
    if len(caps) < 2:
        return _result("limit-cross-source-calcs", "skipped", skip_reason="single datasource")
    hits = []
    for c in _calcs(usage):
        formula = c["formula"] or ""
        others = [cap for cap in caps if cap != c["datasourceCaption"] and cap in formula]
        if others:
            hits.append(_col_finding(c))
    if not hits:
        return _result("limit-cross-source-calcs", "clear")
    return _result(
        "limit-cross-source-calcs",
        "hit",
        hits,
        "Cross-source calculations query sequentially.",
    )


def check_minimize_lod(usage: dict) -> dict:
    hits = [
        c
        for c in _calcs(usage)
        if re.search(r"\{[^}]*(FIXED|INCLUDE|EXCLUDE)\b", c["formula"] or "", re.I)
    ]
    if not hits:
        return _result("minimize-lod", "clear")
    return _result(
        "minimize-lod",
        "hit",
        [_col_finding(c) for c in hits],
        "LOD expressions add compile cost; keep them only when they earn their keep.",
    )


def check_avoid_nested_calcs(usage: dict) -> dict:
    def _depth(name: str, stack: set[str]) -> int:
        if name in stack:
            return 0
        col = next((c for c in usage["columns"] if c["name"] == name), None)
        if not col or not col["references"]:
            return 0
        stack.add(name)
        d = 1 + max((_depth(r, stack) for r in col["references"]), default=0)
        stack.remove(name)
        return d

    deep = []
    for c in _calcs(usage):
        d = _depth(c["name"], set())
        if d >= 3:
            rec = _col_finding(c)
            rec["nestingDepth"] = d
            deep.append(rec)
    if not deep:
        return _result("avoid-nested-calcs", "clear")
    return _result(
        "avoid-nested-calcs",
        "hit",
        deep,
        "Deep calc nesting slows query compilation.",
    )


def check_limit_table_calcs(usage: dict) -> dict:
    pat = re.compile(
        r"\b(LOOKUP|RUNNING_SUM|RUNNING_AVG|WINDOW_|INDEX|SIZE|TOTAL|PREVIOUS_VALUE)\s*\(",
        re.I,
    )
    hits = [c for c in _calcs(usage) if pat.search(c["formula"] or "")]
    if not hits:
        return _result("limit-table-calcs", "clear")
    return _result(
        "limit-table-calcs",
        "hit",
        [_col_finding(c) for c in hits],
        "Table calcs run in the local engine; prefer an LOD when it is cheaper.",
    )


def check_avoid_hierarchies(usage: dict) -> dict:
    if "<drill-path" not in _xml(usage) and "<drill-paths" not in _xml(usage):
        return _result("avoid-hierarchies", "skipped", skip_reason="no drill-paths")
    return _result(
        "avoid-hierarchies",
        "hit",
        [],
        "Hierarchies add local compute; drop unused drill paths.",
    )


def _col_finding(c: dict) -> dict:
    return {
        "name": c["name"],
        "caption": c["caption"],
        "formula": c["formula"],
        "formulaNormalized": c["formulaNormalized"],
        "usedOnWorksheets": c["usedOnWorksheets"],
        "usedOnDashboards": c["usedOnDashboards"],
    }


def check_consolidate_duplicate_calcs(usage: dict) -> dict:
    calcs = [c for c in _calcs(usage) if c["formulaNormalized"]]
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in calcs:
        groups[c["formulaNormalized"]].append(c)
    exact = [g for g in groups.values() if len(g) >= 2]
    wrappers = []
    norms = [(c, c["formulaNormalized"]) for c in calcs]
    for inner, n_inner in norms:
        if not n_inner:
            continue
        for outer, n_outer in norms:
            if inner["name"] == outer["name"]:
                continue
            if n_inner in n_outer and n_inner != n_outer and len(n_inner) >= 8:
                wrappers.append((inner, outer))
    if not exact and not wrappers:
        if not calcs:
            return _result("consolidate-duplicate-calcs", "skipped", skip_reason="no calculations")
        return _result("consolidate-duplicate-calcs", "clear")
    findings = []
    for g in exact:
        prefer = max(g, key=lambda c: (len(c["usedOnWorksheets"]), c["caption"]))
        findings.append(
            {
                "kind": "duplicate-formula",
                "formulaNormalized": g[0]["formulaNormalized"],
                "members": [_col_finding(c) for c in g],
                "keepCaption": prefer["caption"],
            }
        )
    for inner, outer in wrappers:
        findings.append(
            {
                "kind": "wrapper",
                "inner": _col_finding(inner),
                "outer": _col_finding(outer),
            }
        )
    return _result(
        "consolidate-duplicate-calcs",
        "hit",
        findings,
        "Duplicate or wrapped calc logic found. Consolidate captions to reduce cognitive load; do not rewrite in this tool.",
    )


def _binary_string_hit(formula: str) -> bool:
    text = formula or ""
    if not re.search(r"\b(IF|CASE|IIF)\b", text, re.I):
        return False
    lits = _STRING_LIT_RE.findall(text)
    # Branch results: literals after THEN/ELSE (rough).
    branch = re.findall(r"(?:THEN|ELSE)\s+\"([^\"]*)\"", text, flags=re.I)
    if not branch:
        branch = lits
    return len(set(branch)) == 2


def check_binary_string_branches(usage: dict) -> dict:
    calcs = _calcs(usage)
    if not calcs:
        return _result("binary-string-branches", "skipped", skip_reason="no calculations")
    hits = [c for c in calcs if _binary_string_hit(c["formula"] or "")]
    if not hits:
        return _result("binary-string-branches", "clear")
    return _result(
        "binary-string-branches",
        "hit",
        [_col_finding(c) for c in hits],
        "Two string literals on an IF/CASE look like a Boolean. Grey area: leave the expression to the author.",
    )


def _filter_zones(usage: dict) -> int:
    return sum(db["filterZoneCount"] for db in usage["dashboards"])


def check_minimize_quick_filters(usage: dict) -> dict:
    n = _filter_zones(usage)
    if n == 0:
        return _result("minimize-quick-filters", "clear")
    if n < 4:
        return _result("minimize-quick-filters", "clear")
    return _result(
        "minimize-quick-filters",
        "hit",
        [{"filterZoneCount": n}],
        f"{n} shown filter cards; each needs an option query.",
    )


def check_avoid_only_relevant_values(usage: dict) -> dict:
    xml = _xml(usage)
    if re.search(r"relevant", xml, re.I) and re.search(r"filter", xml, re.I):
        if re.search(r"only.?relevant|show-relevant|relevant-values", xml, re.I):
            return _result(
                "avoid-only-relevant-values",
                "hit",
                [],
                "Only Relevant Values re-queries when other filters change.",
            )
    return _result("avoid-only-relevant-values", "clear")


def check_context_filters_not_query_lever(usage: dict) -> dict:
    # Presence is order-of-operations only. Missing is not a fail.
    return _result("context-filters-not-query-lever", "clear")


def check_filter_actions(usage: dict) -> dict:
    xml = _xml(usage)
    if "<actions" not in xml and "<action " not in xml:
        return _result(
            "filter-actions-over-quick-filters",
            "skipped",
            skip_reason="no actions element present",
        )
    if _filter_zones(usage) >= 4:
        return _result(
            "filter-actions-over-quick-filters",
            "hit",
            [],
            "Prefer filter actions over many quick filters for guided drill-down.",
        )
    return _result("filter-actions-over-quick-filters", "clear")


def check_avoid_user_filters(usage: dict) -> dict:
    hits = [c for c in _calcs(usage) if re.search(r"\bUSERNAME\s*\(", c["formula"] or "", re.I)]
    xml = _xml(usage)
    if "user-filter" in xml or hits:
        return _result(
            "avoid-user-filters",
            "hit",
            [_col_finding(c) for c in hits],
            "User filters prevent shared query cache.",
        )
    return _result("avoid-user-filters", "clear")


def check_limit_filter_count(usage: dict) -> dict:
    n = _filter_zones(usage)
    if n >= 5:
        return _result(
            "limit-filter-count",
            "hit",
            [{"filterZoneCount": n}],
            "Filters compound query complexity across worksheets.",
        )
    return _result("limit-filter-count", "clear")


def check_apply_button(usage: dict) -> dict:
    n = _filter_zones(usage)
    if n == 0:
        return _result("apply-button", "skipped", skip_reason="no shown filter cards")
    if re.search(r"apply-button|show-apply", _xml(usage), re.I):
        return _result("apply-button", "clear")
    if n >= 2:
        return _result(
            "apply-button",
            "hit",
            [{"filterZoneCount": n}],
            "Show Apply Button to batch multi-select filter changes.",
        )
    return _result("apply-button", "clear")


def check_avoid_keep_only_exclude(usage: dict) -> dict:
    xml = _xml(usage)
    if re.search(r"kind=['\"](exclude|keep)['\"]", xml):
        return _result(
            "avoid-keep-only-exclude",
            "hit",
            [],
            "Keep Only / Exclude on discrete items can be expensive.",
        )
    return _result("avoid-keep-only-exclude", "clear")


def check_limit_worksheets_per_dashboard(usage: dict) -> dict:
    heavy = [d for d in usage["dashboards"] if len(d["worksheetZones"]) > 3]
    if not usage["dashboards"]:
        return _result("limit-worksheets-per-dashboard", "skipped", skip_reason="no dashboards")
    if not heavy:
        return _result("limit-worksheets-per-dashboard", "clear")
    return _result(
        "limit-worksheets-per-dashboard",
        "hit",
        [{"name": d["name"], "worksheetZones": d["worksheetZones"]} for d in heavy],
        "Tableau's guideline is two or three views per dashboard.",
    )


def check_fixed_dashboard_size(usage: dict) -> dict:
    autos = [
        d
        for d in usage["dashboards"]
        if (d["sizingMode"] or "").lower() in {"automatic", "auto"}
    ]
    if not usage["dashboards"]:
        return _result("fixed-dashboard-size", "skipped", skip_reason="no dashboards")
    if not autos:
        return _result("fixed-dashboard-size", "clear")
    return _result(
        "fixed-dashboard-size",
        "hit",
        [{"name": d["name"], "sizingMode": d["sizingMode"]} for d in autos],
        "Fixed-size dashboards can be cached; automatic size re-renders per request.",
    )


def check_limit_viz_in_tooltip(usage: dict) -> dict:
    xml = _xml(usage)
    if "viz-in-tooltip" in xml or re.search(r"<tooltip[^>]*worksheet", xml):
        return _result(
            "limit-viz-in-tooltip",
            "hit",
            [],
            "Keep Viz-in-Tooltip targets simple.",
        )
    return _result("limit-viz-in-tooltip", "clear")


def check_minimize_image_sizes(usage: dict, path: str) -> dict:
    if not is_twbx(path):
        return _result("minimize-image-sizes", "skipped", skip_reason="not a .twbx")
    heavy = []
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            name = info.filename.lower()
            if name.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                if info.file_size > 50 * 1024:
                    heavy.append({"name": info.filename, "bytes": info.file_size})
    if not heavy:
        return _result("minimize-image-sizes", "clear")
    return _result(
        "minimize-image-sizes",
        "hit",
        heavy,
        "Images over 50kb render more slowly.",
    )


def check_limit_dashboard_actions(usage: dict) -> dict:
    xml = _xml(usage)
    actions = len(re.findall(r"<action\b", xml))
    if actions == 0:
        return _result("limit-dashboard-actions", "skipped", skip_reason="no actions element present")
    if actions > 5:
        return _result(
            "limit-dashboard-actions",
            "hit",
            [{"actionCount": actions}],
            "Actions run sequentially; excess compounds latency.",
        )
    return _result("limit-dashboard-actions", "clear")


def check_prefer_tiled_over_floating(usage: dict) -> dict:
    floating = [d for d in usage["dashboards"] if d.get("hasFloating")]
    if not floating:
        return _result("prefer-tiled-over-floating", "clear")
    return _result(
        "prefer-tiled-over-floating",
        "hit",
        [{"name": d["name"]} for d in floating],
        "Floating works best on fixed-size dashboards.",
    )


def check_sets_for_top_n(usage: dict) -> dict:
    xml = _xml(usage)
    has_set = "<group" in xml and "set" in xml.lower() or re.search(r"<set\b", xml)
    has_top = re.search(r"end=['\"]top['\"]|filter-class=['\"]quantitative['\"]", xml)
    if not has_top:
        return _result("sets-for-top-n", "skipped", skip_reason="no top-n filter detected")
    if has_set:
        return _result("sets-for-top-n", "clear")
    return _result(
        "sets-for-top-n",
        "hit",
        [],
        "Prefer native sets / top-N over equivalent calculations.",
    )


def check_keep_tooltips_simple(usage: dict) -> dict:
    tooltips = re.findall(r"<tooltip\b[^>]*>.*?</tooltip>", _xml(usage), re.DOTALL | re.I)
    if not tooltips:
        return _result("keep-tooltips-simple", "skipped", skip_reason="no tooltip XML")
    heavy = [t for t in tooltips if t.count("<") > 20 or len(t) > 2000]
    if heavy:
        return _result(
            "keep-tooltips-simple",
            "hit",
            [],
            "Heavy tooltips add hover render cost.",
        )
    return _result("keep-tooltips-simple", "clear")


def check_upgrade_tableau_version(usage: dict) -> dict:
    return _result(
        "upgrade-tableau-version",
        "clear",
        [{"version": usage["version"]}],
        "",
    )


_HIGH_CARD_RE = re.compile(
    r"customer|product name|\bcity\b|email|zip|postal|address|order id|\bsku\b",
    re.I,
)
_PARENT_GRAIN_RE = re.compile(r"\b(state|region|country|category|segment)\b", re.I)
_CHILD_GRAIN_RE = re.compile(
    r"\b(city|product name|postal|zip|customer name|sub-category|subcategory)\b",
    re.I,
)
_AGG_FN_RE = re.compile(
    r"\b(SUM|AVG|MIN|MAX|COUNT|COUNTD|ATTR|TOTAL|STDEV|VAR)\s*\(", re.I
)
_FORMAT_SKIP_ATTRS = {"height", "width", "size", "space"}


def check_prefer_numbers_booleans(usage: dict) -> dict:
    calcs = _calcs(usage)
    if not calcs:
        return _result("prefer-numbers-booleans", "skipped", skip_reason="no calculations")
    hits = []
    for c in calcs:
        dt = (c.get("datatype") or "").lower()
        formula = c.get("formula") or ""
        if dt not in {"string", "date", "datetime"}:
            continue
        if re.search(r"\b(IF|CASE|IIF|STR)\b", formula, re.I):
            hits.append(_col_finding(c))
    if not hits:
        return _result("prefer-numbers-booleans", "clear")
    return _result(
        "prefer-numbers-booleans",
        "hit",
        hits,
        "String/date IF/CASE/STR calcs are slower than numbers and Booleans.",
    )


def check_avoid_row_level_param_calcs(usage: dict) -> dict:
    calcs = _calcs(usage)
    hits = []
    for c in calcs:
        formula = c.get("formula") or ""
        if "[Parameters]." not in formula:
            continue
        if _AGG_FN_RE.search(formula):
            continue
        hits.append(_col_finding(c))
    if not hits:
        return _result("avoid-row-level-param-calcs", "clear")
    return _result(
        "avoid-row-level-param-calcs",
        "hit",
        hits,
        "Row-level parameter calculations recompute per row.",
    )


def _native_pattern(formula: str) -> str | None:
    text = formula or ""
    if re.search(r"\b(DATETRUNC|DATEPART)\s*\(", text, re.I):
        return "custom-date"
    then_strings = re.findall(r"(?:THEN|ELSE)\s+\"", text, flags=re.I)
    if len(re.findall(r"\bWHEN\b", text, re.I)) >= 3 and then_strings:
        return "group"
    if len(re.findall(r"\bELSEIF\b", text, re.I)) >= 2:
        return "group-or-bin"
    if re.search(r"\[[^]]+\]\s*\+\s*(\"|'|\[)", text):
        return "combined-field"
    return None


def check_prefer_native_over_calcs(usage: dict) -> dict:
    calcs = _calcs(usage)
    if not calcs:
        return _result("prefer-native-over-calcs", "skipped", skip_reason="no calculations")
    hits = []
    for c in calcs:
        kind = _native_pattern(c.get("formula") or "")
        if not kind:
            continue
        rec = _col_finding(c)
        rec["nativeEquivalent"] = kind
        hits.append(rec)
    if not hits:
        return _result("prefer-native-over-calcs", "clear")
    return _result(
        "prefer-native-over-calcs",
        "hit",
        hits,
        "These calcs look like groups, bins, custom dates, or combined fields.",
    )


def check_avoid_high_cardinality_filters(usage: dict) -> dict:
    xml = _xml(usage)
    blocks = re.findall(r"<filter\b[^>]*>.*?</filter>", xml, re.DOTALL | re.I)
    if not blocks:
        return _result(
            "avoid-high-cardinality-filters", "skipped", skip_reason="no filters"
        )
    hits = []
    for block in blocks:
        if not re.search(r"class=['\"]categorical['\"]", block):
            continue
        if not re.search(
            r"ui-enumeration=['\"]all['\"]|ui-marker=['\"]enumerate['\"]", block
        ):
            continue
        col = re.search(r"column=['\"]([^'\"]+)['\"]", block)
        name = col.group(1) if col else ""
        if _HIGH_CARD_RE.search(name):
            hits.append({"column": name})
    if not hits:
        return _result("avoid-high-cardinality-filters", "clear")
    return _result(
        "avoid-high-cardinality-filters",
        "hit",
        hits,
        "Enumerated filters on likely high-cardinality strings load slowly.",
    )


def check_prefer_range_over_huge_discrete(usage: dict) -> dict:
    xml = _xml(usage)
    blocks = re.findall(
        r"<filter\b[^>]*class=['\"]categorical['\"][^>]*>.*?</filter>",
        xml,
        re.DOTALL | re.I,
    )
    if not blocks:
        return _result(
            "prefer-range-over-huge-discrete",
            "skipped",
            skip_reason="no categorical filters",
        )
    hits = []
    for block in blocks:
        n = len(re.findall(r"function=['\"]member['\"]", block))
        if n >= 15:
            col = re.search(r"column=['\"]([^'\"]+)['\"]", block)
            hits.append({"column": col.group(1) if col else "", "memberCount": n})
    if not hits:
        return _result("prefer-range-over-huge-discrete", "clear")
    return _result(
        "prefer-range-over-huge-discrete",
        "hit",
        hits,
        "Long itemized member lists are slower than a range filter.",
    )


def check_filter_at_higher_grain(usage: dict) -> dict:
    root = usage.get("root")
    if root is None:
        root = ET.fromstring(_xml(usage))
    ws_container = root.find("worksheets")
    if ws_container is None:
        return _result("filter-at-higher-grain", "skipped", skip_reason="no worksheets")
    hits = []
    saw_filter = False
    for ws in ws_container.findall("worksheet"):
        cols = [f.get("column") or "" for f in _iter(ws, "filter") if f.get("column")]
        if not cols:
            continue
        saw_filter = True
        blob = " ".join(cols)
        if _PARENT_GRAIN_RE.search(blob) and _CHILD_GRAIN_RE.search(blob):
            hits.append({"name": ws.get("name"), "filters": cols})
    if not saw_filter:
        return _result("filter-at-higher-grain", "skipped", skip_reason="no filters")
    if not hits:
        return _result("filter-at-higher-grain", "clear")
    return _result(
        "filter-at-higher-grain",
        "hit",
        hits,
        "Filter at a parent grain instead of listing every child member.",
    )


def check_prefer_transparent_pngs(usage: dict, path: str) -> dict:
    if not is_twbx(path):
        return _result("prefer-transparent-pngs", "skipped", skip_reason="not a .twbx")
    opaque = []
    rasters = 0
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            name = info.filename.lower()
            if not name.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                continue
            rasters += 1
            if name.endswith((".jpg", ".jpeg", ".gif", ".bmp")):
                opaque.append({"name": info.filename, "bytes": info.file_size})
    if rasters == 0:
        return _result(
            "prefer-transparent-pngs", "skipped", skip_reason="no raster images"
        )
    if not opaque:
        return _result("prefer-transparent-pngs", "clear")
    return _result(
        "prefer-transparent-pngs",
        "hit",
        opaque,
        "Prefer PNG with transparency over JPEG/BMP/GIF for workbook images.",
    )


def check_limit_heavy_text_tables(usage: dict) -> dict:
    root = usage.get("root")
    if root is None:
        root = ET.fromstring(_xml(usage))
    ws_container = root.find("worksheets")
    if ws_container is None:
        return _result("limit-heavy-text-tables", "skipped", skip_reason="no worksheets")
    hits = []
    for ws in ws_container.findall("worksheet"):
        mark = next(_iter(ws, "mark"), None)
        mark_class = (mark.get("class") if mark is not None else "") or ""
        rows_el = next(_iter(ws, "rows"), None)
        cols_el = next(_iter(ws, "cols"), None)
        n_row = len(_TOKEN_RE.findall(rows_el.text or "")) if rows_el is not None else 0
        n_col = len(_TOKEN_RE.findall(cols_el.text or "")) if cols_el is not None else 0
        if mark_class.lower() == "text" or n_row >= 4 or (n_row >= 3 and n_col >= 2):
            hits.append(
                {
                    "name": ws.get("name"),
                    "markClass": mark_class,
                    "rowFields": n_row,
                    "colFields": n_col,
                }
            )
    if not hits:
        return _result("limit-heavy-text-tables", "clear")
    return _result(
        "limit-heavy-text-tables",
        "hit",
        hits,
        "Crosstabs and text tables with many pills are a mark-count trap.",
    )


def check_guided_drill_down(usage: dict) -> dict:
    if not usage["dashboards"]:
        return _result("guided-drill-down", "skipped", skip_reason="no dashboards")
    heavy = [d for d in usage["dashboards"] if len(d["worksheetZones"]) > 3]
    if not heavy:
        return _result("guided-drill-down", "clear")
    if re.search(r"<action\b", _xml(usage)):
        return _result("guided-drill-down", "clear")
    return _result(
        "guided-drill-down",
        "hit",
        [{"name": d["name"], "worksheetZones": d["worksheetZones"]} for d in heavy],
        "Spread detail across views connected by actions instead of showing everything.",
    )


def check_default_field_properties(usage: dict) -> dict:
    root = usage.get("root")
    if root is None:
        root = ET.fromstring(_xml(usage))
    ws_container = root.find("worksheets")
    if ws_container is None:
        return _result("default-field-properties", "skipped", skip_reason="no worksheets")
    seen: dict[tuple[str, str], set[str]] = defaultdict(set)
    for ws in ws_container.findall("worksheet"):
        wname = ws.get("name") or ""
        for fmt in _iter(ws, "format"):
            field = fmt.get("field")
            attr = (fmt.get("attr") or "").lower()
            if not field or attr in _FORMAT_SKIP_ATTRS:
                continue
            seen[(field, attr)].add(wname)
    if not seen:
        return _result(
            "default-field-properties",
            "skipped",
            skip_reason="no per-sheet field formatting",
        )
    repeats = [
        {"field": field, "attr": attr, "worksheets": sorted(names)}
        for (field, attr), names in seen.items()
        if len(names) >= 2
    ]
    if not repeats:
        return _result("default-field-properties", "clear")
    return _result(
        "default-field-properties",
        "hit",
        repeats,
        "Repeat per-sheet formats belong on the field default instead.",
    )


def check_avoid_excessive_formatting(usage: dict) -> dict:
    xml = _xml(usage)
    hits = []
    if re.search(r"attr=['\"]animation-on['\"][^>]*value=['\"]ao-on['\"]", xml):
        hits.append({"kind": "animation"})
    for match in re.finditer(
        r"attr=['\"]mark-transparency['\"][^>]*value=['\"](\d+)['\"]", xml
    ):
        value = int(match.group(1))
        if value < 255:
            hits.append({"kind": "mark-transparency", "value": value})
            break
    if not hits:
        return _result("avoid-excessive-formatting", "clear")
    return _result(
        "avoid-excessive-formatting",
        "hit",
        hits,
        "Mark transparency and animation add render cost.",
    )


DETECTORS = {
    "extracts-over-live": check_extracts_over_live,
    "hide-unused-fields": check_hide_unused_fields,
    "close-unused-datasources": check_close_unused_datasources,
    "minimize-data-volume": check_minimize_data_volume,
    "avoid-custom-sql": check_avoid_custom_sql,
    "avoid-params-in-custom-sql": check_avoid_params_in_custom_sql,
    "remove-sql-order-by": check_remove_sql_order_by,
    "prefer-relationships": check_prefer_relationships,
    "referential-integrity": check_referential_integrity,
    "limit-data-blending": check_limit_data_blending,
    "prefer-numbers-booleans": check_prefer_numbers_booleans,
    "count-over-countd": check_count_over_countd,
    "min-max-over-avg-attr": check_min_max_over_avg_attr,
    "limit-calc-fields": check_limit_calc_fields,
    "avoid-row-level-param-calcs": check_avoid_row_level_param_calcs,
    "limit-cross-source-calcs": check_limit_cross_source_calcs,
    "minimize-lod": check_minimize_lod,
    "avoid-nested-calcs": check_avoid_nested_calcs,
    "limit-table-calcs": check_limit_table_calcs,
    "prefer-native-over-calcs": check_prefer_native_over_calcs,
    "avoid-hierarchies": check_avoid_hierarchies,
    "consolidate-duplicate-calcs": check_consolidate_duplicate_calcs,
    "binary-string-branches": check_binary_string_branches,
    "minimize-quick-filters": check_minimize_quick_filters,
    "avoid-only-relevant-values": check_avoid_only_relevant_values,
    "avoid-high-cardinality-filters": check_avoid_high_cardinality_filters,
    "context-filters-not-query-lever": check_context_filters_not_query_lever,
    "prefer-range-over-huge-discrete": check_prefer_range_over_huge_discrete,
    "filter-actions-over-quick-filters": check_filter_actions,
    "avoid-user-filters": check_avoid_user_filters,
    "limit-filter-count": check_limit_filter_count,
    "apply-button": check_apply_button,
    "avoid-keep-only-exclude": check_avoid_keep_only_exclude,
    "filter-at-higher-grain": check_filter_at_higher_grain,
    "limit-worksheets-per-dashboard": check_limit_worksheets_per_dashboard,
    "fixed-dashboard-size": check_fixed_dashboard_size,
    "limit-viz-in-tooltip": check_limit_viz_in_tooltip,
    "minimize-image-sizes": lambda u: check_minimize_image_sizes(u, u["_path"]),
    "prefer-transparent-pngs": lambda u: check_prefer_transparent_pngs(u, u["_path"]),
    "limit-dashboard-actions": check_limit_dashboard_actions,
    "prefer-tiled-over-floating": check_prefer_tiled_over_floating,
    "sets-for-top-n": check_sets_for_top_n,
    "limit-heavy-text-tables": check_limit_heavy_text_tables,
    "guided-drill-down": check_guided_drill_down,
    "keep-tooltips-simple": check_keep_tooltips_simple,
    "default-field-properties": check_default_field_properties,
    "avoid-excessive-formatting": check_avoid_excessive_formatting,
    "upgrade-tableau-version": check_upgrade_tableau_version,
}


def run_checks(usage: dict, check_id: str | None = None) -> list[dict]:
    ids = [check_id] if check_id else list(CHECK_IDS)
    results = []
    for cid in ids:
        fn = DETECTORS[cid]
        results.append(fn(usage))
    return results


# --- fixes -----------------------------------------------------------------
def hide_fields_in_xml(xml: str, fields: list) -> tuple[str, list[str], list[str]]:
    specs: list[tuple[str | None, str]] = []
    for field in fields:
        if isinstance(field, dict):
            specs.append((field.get("datasource"), field["name"]))
        else:
            specs.append((None, str(field)))
    result = xml
    hidden: list[str] = []
    skipped: list[str] = []
    attr_text = r"(?:[^>'\"]|'[^']*'|\"[^\"]*\")*?"
    col_re = re.compile(
        r"(<column(?=[\s/>])" + attr_text + r"\sname=(['\"])(?P<name>.*?)\2" + attr_text + r")(\s*/?>)",
        re.I,
    )
    for ds_name, field_name in specs:
        found = False
        for dm in re.finditer(r"<datasource\b[^>]*>.*?</datasource>", result, re.DOTALL | re.I):
            block = dm.group(0)
            open_m = re.match(r"<datasource\b([^>]*)>", block, re.I)
            block_ds = ""
            if open_m:
                nm = re.search(r"\bname=(['\"])([^'\"]*)\1", open_m.group(1))
                block_ds = nm.group(2) if nm else ""
            if ds_name and block_ds != ds_name:
                continue
            cm = None
            for cand in col_re.finditer(block):
                if cand.group("name") == field_name:
                    cm = cand
                    break
            if cm is None:
                continue
            attrs, close = cm.group(1), cm.group(4)
            if re.search(r"\bhidden=", attrs, re.I):
                skipped.append(field_name)
                found = True
                break
            new_col = (
                f"{attrs} hidden='true'{'' if close.strip() == '>' else ' '}{close.strip()}"
            )
            abs_start = dm.start() + cm.start()
            abs_end = dm.start() + cm.end()
            result = result[:abs_start] + new_col + result[abs_end:]
            hidden.append(field_name)
            found = True
            break
        if not found:
            skipped.append(field_name)
    return result, hidden, skipped


def fixed_dashboard_size_in_xml(xml: str) -> tuple[str, int]:
    """Set sizing-mode='fixed' on automatic dashboards.

    Returns the new XML and the number of dashboards actually changed. This
    does not add a width or height; Tableau decides the fixed size.
    """
    changed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        block = match.group(0)
        new_block, n = re.subn(
            r"sizing-mode=(['\"])(?:automatic|auto)\1",
            r"sizing-mode=\1fixed\1",
            block,
            flags=re.I,
        )
        if n:
            changed += 1
        return new_block

    new = re.sub(r"<dashboard\b.*?</dashboard>", repl, xml, flags=re.DOTALL | re.I)
    return new, changed


def default_out_path(src: str) -> str:
    p = Path(src).resolve(strict=False)
    return str(p.with_name(f"{p.stem}-optimized{p.suffix}"))


def write_workbook(src: str, xml: str, *, out: str | None, in_place: bool) -> str:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".twb", delete=False, encoding="utf-8", newline=""
    ) as tf:
        tf.write(xml)
        edited = tf.name
    try:
        dest = write_fixed(src, None if in_place else out, edited, in_place=in_place)
    finally:
        os.unlink(edited)
    return dest


class InvalidOutputError(Exception):
    pass


def _skip_obj(cid: str, reason: str, message: str = "") -> dict:
    return {"id": cid, "reason": reason, "message": message}


def apply_fixes(
    src: str,
    xml: str,
    usage: dict,
    *,
    check_id: str | None,
    out: str | None,
    in_place: bool,
) -> tuple[str, list[str], list[dict], str | None]:
    ids = [check_id] if check_id else list(MECHANICAL_FIX_IDS)
    applied: list[str] = []
    skipped: list[dict] = []
    current = xml
    for cid in ids:
        if cid == "hide-unused-fields":
            cols = unused_columns(usage)
            if not cols:
                skipped.append(_skip_obj(cid, "not-applicable"))
                continue
            current, hidden, _skip = hide_fields_in_xml(current, cols)
            if hidden:
                applied.append(cid)
            else:
                skipped.append(_skip_obj(cid, "not-applicable"))
        elif cid == "fixed-dashboard-size":
            autos = [
                d
                for d in usage["dashboards"]
                if (d["sizingMode"] or "").lower() in {"automatic", "auto"}
            ]
            if not autos:
                skipped.append(_skip_obj(cid, "not-applicable"))
                continue
            current, _n = fixed_dashboard_size_in_xml(current)
            if "sizing-mode='fixed'" in current or 'sizing-mode="fixed"' in current:
                applied.append(cid)
            else:
                skipped.append(_skip_obj(cid, "not-applicable"))
        else:
            skipped.append(_skip_obj(cid, "not-applicable"))
    if not applied:
        return xml, applied, skipped, None
    try:
        ET.fromstring(current)
    except ET.ParseError as exc:
        raise InvalidOutputError(f"fix produced XML that is not well-formed: {exc}") from exc
    dest = write_workbook(src, current, out=out, in_place=in_place)
    return current, applied, skipped, dest


# --- CLI -------------------------------------------------------------------
def _load(path: str) -> tuple[str | None, dict | None, str | None]:
    try:
        xml = read_twb(path)
    except FileNotFoundError:
        return None, None, "file not found"
    except (OSError, zipfile.BadZipFile, ValueError, UnicodeDecodeError) as exc:
        return None, None, str(exc)
    try:
        usage = build_usage(xml)
    except ET.ParseError as exc:
        return xml, None, f"malformed XML: {exc}"
    usage["_path"] = path
    usage["xml"] = xml
    return xml, usage, None


def cmd_stats(path: str, as_json: bool) -> int:
    xml, usage, err = _load(path)
    if err or usage is None:
        print(json.dumps(fail_envelope("stats", path, "io", err or "parse failed"), indent=2))
        return 1
    summary = summarize_usage(usage)
    warnings = collect_warnings(path, summary)
    if not as_json:
        print(_format_warnings(warnings) + _human(summary))
        return 0
    payload = envelope(
        "stats",
        path,
        version=usage["version"],
        usage=_usage_view(usage),
        summary=summary,
        warnings=warnings,
        diagrams={"workbook": diagrams_workbook(usage), "findings": []},
    )
    print(json.dumps(payload, indent=2))
    return 0


def _slug_for(path: str) -> str:
    """Kebab-case the workbook filename (no extension) for the report basename."""
    stem = Path(path).stem
    slug = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return slug or "workbook"


def cmd_check(
    path: str,
    check_id: str | None,
    fmt: str,
    out: str | None,
    report_dir: str | None = None,
    token: str | None = None,
) -> int:
    as_json = fmt == "json"
    if token and not report_dir:
        return _print_fail(
            "check", path, "usage", "--token only applies with --report-dir", True
        )
    if report_dir:
        # The bundle writes json+html+md itself; it is the agent's one-shot form.
        if out:
            return _print_fail(
                "check", path, "usage", "--report-dir conflicts with --out", True
            )
        if fmt not in {"human", "json"}:
            return _print_fail(
                "check",
                path,
                "usage",
                "--report-dir writes html, markdown and json together; drop --format",
                True,
            )
        if check_id:
            return _print_fail(
                "check",
                path,
                "usage",
                "--report-dir writes the full report; drop the single check id",
                True,
            )
    if out and fmt not in {"markdown", "html"}:
        return _print_fail(
            "check", path, "usage", "--out requires --format markdown or --format html", as_json
        )
    xml, usage, err = _load(path)
    if err or usage is None:
        return _print_fail("check", path, "io", err or "parse failed", as_json)
    if check_id:
        rec = CATALOG_BY_ID.get(check_id)
        if rec is None:
            return _print_fail(
                "check", path, "unknown-id", f"unknown check id {check_id!r}", as_json
            )
        if not rec["programmable"]:
            return _print_fail(
                "check",
                path,
                "not-programmable",
                f"{check_id!r} has no detector; use list check {check_id}",
                as_json,
            )
    checks = run_checks(usage, check_id)
    stamp_severity(usage, checks)
    summary = summarize_usage(usage)
    warnings = collect_warnings(path, summary)
    if report_dir:
        dest_dir = Path(report_dir)
        if under_training_data(dest_dir):
            return _print_fail(
                "check", path, "forbidden-path", "refusing to write under training-data/", True
            )
        payload = envelope(
            "check",
            path,
            version=usage["version"],
            usage=_usage_view(usage),
            summary=summary,
            checks=checks,
            warnings=warnings,
            diagrams={
                "workbook": diagrams_workbook(usage),
                "findings": diagrams_findings(checks),
            },
        )
        slug = _slug_for(path)
        if token:
            safe = re.sub(r"[^A-Za-z0-9]+", "", token)
            if safe:
                slug = f"{slug}-{safe}"
        jf = dest_dir / f"{slug}.json"
        hf = dest_dir / f"{slug}.html"
        mf = dest_dir / f"{slug}.md"
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            jf.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            hf.write_text(_html_check(path, usage, checks, warnings), encoding="utf-8")
            mf.write_text(_markdown_check(path, usage, checks, warnings), encoding="utf-8")
        except OSError as exc:
            return _print_fail("check", path, "io", str(exc), True)
        payload["reports"] = {
            "dir": str(dest_dir),
            "json": str(jf),
            "html": str(hf),
            "markdown": str(mf),
        }
        print(json.dumps(payload, indent=2))
        return 0
    if fmt == "human":
        print(_human_check(path, usage["version"], checks, warnings), end="")
        return 0
    if fmt in {"markdown", "html"}:
        if fmt == "html":
            report = _html_check(path, usage, checks, warnings)
            suffix_hint = "an .html path"
        else:
            report = _markdown_check(path, usage, checks, warnings)
            suffix_hint = "a .md path"
        if out:
            dest = Path(out)
            if under_training_data(dest):
                return _print_fail(
                    "check",
                    path,
                    "forbidden-path",
                    "refusing to write under training-data/",
                    False,
                )
            if _same_path(dest, path) or dest.suffix.lower() in {".twb", ".twbx"}:
                return _print_fail(
                    "check",
                    path,
                    "forbidden-path",
                    f"refusing to overwrite the workbook; use {suffix_hint}",
                    False,
                )
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(report, encoding="utf-8")
            except OSError as exc:
                return _print_fail("check", path, "io", str(exc), False)
            print(out)
            return 0
        print(report, end="" if report.endswith("\n") else "\n")
        return 0
    usage_out = _usage_view(usage)
    payload = envelope(
        "check",
        path,
        version=usage["version"],
        usage=usage_out,
        summary=summary,
        checks=checks,
        warnings=warnings,
        diagrams={
            "workbook": diagrams_workbook(usage),
            "findings": diagrams_findings(checks),
        },
    )
    print(json.dumps(payload, indent=2))
    return 0


def _human_fix(
    applied: list[str],
    skipped: list[dict],
    output_path: str | None,
    *,
    in_place: bool,
) -> str:
    lines: list[str] = []
    where = "in place" if in_place and applied else (output_path or "")
    for cid in applied:
        lines.append(f"applied: {cid}" + (f" -> {where}" if where else ""))
    for item in skipped:
        reason = item.get("reason")
        cid = item.get("id", "")
        if reason == "author-only":
            msg = (item.get("message") or "").strip()
            lines.append(msg or f"{cid}: author must change this in Desktop")
        else:
            extra = f" {item['message']}" if item.get("message") else ""
            lines.append(f"skipped: {cid} ({reason}){extra}")
    if not applied:
        lines.append("nothing written")
    return "\n".join(lines).rstrip() + "\n"


def _emit_fix(as_json: bool, payload: dict, *, in_place: bool = False) -> int:
    if as_json:
        print(json.dumps(payload, indent=2))
        return 0 if payload.get("ok", True) else 1
    if not payload.get("ok", True):
        err = payload.get("error") or {}
        print(f"error: {err.get('message') or 'fix failed'}")
        return 1
    print(
        _human_fix(
            payload.get("applied") or [],
            payload.get("skipped") or [],
            payload.get("outputPath"),
            in_place=in_place,
        ),
        end="",
    )
    return 0


def cmd_fix(
    path: str,
    check_id: str | None,
    out: str | None,
    in_place: bool,
    fmt: str,
    all_fixes: bool = False,
) -> int:
    as_json = fmt == "json"
    if in_place and out:
        return _print_fail(
            "fix", path, "usage", "--out conflicts with --in-place", as_json
        )
    if not check_id and not all_fixes:
        return _print_fail(
            "fix",
            path,
            "usage",
            "pass a specific id (fix <path> <id>) or --all to apply every "
            "mechanical fix; fix will not change anything implicitly",
            as_json,
        )
    xml, usage, err = _load(path)
    if err or usage is None:
        return _print_fail("fix", path, "io", err or "parse failed", as_json)
    if check_id:
        rec = CATALOG_BY_ID.get(check_id)
        if rec is None:
            return _print_fail(
                "fix", path, "unknown-id", f"unknown check id {check_id!r}", as_json
            )
        if rec["fixMethod"] != "mechanical":
            payload = envelope(
                "fix",
                path,
                version=usage["version"],
                applied=[],
                skipped=[
                    _skip_obj(check_id, "author-only", rec["detail"]),
                ],
                outputPath=None,
            )
            return _emit_fix(as_json, payload, in_place=False)
    dest = path if in_place else (out or default_out_path(path))
    if in_place:
        dest = str(Path(path).resolve(strict=False))
        path = dest
    if under_training_data(dest):
        return _print_fail(
            "fix", path, "forbidden-path", "refusing to write under training-data/", as_json
        )
    if not in_place and _same_path(dest, path):
        return _print_fail(
            "fix",
            path,
            "forbidden-path",
            "refusing to overwrite the original; pass --in-place",
            as_json,
        )
    try:
        _new, applied, skipped, written = apply_fixes(
            path, xml, usage, check_id=check_id, out=None if in_place else dest, in_place=in_place
        )
    except InvalidOutputError as exc:
        return _print_fail("fix", path, "invalid-output", str(exc), as_json)
    except OSError as exc:
        # Locked by Tableau Studio, read-only folder, disk full, ...
        return _print_fail(
            "fix", path, "io", f"could not write the fixed workbook: {exc}", as_json
        )
    payload = envelope(
        "fix",
        path,
        version=usage["version"],
        applied=applied,
        skipped=skipped,
        outputPath=written if written else (path if in_place and applied else None),
    )
    return _emit_fix(as_json, payload, in_place=in_place)


def _catalog_public(rec: dict) -> dict:
    keys = (
        "id",
        "title",
        "summary",
        "detail",
        "detectability",
        "programmable",
        "impact",
        "priority",
        "fixMethod",
        "sources",
    )
    return {k: rec[k] for k in keys}


def _human_list(records: list[dict], *, detailed: bool) -> str:
    lines = []
    for rec in records:
        lines.append(f"{rec['id']}  {rec['fixMethod']}")
        lines.append(f"  {rec['summary']}")
        detail = (rec.get("detail") or "").strip()
        if detailed and detail and detail != (rec.get("summary") or "").strip():
            lines.append(f"  {detail}")
    return "\n".join(lines).rstrip() + "\n"


def cmd_list(*, kind: str | None, check_id: str | None, as_json: bool) -> int:
    if kind not in {"check", "fix"}:
        return 2
    if kind == "check":
        pool = CATALOG
        key = "checks"
        if check_id:
            rec = CATALOG_BY_ID.get(check_id)
            if rec is None:
                return _print_fail(
                    "list", "", "unknown-id", f"unknown check id {check_id!r}", as_json
                )
            records = [_catalog_public(rec)]
        else:
            records = [_catalog_public(r) for r in pool]
    else:
        key = "fixes"
        mechanical = [r for r in CATALOG if r["fixMethod"] == "mechanical"]
        if check_id:
            rec = CATALOG_BY_ID.get(check_id)
            if rec is None or rec["fixMethod"] != "mechanical":
                msg = (
                    f"{check_id!r} is not a mechanical fix"
                    if rec is not None
                    else f"unknown check id {check_id!r}"
                )
                return _print_fail("list", "", "unknown-id", msg, as_json)
            records = [_catalog_public(rec)]
        else:
            records = [_catalog_public(r) for r in mechanical]
    if as_json:
        print(json.dumps(envelope("list", "", **{key: records}), indent=2))
        return 0
    print(_human_list(records, detailed=bool(check_id)), end="")
    return 0


_HELP_FORMATTER = argparse.RawDescriptionHelpFormatter

_ROOT_EPILOG = """\
Examples:
  wbo.py stats workbook.twbx
  wbo.py check workbook.twbx
  wbo.py check workbook.twbx --format markdown --out report.md
  wbo.py check workbook.twbx --json
  wbo.py check workbook.twbx hide-unused-fields --json
  wbo.py fix workbook.twbx
  wbo.py fix workbook.twbx hide-unused-fields --json
  wbo.py list check
  wbo.py list fix --json
Run "wbo.py COMMAND --help" for details on a command.
"""


def _add_workbook_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "path",
        metavar="WORKBOOK",
        help="path to a .twb or .twbx file",
    )


def _add_list_format_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the catalog as a JSON envelope (same as --format json)",
    )
    parser.add_argument(
        "--format",
        choices=("json",),
        default=None,
        dest="fmt",
        help="output format (json only; default is human text)",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wbo.py",
        description=(
            "Tableau workbook performance helper. Summarize a workbook, run "
            "catalog checks, or apply mechanical XML fixes.\n"
            "Reads .twb / .twbx. Never overwrites the original unless you pass "
            "fix --in-place."
        ),
        epilog=_ROOT_EPILOG,
        formatter_class=_HELP_FORMATTER,
    )
    sub = parser.add_subparsers(
        dest="cmd",
        required=False,
        metavar="COMMAND",
        title="commands",
    )
    stats = sub.add_parser(
        "stats",
        help="print workbook graph and counts (no catalog judgment)",
        description=(
            "Print datasource, worksheet, dashboard, and field counts.\n"
            "Does not run checks and does not modify the file."
        ),
        formatter_class=_HELP_FORMATTER,
        epilog="Examples:\n  wbo.py stats workbook.twbx\n  wbo.py stats workbook.twbx --json",
    )
    _add_workbook_arg(stats)
    stats.add_argument(
        "--json",
        action="store_true",
        help="print the machine-readable envelope (usage, summary, mermaid)",
    )
    check = sub.add_parser(
        "check",
        help="run programmable catalog checks (does not modify the workbook)",
        description=(
            "Run programmable performance checks and print hits only, ordered "
            "CRITICAL, HIGH, MEDIUM, then CLEANUP.\n"
            "Does not modify the workbook.\n\n"
            "Formats:\n"
            "  human     terminal summary of hit ids and display names (default)\n"
            "  html      self-contained styled customer report (open in a browser)\n"
            "  markdown  customer report with mermaid graph and Tableau Help links\n"
            "  json      machine-readable envelope for agents (same as --json)"
        ),
        formatter_class=_HELP_FORMATTER,
        epilog=(
            "Examples:\n"
            "  wbo.py check workbook.twbx\n"
            "  wbo.py check workbook.twbx --report-dir ./out\n"
            "  wbo.py check workbook.twbx --format html --out report.html\n"
            "  wbo.py check workbook.twbx --format markdown --out report.md\n"
            "  wbo.py check workbook.twbx --json\n"
            "  wbo.py check workbook.twbx hide-unused-fields --json\n"
            "\n"
            "See also: wbo.py list check"
        ),
    )
    _add_workbook_arg(check)
    check.add_argument(
        "id",
        nargs="?",
        metavar="ID",
        help="run one check only (ids: wbo.py list check)",
    )
    check.add_argument(
        "--format",
        choices=("human", "html", "markdown", "json"),
        default=None,
        dest="fmt",
        help="output format (default: human)",
    )
    check.add_argument(
        "--json",
        action="store_true",
        help="same as --format json; conflicts with --format human|html|markdown",
    )
    check.add_argument(
        "--out",
        metavar="FILE",
        help="write the html/markdown report to FILE (requires --format html or markdown)",
    )
    check.add_argument(
        "--report-dir",
        metavar="DIR",
        dest="report_dir",
        help=(
            "write <slug>.json, <slug>.html and <slug>.md into DIR from one parse "
            "(shared basename); prints the json envelope with a reports{} index"
        ),
    )
    check.add_argument(
        "--token",
        metavar="TOKEN",
        dest="token",
        help=(
            "append -<TOKEN> to the report basename (requires --report-dir), "
            "e.g. --token a1b2c3 writes <slug>-a1b2c3.{json,html,md}"
        ),
    )

    fix = sub.add_parser(
        "fix",
        help="apply mechanical XML fixes to a copy of the workbook",
        description=(
            "Apply non-semantic XML fixes and write a copy by default.\n"
            "Mechanical ids: hide-unused-fields, fixed-dashboard-size.\n"
            "Pass a specific id, or --all to apply every mechanical fix.\n"
            "A bare fix with no id and no --all changes nothing (read-only safe).\n"
            "Does not rewrite calculations. Refuses to write under training-data/.\n"
            "Default output is human; agents pass --json."
        ),
        formatter_class=_HELP_FORMATTER,
        epilog=(
            "Examples:\n"
            "  wbo.py fix workbook.twbx hide-unused-fields --json\n"
            "  wbo.py fix workbook.twbx --all\n"
            "  wbo.py fix workbook.twbx --all --out workbook-optimized.twbx\n"
            "\n"
            "See also: wbo.py list fix"
        ),
    )
    _add_workbook_arg(fix)
    fix.add_argument(
        "id",
        nargs="?",
        metavar="ID",
        help="apply one catalog id (mechanical writes; author-only prints guidance)",
    )
    fix.add_argument(
        "--all",
        action="store_true",
        dest="all_fixes",
        help="apply every mechanical fix (required to fix without naming an id)",
    )
    fix.add_argument(
        "--format",
        choices=("human", "json"),
        default=None,
        dest="fmt",
        help="output format (default: human)",
    )
    fix.add_argument(
        "--json",
        action="store_true",
        help="same as --format json; conflicts with --format human",
    )
    fix.add_argument(
        "--out",
        metavar="FILE",
        help="write the copy to FILE (default: sibling *-optimized.twb[x])",
    )
    fix.add_argument(
        "--in-place",
        action="store_true",
        help="overwrite WORKBOOK instead of writing a copy (off by default)",
    )
    listing = sub.add_parser(
        "list",
        help="print catalog records (list check) or mechanical fixes (list fix)",
        description=(
            "Print catalog records without a workbook.\n"
            "Use list check for every id, list fix for mechanical rewriters."
        ),
        formatter_class=_HELP_FORMATTER,
        epilog="Examples:\n  wbo.py list check\n  wbo.py list check count-over-countd --json\n  wbo.py list fix",
    )
    list_sub = listing.add_subparsers(dest="list_kind", required=False, metavar="KIND")
    list_check = list_sub.add_parser(
        "check",
        help="list catalog checks",
        formatter_class=_HELP_FORMATTER,
    )
    list_check.add_argument("id", nargs="?", metavar="ID", help="one catalog id")
    _add_list_format_args(list_check)
    list_fix = list_sub.add_parser(
        "fix",
        help="list mechanical fix ids",
        formatter_class=_HELP_FORMATTER,
    )
    list_fix.add_argument("id", nargs="?", metavar="ID", help="one mechanical id")
    _add_list_format_args(list_fix)
    return parser


def _resolve_fmt(args, *, human_ok: bool) -> tuple[str | None, str | None]:
    fmt = getattr(args, "fmt", None)
    as_json_flag = bool(getattr(args, "json", False))
    if as_json_flag and fmt not in (None, "json"):
        return None, f"--json conflicts with --format {fmt}"
    if as_json_flag:
        return "json", None
    if fmt is None:
        return "human", None
    if fmt == "json":
        return "json", None
    if human_ok:
        return fmt, None
    return None, f"unsupported --format {fmt}"


def _main(argv: list[str]) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if not exc.code else int(exc.code)
    if not args.cmd:
        parser.print_help()
        return 2
    if args.cmd == "stats":
        return cmd_stats(args.path, args.json)
    if args.cmd == "check":
        fmt, err = _resolve_fmt(args, human_ok=True)
        if err:
            return _print_fail("check", args.path, "usage", err, False)
        return cmd_check(args.path, args.id, fmt, args.out, args.report_dir, args.token)
    if args.cmd == "list":
        kind = getattr(args, "list_kind", None)
        if kind not in {"check", "fix"}:
            for action in parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    action.choices["list"].print_help(sys.stderr)
                    break
            return 2
        fmt, err = _resolve_fmt(args, human_ok=False)
        if err:
            return _print_fail("list", "", "usage", err, False)
        as_json = fmt == "json"
        return cmd_list(kind=kind, check_id=getattr(args, "id", None), as_json=as_json)
    fmt, err = _resolve_fmt(args, human_ok=True)
    if err:
        return _print_fail("fix", args.path, "usage", err, False)
    if fmt not in {"human", "json"}:
        return _print_fail("fix", args.path, "usage", "fix format is human or json", False)
    return cmd_fix(args.path, args.id, args.out, args.in_place, fmt, args.all_fixes)


def _stdout_closed(exc: OSError) -> bool:
    # A reader that stops early (`| head -c 300`) closes the pipe mid-write.
    # POSIX raises BrokenPipeError; Windows can raise OSError EINVAL instead,
    # so confirm EINVAL came from stdout by retrying the pending flush.
    if isinstance(exc, BrokenPipeError):
        return True
    if exc.errno != errno.EINVAL:
        return False
    try:
        sys.stdout.flush()
    except OSError:
        return True
    return False


def _run(argv: list[str]) -> int:
    # Keep the command's own code when it returned before the pipe closed
    # (e.g. an ok:false envelope); otherwise exit 0 — the command ran, only
    # the reader left early.
    code = 0
    try:
        code = _main(argv)
        sys.stdout.flush()
    except OSError as exc:
        if not _stdout_closed(exc):
            raise
        # Point stdout at devnull so the interpreter's exit flush stays quiet.
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
    return code


if __name__ == "__main__":
    raise SystemExit(_run(sys.argv[1:]))
