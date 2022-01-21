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
#ifndef MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_LOWER_BOUND_CPU_KERNEL_H_
#define MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_LOWER_BOUND_CPU_KERNEL_H_

#include <vector>

#include "backend/kernel_compiler/cpu/cpu_kernel.h"
#include "backend/kernel_compiler/cpu/cpu_kernel_factory.h"
namespace mindspore {
namespace kernel {
template <typename I, typename O>
class LowerBoundCPUKernel : public CPUKernel {
 public:
  LowerBoundCPUKernel() = default;
  ~LowerBoundCPUKernel() override = default;

  void InitKernel(const CNodePtr &kernel_node) override;

  bool Launch(const std::vector<AddressPtr> &inputs, const std::vector<AddressPtr> &workspace,
              const std::vector<AddressPtr> &outputs) override;

 private:
  std::vector<size_t> sorted_x_shape_;
  std::vector<size_t> values_shape_;
  std::vector<size_t> output_shape_;
  size_t sorted_x_num_;
  size_t values_num_;
  size_t output_num_;
};

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeFloat16).AddInputAttr(kNumberTypeFloat16).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, float16, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeFloat32).AddInputAttr(kNumberTypeFloat32).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, float, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeFloat64).AddInputAttr(kNumberTypeFloat64).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, double, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound, KernelAttr().AddInputAttr(kNumberTypeInt8).AddInputAttr(kNumberTypeInt8).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, int8_t, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeInt16).AddInputAttr(kNumberTypeInt16).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, int16_t, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeInt32).AddInputAttr(kNumberTypeInt32).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, int32_t, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeInt64).AddInputAttr(kNumberTypeInt64).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, int64_t, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeUInt8).AddInputAttr(kNumberTypeUInt8).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, uint8_t, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeUInt16).AddInputAttr(kNumberTypeUInt16).AddOutputAttr(kNumberTypeInt32),
  LowerBoundCPUKernel, uint16_t, int32_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeFloat16).AddInputAttr(kNumberTypeFloat16).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, float16, int64_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeFloat32).AddInputAttr(kNumberTypeFloat32).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, float, int64_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeFloat64).AddInputAttr(kNumberTypeFloat64).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, double, int64_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound, KernelAttr().AddInputAttr(kNumberTypeInt8).AddInputAttr(kNumberTypeInt8).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, int8_t, int64_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeInt16).AddInputAttr(kNumberTypeInt16).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, int16_t, int64_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeInt32).AddInputAttr(kNumberTypeInt32).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, int32_t, int64_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeInt64).AddInputAttr(kNumberTypeInt64).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, int64_t, int64_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeUInt8).AddInputAttr(kNumberTypeUInt8).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, uint8_t, int64_t);

MS_REG_CPU_KERNEL_T_S(
  LowerBound,
  KernelAttr().AddInputAttr(kNumberTypeUInt16).AddInputAttr(kNumberTypeUInt16).AddOutputAttr(kNumberTypeInt64),
  LowerBoundCPUKernel, uint16_t, int64_t);
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_LOWER_BOUND_CPU_KERNEL_H_