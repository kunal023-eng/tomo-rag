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
        unsupported_path = Path(temp_directory) / "sample.docx"
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
