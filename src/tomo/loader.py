from pathlib import Path

from pypdf import PdfReader


def load_document_text(document_path):
    path = Path(document_path)
    if not path.exists():
        raise FileNotFoundError(f"No file at {path}")
    file_extension = path.suffix.lower()
    if file_extension == ".pdf":
        extracted_text = read_pdf_text(path)
    elif file_extension == ".txt":
        extracted_text = read_text_file(path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    if not extracted_text.strip():
        raise ValueError(f"No readable text found in {path}")
    return extracted_text


def read_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    page_texts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text is None:
            page_text = ""
        page_texts.append(page_text)
    return "\n".join(page_texts)


def read_text_file(text_path):
    return text_path.read_text(encoding="utf-8")
