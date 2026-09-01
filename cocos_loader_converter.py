import re


def convert_cocos_loader(html):

    # Fix Cocos import-map path
    html = html.replace(
        "./../cocos-js/cc.js",
        "./cocos-js/cc.js"
    )

    # Remove old fake System loader if it exists
    html = re.sub(
        r'<script>\s*\(function\(global\).*?</script>',
        '',
        html,
        flags=re.DOTALL
    )

    # Remove old placeholders if they exist
    old_placeholders = [
        "/* COCOS_SYSTEM_JS_PLACEHOLDER */",
        "/* COCOS_INDEX_JS_PLACEHOLDER */",
        "<!-- COCOS_RUNTIME_PLACEHOLDER -->",
        "<!-- COCOS_BOOT_PLACEHOLDER -->"
    ]


    for placeholder in old_placeholders:

        html = html.replace(
            placeholder,
            ""
        )

    # Remove any external script tag that directly loads index.js
    # We will start Cocos using System.import("./index.js") instead.
    html = re.sub(
        r'<script[^>]*src=["\'](?:\./)?index\.js["\'][^>]*></script>',
        '',
        html,
        flags=re.IGNORECASE
    )

    # Runtime placeholder.
    # converter.py will replace this with inline:
    # polyfills.bundle.js
    # system.bundle.js
    # cc.adapter.js
    runtime_placeholder = """

<!-- COCOS_RUNTIME_PLACEHOLDER -->

"""

    # Boot Cocos through SystemJS.
    # This keeps index.js as a proper Cocos SystemJS module.
    boot_placeholder = """

<script>
(function () {

    function bootCocos() {

        if (!window.System || !System.import) {

            console.error(
                "COCOS BOOT FAILED",
                "SystemJS is not available"
            );

            return;
        }


        System.import("./index.js")
            .then(function () {

                console.log(
                    "COCOS BOOT OK"
                );

            })
            .catch(function (error) {

                console.error(
                    "COCOS BOOT FAILED",
                    error
                );

            });
    }


    bootCocos();

})();
</script>

"""

    # Put Cocos runtime before import map
    if "systemjs-importmap" in html:

        html = html.replace(
            '<script type="systemjs-importmap">',
            runtime_placeholder
            + '\n<script type="systemjs-importmap">',
            1
        )

    else:

        # Fallback import map if missing
        fallback_import_map = """
<script type="systemjs-importmap">
{
    "imports": {
        "cc": "./cocos-js/cc.js"
    }
}
</script>
"""

        if "</head>" in html:

            html = html.replace(
                "</head>",
                runtime_placeholder
                + fallback_import_map
                + "\n</head>",
                1
            )

        else:

            html = (
                runtime_placeholder
                + fallback_import_map
                + html
            )

    # Put boot script before body close
    if "</body>" in html:

        html = html.replace(
            "</body>",
            boot_placeholder
            + "\n</body>",
            1
        )

    else:

        html += "\n" + boot_placeholder

    return html