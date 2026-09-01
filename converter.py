import os
from embedded_zip_extractor import extract_embedded_zip
from applovin_parser import parse_applovin_payload
from html_processor import process_html
from zip_exporter import export_google_ads_zip

def convert(html_file, js_file=None):
    """
    Converts an AppLovin playable ad (HTML and optional separate JS loader) 
    into a Google Ads compliant package.
    """
    output_dir = "google_ads_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # If a separate JS file is provided, parse both; otherwise process HTML directly
    if js_file:
        extracted_html = parse_applovin_payload(html_file, js_file)
    else:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            extracted_html = f.read()
            
    # Process HTML, inject ExitApi/clickTag, and save assets
    final_html = process_html(extracted_html, output_dir)
    
    # Export final Google Ads ready ZIP package
    export_google_ads_zip(output_dir, final_html)
    
    return final_html
