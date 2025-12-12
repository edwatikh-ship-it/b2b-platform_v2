import io
import logging
from typing import Optional
from pypdf import PdfReader
from docx import Document
from openpyxl import load_workbook

logger = logging.getLogger(__name__)


class DocumentParser:
    """Парсер документов (PDF, DOCX, XLSX)"""

    def parse_pdf_bytes(self, data: bytes) -> str:
        """Парсим PDF из bytes"""
        try:
            pdf_file = io.BytesIO(data)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF parse error: {e}")
            return ""

    def parse_docx_bytes(self, data: bytes) -> str:
        """Парсим DOCX из bytes"""
        try:
            docx_file = io.BytesIO(data)
            doc = Document(docx_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            
            # Также парсим таблицы
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join([cell.text for cell in row.cells])
                    text += "\n" + row_text
            
            return text
        except Exception as e:
            logger.error(f"DOCX parse error: {e}")
            return ""

    def parse_xlsx_bytes(self, data: bytes) -> str:
        """Парсим XLSX из bytes"""
        try:
            xlsx_file = io.BytesIO(data)
            wb = load_workbook(xlsx_file)
            ws = wb.active
            
            text = ""
            for row in ws.iter_rows(values_only=True):
                row_text = " | ".join([str(cell) if cell else "" for cell in row])
                text += row_text + "\n"
            
            return text
        except Exception as e:
            logger.error(f"XLSX parse error: {e}")
            return ""

    def parse_file(self, file_path: str, file_ext: str) -> str:
        """Парсим файл по пути"""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            
            if file_ext.lower() == ".pdf":
                return self.parse_pdf_bytes(data)
            elif file_ext.lower() == ".docx":
                return self.parse_docx_bytes(data)
            elif file_ext.lower() == ".xlsx":
                return self.parse_xlsx_bytes(data)
            else:
                return ""
        except Exception as e:
            logger.error(f"File parse error: {e}")
            return ""
