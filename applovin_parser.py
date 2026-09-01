import os
import re
import requests
from bs4 import BeautifulSoup
from embedded_zip_extractor import extract_embedded_zip

def extract_applovin_payload(js_content):
    # Look for al_renderHtml wrappers
    start = js_content.find('al_renderHtml({"html":"')
    if start == -1:
        start = js_content.find("al_renderHtml({'html':'")
    if start == -1:
        match = re.search(r'al_renderHtml\(\s*\{\s*["\']html["\']\s*:\s*["\'](.*?)["\']\s*\}\s*\)', js_content, re.DOTALL)
        if match:
            return decode_payload(match.group(1))
        return None

    prefix = 'al_renderHtml({"html":"' if 'al_renderHtml({"html":"' in js_content else "al_renderHtml({'html':'"
    start += len(prefix)
    
    end = js_content.find('"})', start)
    if end == -1:
        end = js_content.find("'})", start)
    if end == -1:
        end = js_content.rfind('")')

    if end == -1:
        return None

    payload = js_content[start:end]
    return decode_payload(payload)

def decode_payload(payload):
    return (
        payload
        .replace('\\"', '"')
        .replace("\\'", "'")
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t")
        .replace("\\/", "/")
    )

def parse_applovin_payload(html_file, js_file=None):
    """
    Parses AppLovin inputs. Detects external script references, downloads them,
    and extracts the actual underlying game HTML payload.
    """
    html_content = ""
    
    if js_file:
        with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
            js_content = f.read()
        html_content = extract_applovin_payload(js_content)

    if not html_content and os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            raw_html = f.read()
        
        # Check if raw HTML contains an external AppLovin script URL
        soup = BeautifulSoup(raw_html, "html.parser")
        script_url = None
        for s in soup.find_all("script"):
            src = s.get("src", "")
            if "applovin.com" in src:
                script_url = src
                break
        
        if script_url:
            try:
                print("Fetching external AppLovin script payload from:", script_url)
                resp = requests.get(script_url, timeout=15)
                if resp.status_code == 200:
                    payload = extract_applovin_payload(resp.text)
                    if payload:
                        html_content = payload
            except Exception as e:
                print("Error fetching remote AppLovin script:", e)
        
        if not html_content:
            # Check if payload is directly inside the file content
            payload = extract_applovin_payload(raw_html)
            if payload:
                html_content = payload
            else:
                html_content = raw_html

    # Handle embedded zips if present
    input_target = html_file if os.path.exists(html_file) else html_content
    extracted_folder, extracted_files = extract_embedded_zip(input_target)

    target_html = html_content
    index_path = os.path.join(extracted_folder, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_html_content = f.read()
            if extracted_html_content and len(extracted_html_content.strip()) > 50:
                target_html = extracted_html_content

    return target_html, extracted_folder
