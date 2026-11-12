from datetime import datetime
from pathlib import Path
from zipfile import BadZipFile

import openpyxl
from docx import Document
from openpyxl.utils.exceptions import InvalidFileException
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
    elif file_extension == ".xlsx":
        extracted_text = read_xlsx_text(path)
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


def read_xlsx_text(xlsx_path):
    try:
        workbook = openpyxl.load_workbook(xlsx_path, data_only=True)
    except (BadZipFile, InvalidFileException) as read_error:
        raise ValueError(f"Could not read xlsx file: {read_error}")
    sheet_texts = []
    for worksheet in workbook.worksheets:
        sheet_name = worksheet.title
        row_lines = extract_xlsx_row_lines(worksheet, sheet_name)
        if len(row_lines) == 0:
            continue
        sheet_texts.append("\n".join(row_lines))
    return "\n\n".join(sheet_texts)


def extract_xlsx_row_lines(worksheet, sheet_name):
    row_lines = []
    header_values = None
    for row in worksheet.iter_rows(values_only=True):
        row_strings = [cell_value_to_text(cell_value) for cell_value in row]
        if not any(row_strings):
            continue
        if header_values is None:
            header_values = row_strings
            continue
        row_parts = build_labelled_row_parts(header_values, row_strings)
        if len(row_parts) == 0:
            continue
        row_line = f"[Sheet: {sheet_name}] " + " | ".join(row_parts)
        row_lines.append(row_line)
    return row_lines


def build_labelled_row_parts(header_values, row_strings):
    row_parts = []
    for column_index, cell_text in enumerate(row_strings):
        if cell_text == "":
            continue
        if column_index < len(header_values) and header_values[column_index] != "":
            column_label = header_values[column_index]
            row_parts.append(f"{column_label}: {cell_text}")
        else:
            row_parts.append(cell_text)
    return row_parts


def cell_value_to_text(cell_value):
    if cell_value is None:
        return ""
    if isinstance(cell_value, datetime):
        return cell_value.date().isoformat()
    return str(cell_value).strip()
