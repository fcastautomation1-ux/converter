import zipfile
import os
import shutil
from PIL import Image

def validate_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except Exception:
        return False

def create_google_ads_zip(
        html_content,
        extracted_folder=None,
        output="Google_Ads_Ready.zip"
):
    temp_folder = "google_ads_output"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder, exist_ok=True)

    # 1. Copy all extracted game asset folders (assets, cocos-js, src, etc.)
    if extracted_folder and os.path.exists(extracted_folder):
        for item in os.listdir(extracted_folder):
            if item.lower() == "index.html":
                continue  # We will write index.html fresh with our injected exit handlers
            
            source = os.path.join(extracted_folder, item)
            destination = os.path.join(temp_folder, item)
            
            if os.path.abspath(source) == os.path.abspath(destination):
                continue

            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(source, destination)

    # 2. Write the processed index.html at the root
    index_path = os.path.join(temp_folder, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. Create final Google Ads compliant ZIP
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                file_path = os.path.join(root, file)

                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    if not validate_image(file_path):
                        continue

                archive_path = os.path.relpath(file_path, temp_folder)
                zipf.write(file_path, archive_path)

    return output

def export_google_ads_zip(output_dir, final_html, zip_filename="Google_Ads_Ready.zip"):
    return create_google_ads_zip(final_html, extracted_folder=output_dir, output=zip_filename)
