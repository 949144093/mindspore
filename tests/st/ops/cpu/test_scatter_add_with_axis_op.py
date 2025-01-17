# Copyright 2022 Huawei Technologies Co., Ltd
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

import numpy as np
import pytest

import mindspore.context as context
import mindspore.nn as nn
from mindspore import Tensor
from mindspore import Parameter
from mindspore.ops import operations as P

context.set_context(mode=context.GRAPH_MODE, device_target='CPU')


def scatter_add_with_axis(input_x, indices, updates, axis):
    result = input_x.asnumpy().copy()
    indices_np = indices.asnumpy().copy()
    updates_np = updates.asnumpy().copy()

    i_len = indices_np.shape[0]
    j_len = indices_np.shape[1]

    if axis < 0:
        axis += len(result.shape)

    for i in range(i_len):
        for j in range(j_len):
            index = indices_np[i][j]
            if index < 0:
                index += result.shape[axis]
            if axis == 0:
                result[index][j] += updates_np[i][j]
            if axis == 1:
                result[i][index] += updates_np[i][j]

    return result


class TestScatterAddWithAxis(nn.Cell):
    def __init__(self, input_x, indices, updates, axis):
        super(TestScatterAddWithAxis, self).__init__()
        self.axis = axis
        self.input_x = Parameter(input_x, name="input_x")
        self.indices = Parameter(indices, name="indices")
        self.updates = Parameter(updates, name="updates")
        self.scatter_add_with_axis = P.ScatterAddWithAxis(self.axis)

    def construct(self):
        return self.scatter_add_with_axis(self.input_x, self.indices, self.updates)


@pytest.mark.level0
@pytest.mark.platform_x86_cpu
@pytest.mark.env_onecard
@pytest.mark.parametrize('dtype', [np.float32, np.float64, np.int32])
@pytest.mark.parametrize('index_dtype', [np.int32, np.int64])
@pytest.mark.parametrize('axis', [0, 1, -1])
def test_scatter_add_with_axis(dtype, index_dtype, axis):
    """
    Feature: Op ScatterAddWithAxis
    Description: Scatter update value according indices to output.
                output[indices[i][j]][j] += updates[i][j] if axis = 0,
                output[i][indices[i][j]] += updates[i][j] if axis = 1.
    Expectation: Ans is same as expected.
    """
    x = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=dtype))
    indices = Tensor(np.array([[1, -1, 2], [0, 2, 1]], dtype=index_dtype))
    update = Tensor(np.array([[1, 2, 2], [4, 5, 8]], dtype=dtype))

    ms_output = TestScatterAddWithAxis(x, indices, update, axis)()
    np_output = scatter_add_with_axis(x, indices, update, axis)
    print("ms_output:\n", ms_output.asnumpy())
    assert np.allclose(ms_output.asnumpy(), np_output)
