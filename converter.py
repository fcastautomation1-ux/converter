import os
from applovin_parser import parse_applovin_payload
from html_processor import process_html
from zip_exporter import create_google_ads_zip

def convert(html_file, js_file=None):
    """
    Converts an AppLovin playable ad package into a Google Ads compliant package.
    """
    output_dir = "google_ads_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse payload and capture any extracted asset folders
    parse_result = parse_applovin_payload(html_file, js_file)
    if isinstance(parse_result, tuple):
        extracted_html, extracted_folder = parse_result
    else:
        extracted_html = parse_result
        extracted_folder = None
        
    # Process HTML, inject clickTag and exit handlers
    final_html = process_html(extracted_html, output_dir)
    
    # Export final ZIP containing index.html AND all unpacked game folders/assets
    zip_path = create_google_ads_zip(final_html, extracted_folder=extracted_folder, output="Google_Ads_Ready.zip")
    
    return final_html
