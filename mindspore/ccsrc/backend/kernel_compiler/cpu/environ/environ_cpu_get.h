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
#ifndef MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_ENVIRON_ENVIRON_CPU_GET_H_
#define MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_ENVIRON_ENVIRON_CPU_GET_H_

#include <vector>
#include <string>
#include "backend/kernel_compiler/cpu/cpu_kernel.h"
#include "backend/kernel_compiler/cpu/cpu_kernel_factory.h"

namespace mindspore {
namespace kernel {
class EnvironGetCPUKernel : public CPUKernel {
 public:
  EnvironGetCPUKernel() : value_type_attr_(kObjectTypeTensorType), handle_size_(0), key_size_(0), value_size_(0) {}
  ~EnvironGetCPUKernel() = default;

  const std::vector<size_t> &GetInputSizeList() const override;
  const std::vector<size_t> &GetOutputSizeList() const override;
  const std::vector<size_t> &GetWorkspaceSizeList() const override;
  bool Launch(const std::vector<AddressPtr> &inputs, const std::vector<AddressPtr> &workspace,
              const std::vector<AddressPtr> &outputs) override;
  void InitKernel(const CNodePtr &node) override;

 private:
  // The type of env tensor get.
  TypeId value_type_attr_;

  size_t handle_size_;
  size_t key_size_;
  size_t value_size_;

  std::vector<size_t> input_size_list_;
  std::vector<size_t> output_size_list_;
  std::vector<size_t> workspace_size_list_;
};

MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddOutputAttr(kNumberTypeInt64),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt32)
                    .AddOutputAttr(kNumberTypeInt32),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt16)
                    .AddOutputAttr(kNumberTypeInt16),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeUInt32)
                    .AddOutputAttr(kNumberTypeUInt32),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeUInt16)
                    .AddOutputAttr(kNumberTypeUInt16),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeUInt8)
                    .AddOutputAttr(kNumberTypeUInt8),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeUInt64)
                    .AddOutputAttr(kNumberTypeUInt64),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeFloat32)
                    .AddOutputAttr(kNumberTypeFloat32),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeFloat16)
                    .AddOutputAttr(kNumberTypeFloat16),
                  EnvironGetCPUKernel);
MS_REG_CPU_KERNEL(EnvironGet,
                  KernelAttr()
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeInt64)
                    .AddInputAttr(kNumberTypeBool)
                    .AddOutputAttr(kNumberTypeBool),
                  EnvironGetCPUKernel);
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_ENVIRON_ENVIRON_CPU_GET_H_
