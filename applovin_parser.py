import os
from embedded_zip_extractor import extract_embedded_zip

def extract_applovin_payload(js_content):
    start = js_content.find('al_renderHtml({"html":"')
    if start == -1:
        return None

    start += len('al_renderHtml({"html":"')
    end = js_content.find('"})', start)

    if end == -1:
        return None

    payload = js_content[start:end]

    # Decode escaped characters safely
    payload = (
        payload
        .replace('\\"', '"')
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t")
        .replace("\\/", "/")
    )

    return payload

def parse_applovin_payload(html_file, js_file=None):
    """
    Parses AppLovin inputs. If a separate JS loader file is provided, 
    extracts the playable HTML payload using your original al_renderHtml logic.
    Otherwise, reads the HTML file directly.
    """
    if js_file:
        with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
            js_content = f.read()
        extracted = extract_applovin_payload(js_content)
        if extracted:
            return extracted

    # Fallback to direct file reading or embedded zip extraction
    extracted_html = extract_embedded_zip(html_file)
    if extracted_html:
        return extracted_html

    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    return content
