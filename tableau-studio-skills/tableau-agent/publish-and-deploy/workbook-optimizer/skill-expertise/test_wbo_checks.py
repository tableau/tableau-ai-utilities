#!/usr/bin/env python3
"""Fixtures for the programmable check ids.

Every programmable id has a hit fixture (or an always-clear fixture). Many ids
also have clear and skipped fixtures; see SKIP_FIXTURES and the tests below.
"""
from __future__ import annotations

import inspect
import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wbo  # noqa: E402

NEW_CHECK_IDS = (
    "prefer-numbers-booleans",
    "avoid-row-level-param-calcs",
    "prefer-native-over-calcs",
    "avoid-high-cardinality-filters",
    "prefer-range-over-huge-discrete",
    "filter-at-higher-grain",
    "prefer-transparent-pngs",
    "limit-heavy-text-tables",
    "guided-drill-down",
    "default-field-properties",
    "avoid-excessive-formatting",
)


class Skip(Exception):
    """Raised by a test that cannot run here; reported as SKIP, not PASS."""


def _repo_root() -> Path | None:
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "training-data").is_dir() and (parent / "CLAUDE.md").exists():
            return parent
    return None


def _cli(argv: list[str]) -> tuple[int, dict | str]:
    buf = io.StringIO()
    err = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = buf, err
    try:
        code = wbo._main(argv)
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    text = buf.getvalue()
    try:
        return code, json.loads(text)
    except json.JSONDecodeError:
        return code, text


def _col(caption: str, name: str, formula: str | None = None, **attrs: str) -> str:
    attrs.setdefault("role", "measure")
    bits = " ".join(f"{k}='{v}'" for k, v in attrs.items())
    head = f"<column caption='{caption}' name='{name}' {bits}"
    if formula is None:
        return f"{head} />"
    return (
        f"{head}><calculation class='tableau' formula='{formula}' /></column>"
    )


def _ws(
    name: str = "Sheet A",
    fields: tuple[str, ...] = ("[Profit]",),
    ds: str = "ds1",
    ds_captions: tuple[str, ...] = ("Orders",),
    extra: str = "",
    rows: str | None = None,
    cols: str | None = None,
    mark: str | None = None,
) -> str:
    dep = "".join(f"<column name='{f}' />" for f in fields)
    caps = "".join(f"<datasource caption='{c}' />" for c in ds_captions)
    row_xml = f"<rows>{rows}</rows>" if rows else ""
    col_xml = f"<cols>{cols}</cols>" if cols else ""
    mark_xml = f"<mark class='{mark}' />" if mark else ""
    return f"""
    <worksheet name='{name}'>
      <table>
        <view>
          {caps}
          <datasource-dependencies datasource='{ds}'>{dep}</datasource-dependencies>
          {extra}
        </view>
        {row_xml}{col_xml}{mark_xml}
      </table>
    </worksheet>
"""


def _db(
    name: str = "Sales",
    sheets: tuple[str, ...] = ("Sheet A",),
    size: str = "fixed",
    filters: int = 0,
    floating: bool = False,
) -> str:
    zones = "".join(f"<zone name='{s}' type-v2='layout-basic' />" for s in sheets)
    fz = "".join(
        f"<zone name='flt{i}' type-v2='filter' />" for i in range(filters)
    )
    float_zone = (
        "<zone name='floaty' type-v2='layout-basic' floating='true' />"
        if floating
        else ""
    )
    return f"""
    <dashboard name='{name}'>
      <size sizing-mode='{size}' />
      <zones>{zones}{fz}{float_zone}</zones>
    </dashboard>
"""


def _ds(
    name: str = "ds1",
    caption: str = "Orders",
    columns: str = "",
    relation: str = "<relation name='orders' type='table' />",
    extract: bool = False,
    extra: str = "",
    conn_class: str = "excel-direct",
    conn_attrs: str = "",
) -> str:
    if not columns:
        columns = (
            "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
            "<column caption='Sales' datatype='real' name='[Sales]' role='measure' />"
            "<column caption='Status' datatype='string' name='[Status]' role='dimension' />"
            "<column caption='Customer Name' datatype='string' name='[Customer Name]' role='dimension' />"
            "<column caption='City' datatype='string' name='[City]' role='dimension' />"
            "<column caption='State' datatype='string' name='[State]' role='dimension' />"
            "<column caption='Category' datatype='string' name='[Category]' role='dimension' />"
        )
    extract_xml = (
        "<extract enabled='true'><filters><filter /></filters></extract>"
        if extract
        else ""
    )
    attrs = f" {conn_attrs}" if conn_attrs else ""
    return f"""
    <datasource caption='{caption}' inline='true' name='{name}'>
      <connection class='federated'>
        <named-connections>
          <named-connection name='n-{name}'>
            <connection class='{conn_class}'{attrs} />
          </named-connection>
        </named-connections>
        {relation}
        {extract_xml}
      </connection>
      {columns}
      {extra}
    </datasource>
"""


def _live_db_ds(conn_class: str = "sqlserver") -> str:
    return _ds(
        caption="Live Warehouse",
        conn_class=conn_class,
        conn_attrs="server='db.example.com' dbname='sales'",
    )


def _wb(
    datasources: str | None = None,
    worksheets: str | None = None,
    dashboards: str | None = None,
    tail: str = "",
) -> str:
    if datasources is None:
        datasources = _ds()
    if worksheets is None:
        worksheets = _ws()
    if dashboards is None:
        dashboards = _db()
    return f"""<?xml version='1.0' encoding='utf-8' ?>
<workbook version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <datasources>{datasources}</datasources>
  <worksheets>{worksheets}</worksheets>
  <dashboards>{dashboards}</dashboards>
  {tail}
</workbook>
"""


def _write(tmp: Path, xml: str, name: str = "wb.twb") -> Path:
    path = tmp / name
    path.write_text(xml, encoding="utf-8")
    return path


def _status(tmp: Path, xml: str, check_id: str, name: str = "wb.twb") -> dict:
    path = _write(tmp, xml, name)
    code, body = _cli(["check", str(path), check_id, "--json"])
    assert code == 0, body
    assert isinstance(body, dict)
    assert len(body["checks"]) == 1
    return body["checks"][0]


def _hit_status(tmp: Path, check_id: str) -> str:
    if check_id in TWBX_HITS:
        path = TWBX_HITS[check_id](tmp)
        code, body = _cli(["check", str(path), check_id, "--json"])
        assert code == 0, body
        return body["checks"][0]["status"]
    return _status(tmp, HIT_XML[check_id], check_id)["status"]


def _make_twbx(tmp: Path, xml: str, extra: dict[str, bytes]) -> Path:
    twbx = tmp / "pack.twbx"
    with zipfile.ZipFile(twbx, "w") as zf:
        zf.writestr("pack.twb", xml.encode("utf-8"))
        for name, data in extra.items():
            zf.writestr(name, data)
    return twbx


def _many_calcs(n: int) -> str:
    cols = [
        "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
    ]
    fields = ["[Profit]"]
    for i in range(n):
        name = f"[Calculation_{i}]"
        cols.append(
            _col(f"C{i}", name, "SUM([Profit])", datatype="real")
        )
        fields.append(name)
    return _wb(
        datasources=_ds(columns="".join(cols)),
        worksheets=_ws(fields=tuple(fields)),
    )


def _custom_sql(body: str) -> str:
    rel = f"<relation name='sql' type='text'>{body}</relation>"
    return _wb(datasources=_ds(relation=rel))


def _join_rel(*, collection: bool = False, integrity: bool = False) -> str:
    inner = (
        "<relation type='collection'>"
        "<relation name='a' type='table' />"
        "<relation name='b' type='table' />"
        "</relation>"
        if collection
        else (
            "<relation type='join' join='inner'>"
            "<relation name='a' type='table' />"
            "<relation name='b' type='table' />"
            "</relation>"
        )
    )
    extra = "assume-referential-integrity='true'" if integrity else ""
    # integrity string just needs to appear in xml
    ds = _ds(relation=inner, extra=f"<attrs {extra} />" if extra else "")
    if integrity:
        ds = ds.replace("<connection class='federated'>", "<connection class='federated' assume-referential-integrity='true'>")
    return _wb(datasources=ds)


def _nested() -> str:
    cols = (
        "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
        + _col("L1", "[Calculation_1]", "[Profit]", datatype="real")
        + _col("L2", "[Calculation_2]", "[Calculation_1]*1", datatype="real")
        + _col("L3", "[Calculation_3]", "[Calculation_2]*1", datatype="real")
    )
    return _wb(
        datasources=_ds(columns=cols),
        worksheets=_ws(fields=("[Profit]", "[Calculation_3]")),
    )


def _two_ds_blend() -> str:
    ds = _ds() + _ds(name="ds2", caption="People")
    ws = _ws(ds_captions=("Orders", "People"))
    return _wb(datasources=ds, worksheets=ws)


def _cross_source() -> str:
    cols = (
        "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
        + _col("X", "[Calculation_1]", "SUM([Profit])+SUM([People].[X])", datatype="real")
    )
    ds = _ds(columns=cols) + _ds(name="ds2", caption="People")
    return _wb(
        datasources=ds,
        worksheets=_ws(
            fields=("[Profit]", "[Calculation_1]"),
            ds_captions=("Orders", "People"),
        ),
    )


def _filter_zones(n: int, **db_kw) -> str:
    return _wb(dashboards=_db(filters=n, **db_kw))


def _actions(n: int, filters: int = 0, sheets: tuple[str, ...] = ("Sheet A",)) -> str:
    acts = "".join(f"<action name='a{i}' />" for i in range(n))
    return _wb(
        dashboards=_db(filters=filters, sheets=sheets),
        tail=f"<actions>{acts}</actions>",
    )


def _members(n: int) -> str:
    inner = "".join(
        f"<groupfilter function='member' level='[Status]' member='&quot;v{i}&quot;' />"
        for i in range(n)
    )
    extra = (
        f"<filter class='categorical' column='[ds1].[Status]'>"
        f"<groupfilter function='union'>{inner}</groupfilter></filter>"
    )
    return _wb(worksheets=_ws(extra=extra))


def _string_if() -> str:
    cols = (
        "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
        "<column caption='Status' datatype='string' name='[Status]' role='dimension' />"
        + _col(
            "Flag",
            "[Calculation_1]",
            'IF [Status] = &quot;A&quot; THEN &quot;Yes&quot; ELSE &quot;No&quot; END',
            datatype="string",
            role="dimension",
        )
    )
    return _wb(
        datasources=_ds(columns=cols),
        worksheets=_ws(fields=("[Status]", "[Calculation_1]")),
    )


def _param_row() -> str:
    cols = (
        "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
        + _col(
            "Adj",
            "[Calculation_1]",
            "[Profit]*[Parameters].[Rate]",
            datatype="real",
        )
    )
    return _wb(
        datasources=_ds(columns=cols),
        worksheets=_ws(fields=("[Profit]", "[Calculation_1]")),
    )


def _native_case() -> str:
    cols = (
        "<column caption='Status' datatype='string' name='[Status]' role='dimension' />"
        "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
        + _col(
            "Grp",
            "[Calculation_1]",
            "CASE [Status] WHEN &quot;A&quot; THEN &quot;East&quot; "
            "WHEN &quot;B&quot; THEN &quot;West&quot; "
            "WHEN &quot;C&quot; THEN &quot;Central&quot; ELSE &quot;Other&quot; END",
            datatype="string",
            role="dimension",
        )
    )
    return _wb(
        datasources=_ds(columns=cols),
        worksheets=_ws(fields=("[Status]", "[Calculation_1]")),
    )


def _high_card() -> str:
    extra = (
        "<filter class='categorical' column='[ds1].[Customer Name]'>"
        "<groupfilter function='level-members' level='[Customer Name]' "
        "user:ui-enumeration='all' user:ui-marker='enumerate' />"
        "</filter>"
    )
    return _wb(worksheets=_ws(fields=("[Customer Name]", "[Profit]"), extra=extra))


def _grain() -> str:
    extra = (
        "<filter class='categorical' column='[ds1].[City]'>"
        "<groupfilter function='level-members' level='[City]' /></filter>"
        "<filter class='categorical' column='[ds1].[State]'>"
        "<groupfilter function='level-members' level='[State]' /></filter>"
    )
    return _wb(worksheets=_ws(fields=("[City]", "[State]", "[Profit]"), extra=extra))


def _crosstab() -> str:
    return _wb(
        worksheets=_ws(
            rows="([ds1].[Category] / ([ds1].[Status] / ([ds1].[City] / [ds1].[Customer Name])))",
            cols="[ds1].[Profit]",
            mark="Text",
        )
    )


def _repeat_format() -> str:
    fmt = (
        "<style><style-rule element='cell'>"
        "<format attr='number-format' field='[Profit]' value='$#,##0' />"
        "</style-rule></style>"
    )
    ws = _ws(name="Sheet A", extra=fmt) + _ws(name="Sheet B", extra=fmt)
    db = _db(sheets=("Sheet A", "Sheet B"))
    return _wb(worksheets=ws, dashboards=db)


def _transparent_marks() -> str:
    extra = (
        "<style><style-rule element='mark'>"
        "<format attr='mark-transparency' value='180' />"
        "</style-rule></style>"
    )
    return _wb(worksheets=_ws(extra=extra))


def _twbx_heavy_png(tmp: Path) -> Path:
    return _make_twbx(tmp, _wb(), {"Image/big.png": b"x" * (51 * 1024)})


def _twbx_jpeg(tmp: Path) -> Path:
    return _make_twbx(tmp, _wb(), {"Image/shape.jpg": b"jpeg-bytes"})


HIT_XML = {
    "extracts-over-live": _wb(),
    "hide-unused-fields": _wb(
        datasources=_ds(
            columns=(
                "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
                "<column caption='Unused' datatype='string' name='[Unused]' role='dimension' />"
            )
        )
    ),
    "close-unused-datasources": _wb(
        datasources=_ds() + _ds(name="ds2", caption="Spare")
    ),
    "minimize-data-volume": _wb(),
    "avoid-custom-sql": _custom_sql("SELECT * FROM orders"),
    "avoid-params-in-custom-sql": _custom_sql(
        "SELECT * FROM orders WHERE x = Parameters.Region"
    ),
    "remove-sql-order-by": _custom_sql("SELECT * FROM orders ORDER BY sales"),
    "prefer-relationships": _join_rel(),
    "referential-integrity": _join_rel(),
    "limit-data-blending": _two_ds_blend(),
    "count-over-countd": _wb(
        datasources=_ds(
            columns=(
                "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
                + _col("N", "[Calculation_1]", "COUNTD([Status])", datatype="real")
            )
        ),
        worksheets=_ws(fields=("[Profit]", "[Calculation_1]")),
    ),
    "min-max-over-avg-attr": _wb(
        datasources=_ds(
            columns=(
                "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
                + _col("A", "[Calculation_1]", "AVG([Profit])", datatype="real")
            )
        ),
        worksheets=_ws(fields=("[Profit]", "[Calculation_1]")),
    ),
    "limit-calc-fields": None,  # filled in tests via _many_calcs
    "limit-cross-source-calcs": _cross_source(),
    "minimize-lod": _wb(
        datasources=_ds(
            columns=(
                "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
                + _col(
                    "Lod",
                    "[Calculation_1]",
                    "{FIXED [Status]: SUM([Profit])}",
                    datatype="real",
                )
            )
        ),
        worksheets=_ws(fields=("[Profit]", "[Calculation_1]")),
    ),
    "avoid-nested-calcs": _nested(),
    "limit-table-calcs": _wb(
        datasources=_ds(
            columns=(
                "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
                + _col("T", "[Calculation_1]", "LOOKUP(SUM([Profit]), -1)", datatype="real")
            )
        ),
        worksheets=_ws(fields=("[Profit]", "[Calculation_1]")),
    ),
    "avoid-hierarchies": _wb(
        datasources=_ds(
            extra="<drill-paths><drill-path name='geo'><field>[City]</field></drill-path></drill-paths>"
        )
    ),
    "consolidate-duplicate-calcs": _wb(
        datasources=_ds(
            columns=(
                "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
                + _col("A", "[Calculation_1]", "SUM([Profit])/SUM([Sales])", datatype="real")
                + _col("B", "[Calculation_2]", "SUM([Profit])/SUM([Sales])", datatype="real")
            )
        ),
        worksheets=_ws(fields=("[Profit]", "[Calculation_1]")),
    ),
    "binary-string-branches": _string_if(),
    "minimize-quick-filters": _filter_zones(4),
    "avoid-only-relevant-values": _wb(
        worksheets=_ws(extra="<filter class='categorical' column='[ds1].[Status]' show-relevant-values='true' />")
    ),
    "filter-actions-over-quick-filters": _actions(1, filters=4),
    "avoid-user-filters": _wb(
        datasources=_ds(
            columns=(
                "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
                + _col("U", "[Calculation_1]", "USERNAME()", datatype="string")
            )
        ),
        worksheets=_ws(fields=("[Profit]", "[Calculation_1]")),
    ),
    "limit-filter-count": _filter_zones(5),
    "apply-button": _filter_zones(2),
    "avoid-keep-only-exclude": _wb(
        worksheets=_ws(extra="<filter class='categorical' column='[ds1].[Status]' kind='exclude' />")
    ),
    "limit-worksheets-per-dashboard": _wb(
        worksheets=_ws(name="S1") + _ws(name="S2") + _ws(name="S3") + _ws(name="S4"),
        dashboards=_db(sheets=("S1", "S2", "S3", "S4")),
    ),
    "fixed-dashboard-size": _wb(dashboards=_db(size="automatic")),
    "limit-viz-in-tooltip": _wb(worksheets=_ws(extra="<tooltip viz-in-tooltip='true' />")),
    "limit-dashboard-actions": _actions(6),
    "prefer-tiled-over-floating": _wb(dashboards=_db(floating=True)),
    "sets-for-top-n": _wb(
        worksheets=_ws(extra="<filter class='quantitative' column='[ds1].[Profit]' end='top' />")
    ),
    "keep-tooltips-simple": _wb(
        worksheets=_ws(
            extra="<tooltip>" + "".join(f"<run>{i}</run>" for i in range(25)) + "</tooltip>"
        )
    ),
    "prefer-numbers-booleans": _string_if(),
    "avoid-row-level-param-calcs": _param_row(),
    "prefer-native-over-calcs": _native_case(),
    "avoid-high-cardinality-filters": _high_card(),
    "prefer-range-over-huge-discrete": _members(20),
    "filter-at-higher-grain": _grain(),
    "limit-heavy-text-tables": _crosstab(),
    "guided-drill-down": _wb(
        worksheets=_ws(name="S1") + _ws(name="S2") + _ws(name="S3") + _ws(name="S4"),
        dashboards=_db(sheets=("S1", "S2", "S3", "S4")),
    ),
    "default-field-properties": _repeat_format(),
    "avoid-excessive-formatting": _transparent_marks(),
}

TWBX_HITS = {
    "minimize-image-sizes": _twbx_heavy_png,
    "prefer-transparent-pngs": _twbx_jpeg,
}

ALWAYS_CLEAR = ("context-filters-not-query-lever", "upgrade-tableau-version")

SKIP_FIXTURES = {
    "avoid-custom-sql": (_wb(), "skipped"),
    "avoid-params-in-custom-sql": (_wb(), "skipped"),
    "remove-sql-order-by": (_wb(), "skipped"),
    "prefer-relationships": (_wb(), "skipped"),
    "referential-integrity": (_wb(), "skipped"),
    "minimize-image-sizes": (_wb(), "skipped"),
    "prefer-transparent-pngs": (_wb(), "skipped"),
    "sets-for-top-n": (_wb(), "skipped"),
    "keep-tooltips-simple": (_wb(), "skipped"),
    "limit-dashboard-actions": (_wb(), "skipped"),
    "filter-actions-over-quick-filters": (_wb(), "skipped"),
}


def test_new_ids_are_registered():
    for cid in NEW_CHECK_IDS:
        assert cid in wbo.CHECK_IDS, f"{cid} missing from CHECK_IDS"
        assert cid in wbo.CHECK_SUMMARIES
        assert cid in wbo.DETECTORS


def test_every_programmable_id_has_a_hit_or_clear(tmp: Path):
    missing = []
    for cid in list(dict.fromkeys([*wbo.CHECK_IDS, *NEW_CHECK_IDS])):
        if cid in ALWAYS_CLEAR:
            row = _status(tmp, _wb(), cid)
            if row["status"] != "clear":
                missing.append((cid, row["status"], "expected clear"))
            continue
        if cid == "limit-calc-fields":
            row = _status(tmp, _many_calcs(15), cid)
            if row["status"] != "hit":
                missing.append((cid, row["status"], "expected hit"))
            continue
        if cid not in HIT_XML and cid not in TWBX_HITS:
            missing.append((cid, "no-fixture", "missing HIT_XML"))
            continue
        status = _hit_status(tmp, cid)
        if status != "hit":
            missing.append((cid, status, "expected hit"))
    assert not missing, missing


def test_skip_and_clear_counterparts(tmp: Path):
    for cid, (xml, expected) in SKIP_FIXTURES.items():
        row = _status(tmp, xml, cid)
        assert row["status"] == expected, (cid, row)
        if expected == "skipped":
            # The skill quotes skipReason as the evidence for `n/a`.
            assert row["skipReason"], (cid, row)


def test_binary_string_three_branches_is_clear(tmp: Path):
    cols = (
        "<column caption='Status' datatype='string' name='[Status]' role='dimension' />"
        "<column caption='Profit' datatype='real' name='[Profit]' role='measure' />"
        + _col(
            "Lbl",
            "[Calculation_1]",
            "IF [Status] = &quot;A&quot; THEN &quot;Active&quot; "
            "ELSEIF [Status] = &quot;P&quot; THEN &quot;Pending&quot; "
            "ELSE &quot;Closed&quot; END",
            datatype="string",
        )
    )
    xml = _wb(
        datasources=_ds(columns=cols),
        worksheets=_ws(fields=("[Status]", "[Calculation_1]")),
    )
    assert _status(tmp, xml, "binary-string-branches")["status"] == "clear"


def test_extract_clears_live_check(tmp: Path):
    xml = _wb(datasources=_ds(extract=True))
    assert _status(tmp, xml, "extracts-over-live")["status"] == "clear"


def test_direct_hyper_source_is_not_live(tmp: Path):
    # A .hyper/.tde opened directly is an extract even with no <extract> element.
    xml = _wb(datasources=_ds(conn_class="hyper"))
    assert _status(tmp, xml, "extracts-over-live")["status"] == "clear"


def test_live_database_is_classified_distinctly(tmp: Path):
    # A2: a real DB server connection is a live database, not a live file.
    xml = _wb(datasources=_live_db_ds("sqlserver"))
    row = _status(tmp, xml, "extracts-over-live")
    assert row["status"] == "hit"
    findings = row["findings"]
    assert len(findings) == 1, findings
    f = findings[0]
    assert f["connectionClass"] == "sqlserver", f
    assert f["connectionType"] == "live-database", f
    assert f["isLiveDatabase"] is True, f


def test_live_file_is_not_a_live_database(tmp: Path):
    # A2: a file-backed live connection (Excel/CSV) is not a live database.
    xml = _wb(datasources=_ds())  # excel-direct by default
    row = _status(tmp, xml, "extracts-over-live")
    assert row["status"] == "hit"
    f = row["findings"][0]
    assert f["connectionType"] == "file", f
    assert f["isLiveDatabase"] is False, f


def test_other_file_connectors_classified_as_file(tmp: Path):
    # A2 (reviewer): text, JSON, and PDF are file connectors Tableau can read —
    # like Excel/CSV they are live *files*, never live *databases*. Classify by
    # connection class even when no `filename` attribute is present.
    for conn_class in ("textscan", "jsonfile", "pdf"):
        xml = _wb(datasources=_ds(conn_class=conn_class))
        row = _status(tmp, xml, "extracts-over-live")
        assert row["status"] == "hit", (conn_class, row)
        f = row["findings"][0]
        assert f["connectionType"] == "file", (conn_class, f)
        assert f["isLiveDatabase"] is False, (conn_class, f)


def _snapshot(root: Path) -> dict[str, int]:
    return {str(p): p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}


def test_superstore_smoke():
    root = _repo_root()
    path = root / "training-data" / "Superstore.twbx" if root else None
    if path is None or not path.exists():
        raise Skip("no training-data/Superstore.twbx here")
    before = _snapshot(path.parent)
    code, body = _cli(["check", str(path), "--json"])
    assert code == 0, body
    ids = [c["id"] for c in body["checks"]]
    assert ids == list(wbo.CHECK_IDS)
    assert {c["status"] for c in body["checks"]} <= {"hit", "clear", "skipped"}
    # check reads fixtures in place and never writes under training-data/.
    assert _snapshot(path.parent) == before


def main() -> int:
    """Run every test_* function in this file (discovered, not hand-listed)."""
    import tempfile

    tests = [
        fn
        for name, fn in list(globals().items())
        if name.startswith("test_") and inspect.isfunction(fn)
    ]
    failed = 0
    for test in tests:
        try:
            if inspect.signature(test).parameters:
                with tempfile.TemporaryDirectory() as td:
                    test(Path(td))
            else:
                test()
            print(f"PASS  {test.__name__}")
        except Skip as exc:
            print(f"SKIP  {test.__name__}: {exc}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {test.__name__}: {exc}")
        except Exception as exc:
            failed += 1
            print(f"ERROR {test.__name__}: {type(exc).__name__}: {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
