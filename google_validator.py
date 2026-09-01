import re

def validate_google_ads(html):

    # clickTag check
    clicktag_ok = bool(re.search(r'\bclickTag\b', html))

    # exitAd or ExitApi check
    exitad_ok = bool(re.search(r'\bexitAd\b|ExitApi\.exit', html))

    # Find script src values
    script_sources = re.findall(
        r'<script[^>]+src=["\']([^"\']+)["\']',
        html,
        flags=re.IGNORECASE
    )

    external_scripts = []

    for src in script_sources:
        src_clean = src.strip().lower()
        if (
            src_clean.startswith("http://")
            or src_clean.startswith("https://")
            or src_clean.startswith("//")
        ):
            # ALLOW Google's official exit API because App Campaigns require it
            if "exitapi.js" not in src_clean:
                external_scripts.append(src)

    # Detect AppLovin remote URLs
    applovin_urls = re.findall(
        r'https?://[^"\']*applovin[^"\']*',
        html,
        flags=re.IGNORECASE
    )

    applovin_urls = list(dict.fromkeys(applovin_urls))

    html_size_kb = round(len(html.encode("utf-8")) / 1024, 2)

    status = "PASS"

    if not exitad_ok:
        status = "FAIL: exitAd or ExitApi missing"
    elif external_scripts:
        status = "FAIL: Remote external scripts found"
    elif applovin_urls:
        status = "FAIL: AppLovin URLs found"

    return {
        "clickTag": clicktag_ok,
        "exitAd": exitad_ok,
        "external_scripts": external_scripts,
        "applovin_urls": applovin_urls,
        "html_size_kb": html_size_kb,
        "status": status
    }

if __name__ == "__main__":
    import sys
    import zipfile
    import tempfile
    import os

    if len(sys.argv) < 2:
        print("Usage: python google_validator.py <zip_file>")
        sys.exit(1)

    zip_file = sys.argv[1]

    with tempfile.TemporaryDirectory() as temp:
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(temp)

        html_path = os.path.join(temp, "index.html")

        if not os.path.exists(html_path):
            print("index.html not found in ZIP")
            sys.exit(1)

        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        result = validate_google_ads(html)

        print("\n========== Google Ads Validation ==========")
        for key, value in result.items():
            print(f"{key}: {value}")
        print("==========================================")