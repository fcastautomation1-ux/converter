import re
import base64
import zipfile
import io
import os


def extract_embedded_zip(
        html_input,
        output_folder="extracted_assets"
):
    """
    Universal extractor that detects direct ZIP files, standard variable patterns,
    or searches for base64 zip signatures (UEsDB) anywhere in the file content.
    """
    os.makedirs(output_folder, exist_ok=True)
    extracted_files = []

    content = ""
    # Check if html_input is a valid file path on disk
    if isinstance(html_input, str) and os.path.exists(html_input):
        try:
            with open(html_input, "rb") as f:
                raw_bytes = f.read()
            # 1. Check if the file itself is a direct binary ZIP archive
            if zipfile.is_zipfile(io.BytesIO(raw_bytes)):
                with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
                    for file in z.namelist():
                        z.extract(file, output_folder)
                        extracted_files.append(file)
                print("Direct ZIP file extracted:", len(extracted_files), "files")
                return output_folder, extracted_files
            content = raw_bytes.decode('utf-8', errors='ignore')
        except Exception:
            content = str(html_input)
    else:
        content = str(html_input)

    # 2. Search for common variable patterns or universal UEsDB base64 zip signatures
    patterns = [
        r'["\'](UEsDB[A-Za-z0-9+/=]+)["\']',
        r'window\.__zip\s*=\s*"([^"]+)"',
        r"window\.__zip\s*=\s*'([^']+)'",
        r'__zip\s*[:=]\s*"([^"]+)"',
        r'data:application/zip;base64,([A-Za-z0-9+/=]+)'
    ]

    zip_data = None
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            zip_data = match.group(1)
            break

    # Fallback: scan for any long base64 string starting with UEsDB
    if not zip_data:
        matches = re.findall(r'(UEsDB[A-Za-z0-9+/=]{100,})', content)
        if matches:
            zip_data = max(matches, key=len)

    if not zip_data:
        print("No embedded ZIP found in content.")
        return output_folder, []

    try:
        zip_data = (
            zip_data
            .replace("\\n", "")
            .replace('\\"', '"')
            .strip()
        )

        decoded = base64.b64decode(zip_data)

        with zipfile.ZipFile(io.BytesIO(decoded)) as z:
            for file in z.namelist():
                z.extract(
                    file,
                    output_folder
                )
                extracted_files.append(
                    file
                )

        print(
            "Embedded ZIP extracted successfully:",
            len(extracted_files),
            "files"
        )

        return output_folder, extracted_files

    except Exception as e:
        print(
            "Embedded ZIP extraction failed:",
            e
        )
        return output_folder, []
