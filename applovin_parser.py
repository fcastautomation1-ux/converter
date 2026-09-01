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
    Parses AppLovin inputs. Extracts embedded zip assets and returns (html_content, extracted_folder).
    """
    extracted_folder = None
    extracted_html = None

    if js_file:
        with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
            js_content = f.read()
        extracted_html = extract_applovin_payload(js_content)

    # Always attempt embedded zip extraction on the HTML file to get game assets/folders
    res = extract_embedded_zip(html_file)
    if isinstance(res, tuple):
        extracted_html_res, folder_path = res
        if extracted_html_res:
            extracted_html = extracted_html_res
        if folder_path:
            extracted_folder = folder_path
    elif isinstance(res, str) and os.path.isdir(res):
        extracted_folder = res
        index_p = os.path.join(res, "index.html")
        if os.path.exists(index_p):
            with open(index_p, "r", encoding="utf-8", errors="ignore") as f:
                extracted_html = f.read()
    elif isinstance(res, str):
        extracted_html = res

    if not extracted_html:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            extracted_html = f.read()

    return extracted_html, extracted_folder
