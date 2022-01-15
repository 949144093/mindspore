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

#include "tools/converter/quantizer/dynamic_quantizer.h"
#include "tools/converter/quantizer/weight_quantizer.h"
#include "tools/converter/quantizer/insert_quant_node_manager.h"

namespace mindspore::lite::quant {
int DynamicQuantizer::DoQuantize(FuncGraphPtr func_graph) {
  InsertQuantNodeManager manager;
  auto ret = manager.InsertDynamicQuantPass(func_graph);
  if (ret != RET_OK) {
    MS_LOG(ERROR) << "Insert dynamic quant failed.";
    return ret;
  }
  auto quantizer = WeightQuantizer(flags_);
  flags_.commonQuantParam.min_quant_weight_channel = 0;
  flags_.commonQuantParam.min_quant_weight_size = 0;
  const std::set<PrimitivePtr> support_weight_quant_nodes = {prim::kPrimMatMulFusion, prim::kPrimGather};
  const std::set<PrimitivePtr> symmetric_nodes = {prim::kPrimMatMulFusion};
  ret = quantizer.WeightQuant(func_graph, support_weight_quant_nodes, {}, symmetric_nodes);
  if (ret != RET_OK) {
    MS_LOG(ERROR) << "Weight Quant failed.";
    return ret;
  }
  return RET_OK;
}
}  // namespace mindspore::lite::quant