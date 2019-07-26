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

#ifndef TESTS_MOCK_MOCK_HASH_UTILS_HPP_
#define TESTS_MOCK_MOCK_HASH_UTILS_HPP_

#include "hash_ring.hpp"
#include "zmq/zmq_util.hpp"

class MockHashRingUtil : public HashRingUtilInterface {
public:
  virtual ~MockHashRingUtil(){};

  virtual ServerThreadList get_responsible_threads(
      Address respond_address, const Key &key, bool metadata,
      GlobalRingMap &global_hash_rings, LocalRingMap &local_hash_rings,
      map<Key, KeyReplication> &key_replication_map, SocketCache &pushers,
      const vector<Tier> &tiers, bool &succeed, unsigned &seed);
};

#endif // TESTS_MOCK_MOCK_HASH_UTILS_HPP_
