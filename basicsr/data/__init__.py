import importlib
import torch
import torch.utils.data
from copy import deepcopy
from os import path as osp

from basicsr.utils import scandir
from basicsr.utils.registry import DATASET_REGISTRY

__all__ = ['build_dataset', 'build_dataloader']

# automatically scan and import dataset modules for registry
# scan all the files under the data folder with '_dataset' in file names
data_folder = osp.dirname(osp.abspath(__file__))
dataset_filenames = [osp.splitext(osp.basename(v))[0] for v in scandir(data_folder) if v.endswith('_dataset.py')]
# import all the dataset modules
_dataset_modules = [importlib.import_module(f'basicsr.data.{file_name}') for file_name in dataset_filenames]


def build_dataset(dataset_opt):
    """Build dataset from options.

    Args:
        dataset_opt (dict): Configuration for dataset. It must contain:
            name (str): Dataset name.
            type (str): Dataset type.
    """
    dataset_opt = deepcopy(dataset_opt)
    dataset = DATASET_REGISTRY.get(dataset_opt['type'])(dataset_opt)
    return dataset


def build_dataloader(dataset, dataset_opt):
    """Build dataloader.

    Args:
        dataset (torch.utils.data.Dataset): Dataset.
        dataset_opt (dict): Dataset options. It contains the following keys:
            num_worker_per_gpu (int): Number of workers for each GPU.
            batch_size_per_gpu (int): Training batch size for each GPU.
    """
    dataloader_args = dict(dataset=dataset, batch_size=1, shuffle=False, num_workers=0)
    dataloader_args['pin_memory'] = dataset_opt.get('pin_memory', False)
    dataloader_args['persistent_workers'] = dataset_opt.get('persistent_workers', False)

    return torch.utils.data.DataLoader(**dataloader_args)
