def inject_mraid_compatibility(html):

    mraid_mock = r"""
<script>

window.mraid = {

    addEventListener: function(){},

    removeEventListener: function(){},

    isViewable: function(){
        return true;
    },

    getState: function(){
        return "default";
    },

    open: function(url){
        if(url){
            window.open(url, "_blank");
        }
    },

    close: function(){},

    expand: function(){},

    resize: function(){}

};


window.super_log = function(){};


window.super_check_channel = function(){
    return false;
};


window.super_boot_engine = function(){

    if(typeof viewable_start_ads === "function"){
        viewable_start_ads();
    }

};


window.super_open = function(url){

    if(url){
        window.open(url, "_blank");
    }

};

</script>
"""

    return html.replace(
        "<head>",
        "<head>" + mraid_mock
    )