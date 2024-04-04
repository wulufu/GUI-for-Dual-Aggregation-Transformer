import subprocess

import webview
import googlemaps

API_KEY = "AIzaSyAz7DIMRFMREUS1oea5JnwxDck_veuDqWI"


def execute_enhance(enhance_level):
    subprocess.run(["python", "basicsr/test.py", "-opt",
                    f"options/Test/test_single_{enhance_level}.yml"])


def get_image(center, zoom, size=(640, 640), scale=2):
    client = googlemaps.Client(API_KEY)
    map = client.static_map(size, center, zoom, scale, "png", "satellite")
    
    with open("datasets/single/img.png", "wb") as file:
        for chunk in map:
            if chunk:
                file.write(chunk)


if __name__ == '__main__':
    window = webview.create_window(title="DAT Image Enhancer",
                                   url="../web/layout.html",
                                   width=864, height=734, resizable=False)
    window.expose(execute_enhance, get_image)
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    webview.start(debug=True)
