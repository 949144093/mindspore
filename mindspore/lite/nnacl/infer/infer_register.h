/**
 * Copyright 2021 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef MINDSPORE_LITE_NNACL_INFER_INFER_REGISTER_H_
#define MINDSPORE_LITE_NNACL_INFER_INFER_REGISTER_H_

#include "nnacl/tensor_c.h"
#include "nnacl/op_base.h"
#include "nnacl/infer/infer.h"

#ifdef __cplusplus
extern "C" {
#endif
enum PrimType {
  PrimType_NONE = 0,
  PrimType_Abs = 1,
  PrimType_Activation = 2,
  PrimType_ActivationGrad = 3,
  PrimType_Adam = 4,
  PrimType_AddFusion = 5,
  PrimType_AdderFusion = 6,
  PrimType_AddGrad = 7,
  PrimType_AddN = 8,
  PrimType_All = 9,
  PrimType_ApplyMomentum = 10,
  PrimType_ArgMaxFusion = 11,
  PrimType_ArgMinFusion = 12,
  PrimType_Assert = 13,
  PrimType_Assign = 14,
  PrimType_AssignAdd = 15,
  PrimType_AudioSpectrogram = 16,
  PrimType_AvgPoolFusion = 17,
  PrimType_AvgPoolGrad = 18,
  PrimType_BatchNorm = 19,
  PrimType_BatchNormGrad = 20,
  PrimType_BatchToSpace = 21,
  PrimType_BatchToSpaceND = 22,
  PrimType_BiasAdd = 23,
  PrimType_BinaryCrossEntropy = 24,
  PrimType_BinaryCrossEntropyGrad = 25,
  PrimType_BiasAddGrad = 26,
  PrimType_BroadcastTo = 27,
  PrimType_Cast = 28,
  PrimType_Ceil = 29,
  PrimType_Clip = 30,
  PrimType_Concat = 31,
  PrimType_ControlDepend = 32,
  PrimType_Conv2DBackpropFilterFusion = 33,
  PrimType_Conv2DBackpropInputFusion = 34,
  PrimType_Conv2DFusion = 35,
  PrimType_Conv2dTransposeFusion = 36,
  PrimType_Cos = 37,
  PrimType_ConstantOfShape = 38,
  PrimType_Crop = 39,
  PrimType_CustomExtractFeatures = 40,
  PrimType_CustomNormalize = 41,
  PrimType_CustomPredict = 42,
  PrimType_DeConv2DGradFilter = 43,
  PrimType_Depend = 44,
  PrimType_DepthToSpace = 45,
  PrimType_DetectionPostProcess = 46,
  PrimType_DivFusion = 47,
  PrimType_DivGrad = 48,
  PrimType_Dropout = 49,
  PrimType_DropoutGrad = 50,
  PrimType_Elu = 51,
  PrimType_Eltwise = 52,
  PrimType_Equal = 53,
  PrimType_EmbeddingLookupFusion = 54,
  PrimType_ExpFusion = 55,
  PrimType_ExpandDims = 56,
  PrimType_FakeQuantWithMinMaxVars = 57,
  PrimType_FakeQuantWithMinMaxVarsPerChannel = 58,
  PrimType_FftReal = 59,
  PrimType_FftImag = 60,
  PrimType_Flatten = 61,
  PrimType_FlattenGrad = 62,
  PrimType_Floor = 63,
  PrimType_FloorDiv = 64,
  PrimType_FloorMod = 65,
  PrimType_Fill = 66,
  PrimType_FullConnection = 67,
  PrimType_FusedBatchNorm = 68,
  PrimType_Gather = 69,
  PrimType_GatherNd = 70,
  PrimType_Greater = 71,
  PrimType_GreaterEqual = 72,
  PrimType_HashtableLookup = 73,
  PrimType_InstanceNorm = 74,
  PrimType_LayerNormFusion = 75,
  PrimType_LeakyRelu = 76,
  PrimType_Less = 77,
  PrimType_LessEqual = 78,
  PrimType_Log = 79,
  PrimType_LogGrad = 80,
  PrimType_LogicalAnd = 81,
  PrimType_LogicalNot = 82,
  PrimType_LogicalOr = 83,
  PrimType_LpNormalization = 84,
  PrimType_LRN = 85,
  PrimType_LshProjection = 86,
  PrimType_LSTM = 87,
  PrimType_L2NormalizeFusion = 88,
  PrimType_MatMul = 89,
  PrimType_Maximum = 90,
  PrimType_MaximumGrad = 91,
  PrimType_MaxPoolFusion = 92,
  PrimType_MaxPoolGrad = 93,
  PrimType_Merge = 94,
  PrimType_Mfcc = 95,
  PrimType_Minimum = 96,
  PrimType_MinimumGrad = 97,
  PrimType_Mod = 98,
  PrimType_MulFusion = 99,
  PrimType_MulGrad = 100,
  PrimType_Neg = 101,
  PrimType_NegGrad = 102,
  PrimType_NotEqual = 103,
  PrimType_NonMaxSuppression = 104,
  PrimType_OneHot = 105,
  PrimType_OnesLike = 106,
  PrimType_PadFusion = 107,
  PrimType_PartialFusion = 108,
  PrimType_PowerGrad = 109,
  PrimType_PowFusion = 110,
  PrimType_PriorBox = 111,
  PrimType_PReLUFusion = 112,
  PrimType_QuantDTypeCast = 113,
  PrimType_Rank = 114,
  PrimType_Range = 115,
  PrimType_Reciprocal = 116,
  PrimType_RealDiv = 117,
  PrimType_ReduceFusion = 118,
  PrimType_Reshape = 119,
  PrimType_Resize = 120,
  PrimType_ReverseSequence = 121,
  PrimType_ReverseV2 = 122,
  PrimType_Rfft = 123,
  PrimType_ROIPooling = 124,
  PrimType_Round = 125,
  PrimType_Rsqrt = 126,
  PrimType_ScaleFusion = 127,
  PrimType_ScatterNd = 128,
  PrimType_SGD = 129,
  PrimType_Shape = 130,
  PrimType_SigmoidCrossEntropyWithLogits = 131,
  PrimType_SigmoidCrossEntropyWithLogitsGrad = 132,
  PrimType_Sin = 133,
  PrimType_SkipGram = 134,
  PrimType_SliceFusion = 135,
  PrimType_SmoothL1Loss = 136,
  PrimType_SmoothL1LossGrad = 137,
  PrimType_Softmax = 138,
  PrimType_SoftmaxCrossEntropyWithLogits = 139,
  PrimType_SpaceToBatch = 140,
  PrimType_SpaceToBatchND = 141,
  PrimType_SpaceToDepth = 142,
  PrimType_SparseSoftmaxCrossEntropyWithLogits = 143,
  PrimType_SparseToDense = 144,
  PrimType_Split = 145,
  PrimType_Sqrt = 146,
  PrimType_Squeeze = 147,
  PrimType_Square = 148,
  PrimType_SquaredDifference = 149,
  PrimType_Stack = 150,
  PrimType_StridedSlice = 151,
  PrimType_SubFusion = 152,
  PrimType_SubGrad = 153,
  PrimType_Switch = 154,
  PrimType_TensorListFromTensor = 155,
  PrimType_TensorListGetItem = 156,
  PrimType_TensorListReserve = 157,
  PrimType_TensorListSetItem = 158,
  PrimType_TensorListStack = 159,
  PrimType_TileFusion = 160,
  PrimType_TopKFusion = 161,
  PrimType_Transpose = 162,
  PrimType_Unique = 163,
  PrimType_UnsortedSegmentSum = 164,
  PrimType_Unsqueeze = 165,
  PrimType_Unstack = 166,
  PrimType_While = 167,
  PrimType_Where = 168,
  PrimType_ZerosLike = 169,
  PrimType_Select = 170,
  PrimType_If = 171,
  PrimType_GRU = 172,
  PrimType_NonZero = 173,
  PrimType_InvertPermutation = 174,
  PrimType_Size = 175,
  PrimType_RandomStandardNormal = 176,
  PrimType_CropAndResize = 177,
  PrimType_Erf = 178,
  PrimType_StridedSliceGrad = 179,
  PrimType_IsFinite = 180,
  PrimType_LinSpace = 181,
  PrimType_UniformReal = 182,
  PrimType_AbsGrad = 183,
  PrimType_RsqrtGrad = 184,
  PrimType_SqrtGrad = 185,
  PrimType_LayerNormGrad = 186,
  PrimType_ResizeGrad = 187,
  PrimType_Splice = 188,
  PrimType_MIN = PrimType_NONE,
  PrimType_MAX = PrimType_Splice
};

void RegInfer(int prim_type, InferShape func);

#define REG_INFER(op, type, func) \
  __attribute__((constructor(102))) void Reg##op##Infer() { RegInfer(type, func); }
#ifdef __cplusplus
}
#endif
#endif  // MINDSPORE_LITE_NNACL_INFER_INFER_REGISTER_H_
