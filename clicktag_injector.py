def inject_clicktag(html):

    clicktag_script = r"""

<script>

var clickTag = "https://example.com";


function exitAd(){

    if(clickTag){

        window.open(
            clickTag,
            "_blank"
        );

    }

}


</script>

"""

    return html.replace(
        "</head>",
        clicktag_script + "</head>"
    )