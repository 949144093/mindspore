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

#ifndef MINDSPORE_CCSRC_RUNTIME_FRAMEWORK_ACTOR_RPC_RECV_ACTOR_H_
#define MINDSPORE_CCSRC_RUNTIME_FRAMEWORK_ACTOR_RPC_RECV_ACTOR_H_

#include <set>
#include <vector>
#include <string>
#include <memory>
#include "runtime/graph_scheduler/actor/rpc/rpc_actor.h"

namespace mindspore {
namespace runtime {
// RecvActor inherits from RpcActor and it's used to receive data from other processes.
class RecvActor : public RpcActor {
 public:
  explicit RecvActor(const std::string &name, const CNodePtr &kernel, const DeviceContext *device_context,
                     const AID &memory_manager_aid, const AID *debug_aid, const AID *recorder_aid,
                     GraphExecutionStrategy strategy, const std::set<size_t> &modifiable_ref_input_indexes,
                     const std::set<size_t> &modifiable_ref_output_indexes)
      : RpcActor(name, kernel, device_context, memory_manager_aid, debug_aid, recorder_aid, strategy,
                 modifiable_ref_input_indexes, modifiable_ref_output_indexes, KernelTransformType::kRecvActor) {}
  ~RecvActor() override = default;

  void SetRouteInfo(uint32_t src_rank, const std::string &src_role, const std::string &src_node_name,
                    const std::string &dst_node_name) override;

 private:
  friend class GraphScheduler;
};

using RecvActorPtr = std::shared_ptr<RecvActor>;
}  // namespace runtime
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_RUNTIME_FRAMEWORK_ACTOR_RPC_RECV_ACTOR_H_