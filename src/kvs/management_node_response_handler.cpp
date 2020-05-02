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

#include "kvs/kvs_handlers.hpp"

void management_node_response_handler(string &serialized,
                                      set<Address> &extant_caches,
                                      map<Address, set<Key>> &cache_ip_to_keys,
                                      map<Key, set<Address>> &key_to_cache_ips,
                                      GlobalRingMap &global_hash_rings,
                                      LocalRingMap &local_hash_rings,
                                      SocketCache &pushers, ServerThread &wt,
                                      unsigned &rid) {
  // Get the response.
  StringSet func_nodes;
  func_nodes.ParseFromString(serialized);

  // Update extant_caches with the response.
  set<Address> deleted_caches = std::move(extant_caches);
  extant_caches = set<Address>();
  for (const auto &func_node : func_nodes.keys()) {
    deleted_caches.erase(func_node);
    extant_caches.insert(func_node);
  }

  // Process deleted caches
  // (cache IPs that we were tracking but were not in the newest list of
  // caches).
  for (const auto &cache_ip : deleted_caches) {
    cache_ip_to_keys.erase(cache_ip);
    for (auto &key_and_caches : key_to_cache_ips) {
      key_and_caches.second.erase(cache_ip);
    }
  }

  // Get the cached keys by cache IP.
  // First, prepare the requests for all the IPs we know about
  // and put them in an address request map.
  map<Address, KeyRequest> addr_request_map;
  for (const auto &cacheip : extant_caches) {
    Key key = get_user_metadata_key(cacheip, UserMetadataType::cache_ip);
    prepare_metadata_get_request(
        key, global_hash_rings[Tier::MEMORY], local_hash_rings[Tier::MEMORY],
        addr_request_map, wt.cache_ip_response_connect_address(), rid);
  }

  // Loop over the address request map and execute all the requests.
  for (const auto &addr_request : addr_request_map) {
    send_request<KeyRequest>(addr_request.second, pushers[addr_request.first]);
  }
}
