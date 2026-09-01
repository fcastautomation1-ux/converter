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
    Parses AppLovin inputs. Extracts embedded zip assets and returns 
    (target_html, extracted_folder).
    """
    html_content = ""
    
    if js_file:
        with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
            js_content = f.read()
        html_content = extract_applovin_payload(js_content)

    if not html_content and os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()

    # Pass html_file path to the universal extractor
    input_target = html_file if os.path.exists(html_file) else html_content
    extracted_folder, extracted_files = extract_embedded_zip(input_target)

    # Use index.html from the extracted assets if available
    target_html = html_content
    index_path = os.path.join(extracted_folder, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_html_content = f.read()
            if extracted_html_content and len(extracted_html_content.strip()) > 50:
                target_html = extracted_html_content

    return target_html, extracted_folder
