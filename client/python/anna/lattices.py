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
    # Anna's lattice types as an enum
    LWW, SET, ORDERED_SET, SINGLE_CAUSAL, MULTI_CAUSAL,
    # Serialized representations of Anna's lattices
    LWWValue, SetValue, SingleKeyCausalValue, MultiKeyCausalValue
)


class Lattice:
    def __init__(self):
        raise NotImplementedError

    def __str__(self):
        return str(self.reveal())

    def __eq__(self, other):
        if other is None:
            return False

        if type(other) != type(self):
            return False

        return self.reveal() == other.reveal()

    def reveal(self):
        '''
        The reveal method returns an unwrapped version of the data underlying
        data structure stored by the lattice.
        '''
        raise NotImplementedError

    def assign(self, value):
        '''
        Assigns a new value to the lattice -- this must be the same as the type
        expected when creating an instance of a particular lattice.
        '''
        raise NotImplementedError

    def merge(self, other):
        '''
        Merge two lattices into one. How the merge function works is contingent
        on what the underlying data structure us.
        '''
        raise NotImplementedError

    def serialize(self):
        '''
        Serializes the underlying data structure, including metadata relevant
        to the lattice, into a protobuf and returns a protobuf object along
        with an enum tag indicating the type of this lattice.
        '''
        raise NotImplementedError


class LWWPairLattice(Lattice):
    def __init__(self, timestamp, value):
        if type(timestamp) != int or type(value) != bytes:
            raise ValueError('LWWPairLattice must be a timestamp-bytes pair.')

        self.ts = timestamp
        self.val = value

    def reveal(self):
        return self.val

    def assign(self, value):
        if type(value) == str:
            value = bytes(value, 'utf-8')

        if type(value) != tuple or type(value[0]) != int \
                or type(value[1]) != bytes:
            raise ValueError('LWWPairLattice must be a timestamp-bytes pair.')

        self.ts = value[0]
        self.val = value[1]

    def merge(self, other):
        if other.ts > self.ts:
            return other
        else:
            return self

    def serialize(self):
        res = LWWValue()
        res.timestamp = self.ts
        res.value = self.val

        return res, LWW


class SetLattice(Lattice):
    def __init__(self, value=set()):
        if type(value) != set:
            raise ValueError('SetLattice can only be formed from a set.')

        self.val = value

    def reveal(self):
        return self.val

    def assign(self, value):
        if type(value) != set:
            raise ValueError('SetLattice can only be formed from a set.')

        self.val = value

    def merge(self, other):
        if type(other) != SetLattice:
            raise ValueError('Cannot merge SetLattice with invalid type ' +
                             str(type(other)) + '.')

        new_set = set()

        for v in other.val:
            new_set.insert(v)

        for v in self.val:
            new_set.insert(v)

        return SetLattice(new_set)

    def serialize(self):
        res = SetValue()

        for v in self.val:
            if type(v) == str:
                v = bytes(v, 'utf-8')
            if type(v) != bytes:
                raise ValueError('Unsupported type %s in SetLattice!' %
                                 (str(type(v))))

            res.values.append(v)

        return res, SET


# A wrapper class that implements some convenience OrderedSet operations on
# top of a list.  # We use this because it is way cheaper to deserialize into,
# at the cost of having expensive reordering operations (e.g. random insert),
# which we expect to be rare for our use cases (we will almost always be
# inserting at the end).
class ListBasedOrderedSet:
    # Preconditions: iterable's elements are unique and sorted ascending.
    # Behaviour is undefined if it is not.
    def __init__(self, iterable=[]):
        self.lst = []
        for val in iterable:
            self.insert(val)

    # Inserts a value, maintaining sorted order.
    def insert(self, value):
        # Microoptimization for the common case.
        if len(self.lst) == 0:
            self.lst.append(value)
        elif value > self.lst[-1]:
            self.lst.append(value)
        else:
            idx, present = self._index_of(value)
            if not present:
                self.lst.insert(idx, value)

    # Finds the index of an element, or where to insert it if you want to
    # maintain sorted order.
    # Returns (int index, bool present).
    # E.g. _index_of(lst, 'my-value') -> (42, true)
    #           => lst[42] = 'my-value'
    #      _index_of(lst, 'my-value') -> (42, false)
    #           => lst[41] < 'my-value' < lst[42]
    def _index_of(self, value):
        low = 0
        high = len(self.lst)
        while low < high:
            middle = low + int((high - low) / 2)
            pivot = self.lst[middle]
            if value == pivot:
                return (middle, True)
            elif value < pivot:
                high = middle
            elif pivot < value:
                low = middle + 1
        return (low, False)


class OrderedSetLattice(Lattice):
    def __init__(self, value=ListBasedOrderedSet()):
        if type(value) != ListBasedOrderedSet:
            raise ValueError('OrderedSetLattice can only be formed from a '
                             + 'ListBasedOrderedSet.')
        self.val = value

    def reveal(self):
        return self.val.lst

    def assign(self, value):
        if type(value) != ListBasedOrderedSet:
            raise ValueError('OrderedSetLattice can only be formed from a' +
                             ' ListBasedOrderedSet.')
        self.val = value

    def merge(self, other):
        if type(other) != OrderedSetLattice:
            raise ValueError('Cannot merge OrderedSetLattice with type ' +
                             str(type(other)) + '.')

        # Merge the two sorted lists by lockstep merge.
        # Note that reconstruction is faster than in-place merge.
        new_lst = []

        other = other.reveal().lst
        us = self.val.lst
        i, j = 0, 0  # Earliest unmerged indices.
        while i < len(us) or j < len(other):
            if i == len(us):
                new_lst.extend(other[j:])
                break
            elif j == len(other):
                new_lst.extend(us[i:])
                break
            else:
                a = us[i]
                b = other[j]
                if a == b:
                    new_lst.append(a)
                    i += 1
                    j += 1
                elif a < b:
                    new_lst.append(a)
                    i += 1
                elif b < a:
                    new_lst.append(b)
                    j += 1

        return OrderedSetLattice(ListBasedOrderedSet(new_lst))

    def serialize(self):
        res = SetValue()
        res.values.extend(self.val.lst)

        return res, ORDERED_SET


class MaxIntLattice(Lattice):
    def __init__(self, value):
        if type(value) != int:
            raise ValueError('MaxIntLattice only accepts integers.')

        self.value = value

    def reveal(self):
        return self.value

    def assign(self, value):
        if type(value) != int:
            raise ValueError('MaxIntLattice only accepts integers.')

        self.value = value

    def merge(self, other):
        if type(other) != MaxIntLattice:
            raise ValueError('Cannot merge MaxIntLattice with type ' +
                             str(type(other)) + '.')

        if other.value > self.value:
            self.value = other.value


class MapLattice(Lattice):
    def __init__(self, mp):
        if type(mp) != dict:
            raise ValueError('MapLattice only accepts dict data structures.')

        self.mp = mp

    def reveal(self):
        return self.mp

    def assign(self, mp):
        if type(mp) != dict:
            raise ValueError('MapLattice only accepts dict data structures.')

        self.mp = mp

    def merge(self, other):
        if type(other) != MapLattice:
            raise ValueError('Cannot merge MapLattice with type ' +
                             str(type(other)) + '.')

        for key in other.mp.keys:
            if key in self.mp:
                if (not isinstance(self.mp[key], Lattice) or not
                        isinstance(other.mp[key], Lattice)):
                    raise ValueError('Cannot merge a MapLattice with values' +
                                     ' that are not lattice types.')
                self.mp[key].merge(other.mp[key])
            else:
                self.mp[key] = other.mp[key]

    def copy(self):
        return MapLattice(self.mp.copy())


class VectorClock(MapLattice):
    def __init__(self, mp, deserialize=False):
        if type(mp) != dict:
            raise ValueError(f'VectorClock must be a dict, not {type(mp)}.')

        if deserialize:
            self.mp = VectorClock._deserialize(mp)
        else:
            VectorClock._validate_vc(mp)
            self.mp = mp

    def _deserialize(mp):
        result = {}

        for key in mp:
            if type(mp[key]) != int:
                raise ValueError('Cannot deserialize VectorClock from'
                                 + ' non-integer values.')

            result[key] = MaxIntLattice(mp[key])

        return result

    def _validate_vc(mp):
        for val in mp.values():
            if type(val) != MaxIntLattice:
                raise ValueError(('VectorClock values must be MaxIntLattices,'
                                 + ' not %s.') % str(type(val)))

    def assign(self, mp):
        if type(mp) != dict:
            raise ValueError('VectorClock must be a dict.')

        VectorClock._validate_vc(mp)
        self.mp = mp

    def update(self, key, count):
        if key in self.mp:
            lattice = MaxIntLattice(count)
            self.mp[key].merge(lattice)

    def serialize(self, pobj):
        for key in self.mp:
            pobj[key] = self.mp[key].reveal()


class SingleKeyCausalLattice(Lattice):
    def __init__(self, vector_clock, value):
        if type(vector_clock) != VectorClock:
            raise ValueError('Vector clock of SingleKeyCausalLattice must be a'
                             + ' VectorClock.')
        if type(value) != SetLattice:
            raise ValueError('Value of SingleKeyCausalLattice must be a'
                             + ' SetLattice.')

        self.vector_clock = vector_clock
        self.value = value

    def reveal(self):
        return list(self.value.reveal())

    def assign(self, value):
        if type(value) != SetLattice:
            raise ValueError('Value of SingleKeyCausalLattice must be a'
                             + ' SetLattice.')
        self.value = value

    def merge(self, other):
        if type(other) != SingleKeyCausalLattice:
            raise ValueError('Cannot merge SingleKeyCausalLattice with type ' +
                             str(type(other)) + '.')

        previous = self.vector_clock.copy()
        self.vector_clock.merge(other.vector_clock)

        if self.vector_clock == other.vector_clock:
            # The other version dominates this version.
            self.value = other.value
        elif self.vector_clock != previous:
            # The versions are concurrent.
            self.value.merge(other.value)
        else:
            # This version dominates, so we do nothing.
            pass

    def serialize(self):
        skcv = SingleKeyCausalValue()

        # Serialize the vector clock for this particular lattice by adding each
        # key-counter pair.
        self.vector_clock.serialize(skcv.vector_clock)

        # Add the value(s) stored by this lattice.
        for v in self.value:
            skcv.values.add(v)

        return skcv, SINGLE_CAUSAL


class MultiKeyCausalLattice(Lattice):
    def __init__(self, vector_clock, dependencies, value):
        if type(vector_clock) != VectorClock:
            raise ValueError('Vector clock of MultiKeyCausalLattice must be a'
                             + ' VectorClock.')
        if type(dependencies) != MapLattice:
            raise ValueError('Dependency set of MultiKeyCausalLattice must be'
                             + ' a MapLattice.')
        if type(value) != SetLattice:
            raise ValueError('Value of MultiKeyCausalLattice must be a'
                             + ' SetLattice.')

        self.vector_clock = vector_clock
        self.dependencies = dependencies
        self.value = value

    def reveal(self):
        return list(self.value.reveal())

    def assign(self, value):
        if type(value) != SetLattice:
            raise ValueError('Value of MultiKeyCausalLattice must be a'
                             + ' SetLattice.')
        self.value = value

    def merge(self, other):
        if type(other) != MultiKeyCausalLattice:
            raise ValueError('Cannot merge MultiKeyCausalLattice with type ' +
                             str(type(other)) + '.')

        previous = self.vector_clock.copy()
        self.vector_clock.merge(other.vector_clock)

        if self.vector_clock == other.vector_clock:
            # other version dominates this version
            self.dependencies = other.dependencies
            self.value = other.value
        elif self.vector_clock != previous:
            # versions are concurrent
            self.dependencies.merge(other.dependencies)
            self.value.merge(other.value)
        else:
            # this version dominates, so we do nothing
            pass

    def serialize(self):
        mkcv = MultiKeyCausalValue()

        # Serialize the vector clock for this particular lattice by adding each
        # key-counter pair.
        self.vector_clock.serialize(mkcv.vector_clock)

        # Serialize the vector clocks for each of the keys this lattice depends
        # on.
        for key in self.dependencies:
            kv = mkcv.add_dependences()
            kv.key = key
            self.dependencies[key].serialize(kv.vector_clock)

        # Add the value(s) stored by this lattice.
        for v in self.value:
            mkcv.values.add(v)

        return mkcv, MULTI_CAUSAL
