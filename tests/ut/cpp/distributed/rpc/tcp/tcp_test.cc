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

#include <sys/resource.h>
#include <sys/types.h>
#include <dirent.h>
#include <atomic>
#include <string>
#include <thread>
#include <csignal>

#include <gtest/gtest.h>
#define private public
#include "distributed/rpc/tcp/tcp_server.h"
#include "distributed/rpc/tcp/tcp_client.h"
#include "distributed/rpc/tcp/constants.h"
#include "common/common_test.h"

namespace mindspore {
namespace distributed {
namespace rpc {
int g_recv_num = 0;
int g_exit_msg_num = 0;

static size_t g_data_msg_num = 0;

static void Init() { g_data_msg_num = 0; }

static bool WaitForDataMsg(size_t expected_msg_num, int timeout_in_sec) {
  bool rt = false;
  int timeout = timeout_in_sec * 1000 * 1000;
  int usleepCount = 100000;

  while (timeout) {
    if (g_data_msg_num == expected_msg_num) {
      rt = true;
      break;
    }
    timeout = timeout - usleepCount;
    usleep(usleepCount);
  }
  return rt;
}

static void IncrDataMsgNum(size_t number) { g_data_msg_num += number; }

static size_t GetDataMsgNum() { return g_data_msg_num; }

std::atomic<int> m_sendNum(0);
std::string m_localIP = "127.0.0.1";
bool m_notRemote = false;

class TCPTest : public UT::Common {
 protected:
  char *testServerPath;
  static const size_t pid_num = 100;
  pid_t pid1;
  pid_t pid2;

  pid_t pids[pid_num];

  void SetUp() {}
  void TearDown() {}

  std::unique_ptr<MessageBase> CreateMessage(const std::string &serverUrl, const std::string &client_url,
                                             size_t msg_size = 100);

  bool CheckRecvNum(int expectedRecvNum, int _timeout);
  bool CheckExitNum(int expectedExitNum, int _timeout);
};

std::unique_ptr<MessageBase> TCPTest::CreateMessage(const std::string &serverUrl, const std::string &clientUrl,
                                                    size_t msg_size) {
  std::unique_ptr<MessageBase> message = std::make_unique<MessageBase>();
  std::string data(msg_size, 'A');
  message->name = "testname";
  message->from = AID("client", clientUrl);
  message->to = AID("server", serverUrl);
  message->body = data;
  return message;
}

bool TCPTest::CheckRecvNum(int expectedRecvNum, int _timeout) {
  int timeout = _timeout * 1000 * 1000;  // us
  int usleepCount = 100000;

  while (timeout) {
    usleep(usleepCount);
    if (g_recv_num >= expectedRecvNum) {
      return true;
    }
    timeout = timeout - usleepCount;
  }
  return false;
}

bool TCPTest::CheckExitNum(int expectedExitNum, int _timeout) {
  int timeout = _timeout * 1000 * 1000;
  int usleepCount = 100000;

  while (timeout) {
    usleep(usleepCount);
    if (g_exit_msg_num >= expectedExitNum) {
      return true;
    }
    timeout = timeout - usleepCount;
  }

  return false;
}

/// Feature: test failed to start a socket server.
/// Description: start a socket server with an invalid url.
/// Expectation: failed to start the server with invalid url.
TEST_F(TCPTest, StartServerFail) {
  std::unique_ptr<TCPServer> server = std::make_unique<TCPServer>();
  bool ret = server->Initialize("0:2225");
  ASSERT_FALSE(ret);
  server->Finalize();
}

/// Feature: test start a socket server.
/// Description: start the socket server with a specified socket.
/// Expectation: the socket server is started successfully.
TEST_F(TCPTest, StartServerSucc) {
  std::unique_ptr<TCPServer> server = std::make_unique<TCPServer>();
  bool ret = server->Initialize("127.0.0.1:8081");
  ASSERT_TRUE(ret);
  server->Finalize();
}

/// Feature: test normal tcp message sending.
/// Description: start a socket server and send a normal message to it.
/// Expectation: the server received the message sented from client.
TEST_F(TCPTest, SendOneMessage) {
  Init();

  // Start the tcp server.
  auto server_url = "127.0.0.1:8081";
  std::unique_ptr<TCPServer> server = std::make_unique<TCPServer>();
  bool ret = server->Initialize(server_url);
  ASSERT_TRUE(ret);

  server->SetMessageHandler([](MessageBase *const message) -> MessageBase *const {
    IncrDataMsgNum(1);
    return NULL_MSG;
  });

  // Start the tcp client.
  auto client_url = "127.0.0.1:1234";
  std::unique_ptr<TCPClient> client = std::make_unique<TCPClient>();
  ret = client->Initialize();
  ASSERT_TRUE(ret);

  // Create the message.
  auto message = CreateMessage(server_url, client_url);

  // Send the message.
  client->Connect(server_url);
  client->SendAsync(std::move(message));

  // Wait timeout: 5s
  WaitForDataMsg(1, 5);

  // Check result
  EXPECT_EQ(1, GetDataMsgNum());

  // Destroy
  client->Disconnect(server_url);
  client->Finalize();
  server->Finalize();
}

/// Feature: test sending two message continuously.
/// Description: start a socket server and send two normal message to it.
/// Expectation: the server received the two messages sented from client.
TEST_F(TCPTest, SendTwoMessages) {
  Init();

  // Start the tcp server.
  auto server_url = "127.0.0.1:8081";
  std::unique_ptr<TCPServer> server = std::make_unique<TCPServer>();
  bool ret = server->Initialize(server_url);
  ASSERT_TRUE(ret);

  server->SetMessageHandler([](MessageBase *const message) -> MessageBase *const {
    IncrDataMsgNum(1);
    return NULL_MSG;
  });

  // Start the tcp client.
  auto client_url = "127.0.0.1:1234";
  std::unique_ptr<TCPClient> client = std::make_unique<TCPClient>();
  ret = client->Initialize();
  ASSERT_TRUE(ret);

  // Create messages.
  auto message1 = CreateMessage(server_url, client_url);
  auto message2 = CreateMessage(server_url, client_url);

  // Send messages.
  client->Connect(server_url);
  client->SendAsync(std::move(message1));
  client->SendAsync(std::move(message2));

  // Wait timeout: 5s
  WaitForDataMsg(2, 5);

  // Check result
  EXPECT_EQ(2, GetDataMsgNum());
  client->Disconnect(server_url);
  client->Finalize();
  server->Finalize();
}

/// Feature: test start the tcp server with random port.
/// Description: start a socket server without specified fixed port.
/// Expectation: the server started successfully.
TEST_F(TCPTest, StartServerWithRandomPort) {
  std::unique_ptr<TCPServer> server = std::make_unique<TCPServer>();
  bool ret = server->Initialize();
  ASSERT_TRUE(ret);

  auto port = server->GetPort();
  EXPECT_LT(0, port);
  server->Finalize();
}

/// Feature: test send the message synchronously.
/// Description: start a socket server and send the message synchronously.
/// Expectation: the number of bytes sent could be got synchronously.
TEST_F(TCPTest, SendSyncMessage) {
  Init();

  // Start the tcp server.
  auto server_url = "127.0.0.1:8081";
  std::unique_ptr<TCPServer> server = std::make_unique<TCPServer>();
  bool ret = server->Initialize(server_url);
  ASSERT_TRUE(ret);

  server->SetMessageHandler([](MessageBase *const message) -> MessageBase *const {
    IncrDataMsgNum(1);
    return NULL_MSG;
  });

  // Start the tcp client.
  auto client_url = "127.0.0.1:1234";
  std::unique_ptr<TCPClient> client = std::make_unique<TCPClient>();
  ret = client->Initialize();
  ASSERT_TRUE(ret);

  // Create the message.
  auto message = CreateMessage(server_url, client_url);
  auto msg_size = message->body.size();

  // Send the message.
  client->Connect(server_url);
  auto bytes_num = client->SendSync(std::move(message));

  EXPECT_EQ(msg_size, bytes_num);

  WaitForDataMsg(1, 5);
  EXPECT_EQ(1, GetDataMsgNum());

  // Destroy
  client->Disconnect(server_url);
  client->Finalize();
  server->Finalize();
}

/// Feature: test sending large messages.
/// Description: start a socket server and send several large messages to it.
/// Expectation: the server received these large messages sented from client.
TEST_F(TCPTest, SendLargeMessages) {
  Init();

  // Start the tcp server.
  std::unique_ptr<TCPServer> server = std::make_unique<TCPServer>();
  bool ret = server->Initialize();
  ASSERT_TRUE(ret);

  server->SetMessageHandler([](MessageBase *const message) -> MessageBase *const {
    IncrDataMsgNum(1);
    return NULL_MSG;
  });

  // Start the tcp client.
  auto client_url = "127.0.0.1:1234";
  std::unique_ptr<TCPClient> client = std::make_unique<TCPClient>();
  ret = client->Initialize();
  ASSERT_TRUE(ret);

  // Send the message.
  auto ip = server->GetIP();
  auto port = server->GetPort();
  auto server_url = ip + ":" + std::to_string(port);
  client->Connect(server_url);

  size_t msg_cnt = 5;
  size_t large_msg_size = 1024000;
  for (int i = 0; i < msg_cnt; ++i) {
    auto message = CreateMessage(server_url, client_url, large_msg_size);
    client->SendAsync(std::move(message));
  }

  // Wait timeout: 15s
  WaitForDataMsg(msg_cnt, 15);

  // Check result
  EXPECT_EQ(msg_cnt, GetDataMsgNum());

  // Destroy
  client->Disconnect(server_url);
  client->Finalize();
  server->Finalize();
}

/// Feature: test creating many TCP connections.
/// Description: create many servers and clients, then connect each client to a server.
/// Expectation: all the servers and clients are created successfully.
TEST_F(TCPTest, CreateManyConnectionPairs) {
  Init();

  std::vector<std::shared_ptr<TCPServer>> servers;
  std::vector<std::shared_ptr<TCPClient>> clients;
  std::vector<std::string> server_urls;

  size_t total_connection_num = 10;

  for (size_t i = 0; i < total_connection_num; ++i) {
    // Start the tcp server.
    std::shared_ptr<TCPServer> server = std::make_shared<TCPServer>();
    bool ret = server->Initialize();
    auto ip = server->GetIP();
    auto port = server->GetPort();
    ASSERT_TRUE(ret);

    server->SetMessageHandler([](MessageBase *const message) -> MessageBase *const {
      IncrDataMsgNum(1);
      return NULL_MSG;
    });

    // Start the tcp client.
    auto client_url = "127.0.0.1:1234";
    std::shared_ptr<TCPClient> client = std::make_shared<TCPClient>();
    ret = client->Initialize();
    ASSERT_TRUE(ret);

    // Send the message.
    auto server_url = ip + ":" + std::to_string(port);
    server_urls.push_back(server_url);
    auto success = client->Connect(server_url);
    EXPECT_EQ(true, success);

    size_t msg_cnt = 100;
    size_t large_msg_size = 10240;
    for (int i = 0; i < msg_cnt; ++i) {
      auto message = CreateMessage(server_url, client_url, large_msg_size);
      client->SendAsync(std::move(message));
    }

    // Check result
    servers.push_back(server);
    clients.push_back(client);
  }

  // Check result
  EXPECT_EQ(total_connection_num, servers.size());
  EXPECT_EQ(total_connection_num, clients.size());

  // Destroy
  for (size_t i = 0; i < total_connection_num; ++i) {
    while (!clients[i]->Disconnect(server_urls[i]))
      ;
    clients[i]->Finalize();
    servers[i]->Finalize();
  }
}

/// Feature: test multi clients connecting to one single server.
/// Description: start a socket server and multi clients.
/// Expectation: these clients connected to the server successfully.
TEST_F(TCPTest, SingleServerMultiClients) {
  Init();

  // Start the tcp server.
  auto server_url = "127.0.0.1:8081";
  std::unique_ptr<TCPServer> server = std::make_unique<TCPServer>();
  bool ret = server->Initialize(server_url);
  ASSERT_TRUE(ret);

  server->SetMessageHandler([](MessageBase *const message) -> MessageBase *const {
    IncrDataMsgNum(1);
    return NULL_MSG;
  });

  // Start the tcp client.
  std::vector<std::shared_ptr<TCPClient>> clients;
  uint32_t client_num = 8;

  for (uint32_t i = 0; i < client_num; ++i) {
    std::shared_ptr<TCPClient> client = std::make_shared<TCPClient>();
    clients.push_back(client);

    auto ret = client->Initialize();
    ASSERT_TRUE(ret);
    ret = client->Connect(server_url);
    ASSERT_TRUE(ret);
  }

  // Destroy
  for (uint32_t i = 0; i < client_num; ++i) {
    clients[i]->Disconnect(server_url);
    clients[i]->Finalize();
  }
  server->Finalize();
}
}  // namespace rpc
}  // namespace distributed
}  // namespace mindspore
