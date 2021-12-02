# Copyright 2020-2021 Huawei Technologies Co., Ltd
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
Testing profiling support in DE
"""
import json
import os
import numpy as np
import pytest
import mindspore.common.dtype as mstype
import mindspore.dataset as ds
import mindspore.dataset.transforms.c_transforms as C
import mindspore.dataset.vision.c_transforms as vision
import mindspore._c_dataengine as cde

FILES = ["../data/dataset/testTFTestAllTypes/test.data"]
DATASET_ROOT = "../data/dataset/testTFTestAllTypes/"
SCHEMA_FILE = "../data/dataset/testTFTestAllTypes/datasetSchema.json"

# add file name to rank id mapping to avoid file writing crash
file_name_map_rank_id = {"test_profiling_simple_pipeline": "0",
                         "test_profiling_complex_pipeline": "1",
                         "test_profiling_inline_ops_pipeline1": "2",
                         "test_profiling_inline_ops_pipeline2": "3",
                         "test_profiling_sampling_interval": "4",
                         "test_profiling_basic_pipeline": "5",
                         "test_profiling_cifar10_pipeline": "6",
                         "test_profiling_seq_pipelines_epochctrl3": "7",
                         "test_profiling_seq_pipelines_epochctrl2": "8",
                         "test_profiling_seq_pipelines_repeat": "9"}


@pytest.mark.forked
class TestMinddataProfilingManager:
    """
    Test MinddataProfilingManager
    """

    def setup_class(self):
        """
        Run once for the class
        """
        # Get instance pointer for MindData profiling manager
        self.md_profiler = cde.GlobalContext.profiling_manager()

        self._pipeline_file = "./pipeline_profiling"
        self._cpu_util_file = "./minddata_cpu_utilization"
        self._dataset_iterator_file = "./dataset_iterator_profiling"

    def setup_method(self):
        """
        Run before each test function.
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"
        dataset_iterator_file = self._dataset_iterator_file + "_" + file_id + ".txt"

        # Confirm MindData Profiling files do not yet exist
        assert os.path.exists(pipeline_file) is False
        assert os.path.exists(cpu_util_file) is False
        assert os.path.exists(dataset_iterator_file) is False

        # Set the MindData Profiling related environment variables
        os.environ['RANK_ID'] = file_id
        os.environ['DEVICE_ID'] = file_id

        # Initialize MindData profiling manager
        self.md_profiler.init()

        # Start MindData Profiling
        self.md_profiler.start()

    def teardown_method(self):
        """
        Run after each test function.
        """

        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"
        dataset_iterator_file = self._dataset_iterator_file + "_" + file_id + ".txt"

        # Delete MindData profiling files generated from the test.
        os.remove(pipeline_file)
        os.remove(cpu_util_file)
        os.remove(dataset_iterator_file)

        # Disable MindData Profiling related environment variables
        del os.environ['RANK_ID']
        del os.environ['DEVICE_ID']

    def confirm_cpuutil(self, num_pipeline_ops, cpu_uti_file):
        """
        Confirm CPU utilization JSON file with <num_pipeline_ops> in the pipeline
        """
        with open(cpu_uti_file) as file1:
            data = json.load(file1)
            op_info = data["op_info"]
            assert len(op_info) == num_pipeline_ops

    def confirm_ops_in_pipeline(self, num_ops, op_list, pipeline_file):
        """
        Confirm pipeline JSON file with <num_ops> are in the pipeline and the given list of ops
        """
        with open(pipeline_file) as file1:
            data = json.load(file1)
            op_info = data["op_info"]
            # Confirm ops in pipeline file
            assert len(op_info) == num_ops
            for i in range(num_ops):
                assert op_info[i]["op_type"] in op_list

    def test_profiling_simple_pipeline(self):
        """
        Generator -> Shuffle -> Batch
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"
        dataset_iterator_file = self._dataset_iterator_file + "_" + file_id + ".txt"

        source = [(np.array([x]),) for x in range(1024)]
        data1 = ds.GeneratorDataset(source, ["data"])
        data1 = data1.shuffle(64)
        data1 = data1.batch(32)
        # try output shape type and dataset size and make sure no profiling file is generated
        assert data1.output_shapes() == [[32, 1]]
        assert [str(tp) for tp in data1.output_types()] == ["int64"]
        assert data1.get_dataset_size() == 32

        # Confirm profiling files do not (yet) exist
        assert os.path.exists(pipeline_file) is False
        assert os.path.exists(cpu_util_file) is False
        assert os.path.exists(dataset_iterator_file) is False

        for _ in data1:
            pass

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        # Confirm profiling files now exist
        assert os.path.exists(pipeline_file) is True
        assert os.path.exists(cpu_util_file) is True
        assert os.path.exists(dataset_iterator_file) is True

    def test_profiling_complex_pipeline(self):
        """
        Generator -> Map     ->
                                 -> Zip
        TFReader  -> Shuffle ->
        """

        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"

        source = [(np.array([x]),) for x in range(1024)]
        data1 = ds.GeneratorDataset(source, ["gen"])
        data1 = data1.map(operations=[(lambda x: x + 1)], input_columns=["gen"])

        pattern = DATASET_ROOT + "/test.data"
        data2 = ds.TFRecordDataset(pattern, SCHEMA_FILE, shuffle=ds.Shuffle.FILES)
        data2 = data2.shuffle(4)

        data3 = ds.zip((data1, data2))

        for _ in data3:
            pass

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        with open(pipeline_file) as f:
            data = json.load(f)
            op_info = data["op_info"]
            assert len(op_info) == 5
            for i in range(5):
                if op_info[i]["op_type"] != "ZipOp":
                    assert "size" in op_info[i]["metrics"]["output_queue"]
                    assert "length" in op_info[i]["metrics"]["output_queue"]
                else:
                    # Note: Zip is an inline op and hence does not have metrics information
                    assert op_info[i]["metrics"] is None

        # Confirm CPU util JSON file content, when 5 ops are in the pipeline JSON file
        self.confirm_cpuutil(5, cpu_util_file)

    def test_profiling_inline_ops_pipeline1(self):
        """
        Test pipeline with inline ops: Concat and EpochCtrl
        Generator ->
                     Concat -> EpochCtrl
        Generator ->
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"

        # In source1 dataset: Number of rows is 3; its values are 0, 1, 2
        def source1():
            for i in range(3):
                yield (np.array([i]),)

        # In source2 dataset: Number of rows is 7; its values are 3, 4, 5 ... 9
        def source2():
            for i in range(3, 10):
                yield (np.array([i]),)

        data1 = ds.GeneratorDataset(source1, ["col1"])
        data2 = ds.GeneratorDataset(source2, ["col1"])
        data3 = data1.concat(data2)

        num_iter = 0
        # Note: set num_epochs=2 in create_tuple_iterator(), so that EpochCtrl op is added to the pipeline
        # Here i refers to index, d refers to data element
        for i, d in enumerate(data3.create_tuple_iterator(num_epochs=2, output_numpy=True)):
            num_iter += 1
            t = d
            assert i == t[0][0]

        assert num_iter == 10

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        # Confirm pipeline is created with EpochCtrl op
        with open(pipeline_file) as f:
            data = json.load(f)
            op_info = data["op_info"]
            assert len(op_info) == 4
            for i in range(4):
                # Note: The following ops are inline ops: Concat, EpochCtrl
                if op_info[i]["op_type"] in ("ConcatOp", "EpochCtrlOp"):
                    # Confirm these inline ops do not have metrics information
                    assert op_info[i]["metrics"] is None
                else:
                    assert "size" in op_info[i]["metrics"]["output_queue"]
                    assert "length" in op_info[i]["metrics"]["output_queue"]

        # Confirm CPU util JSON file content, when 4 ops are in the pipeline JSON file
        self.confirm_cpuutil(4, cpu_util_file)

    def test_profiling_inline_ops_pipeline2(self):
        """
        Test pipeline with many inline ops
        Generator -> Rename -> Skip -> Repeat -> Take
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"

        # In source1 dataset: Number of rows is 10; its values are 0, 1, 2, 3, 4, 5 ... 9
        def source1():
            for i in range(10):
                yield (np.array([i]),)

        data1 = ds.GeneratorDataset(source1, ["col1"])
        data1 = data1.rename(input_columns=["col1"], output_columns=["newcol1"])
        data1 = data1.skip(2)
        data1 = data1.repeat(2)
        data1 = data1.take(12)

        for _ in data1:
            pass

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        with open(pipeline_file) as f:
            data = json.load(f)
            op_info = data["op_info"]
            assert len(op_info) == 5
            for i in range(5):
                # Check for these inline ops
                if op_info[i]["op_type"] in ("RenameOp", "RepeatOp", "SkipOp", "TakeOp"):
                    # Confirm these inline ops do not have metrics information
                    assert op_info[i]["metrics"] is None
                else:
                    assert "size" in op_info[i]["metrics"]["output_queue"]
                    assert "length" in op_info[i]["metrics"]["output_queue"]

        # Confirm CPU util JSON file content, when 5 ops are in the pipeline JSON file
        self.confirm_cpuutil(5, cpu_util_file)

    def test_profiling_sampling_interval(self):
        """
        Test non-default monitor sampling interval
        """
        interval_origin = ds.config.get_monitor_sampling_interval()

        ds.config.set_monitor_sampling_interval(30)
        interval = ds.config.get_monitor_sampling_interval()
        assert interval == 30

        source = [(np.array([x]),) for x in range(1024)]
        data1 = ds.GeneratorDataset(source, ["data"])
        data1 = data1.shuffle(64)
        data1 = data1.batch(32)

        for _ in data1:
            pass

        ds.config.set_monitor_sampling_interval(interval_origin)

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

    def test_profiling_basic_pipeline(self):
        """
        Test with this basic pipeline
        Generator -> Map -> Batch -> Repeat -> EpochCtrl
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"

        def source1():
            for i in range(8000):
                yield (np.array([i]),)

        # Create this basic and common pipeline
        # Leaf/Source-Op -> Map -> Batch -> Repeat
        data1 = ds.GeneratorDataset(source1, ["col1"])

        type_cast_op = C.TypeCast(mstype.int32)
        data1 = data1.map(operations=type_cast_op, input_columns="col1")
        data1 = data1.batch(16)
        data1 = data1.repeat(2)

        num_iter = 0
        # Note: If create_dict_iterator() is called with num_epochs>1, then EpochCtrlOp is added to the pipeline
        for _ in data1.create_dict_iterator(num_epochs=2):
            num_iter += 1

        assert num_iter == 1000

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        with open(pipeline_file) as f:
            data = json.load(f)
            op_info = data["op_info"]
            assert len(op_info) == 5
            for i in range(5):
                # Check for inline ops
                if op_info[i]["op_type"] in ("EpochCtrlOp", "RepeatOp"):
                    # Confirm these inline ops do not have metrics information
                    assert op_info[i]["metrics"] is None
                else:
                    assert "size" in op_info[i]["metrics"]["output_queue"]
                    assert "length" in op_info[i]["metrics"]["output_queue"]

        # Confirm CPU util JSON file content, when 5 ops are in the pipeline JSON file
        self.confirm_cpuutil(5, cpu_util_file)

    def test_profiling_cifar10_pipeline(self):
        """
        Test with this common pipeline with Cifar10
        Cifar10 -> Map -> Map -> Batch -> Repeat
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"

        # Create this common pipeline
        # Cifar10 -> Map -> Map -> Batch -> Repeat
        DATA_DIR_10 = "../data/dataset/testCifar10Data"
        data1 = ds.Cifar10Dataset(DATA_DIR_10, num_samples=8000)

        type_cast_op = C.TypeCast(mstype.int32)
        data1 = data1.map(operations=type_cast_op, input_columns="label")
        random_horizontal_op = vision.RandomHorizontalFlip()
        data1 = data1.map(operations=random_horizontal_op, input_columns="image")

        data1 = data1.batch(32)
        data1 = data1.repeat(3)

        num_iter = 0
        # Note: If create_dict_iterator() is called with num_epochs=1, then EpochCtrlOp is NOT added to the pipeline
        for _ in data1.create_dict_iterator(num_epochs=1):
            num_iter += 1

        assert num_iter == 750

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        with open(pipeline_file) as f:
            data = json.load(f)
            op_info = data["op_info"]
            assert len(op_info) == 5
            for i in range(5):
                # Check for inline ops
                if op_info[i]["op_type"] == "RepeatOp":
                    # Confirm these inline ops do not have metrics information
                    assert op_info[i]["metrics"] is None
                else:
                    assert "size" in op_info[i]["metrics"]["output_queue"]
                    assert "length" in op_info[i]["metrics"]["output_queue"]

        # Confirm CPU util JSON file content, when 5 ops are in the pipeline JSON file
        self.confirm_cpuutil(5, cpu_util_file)

    def test_profiling_seq_pipelines_epochctrl3(self):
        """
        Test with these 2 sequential pipelines:
        1) Generator -> Batch -> EpochCtrl
        2) Generator -> Batch
        Note: This is a simplification of the user scenario to use the same pipeline for training and then evaluation.
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"

        source = [(np.array([x]),) for x in range(64)]
        data1 = ds.GeneratorDataset(source, ["data"])
        data1 = data1.batch(32)

        # Test A - Call create_dict_iterator with num_epochs>1
        num_iter = 0
        # Note: If create_dict_iterator() is called with num_epochs>1, then EpochCtrlOp is added to the pipeline
        for _ in data1.create_dict_iterator(num_epochs=2):
            num_iter += 1
        assert num_iter == 2

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        # Confirm pipeline file and CPU util file each have 3 ops
        self.confirm_ops_in_pipeline(3, ["GeneratorOp", "BatchOp", "EpochCtrlOp"], pipeline_file)
        self.confirm_cpuutil(3, cpu_util_file)

        # Test B - Call create_dict_iterator with num_epochs=1

        # Initialize and Start MindData profiling manager
        self.md_profiler.init()
        self.md_profiler.start()

        num_iter = 0
        # Note: If create_dict_iterator() is called with num_epochs=1,
        # then EpochCtrlOp should not be NOT added to the pipeline
        for _ in data1.create_dict_iterator(num_epochs=1):
            num_iter += 1
        assert num_iter == 2

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        # Confirm pipeline file and CPU util file each have 2 ops
        self.confirm_ops_in_pipeline(2, ["GeneratorOp", "BatchOp"], pipeline_file)
        self.confirm_cpuutil(2, cpu_util_file)

    def test_profiling_seq_pipelines_epochctrl2(self):
        """
        Test with these 2 sequential pipelines:
        1) Generator -> Batch
        2) Generator -> Batch -> EpochCtrl
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"

        source = [(np.array([x]),) for x in range(64)]
        data2 = ds.GeneratorDataset(source, ["data"])
        data2 = data2.batch(16)

        # Test A - Call create_dict_iterator with num_epochs=1
        num_iter = 0
        # Note: If create_dict_iterator() is called with num_epochs=1, then EpochCtrlOp is NOT added to the pipeline
        for _ in data2.create_dict_iterator(num_epochs=1):
            num_iter += 1
        assert num_iter == 4

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        # Confirm pipeline file and CPU util file each have 2 ops
        self.confirm_ops_in_pipeline(2, ["GeneratorOp", "BatchOp"], pipeline_file)
        self.confirm_cpuutil(2, cpu_util_file)

        # Test B - Call create_dict_iterator with num_epochs>1

        # Initialize and Start MindData profiling manager
        self.md_profiler.init()
        self.md_profiler.start()

        num_iter = 0
        # Note: If create_dict_iterator() is called with num_epochs>1,
        # then EpochCtrlOp should be added to the pipeline
        for _ in data2.create_dict_iterator(num_epochs=2):
            num_iter += 1
        assert num_iter == 4

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        # Confirm pipeline file and CPU util file each have 3 ops
        self.confirm_ops_in_pipeline(3, ["GeneratorOp", "BatchOp", "EpochCtrlOp"], pipeline_file)
        self.confirm_cpuutil(3, cpu_util_file)

    def test_profiling_seq_pipelines_repeat(self):
        """
        Test with these 2 sequential pipelines:
        1) Generator -> Batch
        2) Generator -> Batch -> Repeat
        """
        file_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        file_id = file_name_map_rank_id[file_name]

        pipeline_file = self._pipeline_file + "_" + file_id + ".json"
        cpu_util_file = self._cpu_util_file + "_" + file_id + ".json"

        source = [(np.array([x]),) for x in range(64)]
        data2 = ds.GeneratorDataset(source, ["data"])
        data2 = data2.batch(16)

        # Test A - Call create_dict_iterator with 2 ops in pipeline
        num_iter = 0
        for _ in data2.create_dict_iterator(num_epochs=1):
            num_iter += 1
        assert num_iter == 4

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        # Confirm pipeline file and CPU util file each have 2 ops
        self.confirm_ops_in_pipeline(2, ["GeneratorOp", "BatchOp"], pipeline_file)
        self.confirm_cpuutil(2, cpu_util_file)

        # Test B - Add repeat op to pipeline.  Call create_dict_iterator with 3 ops in pipeline

        # Initialize and Start MindData profiling manager
        self.md_profiler.init()
        self.md_profiler.start()

        data2 = data2.repeat(5)
        num_iter = 0
        for _ in data2.create_dict_iterator(num_epochs=1):
            num_iter += 1
        assert num_iter == 20

        # Stop MindData Profiling and save output files to current working directory
        self.md_profiler.stop()
        self.md_profiler.save('./')

        # Confirm pipeline file and CPU util file each have 3 ops
        self.confirm_ops_in_pipeline(3, ["GeneratorOp", "BatchOp", "RepeatOp"], pipeline_file)
        self.confirm_cpuutil(3, cpu_util_file)
