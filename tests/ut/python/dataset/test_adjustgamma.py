# Copyright 2021-2022 Huawei Technologies Co., Ltd
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
Testing AdjustGamma op in DE
"""
import numpy as np
from numpy.testing import assert_allclose
import PIL

import mindspore.dataset as ds
import mindspore.dataset.transforms.transforms
import mindspore.dataset.vision.transforms as vision
from mindspore import log as logger

DATA_DIR = "../data/dataset/testImageNetData/train/"
MNIST_DATA_DIR = "../data/dataset/testMnistData"

DATA_DIR_2 = ["../data/dataset/test_tf_file_3_images/train-0000-of-0001.data"]
SCHEMA_DIR = "../data/dataset/test_tf_file_3_images/datasetSchema.json"


def generate_numpy_random_rgb(shape):
    """
    Only generate floating points that are fractions like n / 256, since they
    are RGB pixels. Some low-precision floating point types in this test can't
    handle arbitrary precision floating points well.
    """
    return np.random.randint(0, 256, shape) / 255.


def test_adjust_gamma_c_eager():
    """
    Feature: AdjustGamma op
    Description: Test eager support for AdjustGamma C implementation
    Expectation: Receive non-None output image from op
    """
    # Eager 3-channel
    rgb_flat = generate_numpy_random_rgb((64, 3)).astype(np.float32)
    img_in = rgb_flat.reshape((8, 8, 3))

    adjustgamma_op = vision.AdjustGamma(10, 1)
    img_out = adjustgamma_op(img_in)
    assert img_out is not None

    img_in2 = PIL.Image.open("../data/dataset/apple.jpg").convert("RGB")

    adjustgamma_op2 = vision.AdjustGamma(10, 1)
    img_out2 = adjustgamma_op2(img_in2)
    assert img_out2 is not None


def test_adjust_gamma_py_eager():
    """
    Feature: AdjustGamma op
    Description: Test eager support for AdjustGamma Python implementation
    Expectation: Receive non-None output image from op
    """
    # Eager 3-channel
    rgb_flat = generate_numpy_random_rgb((64, 3)).astype(np.uint8)
    img_in = PIL.Image.fromarray(rgb_flat.reshape((8, 8, 3)))

    adjustgamma_op = vision.AdjustGamma(10, 1)
    img_out = adjustgamma_op(img_in)
    assert img_out is not None

    img_in2 = PIL.Image.open("../data/dataset/apple.jpg").convert("RGB")

    adjustgamma_op2 = vision.AdjustGamma(10, 1)
    img_out2 = adjustgamma_op2(img_in2)
    assert img_out2 is not None


def test_adjust_gamma_c_eager_gray():
    # Eager 3-channel
    rgb_flat = generate_numpy_random_rgb((64, 1)).astype(np.float32)
    img_in = rgb_flat.reshape((8, 8))

    adjustgamma_op = vision.AdjustGamma(10, 1)
    img_out = adjustgamma_op(img_in)
    assert img_out is not None


def test_adjust_gamma_py_eager_gray():
    # Eager 3-channel
    rgb_flat = generate_numpy_random_rgb((64, 1)).astype(np.uint8)
    img_in = PIL.Image.fromarray(rgb_flat.reshape((8, 8)))

    adjustgamma_op = vision.AdjustGamma(10, 1)
    img_out = adjustgamma_op(img_in)
    assert img_out is not None


def test_adjust_gamma_invalid_gamma_param_c():
    """
    Test AdjustGamma C implementation with invalid ignore parameter
    """
    logger.info("Test AdjustGamma C implementation with invalid ignore parameter")
    try:
        data_set = ds.ImageFolderDataset(dataset_dir=DATA_DIR, shuffle=False)
        data_set = data_set.map(
            operations=[vision.Decode(), vision.Resize((224, 224)), lambda img: np.array(img[:, :, 0])],
            input_columns=["image"])
        # invalid gamma
        data_set = data_set.map(operations=vision.AdjustGamma(gamma=-10.0, gain=1.0),
                                input_columns="image")
    except ValueError as error:
        logger.info("Got an exception in AdjustGamma: {}".format(str(error)))
        assert "Input is not within the required interval of " in str(error)
    try:
        data_set = ds.ImageFolderDataset(dataset_dir=DATA_DIR, shuffle=False)
        data_set = data_set.map(
            operations=[vision.Decode(), vision.Resize((224, 224)), lambda img: np.array(img[:, :, 0])],
            input_columns=["image"])
        # invalid gamma
        data_set = data_set.map(operations=vision.AdjustGamma(gamma=[1, 2], gain=1.0),
                                input_columns="image")
    except TypeError as error:
        logger.info("Got an exception in AdjustGamma: {}".format(str(error)))
        assert "is not of type [<class 'float'>, <class 'int'>], but got" in str(error)


def test_adjust_gamma_invalid_gamma_param_py():
    """
    Test AdjustGamma Python implementation with invalid ignore parameter
    """
    logger.info("Test AdjustGamma Python implementation with invalid ignore parameter")
    try:
        data_set = ds.ImageFolderDataset(dataset_dir=DATA_DIR, shuffle=False)
        trans = mindspore.dataset.transforms.transforms.Compose([
            vision.Decode(True),
            vision.Resize((224, 224)),
            vision.AdjustGamma(gamma=-10.0),
            vision.ToTensor()
        ])
        data_set = data_set.map(operations=[trans], input_columns=["image"])
    except ValueError as error:
        logger.info("Got an exception in AdjustGamma: {}".format(str(error)))
        assert "Input is not within the required interval of " in str(error)
    try:
        data_set = ds.ImageFolderDataset(dataset_dir=DATA_DIR, shuffle=False)
        trans = mindspore.dataset.transforms.transforms.Compose([
            vision.Decode(True),
            vision.Resize((224, 224)),
            vision.AdjustGamma(gamma=[1, 2]),
            vision.ToTensor()
        ])
        data_set = data_set.map(operations=[trans], input_columns=["image"])
    except TypeError as error:
        logger.info("Got an exception in AdjustGamma: {}".format(str(error)))
        assert "is not of type [<class 'float'>, <class 'int'>], but got" in str(error)


def test_adjust_gamma_invalid_gain_param_c():
    """
    Test AdjustGamma C implementation with invalid gain parameter
    """
    logger.info("Test AdjustGamma C implementation with invalid gain parameter")
    try:
        data_set = ds.ImageFolderDataset(dataset_dir=DATA_DIR, shuffle=False)
        data_set = data_set.map(
            operations=[vision.Decode(), vision.Resize((224, 224)), lambda img: np.array(img[:, :, 0])],
            input_columns=["image"])
        # invalid gain
        data_set = data_set.map(operations=vision.AdjustGamma(gamma=10.0, gain=[1, 10]),
                                input_columns="image")
    except TypeError as error:
        logger.info("Got an exception in AdjustGamma: {}".format(str(error)))
        assert "is not of type [<class 'float'>, <class 'int'>], but got " in str(error)


def test_adjust_gamma_invalid_gain_param_py():
    """
    Test AdjustGamma Python implementation with invalid gain parameter
    """
    logger.info("Test AdjustGamma Python implementation with invalid gain parameter")
    try:
        data_set = ds.ImageFolderDataset(dataset_dir=DATA_DIR, shuffle=False)
        trans = mindspore.dataset.transforms.transforms.Compose([
            vision.Decode(True),
            vision.Resize((224, 224)),
            vision.AdjustGamma(gamma=10.0, gain=[1, 10]),
            vision.ToTensor()
        ])
        data_set = data_set.map(operations=[trans], input_columns=["image"])
    except TypeError as error:
        logger.info("Got an exception in AdjustGamma: {}".format(str(error)))
        assert "is not of type [<class 'float'>, <class 'int'>], but got " in str(error)


def test_adjust_gamma_pipeline_c():
    """
    Test AdjustGamma C implementation Pipeline
    """
    # First dataset
    transforms1 = [vision.Decode(), vision.Resize([64, 64])]
    transforms1 = mindspore.dataset.transforms.transforms.Compose(
        transforms1)
    ds1 = ds.TFRecordDataset(DATA_DIR_2,
                             SCHEMA_DIR,
                             columns_list=["image"],
                             shuffle=False)
    ds1 = ds1.map(operations=transforms1, input_columns=["image"])

    # Second dataset
    transforms2 = [
        vision.Decode(),
        vision.Resize([64, 64]),
        vision.AdjustGamma(1.0, 1.0)
    ]
    transform2 = mindspore.dataset.transforms.transforms.Compose(
        transforms2)
    ds2 = ds.TFRecordDataset(DATA_DIR_2,
                             SCHEMA_DIR,
                             columns_list=["image"],
                             shuffle=False)
    ds2 = ds2.map(operations=transform2, input_columns=["image"])

    num_iter = 0
    for data1, data2 in zip(ds1.create_dict_iterator(num_epochs=1),
                            ds2.create_dict_iterator(num_epochs=1)):
        num_iter += 1
        ori_img = data1["image"].asnumpy()
        cvt_img = data2["image"].asnumpy()
        assert_allclose(ori_img.flatten(),
                        cvt_img.flatten(),
                        rtol=1e-5,
                        atol=0)
        assert ori_img.shape == cvt_img.shape


def test_adjust_gamma_pipeline_py():
    """
    Test AdjustGamma Python implementation Pipeline
    """
    # First dataset
    transforms1 = [vision.Decode(True), vision.Resize([64, 64]), vision.ToTensor()]
    transforms1 = mindspore.dataset.transforms.transforms.Compose(
        transforms1)
    ds1 = ds.TFRecordDataset(DATA_DIR_2,
                             SCHEMA_DIR,
                             columns_list=["image"],
                             shuffle=False)
    ds1 = ds1.map(operations=transforms1, input_columns=["image"])

    # Second dataset
    transforms2 = [
        vision.Decode(True),
        vision.Resize([64, 64]),
        vision.AdjustGamma(1.0, 1.0),
        vision.ToTensor()
    ]
    transform2 = mindspore.dataset.transforms.transforms.Compose(
        transforms2)
    ds2 = ds.TFRecordDataset(DATA_DIR_2,
                             SCHEMA_DIR,
                             columns_list=["image"],
                             shuffle=False)
    ds2 = ds2.map(operations=transform2, input_columns=["image"])

    num_iter = 0
    for data1, data2 in zip(ds1.create_dict_iterator(num_epochs=1),
                            ds2.create_dict_iterator(num_epochs=1)):
        num_iter += 1
        ori_img = data1["image"].asnumpy()
        cvt_img = data2["image"].asnumpy()
        assert_allclose(ori_img.flatten(),
                        cvt_img.flatten(),
                        rtol=1e-5,
                        atol=0)
        assert ori_img.shape == cvt_img.shape


def test_adjust_gamma_pipeline_py_gray():
    """
    Test AdjustGamma Python implementation Pipeline 1-channel
    """
    # First dataset
    transforms1_list = [vision.Decode(True), vision.Resize([60, 60]), vision.Grayscale(), vision.ToTensor()]
    transforms1 = mindspore.dataset.transforms.transforms.Compose(transforms1_list)
    ds1 = ds.TFRecordDataset(DATA_DIR_2,
                             SCHEMA_DIR,
                             columns_list=["image"],
                             shuffle=False)
    ds1 = ds1.map(operations=transforms1, input_columns=["image"])

    # Second dataset
    transforms2_list = [
        vision.Decode(True),
        vision.Resize([60, 60]),
        vision.Grayscale(),
        vision.AdjustGamma(1.0, 1.0),
        vision.ToTensor()
    ]
    transform2 = mindspore.dataset.transforms.transforms.Compose(transforms2_list)
    ds2 = ds.TFRecordDataset(DATA_DIR_2,
                             SCHEMA_DIR,
                             columns_list=["image"],
                             shuffle=False)
    ds2 = ds2.map(operations=transform2, input_columns=["image"])

    num_iter = 0
    for data1, data2 in zip(ds1.create_dict_iterator(num_epochs=1),
                            ds2.create_dict_iterator(num_epochs=1)):
        num_iter += 1
        ori_img = data1["image"].asnumpy()
        cvt_img = data2["image"].asnumpy()
        assert_allclose(ori_img.flatten(),
                        cvt_img.flatten(),
                        rtol=1e-5,
                        atol=0)


if __name__ == "__main__":
    test_adjust_gamma_c_eager()
    test_adjust_gamma_py_eager()
    test_adjust_gamma_c_eager_gray()
    test_adjust_gamma_py_eager_gray()

    test_adjust_gamma_invalid_gamma_param_c()
    test_adjust_gamma_invalid_gamma_param_py()
    test_adjust_gamma_invalid_gain_param_c()
    test_adjust_gamma_invalid_gain_param_py()
    test_adjust_gamma_pipeline_c()
    test_adjust_gamma_pipeline_py()
    test_adjust_gamma_pipeline_py_gray()
