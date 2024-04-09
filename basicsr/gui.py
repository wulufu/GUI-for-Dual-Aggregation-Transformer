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
    file_types = ('Image Files (*.jpg;*.png)',)
    selected_files = window.create_file_dialog(file_types=file_types)

    if selected_files is None:
        return None

    file = selected_files[0]
    file_name = os.path.basename(file)

    clear_image_folder()

    # Use a hard link if possible to save space
    try:
        os.link(file, f"datasets/single/{file_name}")
    except OSError:
        shutil.copy(file, "datasets/single")

    return file_name


def clear_image_folder():
    files = os.scandir("datasets/single")

    for file in files:
        os.remove(file)


if __name__ == '__main__':
    window = webview.create_window(title="DAT Image Enhancer",
                                   url="../web/layout.html",
                                   width=864, height=734, resizable=True)
    window.expose(execute_enhance, get_maps_image, open_file_dialog, clear_image_folder)
    window.events.closing += clear_image_folder
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    webview.start(clear_image_folder, debug=True)
