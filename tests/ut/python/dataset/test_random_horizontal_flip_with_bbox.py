# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
Testing the random horizontal flip with bounding boxes op in DE
"""
import numpy as np
import mindspore.log as logger
import mindspore.dataset as ds
import mindspore.dataset.vision.transforms as vision
from util import visualize_with_bounding_boxes, InvalidBBoxType, check_bad_bbox, \
    config_get_set_seed, config_get_set_num_parallel_workers, save_and_check_md5

GENERATE_GOLDEN = False

# updated VOC dataset with correct annotations
DATA_DIR = "../data/dataset/testVOC2012_2"
DATA_DIR_2 = ["../data/dataset/testCOCO/train/",
              "../data/dataset/testCOCO/annotations/train.json"]  # DATA_DIR, ANNOTATION_DIR


def test_random_horizontal_flip_with_bbox_op_c(plot_vis=False):
    """
    Prints images and bboxes side by side with and without RandomHorizontalFlipWithBBox Op applied
    """
    logger.info("test_random_horizontal_flip_with_bbox_op_c")

    # Load dataset
    data_voc1 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)

    data_voc2 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)

    test_op = vision.RandomHorizontalFlipWithBBox(1)

    data_voc2 = data_voc2.map(operations=[test_op], input_columns=["image", "bbox"],
                              output_columns=["image", "bbox"],
                              column_order=["image", "bbox"])

    unaug_samp, aug_samp = [], []

    for unaug, aug in zip(data_voc1.create_dict_iterator(num_epochs=1, output_numpy=True),
                          data_voc2.create_dict_iterator(num_epochs=1, output_numpy=True)):
        unaug_samp.append(unaug)
        aug_samp.append(aug)

    if plot_vis:
        visualize_with_bounding_boxes(unaug_samp, aug_samp)


def test_random_horizontal_flip_with_bbox_op_coco_c(plot_vis=False):
    """
    Prints images and bboxes side by side with and without RandomHorizontalFlipWithBBox Op applied,
    Testing with COCO dataset
    """
    logger.info("test_random_horizontal_flip_with_bbox_op_coco_c")

    dataCoco1 = ds.CocoDataset(DATA_DIR_2[0], annotation_file=DATA_DIR_2[1], task="Detection",
                               decode=True, shuffle=False)

    dataCoco2 = ds.CocoDataset(DATA_DIR_2[0], annotation_file=DATA_DIR_2[1], task="Detection",
                               decode=True, shuffle=False)

    test_op = vision.RandomHorizontalFlipWithBBox(1)

    dataCoco2 = dataCoco2.map(operations=[test_op], input_columns=["image", "bbox"],
                              output_columns=["image", "bbox"],
                              column_order=["image", "bbox"])

    unaug_samp, aug_samp = [], []

    for unaug, aug in zip(dataCoco1.create_dict_iterator(num_epochs=1, output_numpy=True),
                          dataCoco2.create_dict_iterator(num_epochs=1, output_numpy=True)):
        unaug_samp.append(unaug)
        aug_samp.append(aug)

    if plot_vis:
        visualize_with_bounding_boxes(unaug_samp, aug_samp, "bbox")


def test_random_horizontal_flip_with_bbox_valid_rand_c(plot_vis=False):
    """
    Uses a valid non-default input, expect to pass
    Prints images side by side with and without augmentation applied + bboxes to
    compare and test
    """
    logger.info("test_random_horizontal_bbox_valid_rand_c")

    original_seed = config_get_set_seed(1)
    original_num_parallel_workers = config_get_set_num_parallel_workers(1)

    # Load dataset
    data_voc1 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)

    data_voc2 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)

    test_op = vision.RandomHorizontalFlipWithBBox(0.6)

    # map to apply ops
    data_voc2 = data_voc2.map(operations=[test_op], input_columns=["image", "bbox"],
                              output_columns=["image", "bbox"],
                              column_order=["image", "bbox"])

    filename = "random_horizontal_flip_with_bbox_01_c_result.npz"
    save_and_check_md5(data_voc2, filename, generate_golden=GENERATE_GOLDEN)

    unaug_samp, aug_samp = [], []

    for unaug, aug in zip(data_voc1.create_dict_iterator(num_epochs=1, output_numpy=True),
                          data_voc2.create_dict_iterator(num_epochs=1, output_numpy=True)):
        unaug_samp.append(unaug)
        aug_samp.append(aug)

    if plot_vis:
        visualize_with_bounding_boxes(unaug_samp, aug_samp)

    # Restore config setting
    ds.config.set_seed(original_seed)
    ds.config.set_num_parallel_workers(original_num_parallel_workers)


def test_random_horizontal_flip_with_bbox_valid_edge_c(plot_vis=False):
    """
    Test RandomHorizontalFlipWithBBox op (testing with valid edge case, box covering full image).
    Prints images side by side with and without augmentation applied + bboxes to compare and test
    """
    logger.info("test_horizontal_flip_with_bbox_valid_edge_c")

    data_voc1 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)
    data_voc2 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)

    test_op = vision.RandomHorizontalFlipWithBBox(1)

    # map to apply ops
    # Add column for "bbox"
    data_voc1 = data_voc1.map(
        operations=lambda img, bbox: (img, np.array(
            [[0, 0, img.shape[1], img.shape[0], 0, 0, 0]]).astype(np.float32)),
        input_columns=["image", "bbox"],
        output_columns=["image", "bbox"],
        column_order=["image", "bbox"])
    data_voc2 = data_voc2.map(
        operations=lambda img, bbox: (img, np.array(
            [[0, 0, img.shape[1], img.shape[0], 0, 0, 0]]).astype(np.float32)),
        input_columns=["image", "bbox"],
        output_columns=["image", "bbox"],
        column_order=["image", "bbox"])
    data_voc2 = data_voc2.map(operations=[test_op], input_columns=["image", "bbox"],
                              output_columns=["image", "bbox"],
                              column_order=["image", "bbox"])

    unaug_samp, aug_samp = [], []

    for unaug, aug in zip(data_voc1.create_dict_iterator(num_epochs=1, output_numpy=True),
                          data_voc2.create_dict_iterator(num_epochs=1, output_numpy=True)):
        unaug_samp.append(unaug)
        aug_samp.append(aug)

    if plot_vis:
        visualize_with_bounding_boxes(unaug_samp, aug_samp)


def test_random_horizontal_flip_with_bbox_invalid_prob_c():
    """
    Test RandomHorizontalFlipWithBBox op with invalid input probability
    """
    logger.info("test_random_horizontal_bbox_invalid_prob_c")

    data_voc2 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)

    try:
        # Note: Valid range of prob should be [0.0, 1.0]
        test_op = vision.RandomHorizontalFlipWithBBox(1.5)
        # map to apply ops
        data_voc2 = data_voc2.map(operations=[test_op], input_columns=["image", "bbox"],
                                  output_columns=["image", "bbox"],
                                  column_order=["image", "bbox"])  # Add column for "bbox"
    except ValueError as error:
        logger.info("Got an exception in DE: {}".format(str(error)))
        assert "Input prob is not within the required interval of [0.0, 1.0]." in str(
            error)


def test_random_horizontal_flip_with_bbox_invalid_bounds_c():
    """
    Test RandomHorizontalFlipWithBBox op with invalid bounding boxes
    """
    logger.info("test_random_horizontal_bbox_invalid_bounds_c")

    test_op = vision.RandomHorizontalFlipWithBBox(1)

    data_voc2 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)
    check_bad_bbox(data_voc2, test_op, InvalidBBoxType.WidthOverflow,
                   "bounding boxes is out of bounds of the image")
    data_voc2 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)
    check_bad_bbox(data_voc2, test_op, InvalidBBoxType.HeightOverflow,
                   "bounding boxes is out of bounds of the image")
    data_voc2 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)
    check_bad_bbox(data_voc2, test_op,
                   InvalidBBoxType.NegativeXY, "negative value")
    data_voc2 = ds.VOCDataset(DATA_DIR, task="Detection",
                              usage="train", shuffle=False, decode=True)
    check_bad_bbox(data_voc2, test_op, InvalidBBoxType.WrongShape, "4 features")


if __name__ == "__main__":
    # set to false to not show plots
    test_random_horizontal_flip_with_bbox_op_c(plot_vis=False)
    test_random_horizontal_flip_with_bbox_op_coco_c(plot_vis=False)
    test_random_horizontal_flip_with_bbox_valid_rand_c(plot_vis=False)
    test_random_horizontal_flip_with_bbox_valid_edge_c(plot_vis=False)
    test_random_horizontal_flip_with_bbox_invalid_prob_c()
    test_random_horizontal_flip_with_bbox_invalid_bounds_c()
