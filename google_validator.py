import os

def validate_google_ads(html_content):
    """
    Validates whether the HTML content complies with Google Ads requirements 
    (detects clickTag, ExitApi, and checks package size).
    """
    html_lower = html_content.lower()
    
    has_clickTag = "clicktag" in html_lower
    has_exitAd = "exitapi" in html_lower or "enabler" in html_lower or "window.open" in html_lower
    
    html_size_bytes = len(html_content.encode('utf-8'))
    html_size_kb = round(html_size_bytes / 1024, 2)
    
    status = "PASS" if (has_clickTag or has_exitAd) else "FAIL: exitAd / clickTag missing"
    
    return {
        "status": status,
        "clickTag": has_clickTag,
        "exitAd": has_exitAd,
        "html_size_kb": html_size_kb
    }
