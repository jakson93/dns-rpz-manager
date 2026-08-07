import os
from datetime import datetime
from typing import List, Optional


class RPZService:
    SOA_TEMPLATE = """$TTL 86400
@ IN SOA localhost. localhost. (
    {serial}
    3600
    900
    2419200
    7200
)
    IN NS localhost.
"""

    def generate_serial(self) -> str:
        return datetime.utcnow().strftime("%Y%m%d") + "01"

    def generate_rpz_file(self, domains: List[str], output_path: str) -> str:
        serial = self.generate_serial()
        existing_serial = self._read_existing_serial(output_path)
        if existing_serial:
            date_part = existing_serial[:8]
            counter_part = existing_serial[8:]
            today = datetime.utcnow().strftime("%Y%m%d")
            if date_part == today:
                new_counter = str(int(counter_part) + 1).zfill(2)
                serial = today + new_counter
            else:
                serial = today + "01"

        content = self.SOA_TEMPLATE.format(serial=serial)

        for domain in sorted(domains):
            domain = domain.strip().lower()
            if domain:
                content += f"{domain} CNAME .\n"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            f.write(content)

        return output_path

    def _read_existing_serial(self, file_path: str) -> Optional[str]:
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    for line in f:
                        if "SOA" in line:
                            for _ in range(5):
                                next_line = next(f, None)
                                if next_line:
                                    next_line = next_line.strip()
                                    if next_line.endswith(")") is False and next_line.isdigit():
                                        return next_line
        except Exception:
            pass
        return None

    def parse_rpz_file(self, file_path: str) -> List[str]:
        domains = []
        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("$") and not line.startswith("@") and not line.startswith(";"):
                        parts = line.split()
                        if len(parts) >= 2 and parts[1] == "CNAME":
                            domains.append(parts[0])
        except FileNotFoundError:
            pass
        return domains
