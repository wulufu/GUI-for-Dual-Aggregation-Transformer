from os import path
from pickle import UnpicklingError

import webview
from webview.dom import DOMEventHandler
import googlemaps
from googlemaps.exceptions import ApiError, TransportError, Timeout
from torch.utils.data import DataLoader

from dat import SingleImageDataset, DATModel, imwrite


# Contains methods that can be called from JavaScript
class Api:
    # Gets the image at the file path provided and enhances it using DAT.
    def enhance_image_file(self, file_path, enhance_level):
        file_path = file_path.strip('\"')

        if not path.isabs(file_path):
            show_error_dialog("An absolute file path must be provided.")
            return

        if not path.exists(file_path):
            show_error_dialog("The file at that location does not exist.")
            return

        if path.isdir(file_path):
            show_error_dialog("The file path must not point to a directory.")
            return

        try:
            with open(file_path, 'rb') as f:
                img_bytes = f.read()
        except OSError:
            show_error_dialog("The file could not be accessed.")
            return

        self._enhance_image(img_bytes, enhance_level)

    # Gets an image from the Google Maps API and enhances it using DAT.
    def enhance_maps_image(self, api_key, center, zoom, enhance_level):
        show_loading_dialog("Getting image from Google Maps...")

        try:
            client = googlemaps.Client(api_key, timeout=10)
            img = client.static_map(size=(640, 640), center=center, zoom=zoom,
                                    scale=2, maptype="satellite")
        except (ApiError, ValueError):
            window.evaluate_js("gm_authFailure()")
            return
        except (TransportError, Timeout, ConnectionError):
            show_error_dialog("The satellite image could not be retrieved.")
            return

        img_bytes = bytes(int.from_bytes(chunk) for chunk in img)
        self._enhance_image(img_bytes, enhance_level)

    # Uses DAT to upscale an image stored as bytes by the scale provided.
    def _enhance_image(self, img_bytes, scale):
        show_loading_dialog("Enhancing image...")

        dataset = SingleImageDataset(img_bytes)
        dataloader = DataLoader(dataset)

        try:
            model = DATModel(scale)
        except (FileNotFoundError, UnpicklingError):
            show_error_dialog("Required DAT models are missing or corrupted.")
            return

        try:
            self.enhanced_image = model.validation(dataloader)
        except AttributeError:
            show_error_dialog("The file is in an unsupported format.")
            return

        show_save_dialog("Success! The image has been enhanced.")

    # Opens File Explorer, allowing the user to choose a single image file,
    # then updates the file path displayed in the GUI.
    def choose_image_file(self):
        file_types = ("Image Files (*.jpg;*.jpeg;*.png;*.webp;*.bmp)",
                      "JPEG (*.jpg;*.jpeg;*.jpe;*.jif;*.jfif)", "PNG (*.png)",
                      "WEBP (*.webp)", "BMP (*.bmp)")
        selected_files = window.create_file_dialog(webview.OPEN_DIALOG,
                                                   file_types=file_types)

        if selected_files is None:
            return

        file_path = selected_files[0]
        file_path = file_path.replace("\\", r"\\")
        window.evaluate_js(f'updateCurrentFile("{file_path}")')

    # Opens File Explorer, allowing the user to save an enhanced image.
    def save_enhanced_image(self, file_path):
        file_name = path.basename(file_path)
        save_name = path.splitext(file_name)[0] + ".png"

        save_location = window.create_file_dialog(webview.SAVE_DIALOG,
                                                  save_filename=save_name,
                                                  file_types=("PNG (*.png)",))

        if save_location is None:
            return

        try:
            imwrite(self.enhanced_image, save_location, auto_mkdir=True)
        except OSError:
            show_error_dialog("Failed to save file to the selected location.")
            return


# Displays a loading dialog that can't be closed by the user.
def show_loading_dialog(message):
    window.evaluate_js(f'showDialog("loading", "{message}")')


# Displays a dialog with an error message and a button to close it.
def show_error_dialog(message):
    window.evaluate_js(f'showDialog("popup", "{message}")')


# Displays a dialog that allows the user to save an enhanced image.
def show_save_dialog(message):
    window.evaluate_js(f'showDialog("save", "{message}")')


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
        show_error_dialog("Only one file may be selected at a time.")
        return

    file_info = dragged_files[0]
    file_type = file_info["type"]

    if file_type not in ["image/jpeg", "image/png", "image/webp", "image/bmp"]:
        show_error_dialog("That file type is not supported.")
        return

    file_path = dragged_files[0]["pywebviewFullPath"]
    file_path = file_path.replace("\\", r"\\")
    window.evaluate_js(f'updateCurrentFile("{file_path}")')


# Adds event listeners to the window that can't be handled within JavaScript.
def bind_events():
    window.dom.document.events.drop += DOMEventHandler(on_drop, True, True)


if __name__ == '__main__':
    window = webview.create_window(title="DAT Image Enhancer", js_api=Api(),
                                   url="gui/layout.html", width=832,
                                   height=736, resizable=False,
                                   background_color="#1d262c")
    webview.start(bind_events)
