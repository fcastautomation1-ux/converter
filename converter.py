import os

from applovin_parser import extract_applovin_payload
from html_processor import replace_external_script
from google_validator import validate_google_ads
from zip_exporter import create_google_ads_zip
from embedded_zip_extractor import extract_embedded_zip


def safe_inline_script_text(text):

    text = text.replace(
        "</script",
        "<\\/script"
    )

    text = text.replace(
        "<!--",
        "<\\!--"
    )

    text = text.replace(
        "\u2028",
        "\\u2028"
    )

    text = text.replace(
        "\u2029",
        "\\u2029"
    )

    return text


def wrap_cc_adapter(extracted_folder):

    adapter_path = os.path.join(
        extracted_folder,
        "@src",
        "cc.adapter.js"
    )


    if not os.path.exists(adapter_path):

        print(
            "Warning: cc.adapter.js not found:",
            adapter_path
        )

        return


    with open(
        adapter_path,
        "r",
        encoding="utf-8"
    ) as f:

        adapter_code = f.read()


    # Wrapping cc.adapter.js protects its top-level const/let names
    if not adapter_code.lstrip().startswith("(function"):

        adapter_code = (
            "(function () {\n"
            + adapter_code
            + "\n})();\n"
        )


        with open(
            adapter_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                adapter_code
            )


def read_embedded_resources(extracted_folder):

    import json

    resources = {}


    for root, dirs, files in os.walk(extracted_folder):

        for file in files:

            if file == "__res":
                continue


            full_path = os.path.join(
                root,
                file
            )


            relative_path = os.path.relpath(
                full_path,
                extracted_folder
            ).replace("\\", "/")


            try:

                with open(
                    full_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    resources[relative_path] = f.read()


            except Exception:

                # binary files
                try:

                    with open(
                        full_path,
                        "rb"
                    ) as f:

                        resources[relative_path] = (
                            "data:application/octet-stream;base64,"
                            +
                            __import__("base64")
                            .b64encode(f.read())
                            .decode()
                        )

                except Exception:

                    pass


    # keep original __res too
    res_path = os.path.join(
        extracted_folder,
        "__res"
    )


    if os.path.exists(res_path):

        try:

            with open(
                res_path,
                "r",
                encoding="utf-8"
            ) as f:

                resources.update(
                    json.loads(
                        f.read()
                    )
                )

        except Exception:
            pass


    print(
        "Total embedded resources:",
        len(resources)
    )


    return safe_inline_script_text(
        json.dumps(resources)
    )

def build_clean_cocos_html(res_content):

    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="ad.size" content="width=320,height=480">
    <title>Playable Ad</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
    >

    <style>
        html,
        body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #000000;
        }

        #GameDiv {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }

        #GameCanvas {
            width: 100%;
            height: 100%;
            display: block;
            outline: none;
            touch-action: none;
        }
    </style>

    <!-- Google Ads Official Exit API Script -->
    <script type="text/javascript" src="https://tpc.googlesyndication.com/pagead/gadgets/html5/api/exitapi.js"></script>

<script type="text/javascript">
    window.clickTag = "https://www.google.com";

    // 1. Intercept standard window.open (Catches 90% of direct game exits)
    var originalWindowOpen = window.open;
    window.open = function(url, target, features) {
        if (typeof ExitApi !== "undefined") {
            ExitApi.exit();
        } else {
            originalWindowOpen(window.clickTag, "_blank");
        }
    };

    // 2. Setup standard exit function to funnel everything through our interceptor
    window.exitAd = function () {
        window.open(window.clickTag, "_blank"); 
    };

    // 3. Mock MRAID (Catches ad-network exits)
    window.mraid = window.mraid || {
        addEventListener: function () {},
        removeEventListener: function () {},
        isViewable: function () { return true; },
        getState: function () { return "default"; },
        open: function (url) { window.exitAd(); },
        close: function () {}
    };

    // 4. Mock Cocos super_html (Catches Cocos-specific exits)
    window.super_html = window.super_html || {};
    window.super_html.download = window.exitAd;

    function _createLocalJSElement(url) {
        var script = document.createElement("script");
        script.src = url;
        script.async = true;
        return script;
    }

    window._createLocalJSElement = _createLocalJSElement;

    function super_log(message) {
        console.log("[super-html] " + message);
    }

    window.super_log = window.super_log || super_log;

    function super_eval(url) {
        var resources = window.__res || {};
        var key = url;
        var code = resources[key];

        if (!code) {
            for (var candidate in resources) {
                if (
                    url.indexOf(candidate) !== -1
                    && url.indexOf(candidate) + candidate.length === url.length
                ) {
                    key = candidate;
                    code = resources[candidate];
                    break;
                }
            }
        }

        if (!code) {
            console.error("super_eval missing resource", url);
            return;
        }

        code = String(code);

        // Forcefully override location changes just in case they used window.location.href
        code = code.replace(/window\\.location\\.href\\s*=\\s*[^;]+;/gi, "window.exitAd();");
        code = code.replace(/location\\.href\\s*=\\s*[^;]+;/gi, "window.exitAd();");
        
        // Strip parameters from known exit calls to prevent reference errors
        code = code.replace(/super_html\\.download\\s*\\([^)]*\\)/gi, "window.exitAd()");
        code = code.replace(/window\\.super_html\\.download\\s*\\([^)]*\\)/gi, "window.exitAd()");
        code = code.replace(/mraid\\.open\\s*\\([^)]*\\)/gi, "window.exitAd()");

        eval(code);
        delete resources[key];
    }

    window.super_eval = super_eval;
    </script>

    <script>
        window.__res = """ + res_content + """;
    </script>

    <script src="./@src/polyfills.bundle.js"></script>
    <script src="./@src/system.bundle.js"></script>

    <script type="systemjs-importmap">
    {
        "imports": {
            "cc": "./cocos-js/cc.js"
        }
    }
    </script>

    <script src="./@src/cc.adapter.js"></script>
</head>

<body>
    <div id="GameDiv" cc_exact_fit_screen="true">
        <canvas
            id="GameCanvas"
            oncontextmenu="event.preventDefault()"
            tabindex="99"
        ></canvas>
    </div>

    <script>
        (function () {

            function startPlayable() {

                if (typeof window.super_boot_engine === "function") {

                    window.super_boot_engine();

                    console.log(
                        "COCOS BOOT OK"
                    );

                } else {

                    console.error(
                        "COCOS BOOT FAILED",
                        "super_boot_engine is not available"
                    );
                }
            }


            if (document.readyState === "loading") {

                document.addEventListener(
                    "DOMContentLoaded",
                    startPlayable
                );

            } else {

                startPlayable();
            }

        })();
    </script>
</body>
</html>
"""


def convert(html_file, js_file):

    with open(
        html_file,
        "r",
        encoding="utf-8"
    ) as f:

        html_content = f.read()


    with open(
        js_file,
        "r",
        encoding="utf-8"
    ) as f:

        js_content = f.read()


    playable = extract_applovin_payload(
        js_content
    )


    if not playable:

        raise Exception(
            "AppLovin playable payload not detected"
        )


    temp_html = replace_external_script(
        html_content,
        playable
    )


    extracted_folder, extracted_files = extract_embedded_zip(
        temp_html
    )


    print(
        "Extracted files:",
        len(extracted_files)
    )


    wrap_cc_adapter(
        extracted_folder
    )


    res_content = read_embedded_resources(
        extracted_folder
    )


    final_html = build_clean_cocos_html(
        res_content
    )


    validation = validate_google_ads(
        final_html
    )


    print(
        "\n========== Google Ads Validation =========="
    )


    for key, value in validation.items():

        print(
            f"{key}: {value}"
        )


    print(
        "===========================================\n"
    )


    zip_file = create_google_ads_zip(
        final_html,
        extracted_folder
    )


    print(
        "Created ZIP:",
        zip_file
    )


    print(
        "Conversion completed!"
    )


    return final_html