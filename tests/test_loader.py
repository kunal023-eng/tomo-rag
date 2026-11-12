from pathlib import Path
import tempfile

from tomo.loader import load_document_text


def test_loads_plain_text_file():
    with tempfile.TemporaryDirectory() as temp_directory:
        text_path = Path(temp_directory) / "sample.txt"
        text_path.write_text("Hello from a plain text file.", encoding="utf-8")
        loaded_text = load_document_text(text_path)
        assert loaded_text == "Hello from a plain text file."


def test_raises_for_unsupported_file_type():
    with tempfile.TemporaryDirectory() as temp_directory:
        unsupported_path = Path(temp_directory) / "sample.rtf"
        unsupported_path.write_text("not a supported file", encoding="utf-8")
        try:
            load_document_text(unsupported_path)
        except ValueError:
            return
        raise AssertionError("Expected ValueError for unsupported file type")


def test_raises_for_missing_file():
    with tempfile.TemporaryDirectory() as temp_directory:
        missing_path = Path(temp_directory) / "does-not-exist.txt"
        try:
            load_document_text(missing_path)
        except FileNotFoundError:
            return
        raise AssertionError("Expected FileNotFoundError for missing file")


def test_raises_for_empty_text_file():
    with tempfile.TemporaryDirectory() as temp_directory:
        empty_path = Path(temp_directory) / "empty.txt"
        empty_path.write_text("   \n\n  ", encoding="utf-8")
        try:
            load_document_text(empty_path)
        except ValueError:
            return
        raise AssertionError("Expected ValueError for empty text file")


def test_loads_docx_file():
    from docx import Document
    with tempfile.TemporaryDirectory() as temp_directory:
        docx_path = Path(temp_directory) / "sample.docx"
        document = Document()
        document.add_paragraph("Hello from a Word document.")
        document.add_paragraph("A second paragraph of text.")
        document.save(docx_path)
        loaded_text = load_document_text(docx_path)
        assert "Hello from a Word document." in loaded_text
        assert "A second paragraph of text." in loaded_text


def test_loads_pptx_file():
    from pptx import Presentation
    with tempfile.TemporaryDirectory() as temp_directory:
        pptx_path = Path(temp_directory) / "sample.pptx"
        presentation = Presentation()
        slide_layout = presentation.slide_layouts[1]
        slide = presentation.slides.add_slide(slide_layout)
        slide.shapes.title.text = "Project Aurora kickoff"
        slide.placeholders[1].text = "Starts on March 3rd."
        presentation.save(pptx_path)
        loaded_text = load_document_text(pptx_path)
        assert "Slide 1" in loaded_text
        assert "Project Aurora kickoff" in loaded_text
        assert "Starts on March 3rd." in loaded_text


def test_raises_for_corrupt_docx_file():
    with tempfile.TemporaryDirectory() as temp_directory:
        corrupt_path = Path(temp_directory) / "corrupt.docx"
        corrupt_path.write_text("this is not a real docx file", encoding="utf-8")
        try:
            load_document_text(corrupt_path)
        except ValueError:
            return
        raise AssertionError("Expected ValueError for corrupt docx file")


def test_loads_markdown_file_as_plain_text():
    with tempfile.TemporaryDirectory() as temp_directory:
        markdown_path = Path(temp_directory) / "notes.md"
        markdown_path.write_text("# Heading\n\nSome markdown body.", encoding="utf-8")
        loaded_text = load_document_text(markdown_path)
        assert "# Heading" in loaded_text
        assert "Some markdown body." in loaded_text


def test_loads_xlsx_file_with_header_labels():
    from openpyxl import Workbook
    with tempfile.TemporaryDirectory() as temp_directory:
        xlsx_path = Path(temp_directory) / "applicants.xlsx"
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Applicants"
        worksheet.append(["Name", "Age", "GPA"])
        worksheet.append(["Kunal", 22, 3.8])
        workbook.save(xlsx_path)
        loaded_text = load_document_text(xlsx_path)
        assert "[Sheet: Applicants]" in loaded_text
        assert "Name: Kunal" in loaded_text
        assert "GPA: 3.8" in loaded_text


def test_raises_for_corrupt_xlsx_file():
    with tempfile.TemporaryDirectory() as temp_directory:
        corrupt_path = Path(temp_directory) / "corrupt.xlsx"
        corrupt_path.write_text("this is not a real xlsx file", encoding="utf-8")
        try:
            load_document_text(corrupt_path)
        except ValueError:
            return
        raise AssertionError("Expected ValueError for corrupt xlsx file")
