import re
from typing import List, Optional

from app.utils.validators import validate_domain, normalize_domain


class ExcelService:
    @staticmethod
    def read_excel(file_path: str) -> List[str]:
        import openpyxl

        domains = []
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)

        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if cell and isinstance(cell, str):
                        cell = cell.strip()
                        if cell and validate_domain(cell):
                            domains.append(cell)

        wb.close()
        return domains

    @staticmethod
    def validate_domains(domains: List[str]) -> tuple:
        valid = []
        invalid = []
        for domain in domains:
            normalized = normalize_domain(domain)
            if normalized and validate_domain(normalized):
                valid.append(normalized)
            else:
                invalid.append(domain)
        return valid, invalid

    @staticmethod
    def extract_domains_from_text(text: str) -> List[str]:
        domains = []
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line and validate_domain(line):
                domains.append(line)
        return domains
