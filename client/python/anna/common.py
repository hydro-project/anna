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

# Define port offsets for KVS and routing ports
REQUEST_PULLING_BASE_PORT = 6460
KEY_ADDRESS_BASE_PORT = 6760


class Thread():
    def __init__(self, ip, tid):
        self.ip = ip
        self.tid = tid

        self._base = 'tcp://*:'
        self._ip_base = 'tcp://' + self.ip + ':'

    def get_ip(self):
        return self.ip

    def get_tid(self):
        return self.tid


class UserThread(Thread):
    def get_request_pull_connect_addr(self):
        return self._ip_base + str(self.tid + REQUEST_PULLING_BASE_PORT)

    def get_request_pull_bind_addr(self):
        return self._base + str(self.tid + REQUEST_PULLING_BASE_PORT)

    def get_key_address_connect_addr(self):
        return self._ip_base + str(self.tid + KEY_ADDRESS_BASE_PORT)

    def get_key_address_bind_addr(self):
        return self._base + str(self.tid + KEY_ADDRESS_BASE_PORT)
