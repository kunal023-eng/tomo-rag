from pathlib import Path
from zipfile import BadZipFile

from docx import Document
from pptx import Presentation
from pypdf import PdfReader


def load_document_text(document_path):
    path = Path(document_path)
    if not path.exists():
        raise FileNotFoundError(f"No file at {path}")
    file_extension = path.suffix.lower()
    if file_extension == ".pdf":
        extracted_text = read_pdf_text(path)
    elif file_extension == ".txt" or file_extension == ".md":
        extracted_text = read_text_file(path)
    elif file_extension == ".docx":
        extracted_text = read_docx_text(path)
    elif file_extension == ".pptx":
        extracted_text = read_pptx_text(path)
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


def read_docx_text(docx_path):
    try:
        document = Document(docx_path)
    except BadZipFile as read_error:
        raise ValueError(f"Could not read docx file: {read_error}")
    paragraph_texts = []
    for paragraph in document.paragraphs:
        paragraph_texts.append(paragraph.text)
    return "\n".join(paragraph_texts)


def read_pptx_text(pptx_path):
    try:
        presentation = Presentation(pptx_path)
    except BadZipFile as read_error:
        raise ValueError(f"Could not read pptx file: {read_error}")
    slide_texts = []
    for slide_number, slide in enumerate(presentation.slides, start=1):
        slide_text_parts = []
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                slide_text_parts.append(paragraph.text)
        if slide.has_notes_slide:
            speaker_notes = slide.notes_slide.notes_text_frame.text
            if speaker_notes.strip():
                slide_text_parts.append("Speaker notes: " + speaker_notes)
        joined_slide_text = "\n".join(slide_text_parts).strip()
        if joined_slide_text == "":
            continue
        slide_texts.append(f"Slide {slide_number}\n{joined_slide_text}")
    return "\n\n".join(slide_texts)
