"""Supplied MONAI output writer; leaves model and instance decoding upstream."""
from pathlib import Path


class SaveInstanceMask:
    def __init__(self, output_path, keys="pred"):
        self.output_path = output_path
        self.key = keys

    def __call__(self, data):
        import numpy as np
        import tifffile
        mask = data[self.key]
        if hasattr(mask, "detach"):
            mask = mask.detach().cpu().numpy()
        mask = np.asarray(mask)
        if mask.ndim != 2 or not np.issubdtype(mask.dtype, np.integer) or np.any(mask < 0):
            raise ValueError("Expected a 2D nonnegative integer instance mask")
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
        tifffile.imwrite(self.output_path, mask.astype(np.uint32))
        return data
