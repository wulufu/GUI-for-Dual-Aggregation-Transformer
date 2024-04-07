import os
import shutil
import subprocess

import webview
import googlemaps

API_KEY = "AIzaSyAz7DIMRFMREUS1oea5JnwxDck_veuDqWI"


def execute_enhance(enhance_level):
    subprocess.run(["python", "basicsr/test.py", "-opt",
                    f"options/Test/test_single_{enhance_level}.yml"])


def get_maps_image(center, zoom, size=(640, 640), scale=2):
    client = googlemaps.Client(API_KEY)
    map = client.static_map(size, center, zoom, scale, "png", "satellite")
    
    with open("datasets/single/img.png", "wb") as file:
        for chunk in map:
            if chunk:
                file.write(chunk)


def open_file_dialog():
    file_types = ['Image Files (*.jpg;*.png)']
    files = window.create_file_dialog(allow_multiple=True, file_types=file_types)
    file_names = []

    if files is not None:
        for file in files:
            shutil.copy(file, "datasets/single")
            file_names.append(os.path.basename(file))

    return file_names


def remove_file(file_name):
    os.remove(f"datasets/single/{file_name}")


if __name__ == '__main__':
    window = webview.create_window(title="DAT Image Enhancer",
                                   url="../web/layout.html",
                                   width=864, height=734, resizable=False)
    window.expose(execute_enhance, get_maps_image, open_file_dialog, remove_file)
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    webview.start(debug=True)
