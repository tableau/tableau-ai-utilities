import tempfile
import unittest
import zipfile
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from workbook_tools import package, replace_run_color, safe_extract, validate


VALID_TWB = """<?xml version='1.0' encoding='utf-8'?>
<workbook><actions/><worksheets><worksheet name='Sheet 1'><run fontcolor='#000000'>Text</run></worksheet></worksheets></workbook>
"""


class WorkbookToolsTests(unittest.TestCase):
    def test_existing_temporary_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory,'extracted')
            root.mkdir()
            source = root/'book.twb'
            source.write_text(VALID_TWB)
            output = Path(directory,'out.twbx')
            temporary = Path(directory,'out.twbx.tmp')
            temporary.write_text('other run')
            with self.assertRaises(FileExistsError):
                package(str(root),str(source),'book.twb',str(output))
            self.assertEqual(temporary.read_text(),'other run')
            self.assertFalse(output.exists())

    def test_comments_and_processing_instructions_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            twb = Path(directory, 'comment.twb')
            twb.write_text('<workbook><!-- note --><?test ok?><worksheets/></workbook>')
            self.assertTrue(validate(str(twb))['ok'])

    def test_wrong_root_and_unknown_namespace_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            twb = Path(directory, 'bad.twb')
            for xml in ('<other><worksheets/></other>', '<workbook xmlns="urn:unknown"><worksheets/></workbook>'):
                twb.write_text(xml)
                self.assertFalse(validate(str(twb))['ok'])

    def test_duplicate_case_and_file_directory_conflicts_rejected_before_writes(self):
        pairs = [('Data/a.txt','data/A.txt'), ('data','data/a.txt')]
        for first, second in pairs:
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory,'bad.twbx')
                run = Path(directory,'run')
                with zipfile.ZipFile(source,'w') as archive:
                    archive.writestr('book.twb', VALID_TWB)
                    archive.writestr(first,'first')
                    archive.writestr(second,'second')
                with self.assertRaises(ValueError):
                    safe_extract(str(source),str(run))
                self.assertFalse(run.exists())

    def test_package_replaces_only_archive_member_not_extracted_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory, 'extracted')
            root.mkdir()
            member = root/'book.twb'
            member.write_text(VALID_TWB)
            edited = Path(directory,'edited.twb')
            edited.write_text(VALID_TWB.replace('#000000','#ffffff'))
            output = Path(directory,'out.twbx')
            package(str(root),str(edited),'book.twb',str(output))
            self.assertEqual(member.read_text(),VALID_TWB)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.read('book.twb'),edited.read_bytes())

    def test_validate_and_replace_color(self):
        with tempfile.TemporaryDirectory() as directory:
            twb = Path(directory, "book.twb")
            twb.write_text(VALID_TWB, encoding="utf-8")
            self.assertTrue(validate(str(twb))["ok"])
            self.assertEqual(replace_run_color(str(twb), "#000000", "#E6E6E6"), 1)
            self.assertIn("#E6E6E6", twb.read_text(encoding="utf-8"))

    def test_validate_rejects_forbidden_format(self):
        with tempfile.TemporaryDirectory() as directory:
            twb = Path(directory, "book.twb")
            twb.write_text("<workbook><worksheets/><format attr='font-color'/></workbook>", encoding="utf-8")
            self.assertFalse(validate(str(twb))["ok"])

    def test_extract_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory, "unsafe.twbx")
            with zipfile.ZipFile(archive, "w") as package_file:
                package_file.writestr("../escape.twb", VALID_TWB)
            with self.assertRaisesRegex(ValueError, "unsafe archive member"):
                safe_extract(str(archive), str(Path(directory, "run")))

    def test_extract_and_deterministic_package(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory, "input.twbx")
            with zipfile.ZipFile(archive, "w") as package_file:
                package_file.writestr("Workbook/book.twb", VALID_TWB)
                package_file.writestr("Data/data.txt", "preserve me")
            result = safe_extract(str(archive), str(Path(directory, "run")))
            output = Path(directory, "output.twbx")
            package(result["extracted_dir"], result["working_twb"], result["original_member"], str(output))
            with zipfile.ZipFile(output) as package_file:
                self.assertEqual(package_file.read("Data/data.txt"), b"preserve me")
                self.assertIn(b"worksheets", package_file.read("Workbook/book.twb"))

    def test_package_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory, "extracted")
            root.mkdir()
            member = root / "book.twb"
            member.write_text(VALID_TWB, encoding="utf-8")
            edited = Path(directory, "edited.twb")
            edited.write_text(VALID_TWB, encoding="utf-8")
            output = Path(directory, "existing.twbx")
            output.write_bytes(b"keep")
            with self.assertRaisesRegex(FileExistsError, "output already exists"):
                package(str(root), str(edited), "book.twb", str(output))
            self.assertEqual(output.read_bytes(), b"keep")


if __name__ == "__main__":
    unittest.main()
