import re

def is_valid_url(url: str) -> bool:
    """بررسی معتبر بودن لینک"""
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(pattern, url) is not None

def truncate_text(text: str, max_len: int = 100) -> str:
    """کوتاه کردن متن"""
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."