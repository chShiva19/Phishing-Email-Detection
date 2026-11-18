
import re
import ipaddress
from urllib.parse import urlparse


URL_PATTERN = re.compile(
    r"""https?://[^\s<>"']+|www\.[^\s<>"']+""",
    re.IGNORECASE
)

SHORTENED_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co",
    "is.gd", "cutt.ly", "rebrand.ly"
}

INDICATOR_RULES = {
    "Urgent language": [
        r"\burgent\b",
        r"\bimmediately\b",
        r"\bact now\b",
        r"\bexpires today\b"
    ],
    "Credential request": [
        r"\bpassword\b",
        r"\bverify your account\b",
        r"\blog in\b",
        r"\blogin details\b",
        r"\breset your password\b"
    ],
    "Account threat": [
        r"\baccount will be suspended\b",
        r"\baccount will be closed\b",
        r"\bpermanently blocked\b",
        r"\baccess will be terminated\b"
    ],
    "Financial request": [
        r"\bbank details\b",
        r"\bcredit card\b",
        r"\bpayment information\b",
        r"\bwire transfer\b",
        r"\bsend money\b"
    ]
}


def extract_urls(email_text):
    urls = URL_PATTERN.findall(email_text)

    result = []

    for url in urls:
        url = url.rstrip(".,;:!?)\"]}")

        if url.lower().startswith("www."):
            url = "http://" + url

        if url not in result:
            result.append(url)

    return result


def inspect_url(url):
    findings = []

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return ["Unable to identify URL hostname"]

        hostname = hostname.lower()

        if hostname in SHORTENED_DOMAINS:
            findings.append("Uses a URL shortening service")

        if hostname.startswith("xn--") or ".xn--" in hostname:
            findings.append("Contains a punycode domain")

        try:
            ipaddress.ip_address(hostname)
            findings.append("Uses an IP address instead of a domain")
        except ValueError:
            pass

        if parsed.username or parsed.password:
            findings.append("Contains embedded user information")

        if parsed.scheme.lower() != "https":
            findings.append("Does not use HTTPS")

    except Exception:
        findings.append("Unable to parse URL")

    return findings


def analyze_email(email_text):
    text = email_text.lower()

    indicators = []

    for name, patterns in INDICATOR_RULES.items():

        if any(re.search(pattern, text) for pattern in patterns):
            indicators.append({
                "indicator": name,
                "description": (
                    f"Email contains language associated with {name.lower()}."
                )
            })

    urls = extract_urls(email_text)

    url_findings = []

    for url in urls:
        url_findings.append({
            "url": url,
            "findings": inspect_url(url)
        })

    return {
        "indicators": indicators,
        "urls": urls,
        "url_findings": url_findings
    }
