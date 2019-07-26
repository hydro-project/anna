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

TEST_F(RoutingHandlerTest, ReplicationResponse) {
  unsigned seed = 0;
  string key = "key";
  vector<string> keys = {"key"};
  warmup_key_replication_map_to_defaults(keys);

  EXPECT_EQ(key_replication_map[key].global_replication_[Tier::MEMORY], 1);
  EXPECT_EQ(key_replication_map[key].global_replication_[Tier::DISK], 1);
  EXPECT_EQ(key_replication_map[key].local_replication_[Tier::MEMORY], 1);
  EXPECT_EQ(key_replication_map[key].local_replication_[Tier::DISK], 1);

  KeyResponse response;
  response.set_type(RequestType::PUT);
  KeyTuple *tp = response.add_tuples();
  tp->set_key(get_metadata_key(key, MetadataType::replication));
  tp->set_lattice_type(LatticeType::LWW);

  string metakey = key;
  ReplicationFactor rf;
  rf.set_key(key);

  for (const Tier &tier : kAllTiers) {
    ReplicationFactor_ReplicationValue *rep_global = rf.add_global();
    rep_global->set_tier(tier);
    rep_global->set_value(2);

    ReplicationFactor_ReplicationValue *rep_local = rf.add_local();
    rep_local->set_tier(tier);
    rep_local->set_value(3);
  }

  string repfactor;
  rf.SerializeToString(&repfactor);

  tp->set_payload(serialize(0, repfactor));

  string serialized;
  response.SerializeToString(&serialized);

  replication_response_handler(log_, serialized, pushers, rt, global_hash_rings,
                               local_hash_rings, key_replication_map,
                               pending_requests, seed);

  EXPECT_EQ(key_replication_map[key].global_replication_[Tier::MEMORY], 2);
  EXPECT_EQ(key_replication_map[key].global_replication_[Tier::DISK], 2);
  EXPECT_EQ(key_replication_map[key].local_replication_[Tier::MEMORY], 3);
  EXPECT_EQ(key_replication_map[key].local_replication_[Tier::DISK], 3);
}
