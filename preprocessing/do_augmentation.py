"""
FILE DESCRIPTION:
This file performs the actual image augmentation. The augmentation is done in a way that's compatible with YOLO5.
The whole process is shown visually in the README.md on github.
"""


import glob
import os
from tqdm import tqdm
import seaborn; seaborn.set_style("darkgrid")
from albumentations import (HueSaturationValue, RandomBrightnessContrast, MultiplicativeNoise, CoarseDropout, Compose)
from helpers import (get_random_image_of_type, get_random_background, place_card_randomly_on_background,
                     unfair_coin_flip, save_all)

if __name__ == "__main__":
    SET_FOLDER_PATH = "?"
    BACKGROUNDS_PATH = "?"
    TRAIN_PATH_IMAGES = "?"
    TRAIN_PATH_LABELS = "?"
    images_per_card_type = 1

    for p in [BACKGROUNDS_PATH, SET_FOLDER_PATH, TRAIN_PATH_IMAGES, TRAIN_PATH_LABELS]:
        assert os.path.exists(p), f"Bad path: {p}"

    background_paths = glob.glob(os.path.join(BACKGROUNDS_PATH, "*"))
    card_types = [path.split('\\')[-1] for path in glob.glob(SET_FOLDER_PATH + "/*")]
    label_map = {card_type: i for i, card_type in enumerate(card_types)}

    augmentations = Compose([
        HueSaturationValue(hue_shift_limit=0.2, sat_shift_limit=0.2, val_shift_limit=0.2, p=0.5),
        RandomBrightnessContrast(brightness_limit=(-0.1, 0.1), contrast_limit=(-0.1, 0.1), p=0.5),
        MultiplicativeNoise(multiplier=[0.9, 1.1], elementwise=True),
        CoarseDropout(max_holes=15, max_width=10, max_height=10, p=0.5)
    ])

    for card_type in tqdm(card_types):
        for i in tqdm(range(images_per_card_type), leave=False):
            card_image = get_random_image_of_type(SET_FOLDER_PATH, card_type)
            background_image = get_random_background(background_paths)
            merged_image, yolo_coord = place_card_randomly_on_background(background_image,
                                                                         card_image,
                                                                         do_rotate=True,
                                                                         do_shear = unfair_coin_flip(0.9),
                                                                         debug=False, 
                                                                         resize_final=False)

            aug_merged_image = augmentations(image=merged_image)['image']
            
            save_all(
                aug_merged_image,
                yolo_coord,
                card_type,
                label_map[card_type],
                str(i),
                TRAIN_PATH_IMAGES,
                TRAIN_PATH_LABELS,
                overwrite=False
            )

