mindspore.ops.bitwise_and
========================

.. py:function:: mindspore.ops.bitwise_and(x, y)

    逐元素执行两个Tensor的与运算。

    .. math::

        out_i = x_{i} \wedge y_{i}

    输入 `x` 和 `y` 遵循 `隐式类型转换规则 <https://www.mindspore.cn/docs/zh-CN/master/note/operator_list_implicit.html>`_ ，使数据类型保持一致。
    如果 `x` 和 `y` 数据类型不同，低精度数据类型将自动转换成高精度数据类型。

    **参数：**

    - **x** (Tensor) - 第一个输入，是一个数据类型为uint16、int16或int32的Tensor。
    - **y** (Tensor) - 第二个输入，是一个与 `x` 相同类型的Tensor。

    **返回：**

    Tensor，是一个与 `x` 相同类型的Tensor。

    **异常：**

    - **TypeError** - `x` 或 `y` 不是Tensor。
    - **RuntimeError** - 输入的 `x` 与 `y` 需要进行参数类型转换时不符合转换规则。
