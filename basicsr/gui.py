import os
import shutil
import subprocess

import webview
import googlemaps
from webview.dom import DOMEventHandler

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
        return

    file = selected_files[0]
    clear_image_folder()
    get_image_file(file)


def clear_image_folder():
    files = os.scandir("datasets/single")

    for file in files:
        os.remove(file)


def on_drag(event):
    pass


def on_drop(event):
    element_id = event["toElement"]["attributes"]["id"]

    if element_id != "fileDropZone":
        return

    dragged_files = event["dataTransfer"]["files"]
    num_files = len(dragged_files)

    if num_files == 0:
        return

    file_type = dragged_files[0]["type"]
    print(type(file_type))

    if file_type != "image/jpeg" and file_type != "image/png":
        return

    file = dragged_files[0]["pywebviewFullPath"]
    clear_image_folder()
    get_image_file(file)


def get_image_file(file):
    file_name = os.path.basename(file)

    # Use a hard link if possible to save space
    try:
        os.link(file, f"datasets/single/{file_name}")
    except OSError:
        shutil.copy(file, "datasets/single")

    window.evaluate_js(f'updateCurrentFile("{file_name}")')


def bind_events():
    window.events.loaded += clear_image_folder
    window.events.closed += clear_image_folder
    window.dom.document.events.dragenter += DOMEventHandler(on_drag, True, True)
    window.dom.document.events.dragstart += DOMEventHandler(on_drag, True, True)
    window.dom.document.events.dragover += DOMEventHandler(on_drag, True, True)
    window.dom.document.events.drop += DOMEventHandler(on_drop, True, True)


if __name__ == '__main__':
    window = webview.create_window(title="DAT Image Enhancer",
                                   url="../web/layout.html",
                                   width=864, height=734, resizable=True)
    window.expose(execute_enhance, get_maps_image, open_file_dialog, clear_image_folder)
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    webview.start(bind_events, debug=True)
