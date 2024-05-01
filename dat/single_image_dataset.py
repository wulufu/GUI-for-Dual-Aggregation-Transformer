from torch.utils import data

from dat.img_util import imfrombytes, img2tensor


class SingleImageDataset(data.Dataset):
    """Read only lq images in the test phase.

    Read LQ (Low Quality, e.g. LR (Low Resolution), blurry, noisy, etc.).

    Args:
        img_bytes (bytes): Bytes for lq image.
    """

    def __init__(self, img_bytes):
        super(SingleImageDataset, self).__init__()
        self.img_bytes = img_bytes

    def __getitem__(self, index):
        # BGR to RGB, HWC to CHW, numpy to tensor
        img_lq = imfrombytes(self.img_bytes, float32=True)
        img_lq = img2tensor(img_lq, bgr2rgb=True, float32=True)
        return img_lq

    def __len__(self):
        return 1
