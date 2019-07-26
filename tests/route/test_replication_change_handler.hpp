//  Copyright 2019 U.C. Berkeley RISE Lab
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

#include "route/routing_handlers.hpp"

TEST_F(RoutingHandlerTest, ReplicationChange) {
  kRoutingThreadCount = 3;
  vector<string> keys = {"key0, key1, key2"};
  warmup_key_replication_map_to_defaults(keys);

  ReplicationFactorUpdate update;
  for (string key : keys) {
    ReplicationFactor *rf = update.add_updates();
    rf->set_key(key);

    for (const Tier &tier : kAllTiers) {
      ReplicationFactor_ReplicationValue *rep_global = rf->add_global();
      rep_global->set_tier(tier);
      rep_global->set_value(2);

      ReplicationFactor_ReplicationValue *rep_local = rf->add_local();
      rep_local->set_tier(tier);
      rep_local->set_value(3);
    }
  }

  string serialized;
  update.SerializeToString(&serialized);

  replication_change_handler(log_, serialized, pushers, key_replication_map,
                             thread_id, ip);

  vector<string> messages = get_zmq_messages();

  EXPECT_EQ(messages.size(), 2);
  for (unsigned i = 0; i < messages.size(); i++) {
    EXPECT_EQ(messages[i], serialized);
  }

  for (string key : keys) {
    EXPECT_EQ(key_replication_map[key].global_replication_[Tier::MEMORY], 2);
    EXPECT_EQ(key_replication_map[key].global_replication_[Tier::DISK], 2);
    EXPECT_EQ(key_replication_map[key].local_replication_[Tier::MEMORY], 3);
    EXPECT_EQ(key_replication_map[key].local_replication_[Tier::DISK], 3);
  }
}
