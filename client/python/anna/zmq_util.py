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


def send_request(req_obj, send_sock):
    req_string = req_obj.SerializeToString()

    send_sock.send(req_string)


def recv_response(req_ids, rcv_sock, resp_class):
    responses = []

    while len(responses) < len(req_ids):
        resp_obj = resp_class()
        resp = rcv_sock.recv()
        resp_obj.ParseFromString(resp)

        while resp_obj.response_id not in req_ids:
            resp_obj.Clear()
            resp_obj.ParseFromString(rcv_sock.recv())

        responses.append(resp_obj)

    return responses


class SocketCache():
    def __init__(self, context, zmq_type):
        self.context = context
        self._cache = {}
        self.zmq_type = zmq_type

    def get(self, addr):
        if addr not in self._cache:
            sock = self.context.socket(self.zmq_type)
            sock.connect(addr)

            self._cache[addr] = sock

            return sock
        else:
            return self._cache[addr]
