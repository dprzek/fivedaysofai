import re
from typing import Any, Dict, List, Union


class PIIRedactor:
    """Enterprise PII (Personally Identifiable Information) redaction utility.
    
    Masks sensitive information such as emails, authorization tokens, API keys, 
    and credit cards from logs, trace attributes, and memory state.
    """
    
    EMAIL_PATTERN = re.compile(r'([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    BEARER_TOKEN_PATTERN = re.compile(r'(?i)(bearer\s+[a-zA-Z0-9_\-\.]{10,})')
    API_KEY_PATTERN = re.compile(r'(?i)(AIza[0-9A-Za-z-_]{20,}|key-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,})')
    PHONE_PATTERN = re.compile(r'(\+?[0-9]{1,3}?[-.\s]?\(?[0-9]{2,3}?\)?[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{4})')

    
    @classmethod
    def mask_email(cls, match: re.Match) -> str:
        user, domain = match.group(1), match.group(2)
        masked_user = user[0] + "***" if len(user) > 1 else "***"
        return f"{masked_user}@{domain}"
    
    @classmethod
    def redact_text(cls, text: str) -> str:
        """Redacts sensitive PII from a plain text string."""
        if not isinstance(text, str):
            return text
        
        redacted = cls.EMAIL_PATTERN.sub(cls.mask_email, text)
        redacted = cls.BEARER_TOKEN_PATTERN.sub("[REDACTED_BEARER_TOKEN]", redacted)
        redacted = cls.API_KEY_PATTERN.sub("[REDACTED_API_KEY]", redacted)
        return redacted
    
    @classmethod
    def redact_dict(cls, data: Union[Dict[str, Any], List[Any], Any]) -> Any:
        """Recursively sanitizes dictionary, list, or primitive data to remove PII."""
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                if any(sensitive in k.lower() for sensitive in ["token", "secret", "password", "api_key", "credential"]):
                    sanitized[k] = "[REDACTED_SECRET]"
                elif k.lower() in ["contact_email", "email"]:
                    sanitized[k] = cls.redact_text(str(v)) if isinstance(v, str) else "[REDACTED_EMAIL]"
                else:
                    sanitized[k] = cls.redact_dict(v)
            return sanitized
        elif isinstance(data, list):
            return [cls.redact_dict(item) for item in data]
        elif isinstance(data, str):
            return cls.redact_text(data)
        return data


redactor = PIIRedactor()
