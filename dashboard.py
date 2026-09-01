import os
import streamlit as st
import tempfile
from converter import convert
from google_validator import validate_google_ads

st.set_page_config(
    page_title="AppLovin to Google Ads Converter",
    page_icon="⚡",
    layout="centered"
)

st.title("🚀 AppLovin to Google Ads Playable Converter")
st.markdown("Upload any AppLovin ad's source files (`.html` and `.js` loader) to instantly convert, validate, and package them into a Google Ads-ready ZIP file.")

with st.container():
    st.subheader("1. Upload Source Files")
    col1, col2 = st.columns(2)
    
    with col1:
        html_upload = st.file_uploader("Upload AppLovin HTML File", type=["html"])
    with col2:
        js_upload = st.file_uploader("Upload AppLovin JS Loader File", type=["js", "txt"])

if st.button("Convert & Package for Google Ads", type="primary", use_container_width=True):
    if html_upload and js_upload:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save uploaded files temporarily
            html_path = os.path.join(tmpdir, html_upload.name)
            with open(html_path, "wb") as f:
                f.write(html_upload.getbuffer())
                
            js_path = os.path.join(tmpdir, js_upload.name)
            with open(js_path, "wb") as f:
                f.write(js_upload.getbuffer())
            
            with st.spinner("Processing payload, injecting Exit API, and validating structure..."):
                try:
                    # Run your existing conversion pipeline
                    final_html = convert(html_path, js_path)
                    
                    # Run validation check to display metrics
                    validation = validate_google_ads(final_html)
                    
                    st.success("Conversion Completed Successfully!")
                    
                    # Display Validation Metrics
                    st.markdown("### 📊 Validation Report")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Status", validation.get("status", "Unknown"))
                    m2.metric("ClickTag Detected", str(validation.get("clickTag")))
                    m3.metric("ExitAd Detected", str(validation.get("exitAd")))
                    
                    st.text(f"Final Package Size: {validation.get('html_size_kb')} KB")
                    
                    # Target the generated zip file for download
                    zip_path = "Google_Ads_Ready.zip"
                    if os.path.exists(zip_path):
                        with open(zip_path, "rb") as fp:
                            st.download_button(
                                label="📥 Download Google_Ads_Ready.zip",
                                data=fp,
                                file_name="Google_Ads_Ready.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                    else:
                        st.error("Error: Output ZIP file was not generated.")
                        
                except Exception as e:
                    st.error(f"An error occurred during conversion: {e}")
    else:
                    st.warning("Please upload both the HTML and JS files before proceeding.")