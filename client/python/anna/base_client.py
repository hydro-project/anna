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

from anna.anna_pb2 import (
    # Protobuf enum lattices types
    LWW, SET, ORDERED_SET, SINGLE_CAUSAL, MULTI_CAUSAL, PRIORITY,
    # Serialized lattice protobuf representations
    LWWValue, SetValue, SingleKeyCausalValue, MultiKeyCausalValue, PriorityValue,
    KeyRequest
)
from anna.lattices import (
    Lattice,
    LWWPairLattice,
    ListBasedOrderedSet,
    MapLattice,
    MultiKeyCausalLattice,
    OrderedSetLattice,
    PriorityLattice,
    SetLattice,
    SingleKeyCausalLattice,
    VectorClock
)


class BaseAnnaClient():
    def __init__(self):
        raise NotImplementedError

    def get(self, keys):
        '''
        Retrieves a key from the key value store.

        keys: The names of the keys being retrieved.

        returns: A Lattice containing the server's response
        '''
        raise NotImplementedError

    def get_all(self, keys):
        '''
        Retrieves all versions of the keys from the KVS; there may be multiple
        versions because the KVS is eventually consistent.

        keys: The names of the keys being retrieved

        returns: A list of Lattices with all the key versions returned by the
        KVS
        '''
        raise NotImplementedError

    def put(self, key, value):
        '''
        Puts a new key into the KVS.

        key: The name of the key being put
        value: A lattice with the data corresponding to this key

        returns: True if the server responded without an error, and False
        otherwise or if the server could not be reached
        '''
        raise NotImplementedError

    def put_all(self, key, value):
        '''
        Puts a new key into the key value store and waits for acknowledgement
        from all key replicas.

        key: The name of the key being put
        value: A Lattice with the data corresponding to this key

        returns: True if all replicas acknowledged the request or False if a
        replica returned an error or could not be reached
        '''
        raise NotImplementedError

    @property
    def response_address(self):
        raise NotImplementedError

    # Takes a KeyTuple (defined in hydro-project/common/proto/anna.proto) as an
    # input and returns either a lattice data structure corresponding to the
    # type of the KeyTuple.
    def _deserialize(self, tup):
        if isinstance(tup, CausalTuple):
            # Deserialize multi-key causal lattices
            val = MultiKeyCausalValue()
            val.ParseFromString(tup.payload)

            # Deserialize the vector_clock stored in the Protobuf into a
            # MapLattice, where each value is a MaxIntLattice of the VC
            # counter.
            vc = VectorClock(val.vector_clock, True)

            # Deserialize the set of dependencies of this key into a MapLattice
            # where the keys are names of other KVS keys and the values are
            # MapLattices that have the vector clocks for those keys.
            dep_map = {}
            for kv in val.dependencies:
                key = kv.key
                dep_map[key] = VectorClock(kv.vector_clock, True)

            # Create a SetLattice with the value(s) stored by this lattice.
            values = set()
            for v in val.values():
                values.add(v)

            dependencies = MapLattice(dep_map)
            value = SetLattice(values)

            return MultiKeyCausalLattice(vc, dependencies, value)

        elif tup.lattice_type == LWW:
            # Deserialize last-writer-wins lattices
            val = LWWValue()
            val.ParseFromString(tup.payload)

            return LWWPairLattice(val.timestamp, val.value)

        elif tup.lattice_type == SET:
            # Deserialize unordered-set lattices
            s = SetValue()
            s.ParseFromString(tup.payload)

            result = set()
            for k in s.values:
                result.add(k)

            return SetLattice(result)
        elif tup.lattice_type == ORDERED_SET:
            # Deserialize ordered-set lattices
            res = ListBasedOrderedSet()
            val = SetValue()
            val.ParseFromString(tup.payload)
            for v in val.values:
                res.insert(v)

            return OrderedSetLattice(res)

        elif tup.lattice_type == SINGLE_CAUSAL:
            # Deserialize single-key causal lattices
            val = SingleKeyCausalValue()
            val.ParseFromString(tup.payload)

            # Deserialize the vector_clock stored in the Protobuf into a
            # MapLattice, where each value is a MaxIntLattice of the VC
            # counter.
            vc = VectorClock(val.vector_clock, True)

            # Create a SetLattice with the value(s) stored by this lattice.
            values = set()
            for v in val.values():
                values.add(v)

            return SingleKeyCasaulLattice(vc, SetLattice(values))

        elif tup.lattice_type == MULTI_CAUSAL:
            # Deserialize multi-key causal lattices
            val = MultiKeyCausalValue()
            val.ParseFromString(tup.payload)

            # Deserialize the vector_clock stored in the Protobuf into a
            # MapLattice, where each value is a MaxIntLattice of the VC
            # counter.
            vc = VectorClock(val.vector_clock, True)

            # Deserialize the set of dependencies of this key into a MapLattice
            # where the keys are names of other KVS keys and the values are
            # MapLattices that have the vector clocks for those keys.
            dep_map = {}
            for kv in val.dependencies:
                key = kv.key
                dep_map[key] = VectorClock(kv.vector_clock, True)

            # Create a SetLattice with the value(s) stored by this lattice.
            values = set()
            for v in val.values():
                values.add(v)

            dependencies = MapLattice(dep_map)
            value = SetLattice(values)

            return MultiKeyCausalLattice(vc, dependencies, value)
        elif tup.lattice_type == PRIORITY:
            val = PriorityValue()
            val.ParseFromString(tup.payload)

            return PriorityLattice(val.priority, val.value)
        else:
            raise ValueError('Unsupported type cannot be serialized: ' +
                             str(tup.lattice_type))

    # Takes in a Lattice subclass and returns a bytestream representing a
    # serialized Protobuf message.
    def _serialize(self, val):
        if not isinstance(val, Lattice):
            raise ValueError('There is no way to serialize a non-lattice data'
                             + ' structure.')

        pb, typ = val.serialize()
        return pb.SerializeToString(), typ

    # Helper function to create a KeyRequest (see
    # hydro-project/common/proto/anna.proto). Takes in a key name and returns a
    # tuple containing a KeyRequest and a KeyTuple contained in that KeyRequest
    # with response_address, request_id, and address_cache_size automatically
    # populated.
    def _prepare_data_request(self, keys):
        req = KeyRequest()
        req.request_id = self._get_request_id()
        req.response_address = self.response_address

        tuples = []

        for key in keys:
            tup = req.tuples.add()
            tuples.append(tup)
            tup.key = key

            if self.address_cache and key in self.address_cache:
                tup.address_cache_size = len(self.address_cache[key])

        return (req, tuples)

    # Returns and increments a request ID. Loops back after 10,000 requests.
    def _get_request_id(self):
        response = self.ut.get_ip() + ':' + str(self.rid)
        self.rid = (self.rid + 1) % 10000
        return response
