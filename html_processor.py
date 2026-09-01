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

    # Automatically remove unauthorized external scripts/links/iframes that trigger 4th-party call violations
    allowed_domains = ['fonts.googleapis.com', 'fonts.gstatic.com', 'ajax.googleapis.com', 'google.com', 'gstatic.com']
    for tag in soup.find_all(['script', 'link', 'iframe']):
        attr = 'src' if tag.name in ['script', 'iframe'] else 'href'
        url = tag.get(attr, '')
        if url.startswith(('http://', 'https://', '//')):
            if not any(domain in url for domain in allowed_domains):
                tag.decompose() # Safely remove the external 4th-party dependency

    # Inject standard Google Ads clickTag and local exit handler
    exit_script = soup.new_tag('script')
    exit_script.string = """
    // Google Ads required global clickTag variable
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
    """
    head.append(exit_script)

    output_html_path = os.path.join(output_dir, "index.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
        
    return str(soup)
