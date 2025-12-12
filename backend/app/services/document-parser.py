"""
Document OCR Parser - распознавание текста из PDF, DOCX, XLSX
"""
import logging
from typing import Dict, List, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class DocumentParser:
    """OCR парсер для документов"""
    
    def __init__(self):
        self.confidence = 0.0
        self.raw_text = ""
    
    async def parse_document(self, file_path: str, file_type: str) -> Dict:
        """
        Основной метод парсинга документа
        
        Args:
            file_path: путь к файлу
            file_type: тип файла (pdf, docx, xlsx, txt)
        
        Returns:
            {
                "positions": [...],
                "confidence": 75.5,
                "raw_text": "..."
            }
        """
        try:
            # Определяем расширение если нужно
            if not file_type:
                file_type = Path(file_path).suffix.lstrip(".").lower()
            
            file_type = file_type.lower().strip(".")
            
            # Парсим файл в зависимости от типа
            if file_type == "pdf":
                text = await self._parse_pdf(file_path)
            elif file_type == "docx":
                text = await self._parse_docx(file_path)
            elif file_type == "xlsx":
                text = await self._parse_xlsx(file_path)
            elif file_type == "txt":
                text = await self._parse_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            self.raw_text = text
            
            # Извлекаем позиции из текста
            positions = self._extract_positions(text)
            
            # Рассчитываем confidence
            self.confidence = self._calculate_confidence(positions)
            
            return {
                "positions": positions,
                "confidence": self.confidence,
                "raw_text": text
            }
        
        except Exception as e:
            logger.error(f"Error parsing document: {e}")
            return {
                "positions": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _parse_pdf(self, file_path: str) -> str:
        """Парсим PDF"""
        try:
            from PyPDF2 import PdfReader
            
            text = ""
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.warning("PyPDF2 not installed, returning empty text")
            return ""
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            return ""
    
    async def _parse_docx(self, file_path: str) -> str:
        """Парсим DOCX"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text
        except ImportError:
            logger.warning("python-docx not installed")
            return ""
        except Exception as e:
            logger.error(f"DOCX parsing error: {e}")
            return ""
    
    async def _parse_xlsx(self, file_path: str) -> str:
        """Парсим XLSX"""
        try:
            import openpyxl
            
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            text = ""
            for row in sheet.iter_rows(values_only=True):
                text += " ".join([str(cell) if cell else "" for cell in row]) + "\n"
            return text
        except ImportError:
            logger.warning("openpyxl not installed")
            return ""
        except Exception as e:
            logger.error(f"XLSX parsing error: {e}")
            return ""
    
    async def _parse_txt(self, file_path: str) -> str:
        """Парсим TXT"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"TXT parsing error: {e}")
            return ""
    
    def _extract_positions(self, text: str) -> List[Dict]:
        """
        Извлекаем позиции из текста
        
        Ищем паттерны вроде:
        - "1 Труба жесткая 140 м"
        - "№1 - Позиция: D160 Кол-во: 140м"
        - "1. Название позиции 140 м"
        """
        positions = []
        lines = text.split("\n")
        
        pos_number = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ищем строки с числами (номер + название + количество)
            # Паттерн: ^(\d+)\s+(.+?)\s+(\d+(?:[.,]\d+)?)\s*([а-яA-Zм°%]+)?
            match = re.match(
                r'^(\d+)[\.\s]+(.+?)\s+(\d+(?:[.,]\d+)?)\s*([а-яA-Za-z°%/\s]+)?$',
                line
            )
            
            if match:
                pos_number = int(match.group(1))
                name = match.group(2).strip()
                qty_raw = match.group(3).replace(",", ".")
                unit = match.group(4).strip() if match.group(4) else "шт"
                
                try:
                    qty = float(qty_raw)
                except:
                    qty = qty_raw
                
                positions.append({
                    "pos": pos_number,
                    "name": name,
                    "unit": unit,
                    "qty": qty
                })
        
        return positions
    
    def _calculate_confidence(self, positions: List[Dict]) -> float:
        """Рассчитываем уверенность распознавания (0-100)"""
        if not positions:
            return 0.0
        
        score = 50.0  # Базовый скор
        
        for pos in positions:
            # +10 за наличие количества
            if "qty" in pos and pos["qty"]:
                score += 10
            
            # +10 за наличие единицы
            if "unit" in pos and pos["unit"]:
                score += 10
            
            # +15 за длинное название
            if "name" in pos and len(pos["name"]) > 10:
                score += 15
        
        # Делим на количество позиций, чтобы не превысить 100
        confidence = min(100.0, score / (len(positions) + 1))
        return round(confidence, 1)
