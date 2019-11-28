"""
web utilities
"""
import re
import tldextract


fmt = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    # domain...
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
    r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def validate_url(url):
    return re.match(fmt, url)


def extract_links(text):
    return re.findall(r'(https?://[^\s"\\<>]+)', text)


def page_name(url):
    if url[-1] == '/':
        url = url[:-1]
    name = re.search(r'[^\./]*(?!.*/)', url).group(0)
    return name


def extract_domain(url):
    ext = tldextract.extract(url)
    return ext.domain
