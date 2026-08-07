import re
import os
from typing import Optional


DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}$"
)


def validate_domain(domain: str) -> bool:
    if not domain or not isinstance(domain, str):
        return False
    domain = domain.strip().lower()
    if not domain or len(domain) > 255:
        return False
    return bool(DOMAIN_REGEX.match(domain))


def normalize_domain(domain: str) -> Optional[str]:
    if not domain or not isinstance(domain, str):
        return None

    domain = domain.strip().lower()

    for prefix in ["http://", "https://"]:
        if domain.startswith(prefix):
            domain = domain[len(prefix):]

    domain = domain.rstrip("/")

    if "/" in domain:
        return None

    if ":" in domain:
        parts = domain.split(":")
        if len(parts) > 2:
            return None
        domain = parts[0]

    if not domain or len(domain) > 255:
        return None

    return domain


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    if not filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions


def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
    try:
        size_bytes = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        return size_bytes <= max_size_bytes
    except OSError:
        return False
