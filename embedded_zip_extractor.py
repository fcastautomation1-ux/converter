import re
import base64
import zipfile
import io
import os


def extract_embedded_zip(
        html,
        output_folder="extracted_assets"
):

    patterns = [
        r'window\.__zip\s*=\s*"([^"]+)"',
        r"window\.__zip\s*=\s*'([^']+)'",
        r'__zip\s*[:=]\s*"([^"]+)"'
    ]


    zip_data = None


    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            re.DOTALL
        )

        if match:
            zip_data = match.group(1)
            break


    if not zip_data:

        print(
            "No embedded ZIP found"
        )

        return output_folder, []



    try:

        zip_data = (
            zip_data
            .replace("\\n", "")
            .replace('\\"', '"')
        )


        decoded = base64.b64decode(
            zip_data
        )


        os.makedirs(
            output_folder,
            exist_ok=True
        )


        extracted_files = []


        with zipfile.ZipFile(
            io.BytesIO(decoded)
        ) as z:


            for file in z.namelist():

                z.extract(
                    file,
                    output_folder
                )

                extracted_files.append(
                    file
                )


        print(
            "Embedded ZIP extracted:",
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