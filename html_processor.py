from bs4 import BeautifulSoup


def replace_external_script(
        html,
        playable_html
):

    # If AppLovin provides complete HTML,
    # use it directly

    if "<!DOCTYPE html>" in playable_html:
        return playable_html


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    for script in soup.find_all("script"):

        if script.get("src"):
            script.replace_with(
                BeautifulSoup(
                    playable_html,
                    "html.parser"
                )
            )


    return str(soup)