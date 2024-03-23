import platform
import sys
import subprocess

import eel
import googlemaps

API_KEY = "AIzaSyAz7DIMRFMREUS1oea5JnwxDck_veuDqWI"


@eel.expose
def execute_enhance(enhance_level):
    subprocess.run(["python", "basicsr/test.py", "-opt", enhance_level])
    eel.finishEnhance()


@eel.expose
def getImage(center, zoom, size=(640, 640), scale=2):
    client = googlemaps.Client(API_KEY)
    map = client.static_map(size, center, zoom, scale, "png", "satellite")
    
    with open("datasets/single/img.png", "wb") as file:
        for chunk in map:
            if chunk:
                file.write(chunk)

    eel.enhanceImage()


if __name__ == '__main__':
    eel.init("web")

    try:
        eel.start("layout.html", mode="chrome")
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start("layout.html", mode='edge')
        else:
            raise
