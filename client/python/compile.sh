#!/bin/bash

#  Copyright 2019 U.C. Berkeley RISE Lab
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

cd anna
protoc -I=../../../common/proto/ --python_out=. anna.proto shared.proto causal.proto cloudburst.proto

if [[ "$OSTYPE" = "darwin"* ]]; then
  sed -i "" "s/import shared_pb2/from . import shared_pb2/g" anna_pb2.py
  sed -i "" "s/import shared_pb2/from . import shared_pb2/g" causal_pb2.py
  sed -i "" "s/import anna_pb2/from . import anna_pb2/g" causal_pb2.py
  sed -i "" "s/import cloudburst_pb2/from . import cloudburst_pb2/g" causal_pb2.py
  sed -i "" "s/import shared_pb2/from . import shared_pb2/g" cloudburst_pb2.py
else # We assume other distributions are Linux.
  # NOTE: This is a hack that we need to use because our protobufs are
  # not properly packaged, and generally protobufs are supposed to be
  # compiled in the same package that they are defined.
  sed -i "s|import shared_pb2|from . import shared_pb2|g" anna_pb2.py
  sed -i "s|import shared_pb2|from . import shared_pb2|g" causal_pb2.py
  sed -i "s|import anna_pb2|from . import anna_pb2|g" causal_pb2.py
  sed -i "s|import cloudburst_pb2|from . import cloudburst_pb2|g" causal_pb2.py
  sed -i "s|import shared_pb2|from . import shared_pb2|g" cloudburst_pb2.py
fi
