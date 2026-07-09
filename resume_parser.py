# from PyPDF2 import PdfReader

# def extract_text(pdf_file):
#     reader = PdfReader(pdf_file)
#     text = ""

#     for page in reader.pages:
#         text += page.extract_text()

#     return text
from PyPDF2 import PdfReader

def extract_text(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        return text

    except Exception as e:
        return f"Error reading PDF: {e}"