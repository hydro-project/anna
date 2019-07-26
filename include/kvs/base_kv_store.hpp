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

#ifndef INCLUDE_KVS_BASE_KV_STORE_HPP_
#define INCLUDE_KVS_BASE_KV_STORE_HPP_

#include "anna.pb.h"
#include "lattices/core_lattices.hpp"

template <typename K, typename V> class KVStore {
protected:
  MapLattice<K, V> db;

public:
  KVStore<K, V>() {}

  KVStore<K, V>(MapLattice<K, V> &other) { db = other; }

  V get(const K &k, AnnaError &error) {
    if (!db.contains(k).reveal()) {
      error = AnnaError::KEY_DNE;
    }

    return db.at(k);
  }

  void put(const K &k, const V &v) { return db.at(k).merge(v); }

  unsigned size(const K &k) { return db.at(k).size().reveal(); }

  void remove(const K &k) { db.remove(k); }
};

#endif // INCLUDE_KVS_BASE_KV_STORE_HPP_
