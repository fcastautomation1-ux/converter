import re


def extract_applovin_payload(js_content):

    start = js_content.find(
        'al_renderHtml({"html":"'
    )


    if start == -1:
        return None


    start += len(
        'al_renderHtml({"html":"'
    )


    end = js_content.find(
        '"})',
        start
    )


    if end == -1:
        return None


    payload = js_content[start:end]


    # Decode escaped characters safely
    payload = (
        payload
        .replace('\\"', '"')
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t")
        .replace("\\/", "/")
    )


    return payload