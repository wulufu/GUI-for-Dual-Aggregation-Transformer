import os
import shutil

import webview
import googlemaps
from basicsr import execute
from webview.dom import DOMEventHandler


# Contains methods that can be called from JavaScript
class Api:
    MAPS_API_KEY = "AIzaSyAz7DIMRFMREUS1oea5JnwxDck_veuDqWI"
    FILE_TYPES = ('Image Files (*.jpg;*.png)',)
        
    # Runs DAT with an enhance_level of "x2", "x3", or "x4"
    def execute_enhance(self, enhance_level):
        execute(enhance_level)

    # Gets an image from the Google Maps API and saves it to the image folder.
    def get_maps_image(self, center, zoom, size=(640, 640), scale=2):
        maps_client = googlemaps.Client(Api.MAPS_API_KEY)
        img = maps_client.static_map(size, center, zoom, scale, "png", "satellite")

        clear_image_folder()
    
        with open(f"{IMAGE_FOLDER}/img.png", "wb") as file:
            for chunk in img:
                if chunk:
                    file.write(chunk)

    # Opens File Explorer, allowing the user to choose a single image file,
    # and moves that file to the image folder.
    def open_file_dialog(self):
        selected_files = window.create_file_dialog(file_types=Api.FILE_TYPES)

        if selected_files is None:
            return

        file_path = selected_files[0]
        clear_image_folder()
        get_image_file(file_path)


# Called when the window detects that the user has dropped a file. Determines
# if the file was dropped within a designated zone and ensures that the file
# is an image file, then moves it to the image folder.
def on_drop(event):
    try:
        element_class = event["toElement"]["attributes"]["class"]
    except KeyError:
        return

    if element_class != "fileDropAllowed":
        return

    dragged_files = event["dataTransfer"]["files"]
    num_files = len(dragged_files)

    if num_files == 0:
        return
    elif num_files > 1:
        window.evaluate_js("showTooManyFilesDialog()")
        return

    file_info = dragged_files[0]
    file_type = file_info["type"]

    if file_type != "image/jpeg" and file_type != "image/png":
        window.evaluate_js("showWrongFileTypeDialog()")
        return

    file_path = dragged_files[0]["pywebviewFullPath"]
    clear_image_folder()
    get_image_file(file_path)


# Moves the file at file_path to the image folder used by DAT, then tells
# JavaScript to update its current file with the new file name.
def get_image_file(file_path):
    file_name = os.path.basename(file_path)

    # Use a hard link if possible to save space
    try:
        os.link(file_path, f"{IMAGE_FOLDER}/{file_name}")
    except OSError:
        shutil.copy(file_path, IMAGE_FOLDER)

    window.evaluate_js(f'updateCurrentFile("{file_name}")')


# Removes all files in the image folder so a new image can be the only one.
def clear_image_folder():
    files = os.scandir(IMAGE_FOLDER)

    for file in files:
        os.remove(file)


# Adds event listeners to the window that can't be handled within JavaScript.
def bind_events():
    window.events.loaded += clear_image_folder
    window.events.closed += clear_image_folder
    window.dom.document.events.drop += DOMEventHandler(on_drop, True, True)


if __name__ == '__main__':
    IMAGE_FOLDER = "datasets/single"
    WEB_FOLDER = "../web"
    window = webview.create_window(title="DAT Image Enhancer",
                                   js_api=Api(),
                                   url=f"{WEB_FOLDER}/layout.html")
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    webview.start(bind_events, debug=True)
