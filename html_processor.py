import os
from bs4 import BeautifulSoup

def replace_external_script(html, playable_html):
    """
    If AppLovin provides complete HTML, use it directly.
    Otherwise, replace external script tags in the template with the parsed payload.
    """
    if "<!DOCTYPE html>" in playable_html:
        return playable_html

    soup = BeautifulSoup(html, "html.parser")

    for script in soup.find_all("script"):
        if script.get("src"):
            script.replace_with(
                BeautifulSoup(
                    playable_html,
                    "html.parser"
                )
            )

    return str(soup)

def process_html(html_content, output_dir, playable_html=None):
    """
    Wrapper to handle both direct HTML processing and external script replacement,
    saving the final result as index.html.
    """
    if playable_html:
        final_html = replace_external_script(html_content, playable_html)
    else:
        final_html = html_content

    soup = BeautifulSoup(final_html, 'html.parser')
    
    # Ensure Google Ads Studio API script is included
    head = soup.find('head')
    if head:
        api_script_exists = any(
            'studiodapi.js' in str(script.get('src', '')) 
            for script in head.find_all('script')
        )
        if not api_script_exists:
            google_api_tag = soup.new_tag(
                'script', 
                src='https://www.google.com/doubleclick/studio/studiodapi.js'
            )
            head.insert(0, google_api_tag)

    # Save processed index.html to output directory
    output_html_path = os.path.join(output_dir, "index.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
        
    return str(soup)
