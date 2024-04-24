# Dual Aggregation Transformer for Image Super-Resolution

## Dependencies

- Python 3.8
- PyTorch 1.8.0
- NVIDIA GPU + [CUDA](https://developer.nvidia.com/cuda-downloads)

```bash
# Clone the github repo and go to the default directory 'DAT'.
git clone https://github.com/zhengchen1999/DAT.git
conda create -n DAT python=3.8
conda activate DAT
pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio===0.8.0 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt
python setup.py develop
```

## Acknowledgements

This code is built on  [BasicSR](https://github.com/XPixelGroup/BasicSR).
