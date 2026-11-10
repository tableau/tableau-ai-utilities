#!/usr/bin/env python3
"""Safe local helpers for inspecting and packaging Tableau workbooks."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

from lxml import etree


MAX_MEMBERS = 10_000
MAX_UNCOMPRESSED_BYTES = 2_000_000_000


def secure_parser() -> etree.XMLParser:
    return etree.XMLParser(resolve_entities=False, no_network=True, recover=False)


def archive_path(name: str) -> PurePosixPath:
    relative = PurePosixPath(name)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts or "\\" in name:
        raise ValueError(f"unsafe archive member: {name}")
    for part in relative.parts:
        if (part.endswith((' ', '.')) or re.search(r'[<>:"|?*\x00-\x1f]', part)
                or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part, re.I)):
            raise ValueError(f"unsafe archive member: {name}")
    return relative


def safe_extract(twbx_path: str, run_dir: str) -> dict[str, str]:
    source = Path(twbx_path).resolve()
    run = Path(run_dir).resolve()
    destination = run / "extracted"

    with zipfile.ZipFile(source) as archive:
        members = archive.infolist()
        if len(members) > MAX_MEMBERS:
            raise ValueError("archive exceeds member-count limit")
        if sum(member.file_size for member in members) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("archive exceeds uncompressed-size limit")

        paths = {}
        for member in members:
            relative = archive_path(member.filename)
            key = relative.as_posix().casefold()
            if key in paths:
                raise ValueError(f"duplicate archive path: {member.filename}")
            paths[key] = member
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"archive link is not allowed: {member.filename}")
            target = (destination / Path(*relative.parts)).resolve()
            if target != destination and destination not in target.parents:
                raise ValueError(f"archive member escapes destination: {member.filename}")
        for key in paths:
            for parent in PurePosixPath(key).parents:
                if parent.as_posix() in paths and not paths[parent.as_posix()].is_dir():
                    raise ValueError(f"archive file/directory conflict: {key}")
        workbook_members = [m for m in members if not m.is_dir() and PurePosixPath(m.filename).suffix.lower() == '.twb']
        if len(workbook_members) != 1:
            raise ValueError(f"expected exactly one .twb, found {len(workbook_members)}")
        run.mkdir(parents=True, exist_ok=False)
        destination.mkdir()
        for member in members:
            target = destination / Path(*archive_path(member.filename).parts)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source_stream, target.open("xb") as target_stream:
                shutil.copyfileobj(source_stream, target_stream)

    candidates = sorted(p for p in destination.rglob('*') if p.is_file() and p.suffix.lower() == '.twb')
    if len(candidates) != 1:
        raise ValueError(f"expected exactly one .twb, found {len(candidates)}")
    original = candidates[0]
    working = run / "working.vibe.twb"
    shutil.copy2(original, working)
    return {
        "extracted_dir": str(destination),
        "working_twb": str(working),
        "original_member": original.relative_to(destination).as_posix(),
    }


def local_name(element: etree._Element) -> str:
    return etree.QName(element).localname


def validate(twb_path: str) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    try:
        tree = etree.parse(twb_path, secure_parser())
    except (OSError, etree.XMLSyntaxError) as exc:
        return {"ok": False, "checks": [{"id": "xml", "ok": False, "detail": str(exc)}]}

    root = tree.getroot()
    checks.append({"id": "xml", "ok": True, "detail": "well-formed XML"})
    checks.append({"id": "workbook-root", "ok": root.tag == "workbook",
                   "detail": "expected unnamespaced Tableau workbook root; other schemas require separate validation"})
    checks.append({"id": "doctype", "ok": not tree.docinfo.doctype,
                   "detail": "DTD-bearing workbooks require separate review"})

    forbidden_font_formats = root.xpath(".//*[local-name()='format'][@attr='font-color']")
    checks.append({
        "id": "font-color-location",
        "ok": not forbidden_font_formats,
        "detail": f"forbidden font-color format elements: {len(forbidden_font_formats)}",
    })

    empty_external = root.xpath(".//*[local-name()='external'][not(*) and not(normalize-space())]")
    checks.append({
        "id": "empty-external",
        "ok": not empty_external,
        "detail": f"empty external elements: {len(empty_external)}",
    })

    child_names = [local_name(child) for child in root if isinstance(child.tag, str)]
    worksheets_present = "worksheets" in child_names
    actions_index = child_names.index("actions") if "actions" in child_names else None
    worksheets_index = child_names.index("worksheets") if worksheets_present else None
    order_ok = worksheets_present and (actions_index is None or actions_index < worksheets_index)
    checks.append({
        "id": "workbook-collections",
        "ok": order_ok,
        "detail": "worksheets present and actions ordering is valid" if order_ok else "missing worksheets or actions follow worksheets",
    })

    return {"ok": all(bool(check["ok"]) for check in checks), "checks": checks}


def replace_run_color(twb_path: str, source_color: str, target_color: str) -> int:
    tree = etree.parse(twb_path, secure_parser())
    changed = 0
    for run in tree.xpath(".//*[local-name()='run']"):
        if run.get("fontcolor", "").casefold() == source_color.casefold():
            run.set("fontcolor", target_color)
            changed += 1
    tree.write(twb_path, xml_declaration=True, encoding="utf-8")
    return changed


def package(extracted_dir: str, edited_twb: str, original_member: str, out_twbx: str) -> str:
    root = Path(extracted_dir).resolve()
    member_path = archive_path(original_member)
    if member_path.is_absolute() or ".." in member_path.parts or member_path.suffix.lower() != ".twb":
        raise ValueError("invalid workbook member path")
    member = (root / Path(*member_path.parts)).resolve()
    if root not in member.parents:
        raise ValueError("workbook member escapes extraction root")

    if not member.is_file():
        raise ValueError("original workbook member does not exist")
    if not validate(edited_twb)["ok"]:
        raise ValueError("edited workbook failed local validation")
    output = Path(out_twbx).resolve()
    if output == root or root in output.parents:
        raise ValueError("output must be outside the extracted tree")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    temporary = output.with_suffix(output.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"temporary output already exists: {temporary}")
    temporary_owned = False
    try:
        entries = sorted(root.rglob("*"))
        if any(path.is_symlink() or (path.resolve() != root and root not in path.resolve().parents) for path in entries):
            raise ValueError("extracted tree contains a link or escaped member")
        files = [path for path in entries if path.is_file()]
        keys = [archive_path(path.relative_to(root).as_posix()).as_posix().casefold() for path in files]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate package paths")
        if sum(path.suffix.lower() == '.twb' for path in files) != 1:
            raise ValueError("package must contain exactly one workbook")
        with zipfile.ZipFile(temporary, "x", zipfile.ZIP_DEFLATED) as archive:
            temporary_owned = True
            for path in files:
                relative = path.relative_to(root).as_posix()
                info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, Path(edited_twb).read_bytes() if path.resolve() == member else path.read_bytes())
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None or archive.read(member_path.as_posix()) != Path(edited_twb).read_bytes():
                raise ValueError("packaged workbook failed read-back")
        with output.open('xb') as stream:
            try:
                with temporary.open('rb') as source:
                    shutil.copyfileobj(source, stream)
            except Exception:
                stream.close()
                output.unlink()
                raise
        temporary.unlink()
    except Exception:
        if temporary_owned:
            temporary.unlink(missing_ok=True)
        raise
    return str(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    extract_parser = commands.add_parser("extract", help="safely extract one workbook from a .twbx")
    extract_parser.add_argument("twbx")
    extract_parser.add_argument("run_dir")

    validate_parser = commands.add_parser("validate", help="run local XML checks")
    validate_parser.add_argument("twb")
    validate_parser.add_argument("--json", dest="json_path")

    color_parser = commands.add_parser("replace-run-color", help="replace one run font color in place")
    color_parser.add_argument("twb")
    color_parser.add_argument("source_color")
    color_parser.add_argument("target_color")

    package_parser = commands.add_parser("package", help="package an extracted tree as deterministic .twbx")
    package_parser.add_argument("extracted_dir")
    package_parser.add_argument("edited_twb")
    package_parser.add_argument("original_member")
    package_parser.add_argument("output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "extract":
        print(json.dumps(safe_extract(args.twbx, args.run_dir), indent=2, sort_keys=True))
        return 0
    if args.command == "validate":
        result = validate(args.twb)
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.json_path:
            Path(args.json_path).write_text(payload, encoding="utf-8")
        else:
            print(payload, end="")
        return 0 if result["ok"] else 1
    if args.command == "replace-run-color":
        print(json.dumps({"changed": replace_run_color(args.twb, args.source_color, args.target_color)}))
        return 0
    print(package(args.extracted_dir, args.edited_twb, args.original_member, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
