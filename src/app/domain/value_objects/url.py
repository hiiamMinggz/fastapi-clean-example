from dataclasses import dataclass
from app.domain.value_objects.base import ValueObject
from app.domain.exceptions.base import DomainFieldError
import re

@dataclass(frozen=True, slots=True)
class StreamUrl(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise DomainFieldError("Stream URL cannot be empty")
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(self.value):
            raise DomainFieldError("Invalid stream URL format")