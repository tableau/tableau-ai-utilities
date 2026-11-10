#!/usr/bin/env python3
"""Tests for wbo.py (stdlib only)."""

from __future__ import annotations

import html
import inspect
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wbo  # noqa: E402

FIXTURE = """\
<?xml version='1.0' encoding='utf-8' ?>
<workbook version='18.1'>
  <datasources>
    <datasource caption='Orders' inline='true' name='ds1'>
      <connection class='federated'>
        <named-connections>
          <named-connection name='n1'>
            <connection class='excel-direct' />
          </named-connection>
        </named-connections>
        <relation name='orders' type='table' />
      </connection>
      <column caption='Profit' datatype='real' name='[Profit]' role='measure' />
      <column caption='Sales' datatype='real' name='[Sales]' role='measure' />
      <column caption='Status' datatype='string' name='[Status]' role='dimension' />
      <column caption='Margin Pct' datatype='real' name='[Calculation_1]' role='measure'>
        <calculation class='tableau' formula='SUM([Profit])/SUM([Sales])' />
      </column>
      <column caption='Profit Ratio' datatype='real' name='[Calculation_2]' role='measure'>
        <calculation class='tableau' formula='SUM([Profit])/SUM([Sales])' />
      </column>
      <column caption='Is Active' datatype='string' name='[Calculation_3]' role='dimension'>
        <calculation class='tableau' formula='IF [Status] = &quot;Active&quot; THEN &quot;Yes&quot; ELSE &quot;No&quot; END' />
      </column>
      <column caption='Status Label' datatype='string' name='[Calculation_4]' role='dimension'>
        <calculation class='tableau' formula='IF [Status] = &quot;A&quot; THEN &quot;Active&quot; ELSEIF [Status] = &quot;P&quot; THEN &quot;Pending&quot; ELSE &quot;Closed&quot; END' />
      </column>
      <column caption='Unused Dim' datatype='string' name='[Unused]' role='dimension' />
    </datasource>
    <datasource caption='Parameters' hasconnection='false' inline='true' name='Parameters'>
      <column caption='Rate' datatype='real' name='[Parameter 1]' role='measure' value='0.15' />
    </datasource>
  </datasources>
  <worksheets>
    <worksheet name='Sheet A'>
      <table>
        <view>
          <datasource-dependencies datasource='ds1'>
            <column name='[Calculation_1]' />
            <column name='[Profit]' />
            <column name='[Sales]' />
            <column name='[Status]' />
            <column name='[Calculation_3]' />
            <column name='[Calculation_4]' />
          </datasource-dependencies>
          <filter class='categorical' column='[Status]' />
        </view>
      </table>
    </worksheet>
  </worksheets>
  <dashboards>
    <dashboard name='Sales'>
      <size sizing-mode='automatic' />
      <zones>
        <zone name='Sheet A' type-v2='layout-basic' />
        <zone name='Sheet A' param='[Status]' type-v2='filter' />
      </zones>
    </dashboard>
  </dashboards>
</workbook>
"""


def _write_twb(tmp: Path, name: str = "wb.twb", xml: str = FIXTURE) -> Path:
    path = tmp / name
    path.write_text(xml, encoding="utf-8")
    return path


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


class Skip(Exception):
    """Raised by a test that cannot run here; reported as SKIP, not PASS."""


def test_missing_file_returns_json_error(tmp: Path):
    code, body = _cli(["check", str(tmp / "nope.twb"), "--json"])
    assert code == 1
    assert body["ok"] is False
    assert body["schemaVersion"] == 3
    assert body["command"] == "check"
    assert body["error"]["type"]


def test_unknown_check_id(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "not-a-real-id", "--json"])
    assert code == 1
    assert body["ok"] is False
    assert body["error"]["type"] == "unknown-id"


def test_graph_usage_and_duplicates(tmp: Path):
    path = _write_twb(tmp)
    usage = wbo.build_usage(path.read_text())
    cols = {c["name"]: c for c in usage["columns"]}
    assert "Sheet A" in cols["[Calculation_1]"]["usedOnWorksheets"]
    assert "Sales" in cols["[Calculation_1]"]["usedOnDashboards"]
    assert cols["[Calculation_2]"]["usedOnWorksheets"] == []
    assert cols["[Unused]"]["usedOnWorksheets"] == []
    unused = wbo.unused_column_names(usage)
    assert "[Unused]" in unused
    assert "[Calculation_2]" in unused
    assert "[Calculation_1]" not in unused
    assert usage["parameters"][0]["caption"] == "Rate"
    assert usage["worksheets"][0]["filters"] == ["Status"]
    assert usage["dashboards"][0]["filters"] == ["Status"]


def test_unused_is_per_datasource(tmp: Path):
    xml = """\
<?xml version='1.0' encoding='utf-8' ?>
<workbook version='18.1'>
  <datasources>
    <datasource caption='Orders' inline='true' name='dsA'>
      <connection class='federated'>
        <named-connections>
          <named-connection name='n1'><connection class='excel-direct' /></named-connection>
        </named-connections>
        <relation name='orders' type='table' />
      </connection>
      <column caption='Profit A' datatype='real' name='[Profit]' role='measure' />
    </datasource>
    <datasource caption='Returns' inline='true' name='dsB'>
      <connection class='federated'>
        <named-connections>
          <named-connection name='n2'><connection class='excel-direct' /></named-connection>
        </named-connections>
        <relation name='returns' type='table' />
      </connection>
      <column caption='Profit B' datatype='real' name='[Profit]' role='measure' />
    </datasource>
  </datasources>
  <worksheets>
    <worksheet name='Sheet A'>
      <table>
        <view>
          <datasource caption='Orders' />
          <datasource-dependencies datasource='dsA'>
            <column name='[Profit]' />
          </datasource-dependencies>
        </view>
      </table>
    </worksheet>
  </worksheets>
  <dashboards></dashboards>
</workbook>
"""
    path = _write_twb(tmp, "two.twb", xml)
    usage = wbo.build_usage(path.read_text())
    by = {(c["datasource"], c["name"]): c for c in usage["columns"]}
    assert "Sheet A" in by[("dsA", "[Profit]")]["usedOnWorksheets"]
    assert by[("dsB", "[Profit]")]["usedOnWorksheets"] == []
    unused = {(c["datasource"], c["name"]) for c in wbo.unused_columns(usage)}
    assert ("dsB", "[Profit]") in unused
    assert ("dsA", "[Profit]") not in unused


def test_severity_matches_skill_table():
    f = wbo._severity_for
    assert [f("CRITICAL", c) for c in wbo._SEVERITY_COLUMNS] == ["Warning", "Note", "Warning"]
    assert [f("HIGH", c) for c in wbo._SEVERITY_COLUMNS] == ["Warning", "Note", "Note"]
    assert [f("MEDIUM", c) for c in wbo._SEVERITY_COLUMNS] == ["Note", "Info", "Info"]
    assert [f("CLEANUP", c) for c in wbo._SEVERITY_COLUMNS] == ["Note", "Info", "Info"]


def test_severity_column_uses_strictest_connection():
    def col(*types):
        return wbo._severity_column({"datasources": [{"connectionType": t} for t in types]})

    assert col() == "live-database"
    assert col("extract") == "extract"
    assert col("file") == "live-file"
    assert col("extract", "file") == "live-file"
    assert col("file", "live-database") == "live-database"
    assert col("extract", "unknown") == "live-database"


def test_check_hits_carry_severity(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--json"])
    assert code == 0
    hits = [c for c in body["checks"] if c["status"] == "hit"]
    assert hits, "fixture should produce hits"
    # FIXTURE is a live Excel file, so the live-file column applies.
    for chk in hits:
        want = wbo._severity_for(wbo.check_priority(chk["id"]), "live-file")
        assert chk["severity"] == want, (chk["id"], chk["severity"], want)
    assert all("severity" not in c for c in body["checks"] if c["status"] != "hit")


def test_check_json_envelope(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--json"])
    assert code == 0
    assert body["ok"] is True
    assert body["command"] == "check"
    assert "usage" in body
    assert "checks" in body
    assert "diagrams" in body
    # Phase 0 scoping reads the object counts from here.
    assert body["summary"]["worksheets"] == 1
    assert body["summary"]["dashboards"] == 1
    assert "calculations" in body["summary"]
    ids = {c["id"]: c for c in body["checks"]}
    dup = ids["consolidate-duplicate-calcs"]
    assert dup["status"] == "hit"
    names = {m["caption"] for m in dup["findings"][0]["members"]}
    assert names == {"Margin Pct", "Profit Ratio"}
    binary = ids["binary-string-branches"]
    assert binary["status"] == "hit"
    captions = {f["caption"] for f in binary["findings"]}
    assert "Is Active" in captions
    assert "Status Label" not in captions
    assert ids["context-filters-not-query-lever"]["status"] == "clear"
    assert ids["fixed-dashboard-size"]["status"] == "hit"
    assert ids["hide-unused-fields"]["status"] == "hit"
    assert ids["minimize-data-volume"]["status"] == "hit"
    catalog_keys = {
        "summary",
        "detail",
        "detectability",
        "programmable",
        "impact",
        "priority",
        "fixMethod",
        "sources",
    }
    for row in (dup, binary, ids["context-filters-not-query-lever"], ids["hide-unused-fields"]):
        assert catalog_keys <= set(row)
    assert ids["hide-unused-fields"]["fixMethod"] == "mechanical"
    assert ids["hide-unused-fields"]["priority"] == "CLEANUP"
    assert ids["count-over-countd"]["priority"] == "MEDIUM"
    assert body["schemaVersion"] == 3
    assert "Sheet A" in body["diagrams"]["workbook"]
    assert "Sales" in body["diagrams"]["workbook"]
    assert "flowchart TB" in body["diagrams"]["workbook"]
    assert ":::workbook" in body["diagrams"]["workbook"]


def test_check_id_filters(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "binary-string-branches", "--json"])
    assert code == 0
    assert [c["id"] for c in body["checks"]] == ["binary-string-branches"]


def test_check_human_lists_hits_first(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path)])
    assert code == 0
    assert isinstance(body, str)
    assert "HIGH" in body
    assert "MEDIUM" in body
    assert "CLEANUP" in body
    assert body.index("HIGH") < body.index("MEDIUM")
    assert body.index("MEDIUM") < body.index("CLEANUP")
    assert body.index("fixed-dashboard-size") < body.index("hide-unused-fields")
    assert body.index("consolidate-duplicate-calcs") < body.index("hide-unused-fields")
    assert "Unused Dim" in body
    assert "[Unused]" not in body
    assert "CLEAR" not in body
    assert "SKIPPED" not in body
    assert "Suggestion:" not in body
    assert "->" not in body
    assert '"schemaVersion"' not in body


def test_diagrams_workbook_root_and_kinds(tmp: Path):
    path = _write_twb(tmp, "demo.twb")
    usage = wbo.build_usage(path.read_text())
    usage["_path"] = str(path)
    mermaid = wbo.diagrams_workbook(usage, detailed=True)
    assert mermaid.startswith("flowchart TB")
    assert ":::workbook" in mermaid
    assert ":::worksheet" in mermaid
    assert ":::dashboard" in mermaid
    assert ":::datasource" in mermaid
    assert ":::filter" in mermaid
    assert ":::parameter" in mermaid
    assert ":::calculation" in mermaid
    assert "demo.twb" in mermaid
    assert "wb -->" in mermaid
    assert "Status" in mermaid
    assert "Rate" in mermaid
    assert "Margin Pct" in mermaid
    assert "Profit Ratio" in mermaid
    assert "fl_" in mermaid
    assert "pm_" in mermaid
    assert "calc_" in mermaid


def test_mermaid_label_strips_backslash(tmp: Path):
    labeled = wbo._mermaid_label("Sales\\West")
    assert "\\" not in labeled
    assert labeled == "Sales West"


def test_mermaid_label_strips_backticks_and_quotes(tmp: Path):
    labeled = wbo._mermaid_label('```evil``` "x"')
    assert "`" not in labeled
    assert '"' not in labeled


def test_dest_dir_falls_back_to_dot_for_bare_filename(tmp: Path):
    assert wbo._dest_dir("copy.twb") == "."
    assert wbo._dest_dir("copy.twbx") == "."
    nested = os.path.join("out", "copy.twb")
    assert wbo._dest_dir(nested) == os.path.dirname(nested)


def test_check_format_json_alias(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--format", "json"])
    assert code == 0
    assert body["command"] == "check"
    assert body["ok"] is True


def test_check_json_flag_conflicts_with_human(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--format", "human", "--json"])
    assert code == 1
    assert isinstance(body, str)
    assert "conflicts" in body


def test_check_json_flag_conflicts_with_markdown(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--format", "markdown", "--json"])
    assert code == 1
    assert "conflicts" in str(body)


def test_check_markdown_is_hits_only_report(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--format", "markdown"])
    assert code == 0
    assert isinstance(body, str)
    assert body.startswith("# Check report")
    assert "```mermaid" in body
    assert "**Suggestion:**" in body
    assert "## Summary" in body
    assert "SKIPPED" not in body
    assert "federated." not in body
    # M2: the customer report speaks in human titles, not raw ids or CLI commands.
    assert "--check-id" not in body
    assert "wbo.py fix" not in body
    assert "hide-unused-fields" not in body
    assert "Hide unused fields" in body
    assert "Automatic fix available" in body
    assert "help.tableau.com" in body
    assert "practitioner pattern" in body
    assert ":::workbook" in body
    assert "flowchart TB" in body
    assert ":::filter" in body
    assert ":::parameter" in body
    assert ":::calculation" in body
    assert "diamond = calculation" in body
    assert "| filter | Status |" in body
    assert "| parameter | Rate |" in body
    assert "| calculation | Margin Pct |" in body


def test_check_markdown_out_file(tmp: Path):
    path = _write_twb(tmp)
    dest = tmp / "report.md"
    code, body = _cli(["check", str(path), "--format", "markdown", "--out", str(dest)])
    assert code == 0
    assert dest.exists()
    text = dest.read_text(encoding="utf-8")
    assert "# Check report" in text
    assert str(dest) in str(body)


def test_check_markdown_refuses_training_data_out(tmp: Path):
    path = _write_twb(tmp)
    td = tmp / "training-data"
    td.mkdir()
    dest = td / "report.md"
    code, body = _cli(["check", str(path), "--format", "markdown", "--out", str(dest)])
    assert code == 1
    assert not dest.exists()
    assert "training-data" in str(body)


def test_check_html_is_self_contained_grouped_report(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--format", "html"])
    assert code == 0
    assert isinstance(body, str)
    assert body.startswith("<!DOCTYPE html>")
    assert body.rstrip().endswith("</html>")
    # self-contained: inline styles, no external scripts or network calls
    assert "<style>" in body
    assert "<script" not in body
    assert "http://" not in body.replace("http://www.w3.org", "")
    assert "cdn" not in body.lower()
    # the report also blocks scripts and network requests if a name slips through
    assert "Content-Security-Policy" in body
    # item 3: issues grouped into auto-fixable vs author-only
    assert "Issues the optimizer can fix for you" in body
    assert "Issues to fix yourself in Tableau Studio" in body
    # M2: human titles, not raw ids
    assert "Hide unused fields" in body
    assert "hide-unused-fields" not in body
    # severity badge rendered
    assert "sev-warning" in body or "sev-note" in body


def test_check_html_escapes_hostile_workbook_names(tmp: Path):
    evil = "<img src=x onerror=alert(1)>"
    # XML attribute values cannot hold a raw "<", so write them as entities;
    # the parser hands wbo.py the decoded "<img ...>" text.
    xml = FIXTURE.replace("Unused Dim", "&lt;img src=x onerror=alert(1)&gt;").replace(
        "name='Sheet A'", "name='&lt;script&gt;x&lt;/script&gt;'"
    )
    assert "<img src=x" not in xml
    path = _write_twb(tmp, xml=xml)
    code, body = _cli(["check", str(path), "--format", "html"])
    assert code == 0
    assert isinstance(body, str)
    assert evil not in body
    assert "<script>x</script>" not in body
    assert "&lt;img" in body


def test_check_html_out_file(tmp: Path):
    path = _write_twb(tmp)
    dest = tmp / "report.html"
    code, body = _cli(["check", str(path), "--format", "html", "--out", str(dest)])
    assert code == 0
    assert dest.exists()
    text = dest.read_text(encoding="utf-8")
    assert text.startswith("<!DOCTYPE html>")
    assert str(dest) in str(body)


def test_check_html_refuses_workbook_out(tmp: Path):
    path = _write_twb(tmp)
    dest = tmp / "clobber.twbx"
    code, body = _cli(["check", str(path), "--format", "html", "--out", str(dest)])
    assert code == 1
    assert not dest.exists()


def test_check_html_json_conflict(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--format", "html", "--json"])
    assert code == 1
    # resolved before cmd_check, so it prints a plain-text usage error
    assert isinstance(body, str)
    assert "conflicts" in body and "html" in body


def test_check_report_dir_writes_bundle(tmp: Path):
    path = _write_twb(tmp)
    out = tmp / "run"
    code, body = _cli(["check", str(path), "--report-dir", str(out)])
    assert code == 0
    assert isinstance(body, dict)
    assert body["ok"] is True
    # three artifacts, shared basename (the workbook slug), one folder
    slug = wbo._slug_for(str(path))
    jf = out / f"{slug}.json"
    hf = out / f"{slug}.html"
    mf = out / f"{slug}.md"
    for f in (jf, hf, mf):
        assert f.exists(), f
    assert body["reports"] == {
        "dir": str(out),
        "json": str(jf),
        "html": str(hf),
        "markdown": str(mf),
    }
    # each file is the right rendering of the same check
    assert hf.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")
    assert mf.read_text(encoding="utf-8").startswith("# Check report")
    saved = json.loads(jf.read_text(encoding="utf-8"))
    assert saved["command"] == "check" and "checks" in saved
    assert "summary" in saved and "summary" in body
    # the saved json is the clean envelope (no self-referential reports index)
    assert "reports" not in saved


def test_check_reports_list_every_hit(tmp: Path):
    # W-24599017: the chat reply caps each severity group at 5; the saved
    # reports must still list every issue, with no "...and N more" line.
    path = _write_twb(tmp)
    usage = wbo.build_usage(path.read_text())
    usage["_path"] = str(path)
    checks = [
        {**c, "status": "hit", "detail": c.get("detail") or f"detail for {c['id']}"}
        for c in wbo.run_checks(usage)
    ]
    assert len(checks) > 15
    reports = {
        "html": html.unescape(wbo._html_check(str(path), usage, checks, [])),
        "markdown": wbo._markdown_check(str(path), usage, checks, []),
    }
    for kind, text in reports.items():
        missing = [c["id"] for c in checks if c["title"] not in text]
        assert not missing, f"{kind} report drops hits: {missing}"
        assert not re.search(r"\b\d+ more\b|…and", text), f"{kind} report truncates a list"


def test_check_report_dir_conflicts_with_out(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(
        ["check", str(path), "--report-dir", str(tmp / "run"), "--out", str(tmp / "r.html")]
    )
    assert code == 1
    assert isinstance(body, dict)
    assert body["error"]["type"] == "usage"
    assert "conflicts with --out" in body["error"]["message"]


def test_check_report_dir_conflicts_with_format(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(
        ["check", str(path), "--report-dir", str(tmp / "run"), "--format", "html"]
    )
    assert code == 1
    assert isinstance(body, dict)
    assert body["error"]["type"] == "usage"
    assert "drop --format" in body["error"]["message"]


def test_check_report_dir_refuses_training_data(tmp: Path):
    path = _write_twb(tmp)
    td = tmp / "training-data"
    td.mkdir()
    code, body = _cli(["check", str(path), "--report-dir", str(td / "run")])
    assert code == 1
    assert isinstance(body, dict)
    assert body["error"]["type"] == "forbidden-path"
    assert not (td / "run").exists()


def test_check_report_dir_token_suffixes_basename(tmp: Path):
    path = _write_twb(tmp)
    out = tmp / "run"
    code, body = _cli(
        ["check", str(path), "--report-dir", str(out), "--token", "a1b2c3"]
    )
    assert code == 0
    assert isinstance(body, dict)
    base = f"{wbo._slug_for(str(path))}-a1b2c3"
    jf = out / f"{base}.json"
    hf = out / f"{base}.html"
    mf = out / f"{base}.md"
    for f in (jf, hf, mf):
        assert f.exists(), f
    assert body["reports"] == {
        "dir": str(out),
        "json": str(jf),
        "html": str(hf),
        "markdown": str(mf),
    }
    # non-alnum chars in the token are stripped, never used raw in the path
    code2, body2 = _cli(
        ["check", str(path), "--report-dir", str(tmp / "r2"), "--token", "a/b .c"]
    )
    assert code2 == 0
    assert (tmp / "r2" / f"{wbo._slug_for(str(path))}-abc.json").exists()


def test_check_token_requires_report_dir(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--token", "a1b2c3"])
    assert code == 1
    assert isinstance(body, dict)
    assert body["error"]["type"] == "usage"
    assert "--token only applies with --report-dir" in body["error"]["message"]


def test_check_human_error_is_plain_text(tmp: Path):
    code, body = _cli(["check", str(tmp / "nope.twb")])
    assert code == 1
    assert isinstance(body, str)
    assert body.startswith("error:")
    assert "schemaVersion" not in body


def test_fix_does_not_touch_original(tmp: Path):
    path = _write_twb(tmp)
    original = path.read_text()
    # A4: a bare fix changes nothing; --all applies every mechanical fix.
    code, body = _cli(["fix", str(path), "--all", "--json"])
    assert code == 0
    assert body["ok"] is True
    assert body["schemaVersion"] == 3
    assert "hide-unused-fields" in body["applied"]
    assert "fixed-dashboard-size" in body["applied"]
    assert path.read_text() == original
    out = Path(body["outputPath"])
    assert out.exists()
    assert out != path
    xml = out.read_text()
    assert "hidden='true'" in xml
    assert "sizing-mode='fixed'" in xml
    assert all(isinstance(s, dict) for s in body["skipped"])
    assert all(s.get("reason") != "author-only" for s in body["skipped"])
    assert "consolidate-duplicate-calcs" not in [s.get("id") for s in body["skipped"]]


GT_CAPTION_XML = FIXTURE.replace(
    "<column caption='Unused Dim' datatype='string' name='[Unused]' role='dimension' />",
    "<column name='[Unused]' caption='Unused > Dim' datatype='string' role='dimension' />",
)


def test_fix_hide_handles_gt_inside_attribute_value(tmp: Path):
    assert GT_CAPTION_XML != FIXTURE
    path = _write_twb(tmp, xml=GT_CAPTION_XML)
    code, body = _cli(["fix", str(path), "hide-unused-fields", "--json"])
    assert code == 0, body
    assert body["ok"] is True
    assert "hide-unused-fields" in body["applied"]
    out_xml = Path(body["outputPath"]).read_text()
    ET.fromstring(out_xml)
    assert "caption='Unused > Dim'" in out_xml
    assert re.search(r"<column name='\[Unused\]'[^>]*caption='Unused > Dim'[^>]*hidden='true'", out_xml)


def test_fix_rejects_output_that_is_not_well_formed(tmp: Path):
    path = _write_twb(tmp)
    original = path.read_text()
    real = wbo.hide_fields_in_xml
    wbo.hide_fields_in_xml = lambda xml, fields: (xml.replace("<workbook", "<workbook <"), ["[Unused]"], [])
    try:
        code, body = _cli(["fix", str(path), "hide-unused-fields", "--json"])
    finally:
        wbo.hide_fields_in_xml = real
    assert code == 1, body
    assert body["ok"] is False
    assert body["error"]["type"] == "invalid-output"
    assert path.read_text() == original
    assert not (tmp / "wb-optimized.twb").exists()


def test_fix_rejects_invalid_output_in_place_and_keeps_original(tmp: Path):
    path = _write_twb(tmp)
    original = path.read_text()
    real = wbo.hide_fields_in_xml
    wbo.hide_fields_in_xml = lambda xml, fields: (xml.replace("<workbook", "<workbook <"), ["[Unused]"], [])
    try:
        code, body = _cli(["fix", str(path), "hide-unused-fields", "--in-place", "--json"])
    finally:
        wbo.hide_fields_in_xml = real
    assert code == 1, body
    assert body["error"]["type"] == "invalid-output"
    assert path.read_text() == original


def test_fix_rejects_invalid_output_from_dashboard_size_fix(tmp: Path):
    path = _write_twb(tmp)
    original = path.read_text()
    real = wbo.fixed_dashboard_size_in_xml
    wbo.fixed_dashboard_size_in_xml = lambda xml: (
        xml.replace("sizing-mode='automatic'", "sizing-mode='fixed'").replace("<workbook", "<workbook <"),
        1,
    )
    try:
        code, body = _cli(["fix", str(path), "fixed-dashboard-size", "--json"])
    finally:
        wbo.fixed_dashboard_size_in_xml = real
    assert code == 1, body
    assert body["ok"] is False
    assert body["error"]["type"] == "invalid-output"
    assert path.read_text() == original
    assert not (tmp / "wb-optimized.twb").exists()


def test_fix_write_failure_returns_io_envelope(tmp: Path):
    # A workbook locked by Desktop (or a read-only folder) must give an io
    # envelope, not a traceback, and must leave the original untouched.
    path = _write_twb(tmp)
    original = path.read_text()
    real = wbo.shutil.copy2

    def boom(*args, **kwargs):
        raise PermissionError("locked")

    wbo.shutil.copy2 = boom
    try:
        code, body = _cli(["fix", str(path), "hide-unused-fields", "--json"])
    finally:
        wbo.shutil.copy2 = real
    assert code == 1, body
    assert body["ok"] is False
    assert body["error"]["type"] == "io"
    assert "locked" in body["error"]["message"]
    assert path.read_text() == original


def test_fixed_dashboard_size_counts_only_changed_dashboards(tmp: Path):
    xml = (
        "<workbook><dashboards>"
        "<dashboard name='A'><size sizing-mode='automatic' /></dashboard>"
        "<dashboard name='B'><size sizing-mode='fixed' /></dashboard>"
        "<dashboard name='C'><size sizing-mode='automatic' /></dashboard>"
        "</dashboards></workbook>"
    )
    new, changed = wbo.fixed_dashboard_size_in_xml(xml)
    assert changed == 2
    assert "automatic" not in new
    assert new.count("sizing-mode='fixed'") == 3
    same, none = wbo.fixed_dashboard_size_in_xml(new)
    assert none == 0 and same == new


def test_fix_keeps_crlf_line_endings(tmp: Path):
    # Only the intended edit may change; line endings must survive a fix.
    crlf = FIXTURE.replace("\n", "\r\n")
    path = tmp / "crlf.twb"
    path.write_bytes(crlf.encode("utf-8"))
    code, body = _cli(["fix", str(path), "hide-unused-fields", "--json"])
    assert code == 0, body
    assert "hide-unused-fields" in body["applied"]
    out_bytes = Path(body["outputPath"]).read_bytes()
    assert out_bytes.count(b"\r\n") == crlf.count("\r\n")
    assert out_bytes.count(b"\n") == out_bytes.count(b"\r\n")
    ET.fromstring(out_bytes.decode("utf-8"))


def test_fix_author_only_id_skips(tmp: Path):
    path = _write_twb(tmp)
    original = path.read_text()
    code, body = _cli(["fix", str(path), "consolidate-duplicate-calcs", "--json"])
    assert code == 0
    assert body["ok"] is True
    assert body["applied"] == []
    assert body["outputPath"] is None
    assert body["skipped"][0]["id"] == "consolidate-duplicate-calcs"
    assert body["skipped"][0]["reason"] == "author-only"
    assert body["skipped"][0]["message"]
    assert path.read_text() == original
    assert not (tmp / "wb-optimized.twb").exists()


def test_fix_author_only_human(tmp: Path):
    path = _write_twb(tmp)
    original = path.read_text()
    code, body = _cli(["fix", str(path), "consolidate-duplicate-calcs"])
    assert code == 0
    assert isinstance(body, str)
    assert "schemaVersion" not in body
    assert "Do not rewrite XML" in body
    assert "nothing written" in body
    assert path.read_text() == original


def test_fix_in_place_only_with_flag(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["fix", str(path), "fixed-dashboard-size", "--in-place", "--json"])
    assert code == 0
    assert "fixed-dashboard-size" in body["applied"]
    assert "sizing-mode='fixed'" in path.read_text()


def test_fix_refuses_training_data_out(tmp: Path):
    td = tmp / "training-data"
    td.mkdir()
    path = _write_twb(tmp, "src.twb")
    dest = td / "copy.twb"
    code, body = _cli(["fix", str(path), "--out", str(dest), "--json"])
    assert code == 1
    assert body["ok"] is False
    assert not dest.exists()


def test_twbx_preserves_non_twb_bytes(tmp: Path):
    twb = tmp / "pack.twb"
    twb.write_text(FIXTURE, encoding="utf-8")
    twbx = tmp / "pack.twbx"
    extra = b"asset-bytes-xyz"
    with zipfile.ZipFile(twbx, "w") as zf:
        zf.writestr("pack.twb", twb.read_bytes())
        zf.writestr("Data/extra.bin", extra)
    code, body = _cli(["fix", str(twbx), "fixed-dashboard-size", "--json"])
    assert code == 0
    out = Path(body["outputPath"])
    with zipfile.ZipFile(out) as zf:
        assert zf.read("Data/extra.bin") == extra
    with zipfile.ZipFile(twbx) as zf:
        assert zf.read("Data/extra.bin") == extra


def _symlink_or_skip(target: Path, link: Path) -> None:
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError, AttributeError) as exc:
        # Windows needs developer mode or an elevated shell to create symlinks.
        raise Skip(f"cannot create symlinks here: {exc}")


def test_fix_symlink_writes_next_to_resolved_target(tmp: Path):
    real = tmp / "realplace"
    linkdir = tmp / "linkdir"
    real.mkdir()
    linkdir.mkdir()
    twb = real / "pack.twb"
    twb.write_text(FIXTURE, encoding="utf-8")
    target = real / "sym.twbx"
    with zipfile.ZipFile(target, "w") as zf:
        zf.writestr("pack.twb", twb.read_bytes())
        zf.writestr("Data/extra.bin", b"asset-bytes")
    link = linkdir / "sym.twbx"
    _symlink_or_skip(target, link)
    code, body = _cli(["fix", str(link), "fixed-dashboard-size", "--json"])
    assert code == 0
    out = Path(body["outputPath"])
    assert out.parent.resolve() == real.resolve()
    assert out.name == "sym-optimized.twbx"
    assert not (linkdir / "sym-optimized.twbx").exists()
    assert target.exists()


def test_default_out_path_resolves_symlink(tmp: Path):
    real = tmp / "realplace"
    linkdir = tmp / "linkdir"
    real.mkdir()
    linkdir.mkdir()
    target = real / "wb.twb"
    target.write_text(FIXTURE, encoding="utf-8")
    link = linkdir / "wb.twb"
    _symlink_or_skip(target, link)
    out = Path(wbo.default_out_path(str(link)))
    assert out.parent.resolve() == real.resolve()
    assert out.name == "wb-optimized.twb"


def test_stats_json_has_usage(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["stats", str(path), "--json"])
    assert code == 0
    assert body["command"] == "stats"
    assert body["summary"]["worksheets"] == 1
    assert body["summary"]["parameters"] == 1
    assert body["usage"]["parameters"][0]["caption"] == "Rate"
    assert body["diagrams"]["workbook"]


def test_stats_quiet_when_reader_closes_pipe_early(tmp: Path):
    # Agents validate a fix with `wbo.py stats ... --json | head -c 300`. The
    # output must outgrow the OS pipe buffer so the write is still in flight
    # when the reader closes; a closed stdout must exit 0 without a traceback.
    import subprocess

    extra = "".join(
        f"      <column caption='Extra {i}' datatype='string' name='[Extra_{i}]' role='dimension' />\n"
        for i in range(3000)
    )
    anchor = "      <column caption='Unused Dim'"
    path = _write_twb(tmp, xml=FIXTURE.replace(anchor, extra + anchor, 1))
    proc = subprocess.Popen(
        [sys.executable, str(Path(wbo.__file__)), "stats", str(path), "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    head = proc.stdout.read(300)
    proc.stdout.close()
    err = proc.stderr.read().decode("utf-8", "replace")
    proc.stderr.close()
    code = proc.wait(timeout=60)
    assert b'"ok": true' in head
    assert "Traceback" not in err, err
    assert "Exception ignored" not in err, err
    assert code == 0


def test_size_warning_threshold_is_200_mb(tmp: Path):
    assert wbo.SIZE_WARNING_BYTES == 200 * 1024 * 1024


def test_size_warning_skips_small_file(tmp: Path):
    path = _write_twb(tmp)
    assert wbo.size_warning(path) is None


def test_size_warning_fires_over_threshold(tmp: Path):
    path = _write_twb(tmp)
    old = wbo.SIZE_WARNING_BYTES
    wbo.SIZE_WARNING_BYTES = 1
    try:
        warn = wbo.size_warning(path)
    finally:
        wbo.SIZE_WARNING_BYTES = old
    assert warn is not None
    assert warn["id"] == "large-file"
    assert warn["bytes"] == path.stat().st_size
    assert warn["thresholdBytes"] == 1
    assert "extract" in warn["message"].lower()
    assert "not xml" in warn["message"].lower() or "not the whole zip" in warn["message"].lower()


def test_object_count_warning_skips_small_summary(tmp: Path):
    assert wbo.object_count_warning(
        {"worksheets": 1, "dashboards": 1, "fields": 10}
    ) is None


def test_object_count_warning_fires_at_500(tmp: Path):
    warn = wbo.object_count_warning(
        {"worksheets": 100, "dashboards": 50, "fields": 350}
    )
    assert warn is not None
    assert warn["id"] == "large-object-count"
    assert warn["objects"] == 500
    assert warn["threshold"] == 500


def test_stats_json_includes_empty_warnings(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["stats", str(path), "--json"])
    assert code == 0
    assert body["warnings"] == []


def test_stats_json_includes_large_file_warning(tmp: Path):
    path = _write_twb(tmp)
    old = wbo.SIZE_WARNING_BYTES
    wbo.SIZE_WARNING_BYTES = 1
    try:
        code, body = _cli(["stats", str(path), "--json"])
    finally:
        wbo.SIZE_WARNING_BYTES = old
    assert code == 0
    assert body["ok"] is True
    assert body["warnings"][0]["id"] == "large-file"
    assert body["warnings"][0]["bytes"] == path.stat().st_size


def test_stats_json_includes_object_count_warning(tmp: Path):
    path = _write_twb(tmp)
    old = wbo.OBJECT_COUNT_THRESHOLD
    wbo.OBJECT_COUNT_THRESHOLD = 1
    try:
        code, body = _cli(["stats", str(path), "--json"])
    finally:
        wbo.OBJECT_COUNT_THRESHOLD = old
    assert code == 0
    ids = [w["id"] for w in body["warnings"]]
    assert "large-object-count" in ids


def test_check_json_includes_warnings(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--json"])
    assert code == 0
    assert body["warnings"] == []


def test_stats_human_prints_large_file_warning(tmp: Path):
    path = _write_twb(tmp)
    old = wbo.SIZE_WARNING_BYTES
    wbo.SIZE_WARNING_BYTES = 1
    try:
        code, body = _cli(["stats", str(path)])
    finally:
        wbo.SIZE_WARNING_BYTES = old
    assert code == 0
    assert isinstance(body, str)
    assert "warning:" in body.lower()
    assert "large-file" in body


def test_list_check(tmp: Path):
    code, body = _cli(["list", "check", "--json"])
    assert code == 0
    assert body["ok"] is True
    assert body["schemaVersion"] == 3
    assert body["command"] == "list"
    assert body["workbook"]["path"] == ""
    assert body["workbook"]["version"] is None
    ids = [c["id"] for c in body["checks"]]
    assert "consolidate-duplicate-calcs" in ids
    assert "binary-string-branches" in ids
    assert "extracts-over-live" in ids
    for cid in (
        "test-anchor-table",
        "publish-shared-sources",
        "materialize-calcs-in-extract",
        "reduce-mark-count",
        "performance-recorder",
        "fix-source-bottlenecks",
        "clean-structured-data",
    ):
        assert cid in ids
    assert all(c["summary"] for c in body["checks"])
    catalog_keys = {
        "id",
        "summary",
        "detail",
        "detectability",
        "programmable",
        "impact",
        "priority",
        "fixMethod",
        "sources",
    }
    for rec in body["checks"]:
        assert catalog_keys <= set(rec)
    assert "fixes" not in body
    reduce_mark = next(c for c in body["checks"] if c["id"] == "reduce-mark-count")
    assert reduce_mark["programmable"] is False
    assert reduce_mark["priority"] == "HIGH"
    assert reduce_mark["fixMethod"] == "author-only"
    countd = next(c for c in body["checks"] if c["id"] == "count-over-countd")
    assert countd["priority"] == "MEDIUM"


def test_list_check_one_id(tmp: Path):
    code, body = _cli(["list", "check", "count-over-countd", "--json"])
    assert code == 0
    assert [c["id"] for c in body["checks"]] == ["count-over-countd"]
    assert "fixes" not in body


def test_list_check_human_does_not_repeat_identical_detail(tmp: Path):
    code, body = _cli(["list", "check", "fix-source-bottlenecks"])
    assert code == 0
    assert isinstance(body, str)
    line = "Slow in the source means slow in Desktop and almost always on Server."
    assert body.count(line) == 1
    code2, body2 = _cli(["list", "check", "hide-unused-fields"])
    assert code2 == 0
    assert "Hide unused fields so extracts and queries drop them." in str(body2)
    assert "hidden='true'" in str(body2)


def test_list_check_format_json_alias(tmp: Path):
    code_a, body_a = _cli(["list", "check", "--json"])
    code_b, body_b = _cli(["list", "check", "--format", "json"])
    assert code_a == code_b == 0
    assert body_a == body_b


def test_list_fix(tmp: Path):
    code, body = _cli(["list", "fix", "--json"])
    assert code == 0
    ids = [c["id"] for c in body["fixes"]]
    assert ids == ["hide-unused-fields", "fixed-dashboard-size"]
    assert all(c["summary"] for c in body["fixes"])
    assert all(c["fixMethod"] == "mechanical" for c in body["fixes"])
    assert "checks" not in body


def test_list_fix_one_id(tmp: Path):
    code, body = _cli(["list", "fix", "hide-unused-fields", "--json"])
    assert code == 0
    assert [c["id"] for c in body["fixes"]] == ["hide-unused-fields"]


def test_list_fix_author_only_is_unknown(tmp: Path):
    code, body = _cli(["list", "fix", "consolidate-duplicate-calcs", "--json"])
    assert code == 1
    assert body["ok"] is False
    assert body["error"]["type"] == "unknown-id"
    assert "not a mechanical fix" in body["error"]["message"]


def test_list_requires_nested_command(tmp: Path):
    code, body = _cli(["list"])
    assert code == 2
    assert not (isinstance(body, dict) and body.get("ok") is False)


def test_root_help_lists_all_commands(tmp: Path):
    code, body = _cli(["--help"])
    assert code == 0
    assert isinstance(body, str)
    assert "stats" in body
    assert "check" in body
    assert "fix" in body
    assert "list" in body
    assert "wbo.py check workbook.twbx" in body


def test_check_help_describes_formats(tmp: Path):
    code, body = _cli(["check", "--help"])
    assert code == 0
    assert isinstance(body, str)
    assert "--format" in body
    assert "markdown" in body
    assert "WORKBOOK" in body
    assert "--out FILE" in body
    assert "does not modify the workbook" in body.lower()


def test_no_command_prints_help(tmp: Path):
    code, body = _cli([])
    assert code == 2
    assert isinstance(body, str)
    assert "commands:" in body.lower() or "Examples:" in body


def test_source_links_do_not_invent_help(tmp: Path):
    dup = wbo._source_links("consolidate-duplicate-calcs")
    assert "help.tableau.com" not in dup
    assert "practitioner pattern" in dup
    assert "help.tableau.com" in wbo._source_links("hide-unused-fields")
    user = wbo._source_links("avoid-user-filters")
    assert "help.tableau.com" not in user
    assert "InterWorks" in user


def test_detailed_graph_keeps_named_nodes_when_large(tmp: Path):
    path = _write_twb(tmp, "demo.twb")
    usage = wbo.build_usage(path.read_text())
    usage["_path"] = str(path)
    extra = [
        {"name": f"Sheet {i}", "datasources": ["Orders"], "fields": [], "filters": []}
        for i in range(24)
    ]
    usage["worksheets"] = extra + usage["worksheets"]
    mermaid = wbo.diagrams_workbook(usage, detailed=True)
    assert "Margin Pct" in mermaid
    assert "Status" in mermaid
    assert "Rate" in mermaid
    assert "25 worksheets" not in mermaid


def test_compact_graph_collapses_when_large(tmp: Path):
    path = _write_twb(tmp, "demo.twb")
    usage = wbo.build_usage(path.read_text())
    usage["_path"] = str(path)
    extra = [
        {"name": f"Sheet {i}", "datasources": ["Orders"], "fields": [], "filters": []}
        for i in range(24)
    ]
    usage["worksheets"] = extra + usage["worksheets"]
    mermaid = wbo.diagrams_workbook(usage, detailed=False)
    assert "25 worksheets" in mermaid


def test_check_out_refuses_workbook_path(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--format", "markdown", "--out", str(path)])
    assert code == 1
    assert path.read_text(encoding="utf-8") == FIXTURE
    assert "overwrite" in str(body).lower()


def test_fix_out_refuses_original(tmp: Path):
    path = _write_twb(tmp)
    original = path.read_text()
    code, body = _cli(["fix", str(path), "--out", str(path), "--json"])
    assert code == 1
    assert path.read_text() == original
    assert body["ok"] is False


def test_fix_in_place_refuses_training_data(tmp: Path):
    td = tmp / "training-data"
    td.mkdir()
    path = _write_twb(td, "sample.twb")
    original = path.read_text()
    code, body = _cli(["fix", str(path), "--in-place", "--json"])
    assert code == 1
    assert path.read_text() == original
    assert body["ok"] is False


def test_fix_out_refuses_case_alias(tmp: Path):
    path = _write_twb(tmp, "wb.twb")
    alias = path.parent / "WB.twb"
    if not alias.exists():
        return
    try:
        same = path.samefile(alias)
    except OSError:
        return
    if not same:
        return
    original = path.read_text()
    code, body = _cli(["fix", str(path), "--out", str(alias), "--json"])
    assert code == 1
    assert path.read_text() == original
    assert body["ok"] is False


def test_fix_in_place_refuses_training_data_case_alias(tmp: Path):
    td = tmp / "training-data"
    td.mkdir()
    path = _write_twb(td, "sample.twb")
    alias = tmp / "Training-Data" / "sample.twb"
    if not alias.exists():
        return
    try:
        same = path.samefile(alias)
    except OSError:
        return
    if not same:
        return
    original = path.read_text()
    code, body = _cli(["fix", str(alias), "--in-place", "--json"])
    assert code == 1
    assert path.read_text() == original
    assert body["ok"] is False


def test_stats_human_uses_captions(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["stats", str(path)])
    assert code == 0
    assert isinstance(body, str)
    assert "Unused Dim" in body
    assert "[Unused]" not in body


def test_worksheet_filter_does_not_clear_volume(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "minimize-data-volume", "--json"])
    assert code == 0
    assert body["checks"][0]["status"] == "hit"


def test_datasource_filters_clear_volume(tmp: Path):
    xml = """\
<?xml version='1.0' encoding='utf-8' ?>
<workbook version='18.1'>
  <datasources>
    <datasource caption='Orders' inline='true' name='ds1'>
      <connection class='federated'>
        <named-connections>
          <named-connection name='n1'><connection class='excel-direct' /></named-connection>
        </named-connections>
        <relation name='orders' type='table' />
      </connection>
      <datasource-filters>
        <filter class='categorical' column='[Status]' />
      </datasource-filters>
      <column caption='Status' datatype='string' name='[Status]' role='dimension' />
    </datasource>
  </datasources>
  <worksheets></worksheets>
  <dashboards></dashboards>
</workbook>
"""
    path = _write_twb(tmp, "vol.twb", xml)
    code, body = _cli(["check", str(path), "minimize-data-volume", "--json"])
    assert code == 0
    assert body["checks"][0]["status"] == "clear"


def test_check_non_programmable_id(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "reduce-mark-count", "--json"])
    assert code == 1
    assert body["ok"] is False
    assert body["error"]["type"] == "not-programmable"


def test_fix_unknown_id(tmp: Path):
    path = _write_twb(tmp)
    original = path.read_text()
    code, body = _cli(["fix", str(path), "not-a-real-id", "--json"])
    assert code == 1
    assert body["error"]["type"] == "unknown-id"
    assert path.read_text() == original


def test_list_unknown_id(tmp: Path):
    code, body = _cli(["list", "check", "not-a-real-id", "--json"])
    assert code == 1
    assert body["error"]["type"] == "unknown-id"


def test_fix_json_flag_and_format_json_equivalent(tmp: Path):
    path = _write_twb(tmp)
    code_a, body_a = _cli(["fix", str(path), "fixed-dashboard-size", "--json"])
    path_b = _write_twb(tmp, "wb2.twb")
    code_b, body_b = _cli(["fix", str(path_b), "fixed-dashboard-size", "--format", "json"])
    assert code_a == code_b == 0
    assert body_a["applied"] == body_b["applied"]
    assert body_a["ok"] is True


def test_fix_json_conflicts_with_human(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["fix", str(path), "--format", "human", "--json"])
    assert code == 1
    assert isinstance(body, str)
    assert "conflicts" in body


def test_fix_missing_file_is_io_not_author_only(tmp: Path):
    code, body = _cli(
        ["fix", str(tmp / "nope.twb"), "consolidate-duplicate-calcs", "--json"]
    )
    assert code == 1
    assert body["error"]["type"] == "io"


def test_fix_catalog_id_as_path_is_io(tmp: Path):
    # A catalog id in the path position is a bad path, not a check id.
    # --all gets us past the bare-fix guard so we exercise the io path.
    code, body = _cli(["fix", "consolidate-duplicate-calcs", "--all", "--json"])
    assert code == 1
    assert body["error"]["type"] == "io"


def test_fix_bare_path_requires_all_or_id(tmp: Path):
    # A4: a bare `fix <path>` with no id and no --all must change nothing.
    path = _write_twb(tmp)
    code, body = _cli(["fix", str(path), "--json"])
    assert code == 1
    assert body["error"]["type"] == "usage"
    assert "--all" in body["error"]["message"]


def test_check_id_flag_rejected(tmp: Path):
    path = _write_twb(tmp)
    code, body = _cli(["check", str(path), "--check-id", "hide-unused-fields", "--json"])
    assert code == 2
    assert not (isinstance(body, dict) and body.get("command") == "check")


def test_help_has_no_catalog_essay(tmp: Path):
    code, body = _cli(["--help"])
    assert code == 0
    assert "COUNTD is slow" not in str(body)
    assert "Hide unused fields so extracts" not in str(body)
    code2, body2 = _cli(["check", "--help"])
    assert code2 == 0
    assert "list check" in str(body2)


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
