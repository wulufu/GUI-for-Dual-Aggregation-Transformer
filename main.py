import os
import shutil

import webview
import googlemaps

from basicsr.data import build_dataloader, build_dataset
from basicsr.models import build_model
from torch.cuda import is_available as cuda_is_available
from webview.dom import DOMEventHandler

MODELS_PATH = "models"
GUI_PATH = "gui"
TEMP_PATH = "temp"
INPUT_PATH = f"{TEMP_PATH}/in"
OUTPUT_PATH = f"{TEMP_PATH}/out"
DEFAULT_IMG_NAME = "img.png"


# Contains methods that can be called from JavaScript
class Api:
    MAP_SIZE = (640, 640)
    MAP_SCALE = 2
    MAP_FILE_TYPE = "png"
    MAP_TYPE = "satellite"
    GMAPS_API_KEY = "AIzaSyAz7DIMRFMREUS1oea5JnwxDck_veuDqWI"
    FILE_TYPES = ("Image Files (*.jpg;*.jpeg;*.png)",)

    options = {
        "model_type": "DATModel", "num_gpu": 1 if cuda_is_available() else 0,
        "dataset": {"type": "SingleImageDataset", "dataroot_lq": INPUT_PATH},
        "network_g": {
            "type": "DAT", "in_chans": 3, "img_size": 64, "img_range": 1,
            "split_size": [8, 32], "depth": [6, 6, 6, 6, 6, 6],
            "embed_dim": 180, "num_heads": [6, 6, 6, 6, 6, 6],
            "expansion_factor": 4, "resi_connection": '1conv'},
        "path": {"visualization": OUTPUT_PATH}
    }

    # Enhances the image in the input folder using the scale provided.
    def enhance_image(self, scale):
        self.options["scale"] = scale
        self.options["network_g"]["upscale"] = scale
        self.options["path"]["pretrain_network_g"] = f"{MODELS_PATH}/DAT_x{scale}.pth"

        # create test dataset and dataloader
        dataset_options = self.options["dataset"]
        test_set = build_dataset(dataset_options)
        test_loader = build_dataloader(test_set, dataset_options)

        # create model
        model = build_model(self.options)
        model.validation(test_loader)

    # Gets an image from the Google Maps API and saves it to the image folder.
    def get_maps_image(self, map_center, map_zoom):
        gmaps_client = googlemaps.Client(self.GMAPS_API_KEY)
        img = gmaps_client.static_map(self.MAP_SIZE, map_center, map_zoom,
                                      self.MAP_SCALE, self.MAP_FILE_TYPE,
                                      self.MAP_TYPE)

        reset_input_folder()

        with open(f"{INPUT_PATH}/{DEFAULT_IMG_NAME}", "wb") as file:
            for chunk in img:
                if chunk:
                    file.write(chunk)

    # Opens File Explorer, allowing the user to choose a single image file.
    def choose_image_file(self):
        selected_files = window.create_file_dialog(webview.OPEN_DIALOG,
                                                   file_types=self.FILE_TYPES)

        if selected_files is None:
            return

        file_path = selected_files[0]
        get_image_file(file_path)

    # Opens File Explorer, allowing the user to save an enhanced image.
    def save_image_file(self, file_name):
        if not file_name:
            file_name = DEFAULT_IMG_NAME

        save_location = window.create_file_dialog(webview.SAVE_DIALOG,
                                                  save_filename=file_name,
                                                  file_types=("Image File (*.png)",))

        if save_location is None:
            return

        shutil.copyfile(f"{OUTPUT_PATH}/{file_name}", save_location)


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

    if file_type not in ["image/jpeg", "image/png"]:
        window.evaluate_js("showWrongFileTypeDialog()")
        return

    file_path = dragged_files[0]["pywebviewFullPath"]
    get_image_file(file_path)


# Moves the file at file_path to the image folder used by DAT, then tells
# JavaScript to update its current file with the new file name.
def get_image_file(file_path):
    file_name = os.path.basename(file_path)
    reset_input_folder()

    # Use a hard link if possible to save space
    try:
        os.link(file_path, f"{INPUT_PATH}/{file_name}")
    except OSError:
        shutil.copy(file_path, INPUT_PATH)

    window.evaluate_js(f'updateCurrentFile("{file_name}")')


# Removes all files in the input folder to prepare for the next input image.
# The input folder will be created if it does not exist.
def reset_input_folder():
    if os.path.exists(INPUT_PATH):
        shutil.rmtree(INPUT_PATH)

    os.makedirs(INPUT_PATH)


# Removes all files in the output folder to prepare for the next output image.
# The output folder will be created if it does not exist.
def reset_output_folder():
    if os.path.exists(INPUT_PATH):
        shutil.rmtree(INPUT_PATH)

    os.makedirs(INPUT_PATH)


# Removes all files in the output folder to prepare for the next output image.
# The output folder will be created if it does not exist.
def reset_image_folders():
    reset_input_folder()
    reset_output_folder()


# Adds event listeners to the window that can't be handled within JavaScript.
def bind_events():
    window.dom.document.events.drop += DOMEventHandler(on_drop, True, True)
    window.events.loaded += reset_image_folders
    window.events.closed += reset_image_folders


if __name__ == '__main__':
    window = webview.create_window(title="DAT Image Enhancer",
                                   js_api=Api(),
                                   url=f"{GUI_PATH}/layout.html",
                                   width=834,
                                   height=735,
                                   resizable=False)
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    webview.start(bind_events, debug=True)
