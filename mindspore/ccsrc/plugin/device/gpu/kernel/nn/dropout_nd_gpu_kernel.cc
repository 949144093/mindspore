/**
 * Copyright 2021-2022 Huawei Technologies Co., Ltd
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

#include "plugin/device/gpu/kernel/nn/dropout_nd_gpu_kernel.h"
#include <functional>
#include <utility>
#include <string>
#include <algorithm>
#include <memory>
#include "include/curand.h"
#include "mindspore/core/ops/dropout_nd.h"
#include "abstract/utils.h"
#include "plugin/device/gpu/kernel/cuda_impl/cuda_ops/dropout_nd_impl.cuh"

namespace mindspore {
namespace kernel {
bool DropoutNDGpuKernelMod::CheckDropOutNdShape() {
  constexpr size_t k4d = 4;
  constexpr size_t k5d = 5;
  constexpr size_t k4d_remain_dim = 2;
  constexpr size_t k5d_remain_dim = 3;
  size_t nd_dims = input_shape_.size();
  size_t expected_dims;
  size_t last_remain_dim;
  if (kernel_name_ == prim::kPrimDropout2D->name()) {
    // Dropout2D ---> data format NCHW(4 dims)
    expected_dims = k4d;
    last_remain_dim = k4d_remain_dim;
  } else if (kernel_name_ == prim::kPrimDropout3D->name()) {
    // Dropout3D ---> data format NCDHW(5 dims)
    expected_dims = k5d;
    last_remain_dim = k5d_remain_dim;
  } else {
    MS_LOG(ERROR) << "For 'DropoutNd' should only support Dropout2D or Dropout3D, right now, but got " << kernel_name_;
    return false;
  }
  if (nd_dims < expected_dims) {
    MS_LOG(ERROR) << "For '" << kernel_name_ << " input dims should larger than " << expected_dims << "D, but got  "
                  << nd_dims << "D.";
    return false;
  }
  // Flatten input shape to [batch, channels, XHW] for VMap.
  batches_ = 1;
  for (size_t i = 0; i < nd_dims - expected_dims; ++i) {
    batches_ *= input_shape_.at(i);
  }
  channels_ = 1;
  for (size_t i = nd_dims - expected_dims; i < nd_dims - last_remain_dim; ++i) {
    channels_ *= input_shape_.at(i);
  }
  return true;
}

bool DropoutNDGpuKernelMod::Init(const BaseOperatorPtr &base_operator, const std::vector<KernelTensorPtr> &inputs,
                                 const std::vector<KernelTensorPtr> &outputs) {
  kernel_name_ = base_operator->name();
  if (inputs.empty() || outputs.empty()) {
    MS_LOG(ERROR) << "For '" << kernel_name_ << "' got empty inputs or outputs, which is invalid.";
    return false;
  }
  if (kernel_name_ == prim::kPrimDropout2D->name()) {
    auto kernel_ptr = std::make_shared<ops::Dropout2D>(base_operator->GetPrim());
    keep_prob_ = kernel_ptr->get_keep_prob();
  } else if (kernel_name_ == prim::kPrimDropout3D->name()) {
    auto kernel_ptr = std::make_shared<ops::Dropout3D>(base_operator->GetPrim());
    keep_prob_ = kernel_ptr->get_keep_prob();
  } else {
    MS_LOG(ERROR) << "For 'DropoutNDGpuKernelMod' should get Dropout2D or Dropout3D but get invalid kernel name : "
                  << kernel_name_;
    return false;
  }
  if ((keep_prob_ < 0.0) || (keep_prob_ > 1.0)) {
    MS_LOG(ERROR) << "For '" << kernel_name_ << "', the value of 'keep_prob' must be in range [0.0, 1.0], "
                  << "but got " << keep_prob_;
    return false;
  }
  auto kernel_attr = GetKernelAttrFromTensors(inputs, outputs);
  auto [is_match, index] = MatchKernelAttr(kernel_attr, GetOpSupport());
  if (!is_match) {
    MS_LOG(ERROR) << "For '" << kernel_name_ << "' does not support this kernel type: " << kernel_attr;
    return false;
  }
  kernel_func_ = func_list_[index].second;
  unit_size_ = abstract::TypeIdSize(kernel_attr.GetInputAttr(kIndex0).first);
  if (!states_init_) {
    CHECK_CURAND_RET_WITH_EXCEPT(curandCreateGenerator(&cu_rand_generator_, CURAND_RNG_PSEUDO_DEFAULT),
                                 "Failed to create generator");
    MS_EXCEPTION_IF_NULL(cu_rand_generator_);
    CHECK_CURAND_RET_WITH_EXCEPT(curandSetPseudoRandomGeneratorSeed(cu_rand_generator_, time(NULL)),
                                 "Failed to SetPseudoRandomGeneratorSeed");
    states_init_ = true;
  }
  cudnn_handle_ = device::gpu::GPUDeviceManager::GetInstance().GetCudnnHandle();
  return true;
}

int DropoutNDGpuKernelMod::Resize(const BaseOperatorPtr &base_operator, const std::vector<KernelTensorPtr> &inputs,
                                  const std::vector<KernelTensorPtr> &outputs,
                                  const std::map<uint32_t, tensor::TensorPtr> &) {
  ResetResource();
  for (const auto &input : inputs) {
    // If any input shape contains -1, means input shape is dynamic, so just return do nothing.
    auto input_shape = input->GetShapeVector();
    if (!IsValidShape(input_shape)) {
      return KRET_INVALID_SHAPE;
    }
  }
  auto input_shape = inputs.at(kIndex0)->GetShapeVector();
  (void)std::transform(input_shape.begin(), input_shape.end(), std::back_inserter(input_shape_), LongToSize);
  input_elements_ = std::accumulate(input_shape_.begin(), input_shape_.end(), 1, std::multiplies<size_t>());
  if (!CheckDropOutNdShape() || channels_ == 0) {
    MS_LOG(ERROR) << "For '" << kernel_name_ << "' input dims is invalid, must be 4D or 5D "
                  << " but got " << input_shape_.size() << "D";
    return KRET_RESIZE_FAILED;
  }
  size_t input_size = input_elements_ * unit_size_;
  input_size_list_.emplace_back(input_size);
  size_t output_size = input_elements_ * unit_size_;
  size_t output_mask_size = input_elements_ * sizeof(bool);
  output_size_list_.emplace_back(output_size);
  output_size_list_.emplace_back(output_mask_size);
  // The number of elements per channel
  num_per_channel_ = input_elements_ / channels_ / batches_;
  size_t workspace_size = channels_ * sizeof(float);
  workspace_size_list_.emplace_back(workspace_size);
  return KRET_OK;
}

void DropoutNDGpuKernelMod::ResetResource() noexcept {
  is_null_input_ = false;
  input_elements_ = 0;
  channels_ = 0;
  num_per_channel_ = 0;
  input_size_list_.clear();
  output_size_list_.clear();
  workspace_size_list_.clear();
}

template <typename T>
bool DropoutNDGpuKernelMod::LaunchKernel(const std::vector<AddressPtr> &inputs,
                                         const std::vector<AddressPtr> &workspace,
                                         const std::vector<AddressPtr> &outputs) {
  T *input = GetDeviceAddress<T>(inputs, kIndex0);
  T *output = GetDeviceAddress<T>(outputs, kIndex0);
  bool *mask = GetDeviceAddress<bool>(outputs, kIndex1);
  auto *rand_f = GetDeviceAddress<float>(workspace, kIndex0);
  // When keep_prob equal to 0.0, output default to zero, mask default to false.
  if (keep_prob_ == 0.0) {
    CHECK_CUDA_RET_WITH_ERROR_NOTRACE(cudaMemset(output, 0, outputs.at(kIndex0)->size),
                                      "For DropoutNDGpuKernelMod failed to cudaMemset");
    // Default zero to be false.
    CHECK_CUDA_RET_WITH_ERROR_NOTRACE(cudaMemset(mask, 0, outputs.at(kIndex1)->size),
                                      "For DropoutNDGpuKernelMod failed to cudaMemset");
    return true;
  }
  CHECK_CURAND_RET_WITH_EXCEPT(curandSetStream(cu_rand_generator_, reinterpret_cast<cudaStream_t>(cuda_stream_)),
                               "For DropoutNDGpuKernelMod failed to set stream for generator");
  // For cu_rand_generator only supports float or double.
  // To generate random float data for every channel.
  CHECK_CURAND_RET_WITH_EXCEPT(curandGenerateUniform(cu_rand_generator_, rand_f, channels_),
                               "For DropoutNDGpuKernelMod failed to generate uniform");
  DropoutNDForward(input, mask, output, rand_f, input_elements_, keep_prob_, num_per_channel_,
                   reinterpret_cast<cudaStream_t>(cuda_stream_));
  return true;
}

std::vector<std::pair<KernelAttr, DropoutNDGpuKernelMod::DropoutNdFunc>> DropoutNDGpuKernelMod::func_list_ = {
  {KernelAttr().AddInputAttr(kNumberTypeInt8).AddOutputAttr(kNumberTypeInt8).AddOutputAttr(kNumberTypeBool),
   &DropoutNDGpuKernelMod::LaunchKernel<int8_t>},
  {KernelAttr().AddInputAttr(kNumberTypeInt16).AddOutputAttr(kNumberTypeInt16).AddOutputAttr(kNumberTypeBool),
   &DropoutNDGpuKernelMod::LaunchKernel<int16_t>},
  {KernelAttr().AddInputAttr(kNumberTypeInt32).AddOutputAttr(kNumberTypeInt32).AddOutputAttr(kNumberTypeBool),
   &DropoutNDGpuKernelMod::LaunchKernel<int>},
  {KernelAttr().AddInputAttr(kNumberTypeInt64).AddOutputAttr(kNumberTypeInt64).AddOutputAttr(kNumberTypeBool),
   &DropoutNDGpuKernelMod::LaunchKernel<int64_t>},
  {KernelAttr().AddInputAttr(kNumberTypeFloat16).AddOutputAttr(kNumberTypeFloat16).AddOutputAttr(kNumberTypeBool),
   &DropoutNDGpuKernelMod::LaunchKernel<half>},
  {KernelAttr().AddInputAttr(kNumberTypeFloat32).AddOutputAttr(kNumberTypeFloat32).AddOutputAttr(kNumberTypeBool),
   &DropoutNDGpuKernelMod::LaunchKernel<float>},
  {KernelAttr().AddInputAttr(kNumberTypeFloat64).AddOutputAttr(kNumberTypeFloat64).AddOutputAttr(kNumberTypeBool),
   &DropoutNDGpuKernelMod::LaunchKernel<double>}};

std::vector<KernelAttr> DropoutNDGpuKernelMod::GetOpSupport() {
  std::vector<KernelAttr> support_list;
  (void)std::transform(func_list_.begin(), func_list_.end(), std::back_inserter(support_list),
                       [](const std::pair<KernelAttr, DropoutNdFunc> &pair) { return pair.first; });
  return support_list;
}
MS_KERNEL_FACTORY_REG(NativeGpuKernelMod, Dropout2D, DropoutNDGpuKernelMod);
MS_KERNEL_FACTORY_REG(NativeGpuKernelMod, Dropout3D, DropoutNDGpuKernelMod);
}  // namespace kernel
}  // namespace mindspore
