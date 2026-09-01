from PIL import Image
import os

folder = "Google_Ads_Check"

for root, dirs, files in os.walk(folder):

    for f in files:

        if f.lower().endswith((".png", ".jpg", ".jpeg")):

            path = os.path.join(root, f)

            try:
                img = Image.open(path)
                print("OK:", path, img.format, img.size)

                img.verify()

            except Exception as e:
                print("BAD IMAGE:", path)
                print(e)