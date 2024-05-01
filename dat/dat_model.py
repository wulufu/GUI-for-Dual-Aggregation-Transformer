import torch
from copy import deepcopy
from torch.nn.parallel import DataParallel, DistributedDataParallel
from collections import OrderedDict

from dat.dat_arch import DAT
from dat.img_util import tensor2img

MODEL_PATH = "models/DAT_x{}.pth"


class DATModel:
    def __init__(self, scale):
        self.scale = scale
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # define network
        self.net_g = DAT(upscale=self.scale)
        self.net_g = self.model_to_device(self.net_g)

        # load pretrained models
        load_path = MODEL_PATH.format(scale)
        self.load_network(self.net_g, load_path)

    def model_to_device(self, net):
        """Model to device.

        Args:
            net (nn.Module)
        """
        net = net.to(self.device)
        return net

    def load_network(self, net, load_path, strict=True, param_key='params'):
        """Load network.

        Args:
            load_path (str): The path of networks to be loaded.
            net (nn.Module): Network.
            strict (bool): Whether strictly loaded.
            param_key (str): The parameter key of loaded network. If set to
                None, use the root 'path'.
                Default: 'params'.
        """
        net = self.get_bare_model(net)
        load_net = torch.load(load_path,
                              map_location=lambda storage, loc: storage)
        if param_key is not None:
            if param_key not in load_net and 'params' in load_net:
                param_key = 'params'
            load_net = load_net[param_key]
        # remove unnecessary 'module.'
        for k, v in deepcopy(load_net).items():
            if k.startswith('module.'):
                load_net[k[7:]] = v
                load_net.pop(k)
        self._print_different_keys_loading(net, load_net, strict)
        net.load_state_dict(load_net, strict)

    def get_bare_model(self, net):
        """Get bare model, especially under wrapping with
        DistributedDataParallel or DataParallel.
        """
        if isinstance(net, (DataParallel, DistributedDataParallel)):
            net = net.module
        return net

    def _print_different_keys_loading(self, crt_net, load_net, strict=True):
        """Print keys with different name or different size when loading models.

        1. Print keys with different names.
        2. If strict=False, print the same key but with different tensor size.
            It also ignores these keys with different sizes (not load).

        Args:
            crt_net (torch model): Current network.
            load_net (dict): Loaded network.
            strict (bool): Whether strictly loaded. Default: True.
        """
        crt_net = self.get_bare_model(crt_net)
        crt_net = crt_net.state_dict()
        crt_net_keys = set(crt_net.keys())
        load_net_keys = set(load_net.keys())

        # check the size for the same keys
        if not strict:
            common_keys = crt_net_keys & load_net_keys
            for k in common_keys:
                if crt_net[k].size() != load_net[k].size():
                    load_net[k + '.ignore'] = load_net.pop(k)

    def validation(self, dataloader):
        """Validation function.

        Args:
            dataloader (torch.utils.data.DataLoader): Validation dataloader.
        """
        val_data = next(iter(dataloader))
        self.feed_data(val_data)
        self.test()

        visuals = self.get_current_visuals()
        sr_img = tensor2img([visuals['result']])

        # tentative for out of GPU memory
        del self.lq
        del self.output
        torch.cuda.empty_cache()

        return sr_img

    def feed_data(self, data):
        self.lq = data.to(self.device)

    def get_current_visuals(self):
        out_dict = OrderedDict()
        out_dict['lq'] = self.lq.detach().cpu()
        out_dict['result'] = self.output.detach().cpu()
        return out_dict

    def test(self):
        _, C, h, w = self.lq.size()
        split_token_h = h // 200 + 1  # number of horizontal cut sections
        split_token_w = w // 200 + 1  # number of vertical cut sections

        patch_size_tmp_h = split_token_h
        patch_size_tmp_w = split_token_w

        # padding
        mod_pad_h, mod_pad_w = 0, 0
        if h % patch_size_tmp_h != 0:
            mod_pad_h = patch_size_tmp_h - h % patch_size_tmp_h
        if w % patch_size_tmp_w != 0:
            mod_pad_w = patch_size_tmp_w - w % patch_size_tmp_w

        img = self.lq
        img = torch.cat([img, torch.flip(img, [2])], 2)[:, :, :h + mod_pad_h,
              :]
        img = torch.cat([img, torch.flip(img, [3])], 3)[:, :, :,
              :w + mod_pad_w]

        _, _, H, W = img.size()
        split_h = H // split_token_h  # height of each partition
        split_w = W // split_token_w  # width of each partition

        # overlapping
        shave_h = 16
        shave_w = 16
        scale = self.scale
        ral = H // split_h
        row = W // split_w
        slices = []  # list of partition borders
        for i in range(ral):
            for j in range(row):
                if i == 0 and i == ral - 1:
                    top = slice(i * split_h, (i + 1) * split_h)
                elif i == 0:
                    top = slice(i * split_h, (i + 1) * split_h + shave_h)
                elif i == ral - 1:
                    top = slice(i * split_h - shave_h, (i + 1) * split_h)
                else:
                    top = slice(i * split_h - shave_h,
                                (i + 1) * split_h + shave_h)
                if j == 0 and j == row - 1:
                    left = slice(j * split_w, (j + 1) * split_w)
                elif j == 0:
                    left = slice(j * split_w, (j + 1) * split_w + shave_w)
                elif j == row - 1:
                    left = slice(j * split_w - shave_w, (j + 1) * split_w)
                else:
                    left = slice(j * split_w - shave_w,
                                 (j + 1) * split_w + shave_w)
                temp = (top, left)
                slices.append(temp)
        img_chops = []  # list of partitions
        for temp in slices:
            top, left = temp
            img_chops.append(img[..., top, left])
        if hasattr(self, 'net_g_ema'):
            self.net_g_ema.eval()
            with torch.no_grad():
                outputs = []
                for chop in img_chops:
                    out = self.net_g_ema(
                        chop)  # image processing of each partition
                    outputs.append(out)
                _img = torch.zeros(1, C, H * scale, W * scale)
                # merge
                for i in range(ral):
                    for j in range(row):
                        top = slice(i * split_h * scale,
                                    (i + 1) * split_h * scale)
                        left = slice(j * split_w * scale,
                                     (j + 1) * split_w * scale)
                        if i == 0:
                            _top = slice(0, split_h * scale)
                        else:
                            _top = slice(shave_h * scale,
                                         (shave_h + split_h) * scale)
                        if j == 0:
                            _left = slice(0, split_w * scale)
                        else:
                            _left = slice(shave_w * scale,
                                          (shave_w + split_w) * scale)
                        _img[..., top, left] = outputs[i * row + j][
                            ..., _top, _left]
                self.output = _img
        else:
            self.net_g.eval()
            with torch.no_grad():
                outputs = []
                for chop in img_chops:
                    out = self.net_g(
                        chop)  # image processing of each partition
                    outputs.append(out)
                _img = torch.zeros(1, C, H * scale, W * scale)
                # merge
                for i in range(ral):
                    for j in range(row):
                        top = slice(i * split_h * scale,
                                    (i + 1) * split_h * scale)
                        left = slice(j * split_w * scale,
                                     (j + 1) * split_w * scale)
                        if i == 0:
                            _top = slice(0, split_h * scale)
                        else:
                            _top = slice(shave_h * scale,
                                         (shave_h + split_h) * scale)
                        if j == 0:
                            _left = slice(0, split_w * scale)
                        else:
                            _left = slice(shave_w * scale,
                                          (shave_w + split_w) * scale)
                        _img[..., top, left] = outputs[i * row + j][
                            ..., _top, _left]
                self.output = _img
            self.net_g.train()
        _, _, h, w = self.output.size()
        self.output = self.output[:, :, 0:h - mod_pad_h * scale,
                      0:w - mod_pad_w * scale]
