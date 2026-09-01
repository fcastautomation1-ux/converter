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
    Parses AppLovin inputs. Ensures extracted_html is actual HTML code 
    and extracted_folder points to the unpacked game assets directory.
    """
    extracted_html = None
    extracted_folder = None

    # 1. Get HTML content from JS file if provided, otherwise read the uploaded HTML file
    if js_file:
        with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
            js_content = f.read()
        extracted_html = extract_applovin_payload(js_content)

    if not extracted_html:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            extracted_html = f.read()

    # 2. Extract embedded assets/folders safely without breaking HTML content
    try:
        res = extract_embedded_zip(html_file)
        if isinstance(res, tuple):
            html_res, folder_res = res
            if html_res and ("<html" in html_res.lower() or "<doctype" in html_res.lower() or "<script" in html_res.lower()):
                extracted_html = html_res
            if folder_res and os.path.isdir(folder_res):
                extracted_folder = folder_res
        elif isinstance(res, str) and os.path.isdir(res):
            extracted_folder = res
            # Check if an index.html exists inside the extracted folder
            idx_path = os.path.join(res, "index.html")
            if os.path.exists(idx_path):
                with open(idx_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if content and len(content.strip()) > 100:
                        extracted_html = content
        elif isinstance(res, str) and ("<html" in res.lower() or "<doctype" in res.lower()):
            extracted_html = res
    except Exception as e:
        print("Extraction notice:", e)

    return extracted_html, extracted_folder
