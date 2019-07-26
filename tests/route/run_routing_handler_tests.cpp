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

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <vector>

#include "gtest/gtest.h"

#include "anna.pb.h"
#include "metadata.pb.h"
#include "types.hpp"

#include "routing_handler_base.hpp"
#include "test_address_handler.hpp"
#include "test_membership_handler.hpp"
#include "test_replication_change_handler.hpp"
#include "test_replication_response_handler.hpp"
#include "test_seed_handler.hpp"

unsigned kDefaultLocalReplication = 1;
unsigned kDefaultGlobalMemoryReplication = 1;
unsigned kDefaultGlobalEbsReplication = 1;
unsigned kThreadNum = 1;

Tier kSelfTier = Tier::ROUTING;

vector<Tier> kSelfTierIdVector = {kSelfTier};
hmap<Tier, TierMetadata, TierEnumHash> kTierMetadata = {};

unsigned kEbsThreadNum = 1;
unsigned kMemoryThreadNum = 1;
unsigned kRoutingThreadCount = 1;

int main(int argc, char *argv[]) {
  log_->set_level(spdlog::level::off);
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
