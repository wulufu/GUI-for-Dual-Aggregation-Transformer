from torch.utils import data as data

from basicsr.utils import imfrombytes, img2tensor, scandir
from basicsr.utils.registry import DATASET_REGISTRY


@DATASET_REGISTRY.register()
class SingleImageDataset(data.Dataset):
    """Read only lq images in the test phase.

    Read LQ (Low Quality, e.g. LR (Low Resolution), blurry, noisy, etc).

    Args:
        opt (dict): Config for datasets. It contains the following keys:
            dataroot_lq (str): Data root path for lq.
    """

    def __init__(self, opt):
        super(SingleImageDataset, self).__init__()
        self.opt = opt
        self.lq_folder = opt['dataroot_lq']
        self.paths = sorted(list(scandir(self.lq_folder, full_path=True)))

    def __getitem__(self, index):
        # load lq image
        lq_path = self.paths[index]

        with open(lq_path, 'rb') as f:
            img_bytes = f.read()

        img_lq = imfrombytes(img_bytes, float32=True)

        # BGR to RGB, HWC to CHW, numpy to tensor
        img_lq = img2tensor(img_lq, bgr2rgb=True, float32=True)

        return {'lq': img_lq, 'lq_path': lq_path}

    def __len__(self):
        return len(self.paths)
