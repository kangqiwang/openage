# Copyright 2019-2020 the openage authors. See copying.md for legal info.
# TODO pylint: disable=C,R,abstract-method

"""
Storage format for values from data file entries.
Data from ReadMembers is supposed to be transferred
to these objects for easier handling during the conversion
process and advanced features like creating diffs.

Quick usage guide on when to use which ValueMember:
    - IntMember, FloatMember, BooleanMember and StringMember: should
      be self explanatory.
    - IDMember: References to other structures in form of identifiers.
                Also useful for flags with more than two options.
    - BitfieldMember: Value is used as a bitfield.
    - ContainerMember: For modelling specific substructures. ContainerMembers
                       can store members with different types. However, the
                       member names must be unique.
                       (e.g. a unit object)
    - ArrayMember: Stores a list of members with uniform type. Can be used
                   when repeating substructures appear in a data file.
                   (e.g. multiple unit objects, list of coordinates)
"""

from enum import Enum
from math import isclose


class ValueMember:
    """
    Stores a value member from a data file.
    """

    __slots__ = ('name', 'value')

    def __init__(self, name):
        self.name = name
        self.value = None

    def get_name(self):
        """
        Returns the name of the member.
        """
        return self.name

    def get_value(self):
        """
        Returns the value of a member.
        """
        raise NotImplementedError(
            "%s cannot have values" % (type(self)))

    def get_type(self):
        """
        Returns the type of a member.
        """
        raise NotImplementedError(
            "%s cannot have a type" % (type(self)))

    def diff(self, other):
        """
        Returns a new member object that contains the diff between
        self's and other's values.

        If they are equal, return a NoDiffMember.
        """
        raise NotImplementedError(
            "%s has no diff implemented" % (type(self)))

    def __repr__(self):
        raise NotImplementedError(
            "return short description of the member type %s" % (type(self)))


class IntMember(ValueMember):
    """
    Stores numeric integer values.
    """

    def __init__(self, name, value):
        super().__init__(name)

        self.value = int(value)

    def get_value(self):
        return self.value

    def get_type(self):
        return MemberTypes.INT_MEMBER

    def diff(self, other):
        if self.get_type() is other.get_type():

            if self.get_value() == other.get_value():
                return NoDiffMember(self.name, self)

            else:
                diff_value = other.get_value() - self.get_value()

                return IntMember(self.name, diff_value)

        else:
            raise Exception(
                "type %s member cannot be diffed with type %s" % (type(self), type(other)))

    def __repr__(self):
        return "IntMember<%s>" % (self.name)


class FloatMember(ValueMember):
    """
    Stores numeric floating point values.
    """

    def __init__(self, name, value):
        super().__init__(name)

        self.value = float(value)

    def get_value(self):
        return self.value

    def get_type(self):
        return MemberTypes.FLOAT_MEMBER

    def diff(self, other):
        if self.get_type() is other.get_type():
            # Float must have the last 6 digits in common
            if isclose(self.get_value(), other.get_value(), rel_tol=1e-7):
                return NoDiffMember(self.name, self)

            else:
                diff_value = other.get_value() - self.get_value()

                return FloatMember(self.name, diff_value)

        else:
            raise Exception(
                "type %s member cannot be diffed with type %s" % (type(self), type(other)))

    def __repr__(self):
        return "FloatMember<%s>" % (self.name)


class BooleanMember(ValueMember):
    """
    Stores boolean values.
    """

    def __init__(self, name, value):
        super().__init__(name)

        self.value = bool(value)

    def get_value(self):
        return self.value

    def get_type(self):
        return MemberTypes.BOOLEAN_MEMBER

    def diff(self, other):
        if self.get_type() is other.get_type():
            if self.get_value() == other.get_value():
                return NoDiffMember(self.name, self)

            else:
                return BooleanMember(self.name, other.get_value())

        else:
            raise Exception(
                "type %s member cannot be diffed with type %s" % (type(self), type(other)))

    def __repr__(self):
        return "BooleanMember<%s>" % (self.name)


class IDMember(ValueMember):
    """
    Stores references to media/resource IDs.
    """

    def __init__(self, name, value):
        super().__init__(name)

        self.value = int(value)

    def get_value(self):
        return self.value

    def get_type(self):
        return MemberTypes.ID_MEMBER

    def diff(self, other):
        if self.get_type() is other.get_type():
            if self.get_value() == other.get_value():
                return NoDiffMember(self.name, self)

            else:
                return IDMember(self.name, other.get_value())

        else:
            raise Exception(
                "type %s member cannot be diffed with type %s" % (type(self), type(other)))

    def __repr__(self):
        return "IDMember<%s>" % (self.name)


class BitfieldMember(ValueMember):
    """
    Stores bit field members.
    """

    def __init__(self, name, value):
        super().__init__(name)

        self.value = value

    def get_value(self):
        return self.value

    def get_value_at_pos(self, pos):
        """
        Return the boolean value stored at a specific position
        in the bitfield.

        :param pos: Position in the bitfield, starting with the least significant bit.
        :type pos: int
        """
        return bool(self.value & (2 ** pos))

    def get_type(self):
        return MemberTypes.BITFIELD_MEMBER

    def diff(self, other):
        """
        Uses XOR to determine which bits are different in 'other'.
        """
        if self.get_type() is other.get_type():
            if self.get_value() == other.get_value():
                return NoDiffMember(self.name, self)

            else:
                difference = self.value ^ other.get_value()
                return BitfieldMember(self.name, difference)

        else:
            raise Exception(
                "type %s member cannot be diffed with type %s" % (type(self), type(other)))

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "BitfieldMember<%s>" % (self.name)


class StringMember(ValueMember):
    """
    Stores string values.
    """

    def __init__(self, name, value):
        super().__init__(name)

        self.value = str(value)

    def get_value(self):
        return self.value

    def get_type(self):
        return MemberTypes.STRING_MEMBER

    def diff(self, other):
        if self.get_type() is other.get_type():
            if self.get_value() == other.get_value():
                return NoDiffMember(self.name, self)

            else:
                return StringMember(self.name, other.get_value())

        else:
            raise Exception(
                "type %s member cannot be diffed with type %s" % (type(self), type(other)))

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "StringMember<%s>" % (self.name)


class ContainerMember(ValueMember):
    """
    Stores multiple members as key-value pairs.

    The name of the members are the keys, the member objects
    are the value of the dict.
    """

    def __init__(self, name, submembers):
        """
        :param submembers: Stored members as a list or dict
        :type submembers: list, dict
        """
        super().__init__(name)

        self.value = {}

        # submembers is a list of members
        if not isinstance(submembers, dict):
            self._create_dict(submembers)

        else:
            self.value = submembers

    def get_value(self):
        return self.value

    def get_type(self):
        return MemberTypes.CONTAINER_MEMBER

    def diff(self, other):
        if self.get_type() is other.get_type():
            diff_dict = {}

            other_dict = other.get_value()

            for key in self.value.keys():
                if key in other.value.keys():
                    diff_value = self.value[key].diff(other_dict[key])

                else:
                    # Key is missing in other dict
                    diff_value = RightMissingMember(key, self.value[key])

                diff_dict.update({key: diff_value})

            for key in other.value.keys():
                if key not in self.value.keys():
                    # Key is missing in this dict
                    diff_value = LeftMissingMember(key, other_dict[key])
                    diff_dict.update({key: diff_value})

            if all(isinstance(member, NoDiffMember) for member in diff_dict.values()):
                return NoDiffMember(self.name, self)

            return ContainerMember(self.name, diff_dict)

        else:
            raise Exception(
                "type %s member cannot be diffed with type %s" % (type(self), type(other)))

    def _create_dict(self, member_list):
        """
        Creates the dict from the member list passed to __init__.
        """
        for member in member_list:
            key = member.get_name()

            self.value.update({key: member})

    def __getitem__(self, key):
        """
        Short command for getting a member in the container.
        """
        return self.get_value()[key]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "ContainerMember<%s>" % (self.name)


class ArrayMember(ValueMember):
    """
    Stores an ordered list of members with the same type.
    """

    __slots__ = ('_allowed_member_type')

    def __init__(self, name, allowed_member_type, members):
        super().__init__(name)

        self.value = members

        self._allowed_member_type = allowed_member_type

        # Check if members have correct type
        for member in members:
            if not isinstance(member, (NoDiffMember, LeftMissingMember, RightMissingMember)):
                if member.get_type() is not self._allowed_member_type:
                    raise Exception("%s has type %s, but this ArrayMember only allows %s"
                                    % (member, member.get_type(), allowed_member_type))

    def get_value(self):
        return self.value

    def get_type(self):
        if self._allowed_member_type is MemberTypes.INT_MEMBER:
            return MemberTypes.ARRAY_INT

        elif self._allowed_member_type is MemberTypes.FLOAT_MEMBER:
            return MemberTypes.ARRAY_FLOAT

        elif self._allowed_member_type is MemberTypes.BOOLEAN_MEMBER:
            return MemberTypes.ARRAY_BOOL

        elif self._allowed_member_type is MemberTypes.ID_MEMBER:
            return MemberTypes.ARRAY_ID

        elif self._allowed_member_type is MemberTypes.BITFIELD_MEMBER:
            return MemberTypes.ARRAY_BITFIELD

        elif self._allowed_member_type is MemberTypes.STRING_MEMBER:
            return MemberTypes.ARRAY_STRING

        elif self._allowed_member_type is MemberTypes.CONTAINER_MEMBER:
            return MemberTypes.ARRAY_CONTAINER

        raise Exception("%s has no valid member type" % self)

    def get_container(self, key_member_name, force_not_found= False, force_duplicate=False):
        """
        Returns a ContainerMember generated from an array with type ARRAY_CONTAINER.
        It uses the values of the members with the specified name as keys.
        By default, this method raises an exception if a member with this
        name does not exist or the same key is used twice.

        :param key_member_name: A member in the containers whos value is used as the key.
        :type key_member_name: str
        :param force_not_found: Do not raise an exception if the member is not found.
        :type force_not_found: bool
        :param force_duplicate: Do not raise an exception if the same key value is used twice.
        :type force_duplicate: bool
        """
        if self.get_type() is not MemberTypes.ARRAY_CONTAINER:
            raise Exception("%s: Container can only be generated from arrays with"
                            " type 'contarray', not %s"
                            % (self, self.get_type()))

        member_dict = {}
        for container in self.value:
            if key_member_name not in container.get_value().keys():
                if force_not_found:
                    continue

                raise Exception("%s: Container %s has no member called %s"
                                % (self, container, key_member_name))

            key_member_value = container[key_member_name].get_value()

            if key_member_value in member_dict.keys():
                if force_duplicate:
                    continue

                raise Exception("%s: Duplicate key %s for container member %s"
                                % (self, key_member_value, key_member_name))

            member_dict.update({key_member_value: container})

        return ContainerMember(self.name, member_dict)

    def diff(self, other):
        if self.get_type() == other.get_type():
            diff_list = []
            other_list = other.get_value()

            index = 0
            if len(self) <= len(other):
                while index < len(self):
                    diff_value = self.value[index].diff(other_list[index])
                    diff_list.append(diff_value)
                    index += 1

                while index < len(other):
                    diff_value = other_list[index]
                    diff_list.append(LeftMissingMember(diff_value.name, diff_value))
                    index += 1

            else:
                while index < len(other):
                    diff_value = self.value[index].diff(other_list[index])
                    diff_list.append(diff_value)
                    index += 1

                while index < len(self):
                    diff_value = self.value[index]
                    diff_list.append(RightMissingMember(diff_value.name, diff_value))
                    index += 1

            if all(isinstance(member, NoDiffMember) for member in diff_list):
                return NoDiffMember(self.name, self)

            return ArrayMember(self.name, self._allowed_member_type, diff_list)

        else:
            raise Exception(
                "type %s member cannot be diffed with type %s" % (type(self), type(other)))

    def __getitem__(self, key):
        """
        Short command for getting a member in the array.
        """
        return self.get_value()[key]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "ArrayMember<%s>" % (self.name)


class NoDiffMember(ValueMember):
    """
    Is returned when no difference between two members is found.
    """

    def __init__(self, name, value):
        """
        :param value: Reference to the one of the diffed members.
        :type value: ValueMember
        """
        super().__init__(name)

        self.value = value

    def get_reference(self):
        """
        Returns the reference to the diffed object.
        """
        return self.value

    def __repr__(self):
        return "NoDiffMember<%s>" % (self.name)


class LeftMissingMember(ValueMember):
    """
    Is returned when an array or container on the left side of
    the comparison has no member to compare. It stores the right
    side member as value.
    """

    def __init__(self, name, value):
        """
        :param value: Reference to the right member's object.
        :type value: ValueMember
        """
        super().__init__(name)

        self.value = value

    def get_reference(self):
        """
        Returns the reference to the diffed object.
        """
        return self.value

    def __repr__(self):
        return "LeftMissingMember<%s>" % (self.name)


class RightMissingMember(ValueMember):
    """
    Is returned when an array or container on the right side of
    the comparison has no member to compare. It stores the left
    side member as value.
    """

    def __init__(self, name, value):
        """
        :param value: Reference to the left member's object.
        :type value: ValueMember
        """
        super().__init__(name)

        self.value = value

    def get_reference(self):
        """
        Returns the reference to the diffed object.
        """
        return self.value

    def __repr__(self):
        return "RightMissingMember<%s>" % (self.name)


class MemberTypes(Enum):
    """
    Types for values members.
    """

    INT_MEMBER       = "int"
    FLOAT_MEMBER     = "float"
    BOOLEAN_MEMBER   = "boolean"
    ID_MEMBER        = "id"
    BITFIELD_MEMBER  = "bitfield"
    STRING_MEMBER    = "string"
    CONTAINER_MEMBER = "container"

    # Array types                       # array of:
    ARRAY_INT        = "intarray"       # IntegerMembers
    ARRAY_FLOAT      = "floatarray"     # FloatMembers
    ARRAY_BOOL       = "boolarray"      # BooleanMembers
    ARRAY_ID         = "idarray"        # IDMembers
    ARRAY_BITFIELD   = "bitfieldarray"  # BitfieldMembers
    ARRAY_STRING     = "stringarray"    # StringMembers
    ARRAY_CONTAINER  = "contarray"      # ContainerMembers
