import platform
import sys

import eel
from basicsr import execute


@eel.expose
def execute_enhance(enhance_level):
    execute(enhance_level)


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
