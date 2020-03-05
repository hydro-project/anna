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

#ifndef KVS_INCLUDE_METADATA_HPP_
#define KVS_INCLUDE_METADATA_HPP_

#include "metadata.pb.h"
#include "threads.hpp"

const string kMetadataTypeReplication = "replication";
const string kDeltaRequestIdentical = "identical";

struct TierEnumHash {
  template <typename T> std::size_t operator()(T t) const {
    return static_cast<std::size_t>(t);
  }
};

struct KeyReplication {
  hmap<Tier, unsigned, TierEnumHash> global_replication_;
  hmap<Tier, unsigned, TierEnumHash> local_replication_;
};

struct KeyProperty {
  unsigned size_;
  LatticeType type_;
};

inline bool operator==(const KeyReplication &lhs, const KeyReplication &rhs) {
  for (const auto &pair : lhs.global_replication_) {
    Tier id = pair.first;

    if (rhs.global_replication_.find(id) == rhs.global_replication_.end()) {
      return false;
    }

    if (pair.second != rhs.global_replication_.at(id)) {
      return false;
    }
  }

  for (const auto &pair : lhs.local_replication_) {
    Tier id = pair.first;

    if (rhs.local_replication_.find(id) == rhs.local_replication_.end()) {
      return false;
    }

    if (pair.second != rhs.local_replication_.at(id)) {
      return false;
    }
  }

  return true;
}

// per-tier metadata
struct TierMetadata {
  TierMetadata()
      : id_(Tier::MEMORY), thread_number_(1), default_replication_(1),
        node_capacity_(0) {}

  TierMetadata(Tier id, unsigned t_num, unsigned rep,
               unsigned long long node_capacity)
      : id_(id), thread_number_(t_num), default_replication_(rep),
        node_capacity_(node_capacity) {}

  Tier id_;

  unsigned thread_number_;

  unsigned default_replication_;

  unsigned long long node_capacity_;
};

inline bool is_metadata(Key key) {
  vector<string> v;
  split(key, '|', v);

  if (v[0] == kMetadataIdentifier) {
    return true;
  } else {
    return false;
  }
}

// NOTE: This needs to be here because it needs the definition of TierMetadata
extern hmap<Tier, TierMetadata, TierEnumHash> kTierMetadata;

enum MetadataType { replication, server_stats, key_access, key_size };

inline Key get_metadata_key(const ServerThread &st, Tier tier_id,
                            unsigned thread_num, MetadataType type) {
  string metadata_type;

  switch (type) {
  case MetadataType::server_stats:
    metadata_type = "stats";
    break;
  case MetadataType::key_access:
    metadata_type = "access";
    break;
  case MetadataType::key_size:
    metadata_type = "size";
    break;
  default:
    return ""; // this should never happen; see note below about
               // MetadataType::replication
  }

  return kMetadataIdentifier + kMetadataDelimiter + metadata_type +
         kMetadataDelimiter + st.public_ip() + kMetadataDelimiter +
         st.private_ip() + kMetadataDelimiter + std::to_string(thread_num) +
         kMetadataDelimiter + Tier_Name(tier_id);
}

// This version of the function should only be called with
// certain types of MetadataType,
// so if it's called with something else, we return
// an empty string.
// TODO: There should probably be a less silent error check.
inline Key get_metadata_key(string data_key, MetadataType type) {
  if (type == MetadataType::replication) {
    return kMetadataIdentifier + kMetadataDelimiter + kMetadataTypeReplication +
           kMetadataDelimiter + data_key;
  }
  return "";
}

// Inverse of get_metadata_key, returning just the key itself.
// Precondition: metadata_key is actually a metadata key (output of
// get_metadata_key).
// TODO: same problem as get_metadata_key with the metadata types.
inline Key get_key_from_metadata(Key metadata_key) {
  string::size_type n_id;
  string::size_type n_type;
  // Find the first delimiter; this skips over the metadata identifier.
  n_id = metadata_key.find(kMetadataDelimiter);
  // Find the second delimiter; this skips over the metadata type.
  n_type = metadata_key.find(kMetadataDelimiter, n_id + 1);
  string metadata_type = metadata_key.substr(n_id + 1, n_type - (n_id + 1));
  if (metadata_type == kMetadataTypeReplication) {
    return metadata_key.substr(n_type + 1);
  }

  return "";
}

// Precondition: key is from the non-data-key version of get_metadata_key.
inline vector<string> split_metadata_key(Key key) {
  vector<string> tokens;
  split(key, kMetadataDelimiterChar, tokens);

  return tokens;
}

inline void warmup_key_replication_map_to_defaults(
    map<Key, KeyReplication> &key_replication_map,
    unsigned &kDefaultGlobalMemoryReplication,
    unsigned &kDefaultGlobalEbsReplication,
    unsigned &kDefaultLocalReplication) {
  for (unsigned i = 1; i <= 1000000; i++) {
    // key is 8 bytes
    Key key = string(8 - std::to_string(i).length(), '0') + std::to_string(i);
    key_replication_map[key].global_replication_[Tier::MEMORY] =
        kDefaultGlobalMemoryReplication;
    key_replication_map[key].global_replication_[Tier::DISK] =
        kDefaultGlobalEbsReplication;
    key_replication_map[key].local_replication_[Tier::MEMORY] =
        kDefaultLocalReplication;
    key_replication_map[key].local_replication_[Tier::DISK] =
        kDefaultLocalReplication;
  }
}

inline void init_replication(map<Key, KeyReplication> &key_replication_map,
                             const Key &key) {
  for (const Tier &tier : kAllTiers) {
    key_replication_map[key].global_replication_[tier] =
        kTierMetadata[tier].default_replication_;
    key_replication_map[key].local_replication_[tier] =
        kDefaultLocalReplication;
  }
}

#endif // KVS_INCLUDE_METADATA_HPP_
