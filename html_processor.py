import os
from bs4 import BeautifulSoup

def replace_external_script(html, playable_html):
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
    if playable_html:
        final_html = replace_external_script(html_content, playable_html)
    else:
        final_html = html_content

    soup = BeautifulSoup(final_html, 'html.parser')
    
    head = soup.find('head')
    if not head:
        head = soup.new_tag('head')
        soup.insert(0, head)

    # 1. Inject Google Ads Exit API script
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

    # 2. Inject standard clickTag and ExitApi integration script
    exit_script = soup.new_tag('script')
    exit_script.string = """
    // Google Ads required clickTag
    var clickTag = "https://www.google.com";

    window.open = function(url) {
        if (typeof ExitApi !== 'undefined' && ExitApi.exit) {
            ExitApi.exit();
        } else if (typeof Enabler !== 'undefined' && Enabler.exit) {
            Enabler.exit('BackgroundExit');
        } else {
            window.location.href = window.clickTag || url;
        }
    };

    document.addEventListener('click', function(e) {
        // Intercept clicks to ensure Google Ads exit triggers correctly
        if (typeof ExitApi !== 'undefined' && ExitApi.exit) {
            // Let ExitApi handle interaction if available
        }
    }, true);
    """
    head.append(exit_script)

    output_html_path = os.path.join(output_dir, "index.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
        
    return str(soup)
