import os
import re
import requests
from bs4 import BeautifulSoup
from embedded_zip_extractor import extract_embedded_zip

def extract_applovin_payload(js_content):
    start = js_content.find('al_renderHtml({"html":"')
    if start == -1:
        return None

    start += len('al_renderHtml({"html":"')
    end = js_content.find('"})', start)

    if end == -1:
        # Fallback search for alternative quote closures
        end = js_content.rfind('")')

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
    Parses AppLovin inputs. If the HTML contains an external AppLovin script URL,
    it downloads it, extracts the payload, and returns the fully inlined HTML.
    """
    html_content = ""
    
    if js_file:
        with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
            js_content = f.read()
        html_content = extract_applovin_payload(js_content)

    if not html_content and os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()

    # Check if HTML contains an external script pointing to AppLovin
    soup = BeautifulSoup(html_content, "html.parser")
    for script in soup.find_all("script"):
        src = script.get("src", "")
        if "applovin.com" in src:
            try:
                print("Fetching external AppLovin payload from:", src)
                response = requests.get(src, timeout=10)
                if response.status_code == 200:
                    extracted_payload = extract_applovin_payload(response.text)
                    if extracted_payload:
                        # Replace the external script tag with the actual inline HTML/game code
                        new_tag = soup.new_tag("script")
                        new_tag.string = extracted_payload
                        script.replace_with(new_tag)
                        html_content = str(soup)
            except Exception as e:
                print("Failed to fetch external AppLovin script:", e)

    # Also run embedded zip extractor for bundled assets
    input_target = html_file if os.path.exists(html_file) else html_content
    extracted_folder, extracted_files = extract_embedded_zip(input_target)

    # Use index.html from extracted folder if available
    target_html = html_content
    index_path = os.path.join(extracted_folder, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_html_content = f.read()
            if extracted_html_content and len(extracted_html_content.strip()) > 50:
                target_html = extracted_html_content

    return target_html, extracted_folder
