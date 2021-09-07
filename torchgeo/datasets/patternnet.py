# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""PatternNet dataset."""

import os
from typing import Callable, Dict, Optional

import torch
from torch import Tensor
from torchvision.datasets import ImageFolder
from torchvision.transforms import PILToTensor

from .geo import VisionDataset
from .utils import download_and_extract_archive


class PatternNet(VisionDataset, ImageFolder):  # type: ignore[misc]
    """PatternNet dataset.

    The `PatternNet <https://sites.google.com/view/zhouwx/dataset>`_
    dataset is a dataset for remote sensing scene classification and image retrieval.

    Dataset features:
    * 30,400 images with 6-50 cm per pixel resolution (256x256 px)
    * three spectral bands - RGB
    * 38 scene classes, 800 images per class

    Dataset format:
    * images are three-channel jpgs

    Dataset classes:
    0. airplane
    1. baseball_field
    2. basketball_court
    3. beach
    4. bridge
    5. cemetery
    6. chaparral
    7. christmas_tree_farm
    8. closed_road
    9. coastal_mansion
    10. crosswalk
    11. dense_residential
    12. ferry_terminal
    13. football_field
    14. forest
    15. freeway
    16. golf_course
    17. harbor
    18. intersection
    19. mobile_home_park
    20. nursing_home
    21. oil_gas_field
    22. oil_well
    23. overpass
    24. parking_lot
    25. parking_space
    26. railway
    27. river
    28. runway
    29. runway_marking
    30. shipping_yard
    31. solar_panel
    32. sparse_residential
    33. storage_tank
    34. swimming_pool
    35. tennis_court
    36. transformer_station
    37. wastewater_treatment_plant

    If you use this dataset in your research, please cite the following paper:
    * https://www.sciencedirect.com/science/article/abs/pii/S0924271618300042
    """

    url = "https://drive.google.com/file/d/127lxXYqzO6Bd0yZhvEbgIfz95HaEnr9K"
    md5 = "96d54b3224c5350a98d55d5a7e6984ad"
    filename = "PatternNet.zip"
    files = ["images"]

    def __init__(
        self,
        root: str = "data",
        transforms: Optional[Callable[[Tensor], Tensor]] = None,
        download: bool = False,
        checksum: bool = False,
    ) -> None:
        """Initialize a new PatternNet dataset instance.

        Args:
            root: root directory where dataset can be found
            transforms: a function/transform that takes input sample and its target as
                entry and returns a transformed version
            download: if True, download dataset and store it in the root directory
            checksum: if True, check the MD5 of the downloaded files (may be slow)

        Raises:
            RuntimeError: if ``download=False`` and data is not found, or checksums
                don't match
        """
        self.root = root
        self.checksum = checksum

        if download:
            self._download()

        if not self._check_integrity():
            raise RuntimeError(
                "Dataset not found or corrupted. "
                + "You can use download=True to download it"
            )

        super().__init__(
            root=os.path.join(root, "images"),
            transform=PILToTensor(),
            target_transform=torch.tensor,  # type: ignore[attr-defined]
        )

        # Must be set after calling super().__init__()
        self.transforms = transforms

    def __getitem__(self, index: int) -> Dict[str, Tensor]:
        """Return an index within the dataset.

        Args:
            index: index to return

        Returns:
            data and label at that index
        """
        image, label = ImageFolder.__getitem__(self, index)

        if self.transforms is not None:
            image = self.transforms(image)

        sample = {"image": image, "label": label}
        return sample

    def __len__(self) -> int:
        """Return the number of data points in the dataset.

        Returns:
            length of the dataset
        """
        return len(self.imgs)

    def _check_integrity(self) -> bool:
        """Checks the integrity of the dataset structure.

        Returns:
            True if the dataset directories and split files are found, else False
        """
        for filename in self.files:
            filepath = os.path.join(self.root, filename)
            if not os.path.exists(filepath):
                return False
        return True

    def _download(self) -> None:
        """Download the dataset and extract it.

        Raises:
            AssertionError: if the checksum of split.py does not match
        """
        if self._check_integrity():
            print("Files already downloaded and verified")
            return

        download_and_extract_archive(
            self.url,
            self.root,
            filename=self.filename,
            md5=self.md5 if self.checksum else None,
        )