# Copyright 2021 Huawei Technologies Co., Ltd
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
"""Operators for scipy submodule"""
from ..ops import PrimitiveWithInfer, prim_attr_register
from .._checkparam import Validator as validator
from ..common import dtype as mstype
from .. import nn


class SolveTriangular(PrimitiveWithInfer):
    """
    SolveTriangular op frontend implementation.

    Args:
        lower (bool): The input Matrix :math:`A` is lower triangular matrix or not.
        unit_diagonal (bool): If True, diagonal elements of :math:`A` are assumed to be 1 and
            will not be referenced.
        trans (0, 1, 2, 'N', 'T', 'C', optional):
            Type of system to solve:

            ========  =========
            trans     system
            ========  =========
            0 or 'N'  a x  = b
            1 or 'T'  a^T x = b
            2 or 'C'  a^H x = b
            ========  =========

    Inputs:
        - **A** (Tensor) - A triangular matrix of shape :math:`(N, N)`.
        - **b** (Tensor) - A tensor of shape :math:`(M,)` or :math:`(M, N)`. Right-hand side matrix in :math:`A x = b`.

    Returns:
        - **x** (Tensor) - A tensor of shape :math:`(M,)` or :math:`(M, N)`,
            which is the solution to the system :math:`A x = b`.
            Shape of :math:`x` matches :math:`b`.

    Supported Platforms:
        ``GPU`` ``CPU``

    Examples:
        Solve the lower triangular system :math:`A x = b`, where:

                 [3  0  0  0]       [4]
            A =  [2  1  0  0]   b = [2]
                 [1  0  1  0]       [4]
                 [1  1  1  1]       [2]

        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> import mindspore.numpy as mnp
        >>> from mindspore.scipy.ops import SolveTriangular
        >>> A = Tensor(onp.array([[3, 0, 0, 0], [2, 1, 0, 0], [1, 0, 1, 0], [1, 1, 1, 1]], onp.float64))
        >>> b = Tensor(onp.array([4, 2, 4, 2], onp.float64))
        >>> solve_triangular = SolveTriangular(lower=True, unit_diagonal=False, trans='N')
        >>> x = solve_triangular(A, b)
        >>> x
        Tensor(shape=[4], dtype=Float64, value= [ 1.33333333e+00, -6.66666667e-01,  2.66666667e+00, -1.33333333e+00])
        >>> mnp.dot(A, x)  # Check the result
        Tensor(shape=[4], dtype=Float64, value= [ 4.00000000e+00,  2.00000000e+00,  4.00000000e+00,  2.00000000e+00])
    """

    @prim_attr_register
    def __init__(self, lower: bool, unit_diagonal: bool, trans: str):
        """Initialize SolveTriangular"""
        super(SolveTriangular, self).__init__("SolveTriangular")
        self.lower = validator.check_value_type(
            "lower", lower, [bool], self.name)
        self.unit_diagonal = validator.check_value_type(
            "unit_diagonal", unit_diagonal, [bool], self.name)
        self.trans = validator.check_value_type(
            "trans", trans, [str], self.name)

        self.init_prim_io_names(inputs=['A', 'b'], outputs=['output'])

    def __infer__(self, A, b):
        out_shapes = b['shape']
        return {
            'shape': tuple(out_shapes),
            'dtype': A['dtype'],
            'value': None
        }

    def infer_dtype(self, x_dtype):
        validator.check_tensor_dtype_valid(x_dtype, [mstype.float32, mstype.float64],
                                           self.name, True)
        return x_dtype


class Cholesky(PrimitiveWithInfer):
    """
    Inner API for _Cholesky base class.
    """

    @prim_attr_register
    def __init__(self, lower=False, clean=True, split_dim=0):
        super().__init__("Cholesky")
        self.init_prim_io_names(inputs=['x1'], outputs=['y'])
        self.lower = validator.check_value_type("lower", lower, [bool], self.lower)
        self.clean = validator.check_value_type("clean", clean, [bool], self.clean)
        self.lower = lower
        self.add_prim_attr('lower', self.lower)
        self.clean = clean
        self.add_prim_attr('clean', self.clean)
        self.split_dim = split_dim
        self.add_prim_attr('split_dim', self.split_dim)

    def infer_shape(self, x1_shape):
        if self.split_dim != 0:
            height = x1_shape[0]
            width = x1_shape[1]
            if height <= self.split_dim:
                out_shape = [1, height, width]
            else:
                batch = height // self.split_dim
                if height != batch * self.split_dim:
                    batch += 1
                out_shape = [batch, self.split_dim, self.split_dim]
        else:
            out_shape = x1_shape
        return out_shape

    def infer_dtype(self, x1_dtype):
        validator.check_tensor_dtype_valid('x1', x1_dtype, [mstype.float32, mstype.float64], self.name)
        return x1_dtype


class CholeskySolver(PrimitiveWithInfer):
    """Solve the linear equations A x = b, given the Cholesky factorization of A.

    Parameters
    ----------
    lower : bool, optional
        Whether to compute the upper or lower triangular Cholesky factorization
        (Default: upper-triangular)
    b : array
        Right-hand side

    Inputs:
        - **A** (Tensor) - A matrix of shape :math:`(M, M)` to be decomposed.
        - **b** (Tensor) - A tensor of shape :math:`(M,)` or :math:`(..., M)`.
                           Right-hand side matrix in :math:`A x = b`.
    Returns
    -------
    x : array
        The solution to the system A x = b
    Supported Platforms:
        ``CPU`` ``GPU``
    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.ops import CholeskySolver
        >>> from mindspore.scipy.linalg import cho_factor

        >>> A = Tensor(onp.array([[9, 3, 1, 5], [3, 7, 5, 1], [1, 5, 9, 2], [5, 1, 2, 6]]))
        >>> b = Tensor(onp.array([1.0, 1.0, 1.0, 1.0], dtype=onp.dtype))
        >>> c, lower = cho_factor(A)
        >>> cholesky_solver = CholeskySolver(lower=lower)
        >>> x = cholesky_solver(c, b)
    """

    @prim_attr_register
    def __init__(self, lower=False):
        super().__init__(name="CholeskySolver")
        self.lower = validator.check_value_type("lower", lower, [bool], self.lower)
        self.init_prim_io_names(inputs=['x', 'b'], outputs=['y'])

    def __infer__(self, x, b):
        b_shape = b['shape']
        x_dtype = x['dtype']
        return {
            'shape': tuple(b_shape),
            'dtype': x_dtype,
            'value': None
        }


class Eigh(PrimitiveWithInfer):
    """
    Eigh decomposition(Symmetric matrix)
    Ax = lambda * x
    """

    @prim_attr_register
    def __init__(self, compute_eigenvectors):
        super().__init__(name="Eigh")
        self.init_prim_io_names(inputs=['A', 's'], outputs=['output', 'output_v'])
        self.compute_eigenvectors = validator.check_value_type(
            "compute_eigenvectors", compute_eigenvectors, [bool], self.name)

    def __infer__(self, A, s):
        shape = {
            'shape': ((A['shape'][0],), (A['shape'][0], A['shape'][0])),
            'dtype': (A['dtype'], A['dtype']),
            'value': None
        }
        if A['dtype'] == mstype.tensor_type(mstype.float32):
            shape = {
                'shape': ((A['shape'][0],), (A['shape'][0], A['shape'][0])),
                'dtype': (mstype.float32, mstype.float32),
                'value': None
            }
        elif A['dtype'] == mstype.tensor_type(mstype.float64):
            shape = {
                'shape': ((A['shape'][0],), (A['shape'][0], A['shape'][0])),
                'dtype': (mstype.float64, mstype.float64),
                'value': None
            }
        elif A['dtype'] == mstype.tensor_type(mstype.complex64):
            shape = {
                'shape': ((A['shape'][0],), (A['shape'][0], A['shape'][0])),
                'dtype': (A['dtype'], A['dtype']),
                'value': None
            }
        elif A['dtype'] == mstype.tensor_type(mstype.complex128):
            shape = {
                'shape': ((A['shape'][0],), (A['shape'][0], A['shape'][0])),
                'dtype': (mstype.complex128, mstype.complex128),
                'value': None
            }
        return shape


class EighNet(nn.Cell):
    """
    EigenValue /eigenvector solver for symmetric/Hermitian matrix
    Ax = lambda * x
    """
    def __init__(self, b):
        super(EighNet, self).__init__()
        self.b = b
        self.eigh = Eigh(b)

    def construct(self, A, s=True):
        r = self.eigh(A, s)
        if self.b:
            return (r[0], r[1])
        return (r[0],)


class Eig(PrimitiveWithInfer):
    """
    Eig decomposition,(generic matrix)
    Ax = lambda * x
    """

    @prim_attr_register
    def __init__(self, compute_eigenvectors):
        super().__init__(name="Eig")
        self.init_prim_io_names(inputs=['A'], outputs=['output', 'output_v'])
        self.compute_eigenvectors = validator.check_value_type(
            "compute_eigenvectors", compute_eigenvectors, [bool], self.name)

    def __infer__(self, A):
        shape = {}
        if A['dtype'] == mstype.tensor_type(mstype.float32) or A['dtype'] == mstype.tensor_type(mstype.complex64):
            shape = {
                'shape': ((A['shape'][0],), (A['shape'][0], A['shape'][0])),
                'dtype': (mstype.complex64, mstype.complex64),
                'value': None
            }
        elif A['dtype'] == mstype.tensor_type(mstype.float64) or A['dtype'] == mstype.tensor_type(mstype.complex128):
            shape = {
                'shape': ((A['shape'][0],), (A['shape'][0], A['shape'][0])),
                'dtype': (mstype.complex128, mstype.complex128),
                'value': None
            }
        return shape


class EigNet(nn.Cell):
    """
    EigenValue /eigenvector solver for generic matrix
    Ax = lambda * x
    """
    def __init__(self, b):
        super(EigNet, self).__init__()
        self.b = b
        self.eig = Eig(b)

    def construct(self, A):
        r = self.eig(A)
        if self.b:
            return (r[0], r[1])
        return (r[0],)
