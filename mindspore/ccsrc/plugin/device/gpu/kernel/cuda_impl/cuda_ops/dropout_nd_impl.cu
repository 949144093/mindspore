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

#include <stdint.h>
#include "plugin/device/gpu/kernel/cuda_impl/cuda_ops/dropout_nd_impl.cuh"
#include "include/cuda_runtime.h"
#include "include/cuda_fp16.h"

template <typename T>
__global__ void DropoutNDForwardKernel(const T *input, bool *mask, T *output, float *rand_f, const size_t num_count,
                                       const float keep_prob, const float scale, const size_t num_per_chan) {
  size_t chan_idx;
  float drop_f;  // used in output calculations. Either 0.0 or 1.0.
  for (size_t i = blockIdx.x * blockDim.x + threadIdx.x; i < num_count; i += blockDim.x * gridDim.x) {
    chan_idx = i / num_per_chan;  // get channel index over all samples

    drop_f = rand_f[chan_idx] <= keep_prob;
    output[i] = static_cast<T>(scale * input[i] * drop_f);
    mask[i] = static_cast<bool>(drop_f);
  }
}

template <>
__global__ void DropoutNDForwardKernel(const half *input, bool *mask, half *output, float *rand_f,
                                       const size_t num_count, const float keep_prob, const float scale,
                                       const size_t num_per_chan) {
  size_t chan_idx;
  // To use in output calculations. Acts as a single float mask (either 0.0 or 1.0).
  float drop_f;
  // To use to temporarily convert input to float for calculations
  float input_f;
  for (size_t i = blockIdx.x * blockDim.x + threadIdx.x; i < num_count; i += blockDim.x * gridDim.x) {
    // Get channel index over all samples
    chan_idx = i / num_per_chan;
    input_f = __half2float(input[i]);
    drop_f = rand_f[chan_idx] <= keep_prob;
    output[i] = __float2half(scale * input_f * drop_f);  // convert to half
    mask[i] = static_cast<bool>(drop_f);
  }
}

template <typename T>
void DropoutNDForward(const T *input, bool *mask, T *output, float *rand_f, const size_t num_count,
                      const float keep_prob, const size_t num_per_chan, cudaStream_t cuda_stream) {
  // To used to scale output, maintains expected value during training
  const float scale = 1.f / keep_prob;
  DropoutNDForwardKernel<<<GET_BLOCKS(num_count), GET_THREADS, 0, cuda_stream>>>(input, mask, output, rand_f, num_count,
                                                                                 keep_prob, scale, num_per_chan);
}

template CUDA_LIB_EXPORT void DropoutNDForward<float>(const float *input, bool *mask, float *output, float *rand_f,
                                                      const size_t num_count, const float keep_prob,
                                                      const size_t num_per_chan, cudaStream_t cuda_stream);

template CUDA_LIB_EXPORT void DropoutNDForward<double>(const double *input, bool *mask, double *output, float *rand_f,
                                                       const size_t num_count, const float keep_prob,
                                                       const size_t num_per_chan, cudaStream_t cuda_stream);

template CUDA_LIB_EXPORT void DropoutNDForward<half>(const half *input, bool *mask, half *output, float *rand_f,
                                                     const size_t num_count, const float keep_prob,
                                                     const size_t num_per_chan, cudaStream_t cuda_stream);
template CUDA_LIB_EXPORT void DropoutNDForward<int8_t>(const int8_t *input, bool *mask, int8_t *output, float *rand_f,
                                                       const size_t num_count, const float keep_prob,
                                                       const size_t num_per_chan, cudaStream_t cuda_stream);
template CUDA_LIB_EXPORT void DropoutNDForward<int16_t>(const int16_t *input, bool *mask, int16_t *output,
                                                        float *rand_f, const size_t num_count, const float keep_prob,
                                                        const size_t num_per_chan, cudaStream_t cuda_stream);
template CUDA_LIB_EXPORT void DropoutNDForward<int32_t>(const int32_t *input, bool *mask, int32_t *output,
                                                        float *rand_f, const size_t num_count, const float keep_prob,
                                                        const size_t num_per_chan, cudaStream_t cuda_stream);
template CUDA_LIB_EXPORT void DropoutNDForward<int64_t>(const int64_t *input, bool *mask, int64_t *output,
                                                        float *rand_f, const size_t num_count, const float keep_prob,
                                                        const size_t num_per_chan, cudaStream_t cuda_stream);
