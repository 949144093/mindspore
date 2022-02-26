/**
 * Copyright 2022 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_FP32_GRAD_LSTM_GRAD_DATA_H_
#define MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_FP32_GRAD_LSTM_GRAD_DATA_H_

#include <vector>
#include "src/inner_kernel.h"
#include "nnacl/fp32_grad/lstm_grad_fp32.h"

namespace mindspore {
namespace kernel {
constexpr int LSTMGRADDATA_MAX_WORKSPACE_SIZE = 100000;
constexpr int LSTMGRADDATA_MAX_WEIGHTS_SIZE = 100000;
class LSTMGradDataCPUKernel : public InnerKernel {
 public:
  explicit LSTMGradDataCPUKernel(OpParameter *parameter, const std::vector<lite::Tensor *> &inputs,
                                 const std::vector<lite::Tensor *> &outputs, const lite::InnerContext *ctx)
      : InnerKernel(parameter, inputs, outputs, ctx), thread_count_(ctx->thread_num_) {
    lstm_param_ = reinterpret_cast<LstmParameter *>(op_parameter_);
  }
  ~LSTMGradDataCPUKernel() {}
  int Prepare() override;
  int ReSize() override;
  int Run() override;
  int DoGrad(int thread_id);

 private:
  int LstmBackpropUnidirectional(float *output, bool is_backward);

  int InitParam();
  int MallocRunBuffer();
  void FreeRunBuffer();
  int InitInputWeightBias();
  int InitStateWeightBias();

  int thread_count_;
  static const int dy_index = 1;
  static const int dH_index = 2;
  static const int dC_index = 3;
  static const int weights_index = 4;
  static const int cell_state_index = 6;
  static const int intermediate_data_index = 7;
  static const int dX_out_index = 0;
  static const int dH_out_index = 1;
  static const int dC_out_index = 2;
  static const int num_of_gates = 4;

  int input_size_align_ = 1;
  float *dA_tmp_ = nullptr;
  float *workspace_ = nullptr;

  int64_t weight_size_ = 0;
  int64_t weight_h_size_ = 0;
  int64_t input_size_;
  int64_t hidden_size_;
  int64_t num_layers_;
  int64_t batch_size_;
  int64_t seq_len_;
  int num_directions_;
  bool bidirectional_;
  bool has_bias_;
  size_t reserve_size_;
  int row_tile_ = 0;
  int col_tile_ = 0;
  int state_row_tile_ = 0;
  int state_col_tile_ = 0;
  int weight_batch_ = 0;
  bool state_is_vec_ = false;
  int input_thread_count_ = 0;
  int input_thread_stride_ = 0;

  LstmParameter *lstm_param_ = nullptr;
};
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_FP32_GRAD_LSTM_GRAD_DATA_H_