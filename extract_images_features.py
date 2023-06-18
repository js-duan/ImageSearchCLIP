#!/usr/bin/env python3
import os
import pickle
import logging
import argparse
import numpy as np
from tqdm import tqdm
from datetime import datetime

from utils import *
import config as cfg
from models.clip_model import get_model


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--eval", action="store_true")
    # args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    root_path = cfg.IMAGE_PATH
    feature_path = cfg.IMAGE_FEATURE_PATH

    """ model """
    model = get_model(cfg)

    """ traverse image path """
    images = traverse_path(root_path, extensions=cfg.IMAGE_EXTENSIONS)
    extracted_images = traverse_path(
        os.path.join(root_path, feature_path), extensions={".pkl"}, complete=False
    )
    extracted_images = set(extracted_images)
    logging.info(
        f"number of images: {len(images)}; number of extracted images: {len(extracted_images)}."
    )

    """ extract feature for all image """
    for image in tqdm(images, total=len(images), desc="extract image feature"):
        # skip extracted image
        feature_file = image.split("/")[-1].split(".")[0] + ".pkl"
        if feature_file in extracted_images:
            continue
        extension = os.path.splitext(image)[1].lower()[1:]

        # extract image feature
        image_feature, image_size = model.image_feature(image)
        if image_feature is None or image_size is None:
            logging.info(f"skip [{image}], file not exist.")
            continue

        # save info
        stat = os.stat(image)
        image_st_mtime = datetime.fromtimestamp(stat.st_mtime).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        info = {
            "filename": image,
            "extension": extension,
            "height": image_size[1],
            "width": image_size[0],
            "filesize": stat.st_size,
            "date": image_st_mtime,
            "feature": image_feature,
        }

        save_path = os.path.dirname(image).replace(
            root_path, os.path.join(root_path, feature_path)
        )
        os.makedirs(save_path, exist_ok=True)
        with open(os.path.join(save_path, feature_file), "wb") as fw:
            pickle.dump(info, fw)


if __name__ == "__main__":
    main()
