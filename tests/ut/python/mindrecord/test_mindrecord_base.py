# Copyright 2019 Huawei Technologies Co., Ltd
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
# ============================================================================
"""test mindrecord base"""
import numpy as np
import os
import uuid
from mindspore.mindrecord import FileWriter, FileReader, MindPage, SUCCESS
from mindspore import log as logger
from utils import get_data, get_nlp_data

FILES_NUM = 4
CV_FILE_NAME = "./imagenet.mindrecord"
CV2_FILE_NAME = "./imagenet_loop.mindrecord"
CV3_FILE_NAME = "./imagenet_append.mindrecord"
NLP_FILE_NAME = "./aclImdb.mindrecord"

def test_write_read_process():
    mindrecord_file_name = "test.mindrecord"
    data = [{"file_name": "001.jpg", "label": 43, "score": 0.8, "mask": np.array([3, 6, 9], dtype=np.int64),
             "segments": np.array([[5.0, 1.6], [65.2, 8.3]], dtype=np.float32),
             "data": bytes("image bytes abc", encoding='UTF-8')},
            {"file_name": "002.jpg", "label": 91, "score": 5.4, "mask": np.array([1, 4, 7], dtype=np.int64),
             "segments": np.array([[5.1, 9.1], [2.0, 65.4]], dtype=np.float32),
             "data": bytes("image bytes def", encoding='UTF-8')},
            {"file_name": "003.jpg", "label": 61, "score": 6.4, "mask": np.array([7, 6, 3], dtype=np.int64),
             "segments": np.array([[0.0, 5.6], [3.0, 16.3]], dtype=np.float32),
             "data": bytes("image bytes ghi", encoding='UTF-8')},
            {"file_name": "004.jpg", "label": 29, "score": 8.1, "mask": np.array([2, 8, 0], dtype=np.int64),
             "segments": np.array([[5.9, 7.2], [4.0, 89.0]], dtype=np.float32),
             "data": bytes("image bytes jkl", encoding='UTF-8')},
            {"file_name": "005.jpg", "label": 78, "score": 7.7, "mask": np.array([3, 1, 2], dtype=np.int64),
             "segments": np.array([[0.6, 8.1], [5.3, 49.3]], dtype=np.float32),
             "data": bytes("image bytes mno", encoding='UTF-8')},
            {"file_name": "006.jpg", "label": 37, "score": 9.4, "mask": np.array([7, 6, 7], dtype=np.int64),
             "segments": np.array([[4.2, 6.3], [8.9, 81.8]], dtype=np.float32),
             "data": bytes("image bytes pqr", encoding='UTF-8')}
            ]
    writer = FileWriter(mindrecord_file_name)
    schema = {"file_name": {"type": "string"},
              "label": {"type": "int32"},
              "score": {"type": "float64"},
              "mask": {"type": "int64", "shape": [-1]},
              "segments": {"type": "float32", "shape": [2, 2]},
              "data": {"type": "bytes"}}
    writer.add_schema(schema, "data is so cool")
    writer.write_raw_data(data)
    writer.commit()

    reader = FileReader(mindrecord_file_name)
    count = 0
    for index, x in enumerate(reader.get_next()):
        assert len(x) == 6
        for field in x:
            if isinstance(x[field], np.ndarray):
                assert (x[field] == data[count][field]).all()
            else:
                assert x[field] == data[count][field]
        count = count + 1
        logger.info("#item{}: {}".format(index, x))
    assert count == 6
    reader.close()

    os.remove("{}".format(mindrecord_file_name))
    os.remove("{}.db".format(mindrecord_file_name))

def test_write_read_process_with_define_index_field():
    mindrecord_file_name = "test.mindrecord"
    data = [{"file_name": "001.jpg", "label": 43, "score": 0.8, "mask": np.array([3, 6, 9], dtype=np.int64),
             "segments": np.array([[5.0, 1.6], [65.2, 8.3]], dtype=np.float32),
             "data": bytes("image bytes abc", encoding='UTF-8')},
            {"file_name": "002.jpg", "label": 91, "score": 5.4, "mask": np.array([1, 4, 7], dtype=np.int64),
             "segments": np.array([[5.1, 9.1], [2.0, 65.4]], dtype=np.float32),
             "data": bytes("image bytes def", encoding='UTF-8')},
            {"file_name": "003.jpg", "label": 61, "score": 6.4, "mask": np.array([7, 6, 3], dtype=np.int64),
             "segments": np.array([[0.0, 5.6], [3.0, 16.3]], dtype=np.float32),
             "data": bytes("image bytes ghi", encoding='UTF-8')},
            {"file_name": "004.jpg", "label": 29, "score": 8.1, "mask": np.array([2, 8, 0], dtype=np.int64),
             "segments": np.array([[5.9, 7.2], [4.0, 89.0]], dtype=np.float32),
             "data": bytes("image bytes jkl", encoding='UTF-8')},
            {"file_name": "005.jpg", "label": 78, "score": 7.7, "mask": np.array([3, 1, 2], dtype=np.int64),
             "segments": np.array([[0.6, 8.1], [5.3, 49.3]], dtype=np.float32),
             "data": bytes("image bytes mno", encoding='UTF-8')},
            {"file_name": "006.jpg", "label": 37, "score": 9.4, "mask": np.array([7, 6, 7], dtype=np.int64),
             "segments": np.array([[4.2, 6.3], [8.9, 81.8]], dtype=np.float32),
             "data": bytes("image bytes pqr", encoding='UTF-8')}
            ]
    writer = FileWriter(mindrecord_file_name)
    schema = {"file_name": {"type": "string"},
              "label": {"type": "int32"},
              "score": {"type": "float64"},
              "mask": {"type": "int64", "shape": [-1]},
              "segments": {"type": "float32", "shape": [2, 2]},
              "data": {"type": "bytes"}}
    writer.add_schema(schema, "data is so cool")
    writer.add_index(["label"])
    writer.write_raw_data(data)
    writer.commit()

    reader = FileReader(mindrecord_file_name)
    count = 0
    for index, x in enumerate(reader.get_next()):
        assert len(x) == 6
        for field in x:
            if isinstance(x[field], np.ndarray):
                assert (x[field] == data[count][field]).all()
            else:
                assert x[field] == data[count][field]
        count = count + 1
        logger.info("#item{}: {}".format(index, x))
    assert count == 6
    reader.close()

    os.remove("{}".format(mindrecord_file_name))
    os.remove("{}.db".format(mindrecord_file_name))

def test_cv_file_writer_tutorial():
    """tutorial for cv dataset writer."""
    writer = FileWriter(CV_FILE_NAME, FILES_NUM)
    data = get_data("../data/mindrecord/testImageNetData/")
    cv_schema_json = {"file_name": {"type": "string"},
                      "label": {"type": "int64"}, "data": {"type": "bytes"}}
    writer.add_schema(cv_schema_json, "img_schema")
    writer.add_index(["file_name", "label"])
    writer.write_raw_data(data)
    writer.commit()

def test_cv_file_append_writer():
    """tutorial for cv dataset append writer."""
    writer = FileWriter(CV3_FILE_NAME, 4)
    data = get_data("../data/mindrecord/testImageNetData/")
    cv_schema_json = {"file_name": {"type": "string"},
                      "label": {"type": "int64"}, "data": {"type": "bytes"}}
    writer.add_schema(cv_schema_json, "img_schema")
    writer.add_index(["file_name", "label"])
    writer.write_raw_data(data[0:5])
    writer.commit()
    write_append = FileWriter.open_for_append(CV3_FILE_NAME + "0")
    write_append.write_raw_data(data[5:10])
    write_append.commit()
    reader = FileReader(CV3_FILE_NAME + "0")
    count = 0
    for index, x in enumerate(reader.get_next()):
        assert len(x) == 3
        count = count + 1
        logger.info("#item{}: {}".format(index, x))
    assert count == 10
    reader.close()

    paths = ["{}{}".format(CV3_FILE_NAME, str(x).rjust(1, '0'))
             for x in range(4)]
    for x in paths:
        os.remove("{}".format(x))
        os.remove("{}.db".format(x))

def test_cv_file_writer_loop_and_read():
    """tutorial for cv dataset loop writer."""
    writer = FileWriter(CV2_FILE_NAME, FILES_NUM)
    data = get_data("../data/mindrecord/testImageNetData/")
    cv_schema_json = {"file_name": {"type": "string"},
                      "label": {"type": "int64"}, "data": {"type": "bytes"}}
    writer.add_schema(cv_schema_json, "img_schema")
    writer.add_index(["file_name", "label"])
    for row in data:
        writer.write_raw_data([row])
    writer.commit()

    reader = FileReader(CV2_FILE_NAME + "0")
    count = 0
    for index, x in enumerate(reader.get_next()):
        assert len(x) == 3
        count = count + 1
        logger.info("#item{}: {}".format(index, x))
    assert count == 10
    reader.close()

    paths = ["{}{}".format(CV2_FILE_NAME, str(x).rjust(1, '0'))
             for x in range(FILES_NUM)]
    for x in paths:
        os.remove("{}".format(x))
        os.remove("{}.db".format(x))

def test_cv_file_reader_tutorial():
    """tutorial for cv file reader."""
    reader = FileReader(CV_FILE_NAME + "0")
    count = 0
    for index, x in enumerate(reader.get_next()):
        assert len(x) == 3
        count = count + 1
        logger.info("#item{}: {}".format(index, x))
    assert count == 10
    reader.close()

def test_cv_file_reader_partial_tutorial():
    """tutorial for cv file partial reader."""
    reader = FileReader(CV_FILE_NAME + "0")
    count = 0
    for index, x in enumerate(reader.get_next()):
        assert len(x) == 3
        count = count + 1
        logger.info("#item{}: {}".format(index, x))
        if count == 5:
            reader.finish()
    assert count == 5

def test_cv_page_reader_tutorial():
    """tutorial for cv page reader."""
    reader = MindPage(CV_FILE_NAME + "0")
    fields = reader.get_category_fields()
    assert fields == ['file_name', 'label'],\
        'failed on getting candidate category fields.'

    ret = reader.set_category_field("label")
    assert ret == SUCCESS, 'failed on setting category field.'

    info = reader.read_category_info()
    logger.info("category info: {}".format(info))

    row = reader.read_at_page_by_id(0, 0, 1)
    assert len(row) == 1
    assert len(row[0]) == 3
    assert row[0]['label'] == 13

    row1 = reader.read_at_page_by_name("822", 0, 1)
    assert len(row1) == 1
    assert len(row1[0]) == 3
    assert row1[0]['label'] == 822

def test_cv_page_reader_tutorial_by_file_name():
    """tutorial for cv page reader."""
    reader = MindPage(CV_FILE_NAME + "0")
    fields = reader.get_category_fields()
    assert fields == ['file_name', 'label'],\
        'failed on getting candidate category fields.'

    ret = reader.set_category_field("file_name")
    assert ret == SUCCESS, 'failed on setting category field.'

    info = reader.read_category_info()
    logger.info("category info: {}".format(info))

    row = reader.read_at_page_by_id(0, 0, 1)
    assert len(row) == 1
    assert len(row[0]) == 3
    assert row[0]['label'] == 490

    row1 = reader.read_at_page_by_name("image_00007.jpg", 0, 1)
    assert len(row1) == 1
    assert len(row1[0]) == 3
    assert row1[0]['label'] == 13

def test_cv_page_reader_tutorial_new_api():
    """tutorial for cv page reader."""
    reader = MindPage(CV_FILE_NAME + "0")
    fields = reader.candidate_fields
    assert fields == ['file_name', 'label'],\
        'failed on getting candidate category fields.'

    reader.category_field = "file_name"

    info = reader.read_category_info()
    logger.info("category info: {}".format(info))

    row = reader.read_at_page_by_id(0, 0, 1)
    assert len(row) == 1
    assert len(row[0]) == 3
    assert row[0]['label'] == 490

    row1 = reader.read_at_page_by_name("image_00007.jpg", 0, 1)
    assert len(row1) == 1
    assert len(row1[0]) == 3
    assert row1[0]['label'] == 13

    paths = ["{}{}".format(CV_FILE_NAME, str(x).rjust(1, '0'))
             for x in range(FILES_NUM)]
    for x in paths:
        os.remove("{}".format(x))
        os.remove("{}.db".format(x))

def test_nlp_file_writer_tutorial():
    """tutorial for nlp file writer."""
    writer = FileWriter(NLP_FILE_NAME, FILES_NUM)
    data = list(get_nlp_data("../data/mindrecord/testAclImdbData/pos",
                             "../data/mindrecord/testAclImdbData/vocab.txt",
                             10))
    nlp_schema_json = {"id": {"type": "string"}, "label": {"type": "int32"},
                       "rating": {"type": "float32"},
                       "input_ids": {"type": "int64",
                                     "shape": [1, -1]},
                       "input_mask": {"type": "int64",
                                      "shape": [1, -1]},
                       "segment_ids": {"type": "int64",
                                       "shape": [1, -1]}
                       }
    writer.add_schema(nlp_schema_json, "nlp_schema")
    writer.add_index(["id", "rating"])
    writer.write_raw_data(data)
    writer.commit()

def test_nlp_file_reader_tutorial():
    """tutorial for nlp file reader."""
    reader = FileReader(NLP_FILE_NAME + "0")
    count = 0
    for index, x in enumerate(reader.get_next()):
        assert len(x) == 6
        count = count + 1
        logger.info("#item{}: {}".format(index, x))
    assert count == 10
    reader.close()

def test_nlp_page_reader_tutorial():
    """tutorial for nlp page reader."""
    reader = MindPage(NLP_FILE_NAME + "0")
    fields = reader.get_category_fields()
    assert fields == ['id', 'rating'],\
        'failed on getting candidate category fields.'

    ret = reader.set_category_field("rating")
    assert ret == SUCCESS, 'failed on setting category field.'

    info = reader.read_category_info()
    logger.info("category info: {}".format(info))

    row = reader.read_at_page_by_id(0, 0, 1)
    assert len(row) == 1
    assert len(row[0]) == 6
    logger.info("row[0]: {}".format(row[0]))

    row1 = reader.read_at_page_by_name("7", 0, 1)
    assert len(row1) == 1
    assert len(row1[0]) == 6
    logger.info("row1[0]: {}".format(row1[0]))

    paths = ["{}{}".format(NLP_FILE_NAME, str(x).rjust(1, '0'))
             for x in range(FILES_NUM)]
    for x in paths:
        os.remove("{}".format(x))
        os.remove("{}.db".format(x))

def test_cv_file_writer_shard_num_10():
    """test file writer when shard num equals 10."""
    writer = FileWriter(CV_FILE_NAME, 10)
    data = get_data("../data/mindrecord/testImageNetData/")
    cv_schema_json = {"file_name": {"type": "string"},
                      "label": {"type": "int64"}, "data": {"type": "bytes"}}
    writer.add_schema(cv_schema_json, "img_schema")
    writer.add_index(["file_name", "label"])
    writer.write_raw_data(data)
    writer.commit()

    paths = ["{}{}".format(CV_FILE_NAME, str(x).rjust(1, '0'))
            for x in range(10)]
    for x in paths:
        os.remove("{}".format(x))
        os.remove("{}.db".format(x))

def test_cv_file_writer_absolute_path():
    """test cv file writer when file name is absolute path."""
    file_name = "/tmp/" + str(uuid.uuid4())
    writer = FileWriter(file_name, FILES_NUM)
    data = get_data("../data/mindrecord/testImageNetData/")
    cv_schema_json = {"file_name": {"type": "string"},
                      "label": {"type": "int64"}, "data": {"type": "bytes"}}
    writer.add_schema(cv_schema_json, "img_schema")
    writer.add_index(["file_name", "label"])
    writer.write_raw_data(data)
    writer.commit()

    paths = ["{}{}".format(file_name, str(x).rjust(1, '0'))
             for x in range(FILES_NUM)]
    for x in paths:
        os.remove("{}".format(x))
        os.remove("{}.db".format(x))

def test_cv_file_writer_without_data():
    """test cv file writer without data."""
    writer = FileWriter(CV_FILE_NAME, 1)
    cv_schema_json = {"file_name": {"type": "string"},
                      "label": {"type": "int64"}, "data": {"type": "bytes"}}
    writer.add_schema(cv_schema_json, "img_schema")
    writer.add_index(["file_name", "label"])
    writer.commit()
    reader = FileReader(CV_FILE_NAME)
    count = 0
    for index, x in enumerate(reader.get_next()):
        count = count + 1
        logger.info("#item{}: {}".format(index, x))
    assert count == 0
    reader.close()
    os.remove(CV_FILE_NAME)
    os.remove("{}.db".format(CV_FILE_NAME))

def test_cv_file_writer_no_blob():
    """test cv file writer without blob data."""
    writer = FileWriter(CV_FILE_NAME, 1)
    data = get_data("../data/mindrecord/testImageNetData/")
    cv_schema_json = {"file_name": {"type": "string"},
                      "label": {"type": "int64"}}
    writer.add_schema(cv_schema_json, "no_blob_schema")
    writer.add_index(["file_name", "label"])
    writer.write_raw_data(data)
    writer.commit()
    reader = FileReader(CV_FILE_NAME)
    count = 0
    for index, x in enumerate(reader.get_next()):
        count += 1
        assert len(x) == 2
        logger.info("#item{}: {}".format(index, x))
    assert count == 10
    reader.close()
    os.remove(CV_FILE_NAME)
    os.remove("{}.db".format(CV_FILE_NAME))

def test_cv_file_writer_no_raw():
    """test cv file writer without raw data."""
    writer = FileWriter(NLP_FILE_NAME)
    data = list(get_nlp_data("../data/mindrecord/testAclImdbData/pos",
                         "../data/mindrecord/testAclImdbData/vocab.txt",
                         10))
    nlp_schema_json = {"input_ids": {"type": "int64",
                                 "shape": [1, -1]},
                        "input_mask": {"type": "int64",
                                  "shape": [1, -1]},
                        "segment_ids": {"type": "int64",
                                   "shape": [1, -1]}
                       }
    writer.add_schema(nlp_schema_json, "no_raw_schema")
    writer.write_raw_data(data)
    writer.commit()
    reader = FileReader(NLP_FILE_NAME)
    count = 0
    for index, x in enumerate(reader.get_next()):
        count += 1
        assert len(x) == 3
        logger.info("#item{}: {}".format(index, x))
    assert count == 10
    reader.close()
    os.remove(NLP_FILE_NAME)
    os.remove("{}.db".format(NLP_FILE_NAME))
