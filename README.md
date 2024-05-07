# Dual Aggregation Transformer for Image Super-Resolution GUI
This is a graphical user interface for the DAT algorithm, made for our capstone project.

## Contents
1. [Dependencies](#Datasets)
2. [Instructions](#Models)
   1. [Installing Manually](#installing-manually)
   2. [Downloading the Executable](#downloading-the-executable)
3. [Notes](#notes)
4. [Acknowledgments](#acknowledgements)

## Dependencies
- Python 3.12
- NVIDIA GPU (strongly recommended)

## Instructions
The application can be either installed manually and run through Python, or run using a pre-built executable file for Windows (coming soon).

### Installing Manually
1. Use the [pip](https://pip.pypa.io/en/stable/) package manager to install the required packages. We recommend doing this in a virtual environment.
    ```bash
    git clone https://github.com/wulufu/GUI-for-Dual-Aggregation-Transformer
    pip install -r requirements.txt
    ```
2. Download the pre-trained [models](https://drive.google.com/drive/folders/1iBdf_-LVZuz_PAbFtuxSKd_11RL1YKxM?usp=drive_link) and place them in the `models` folder.
3. Navigate to the top-level directory and run the main script ([main.py](main.py)).
   ```bash
   python main.py
   ```

### Downloading the Executable
Coming soon...

## Notes
To use the satellite image portion of the application, you must provide your own Google Maps API key. You can create a Google Cloud account and generate your own API key [here](https://developers.google.com/maps/).

## Acknowledgements

- This code uses [DAT](https://github.com/zhengchen1999/DAT) as its algorithm for upscaling images.
- Our capstone project was supervised by [Professor Xin Li](https://www.linkedin.com/in/xin-li-709766b).
