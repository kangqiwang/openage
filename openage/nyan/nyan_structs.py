# Copyright 2019-2020 the openage authors. See copying.md for legal info.

"""
Nyan structs.

Simple implementation to store nyan objects and
members for usage in the converter. This is not
a real nyan^TM implementation, but rather a "dumb"
storage format.

Python does not enforce static types, so be careful
 and only use the provided functions, please. :)
"""

from enum import Enum
import re

from ..util.ordered_set import OrderedSet


INDENT = "    "


class NyanObject:
    """
    Superclass for nyan objects.
    """

    __slots__ = ('name', '_fqon', '_parents', '_inherited_members', '_members',
                 '_nested_objects', '_children')

    def __init__(self, name, parents=None, members=None,
                 nested_objects=None):
        """
        Initializes the object and does some correctness
        checks, for your convenience.
        """
        self.name = name                        # object name

        # unique identifier (in modpack)
        self._fqon = (self.name,)

        self._parents = OrderedSet()            # parent objects
        self._inherited_members = OrderedSet()  # members inherited from parents
        if parents:
            self._parents.update(parents)

        self._members = OrderedSet()            # members unique to this object
        if members:
            self._members.update(members)

        self._nested_objects = OrderedSet()     # nested objects
        if nested_objects:
            self._nested_objects.update(nested_objects)

            for nested_object in self._nested_objects:
                nested_object.set_fqon("%s.%s" % (self._fqon,
                                                  nested_object.get_name()))

        # Set of children
        self._children = OrderedSet()

        self._sanity_check()

        if len(self._parents) > 0:
            self._process_inheritance()

    def add_nested_object(self, new_nested_object):
        """
        Adds a nested object to the nyan object.
        """
        if not isinstance(new_nested_object, NyanObject):
            raise Exception("nested object must have <NyanObject> type")

        if new_nested_object is self:
            raise Exception(
                "nyan object must not contain itself as nested object")

        self._nested_objects.add(new_nested_object)

        new_nested_object.set_fqon((*self._fqon,
                                    new_nested_object.get_name()))

    def add_member(self, new_member):
        """
        Adds a member to the nyan object.
        """
        if new_member.is_inherited():
            raise Exception("added member cannot be inherited")

        if not isinstance(new_member, NyanMember):
            raise Exception("added member must have <NyanMember> type")

        self._members.add(new_member)

        # Update child objects
        for child in self._children:
            # Create a new member for every child with self as parent and origin
            inherited_member = InheritedNyanMember(
                new_member.get_name(),
                new_member.get_member_type(),
                self,
                self,
                None,
                new_member.get_set_type(),
                None,
                0,
                new_member.is_optional()
            )
            child.update_inheritance(inherited_member)

    def add_child(self, new_child):
        """
        Registers another object as a child.
        """
        if not isinstance(new_child, NyanObject):
            raise Exception("children must have <NyanObject> type")

        self._children.add(new_child)

        # Pass members and inherited members to the child object
        for member in self._members:
            # Create a new member with self as parent and origin
            inherited_member = InheritedNyanMember(
                member.get_name(),
                member.get_member_type(),
                self,
                self,
                None,
                member.get_set_type(),
                None,
                0,
                member.is_optional()
            )
            new_child.update_inheritance(inherited_member)

        for inherited in self._inherited_members:
            # Create a new member with self as parent
            inherited_member = InheritedNyanMember(
                inherited.get_name(),
                inherited.get_member_type(),
                self,
                inherited.get_origin(),
                None,
                inherited.get_set_type(),
                None,
                0,
                inherited.is_optional()
            )
            new_child.update_inheritance(inherited_member)

    def has_member(self, member_name, origin=None):
        """
        Returns True if the NyanMember with the specified name exists.
        """
        if origin and origin is not self:
            for inherited_member in self._inherited_members:
                if origin == inherited_member.get_origin():
                    if inherited_member.get_name() == member_name:
                        return True

        else:
            for member in self._members:
                if member.get_name() == member_name:
                    return True

        return False

    def get_fqon(self):
        """
        Returns the fqon of the nyan object.
        """
        return self._fqon

    def get_members(self):
        """
        Returns all NyanMembers of the object, excluding members from nested objects.
        """
        return self._members.union(self._inherited_members)

    def get_member_by_name(self, member_name, origin=None):
        """
        Returns the NyanMember with the specified name or
        None if there is no member with that name.
        """
        if origin and origin is not self:
            for inherited_member in self._inherited_members:
                if origin == inherited_member.get_origin():
                    if inherited_member.get_name() == member_name:
                        return inherited_member

            raise Exception("%s has no member '%s' with origin '%s'"
                            % (self, member_name, origin))
        else:
            for member in self._members:
                if member.get_name() == member_name:
                    return member

        raise Exception("%s has no member '%s'" % (self, member_name))

    def get_name(self):
        """
        Returns the name of the object.
        """
        return self.name

    def get_nested_objects(self):
        """
        Returns all nested NyanObjects of this object.
        """
        return self._nested_objects

    def get_parents(self):
        """
        Returns all nested parents of this object.
        """
        return self._parents

    def has_ancestor(self, nyan_object):
        """
        Returns True if the given nyan object is an ancestor
        of this nyan object.
        """
        for parent in self._parents:
            if parent is nyan_object:
                return True

        for parent in self._parents:
            if parent.has_ancestor(nyan_object):
                return True

        return False

    def is_abstract(self):
        """
        Returns True if unique or inherited members were
        not initialized.
        """
        for member in self.get_members():
            if not member.is_initialized():
                return True

        return False

    def is_patch(self):
        """
        Returns True if the object is a NyanPatch.
        """
        return False

    def set_fqon(self, new_fqon):
        """
        Set a new value for the fqon.
        """
        if isinstance(new_fqon, str):
            self._fqon = new_fqon.split(".")

        elif isinstance(new_fqon, tuple):
            self._fqon = new_fqon

        else:
            raise Exception("%s: Fqon must be a tuple(str) not %s"
                            % (self, type(new_fqon)))

        # Recursively set fqon for nested objects
        for nested_object in self._nested_objects:
            nested_fqon = (*new_fqon, nested_object.get_name())
            nested_object.set_fqon(nested_fqon)

    def update_inheritance(self, new_inherited_member):
        """
        Add an inherited member to the object. Should only be used by
        parent objects.
        """
        if not self.has_ancestor(new_inherited_member.get_origin()):
            raise Exception("%s: cannot add inherited member %s because"
                            " %s is not an ancestor of %s"
                            % (self.__repr__(), new_inherited_member,
                               new_inherited_member.get_origin(), self))

        if not isinstance(new_inherited_member, InheritedNyanMember):
            raise Exception("added member must have <InheritedNyanMember> type")

        # Only add it, if it was not inherited before
        if not self.has_member(new_inherited_member.get_name(),
                               new_inherited_member.get_origin()):
            self._inherited_members.add(new_inherited_member)

        # Update child objects
        for child in self._children:
            # Create a new member for every child with self as parent
            inherited_member = InheritedNyanMember(
                new_inherited_member.get_name(),
                new_inherited_member.get_member_type(),
                self,
                new_inherited_member.get_origin(),
                None,
                new_inherited_member.get_set_type(),
                None,
                0,
                new_inherited_member.is_optional()
            )
            child.update_inheritance(inherited_member)

    def dump(self, indent_depth=0, import_tree=None):
        """
        Returns the string representation of the object.
        """
        # Header
        output_str = "%s" % (self.get_name())

        output_str += self._prepare_inheritance_content(import_tree=import_tree)

        # Members
        output_str += self._prepare_object_content(indent_depth, import_tree=import_tree)

        return output_str

    def _prepare_object_content(self, indent_depth, import_tree=None):
        """
        Returns a string containing the nyan object's content
        (members, nested objects).

        Subroutine of dump().
        """
        output_str = ""
        empty = True

        if len(self._inherited_members) > 0:
            for inherited_member in self._inherited_members:
                if inherited_member.has_value():
                    empty = False
                    output_str += "%s%s\n" % (
                        (indent_depth + 1) * INDENT,
                        inherited_member.dump(import_tree=import_tree)
                    )
            if not empty:
                output_str += "\n"

        if len(self._members) > 0:
            empty = False
            for member in self._members:
                if self.is_patch():
                    # Patches do not need the type definition
                    output_str += "%s%s\n" % (
                        (indent_depth + 1) * INDENT,
                        member.dump_short(import_tree=import_tree)
                    )
                else:
                    output_str += "%s%s\n" % (
                        (indent_depth + 1) * INDENT,
                        member.dump(import_tree=import_tree)
                    )

            output_str += "\n"

        # Nested objects
        if len(self._nested_objects) > 0:
            empty = False
            for nested_object in self._nested_objects:
                output_str += "%s%s" % (
                    (indent_depth + 1) * INDENT,
                    nested_object.dump(
                        indent_depth + 1,
                        import_tree
                    )
                )

            output_str += ""

        # Empty objects need a 'pass' line
        if empty:
            output_str += "%spass\n\n" % ((indent_depth + 1) * INDENT)

        return output_str

    def _prepare_inheritance_content(self, import_tree=None):
        """
        Returns a string containing the nyan object's inheritance set
        in the header.

        Subroutine of dump().
        """
        output_str = "("

        if len(self._parents) > 0:
            for parent in self._parents:
                if import_tree:
                    sfqon = ".".join(import_tree.get_alias_fqon(parent.get_fqon()))

                else:
                    sfqon = ".".join(parent.get_fqon())

                output_str += "%s, " % (sfqon)

            output_str = output_str[:-2]

        output_str += "):\n"

        return output_str

    def _process_inheritance(self):
        """
        Notify parents of the object.
        """
        for parent in self._parents:
            parent.add_child(self)

    def _sanity_check(self):
        """
        Check if the object conforms to nyan grammar rules. Also does
        a bunch of type checks.
        """
        # self.name must be a string
        if not isinstance(self.name, str):
            raise Exception("%s: 'name' must be a string" % (self.__repr__()))

        # self.name must conform to nyan grammar rules
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", self.name):
            raise Exception("%s: 'name' is not well-formed" %
                            (self.__repr__()))

        # self._parents must be NyanObjects
        for parent in self._parents:
            if not isinstance(parent, NyanObject):
                raise Exception("%s: %s must have NyanObject type"
                                % (self.__repr__(), parent.__repr__()))

        # self._members must be NyanMembers
        for member in self._members:
            if not isinstance(member, NyanMember):
                raise Exception("%s: %s must have NyanMember type"
                                % (self.__repr__(), member.__repr__()))

            # a member in self._members must also not be inherited
            if isinstance(member, InheritedNyanMember):
                raise Exception("%s: %s must not have InheritedNyanMember type"
                                % (self.__repr__(), member.__repr__()))

        # self._nested_objects must be NyanObjects
        for nested_object in self._nested_objects:
            if not isinstance(nested_object, NyanObject):
                raise Exception("%s: %s must have NyanObject type"
                                % (self.__repr__(),
                                   nested_object.__repr__()))

            if nested_object is self:
                raise Exception("%s: must not contain itself as nested object"
                                % (self.__repr__()))

    def __repr__(self):
        return "NyanObject<%s>" % (self.name)


class NyanPatch(NyanObject):
    """
    Superclass for nyan patches.
    """

    __slots__ = ('_target', '_add_inheritance')

    def __init__(self, name, parents=None, members=None, nested_objects=None,
                 target=None, add_inheritance=None):

        self._target = target                  # patch target (can be added later)
        self._add_inheritance = OrderedSet()   # new inheritance
        if add_inheritance:
            self._add_inheritance.update(add_inheritance)

        super().__init__(name, parents, members, nested_objects)

    def get_target(self):
        """
        Returns the target of the patch.
        """
        return self._target

    def is_abstract(self):
        """
        Returns True if unique or inherited members were
        not initialized or the patch target is not set.
        """
        return super().is_abstract() or not self._target

    def is_patch(self):
        """
        Returns True if the object is a nyan patch.
        """
        return True

    def set_target(self, target):
        """
        Set the target of the patch.
        """
        self._target = target

        if not isinstance(self._target, NyanObject):
            raise Exception("%s: '_target' must have NyanObject type"
                            % (self.__repr__()))

    def dump(self, indent_depth=0, import_tree=None):
        """
        Returns the string representation of the object.
        """
        # Header
        output_str = "%s" % (self.get_name())

        if import_tree:
            sfqon = ".".join(import_tree.get_alias_fqon(self._target.get_fqon()))

        else:
            sfqon = ".".join(self._target.get_fqon())

        output_str += "<%s>" % (sfqon)

        if len(self._add_inheritance) > 0:
            output_str += "["

            for new_inheritance in self._add_inheritance:
                if import_tree:
                    sfqon = ".".join(import_tree.get_alias_fqon(new_inheritance.get_fqon()))

                else:
                    sfqon = ".".join(new_inheritance.get_fqon())

                if new_inheritance[0] == "FRONT":
                    output_str += "+%s, " % (sfqon)
                elif new_inheritance[0] == "BACK":
                    output_str += "%s+, " % (sfqon)

            output_str = output_str[:-2] + "]"

        output_str += super()._prepare_inheritance_content(import_tree=import_tree)

        # Members
        output_str += super()._prepare_object_content(indent_depth=indent_depth,
                                                      import_tree=import_tree)

        return output_str

    def _sanity_check(self):
        """
        Check if the object conforms to nyan grammar rules. Also does
        a bunch of type checks.
        """
        super()._sanity_check()

        # Target must be a nyan object
        if self._target:
            if not isinstance(self._target, NyanObject):
                raise Exception("%s: '_target' must have NyanObject type"
                                % (self.__repr__()))

        # Added inheritance must be tuples of "FRONT"/"BACK"
        # and a nyan object
        if len(self._add_inheritance) > 0:
            for inherit in self._add_inheritance:
                if not isinstance(inherit, tuple):
                    raise Exception("%s: '_add_inheritance' must be a tuple"
                                    % (self.__repr__()))

                if len(inherit) != 2:
                    raise Exception("%s: '_add_inheritance' tuples must have length 2"
                                    % (self.__repr__()))

                if inherit[0] not in ("FRONT", "BACK"):
                    raise Exception("%s: added inheritance must be FRONT or BACK mode"
                                    % (self.__repr__()))

                if not isinstance(inherit[1], NyanObject):
                    raise Exception("%s: added inheritance must contain NyanObject"
                                    % (self.__repr__()))

    def __repr__(self):
        return "NyanPatch<%s<%s>>" % (self.name, self._target.name)


class NyanMember:
    """
    Superclass for all nyan members.
    """

    __slots__ = ('name', '_member_type', '_set_type', '_optional', '_override_depth',
                 '_operator', 'value')

    def __init__(self, name, member_type, value=None, operator=None,
                 override_depth=0, set_type=None, optional=False):
        """
        Initializes the member and does some correctness
        checks, for your convenience.
        """
        self.name = name                                # identifier

        if isinstance(member_type, NyanObject):         # type
            self._member_type = member_type
        else:
            self._member_type = MemberType(member_type)

        self._set_type = None                           # set/orderedset type
        if set_type:
            if isinstance(set_type, NyanObject):
                self._set_type = set_type
            else:
                self._set_type = MemberType(set_type)

        self._optional = optional                       # whether the value is allowed to be NYAN_NONE
        self._override_depth = override_depth           # override depth

        self._operator = None
        self.value = None                               # value
        if operator:
            operator = MemberOperator(operator)   # operator type

        if value is not None:
            self.set_value(value, operator)

        # check for errors in the initilization
        self._sanity_check()

    def get_name(self):
        """
        Returns the name of the member.
        """
        return self.name

    def get_member_type(self):
        """
        Returns the type of the member.
        """
        return self._member_type

    def get_set_type(self):
        """
        Returns the set type of the member.
        """
        return self._set_type

    def get_operator(self):
        """
        Returns the operator of the member.
        """
        return self._operator

    def get_override_depth(self):
        """
        Returns the override depth of the member.
        """
        return self._override_depth

    def get_value(self):
        """
        Returns the value of the member.
        """
        return self.value

    def is_complex(self):
        """
        Returns True if the member is a set or orderedset.
        """
        return self._member_type in (MemberType.SET, MemberType.ORDEREDSET)

    def is_initialized(self):
        """
        Returns True if the member has a value.
        """
        return self.value is not None

    def is_inherited(self):
        """
        Returns True if the member is inherited from another object.
        """
        return False

    def is_optional(self):
        """
        Returns True if the member is optional.
        """
        return self._optional

    def set_value(self, value, operator=None):
        """
        Set the value of the nyan member to the specified value and
        optionally, the operator.
        """
        if not self.value and not operator:
            raise Exception("Setting a value for an uninitialized member "
                            "requires also setting the operator")

        self.value = value
        self._operator = operator

        if self.value not in (MemberSpecialValue.NYAN_INF, MemberSpecialValue.NYAN_NONE):
            self._type_conversion()

        self._sanity_check()

        if isinstance(self._member_type, NyanObject) and\
                value is not MemberSpecialValue.NYAN_NONE:
            if not (self.value is self._member_type or
                    self.value.has_ancestor(self._member_type)):
                raise Exception(("%s: 'value' with type NyanObject must "
                                 "have their member type as ancestor")
                                % (self.__repr__()))

    def dump(self, import_tree=None):
        """
        Returns the nyan string representation of the member.
        """
        output_str = "%s" % (self.name)

        type_str = ""

        if isinstance(self._member_type, NyanObject):
            if import_tree:
                sfqon = ".".join(import_tree.get_alias_fqon(self._member_type.get_fqon()))

            else:
                sfqon = ".".join(self._member_type.get_fqon())

            type_str = sfqon

        else:
            type_str = self._member_type.value

        if self._optional:
            output_str += " : optional(%s)" % (type_str)

        else:
            output_str += " : %s" % (type_str)

        if self.is_complex():
            if isinstance(self._set_type, NyanObject):
                if import_tree:
                    sfqon = ".".join(import_tree.get_alias_fqon(self._set_type.get_fqon()))

                else:
                    sfqon = ".".join(self._set_type.get_fqon())

                output_str += "(%s)" % (sfqon)

            else:
                output_str += "(%s)" % (self._set_type.value)

        if self.is_initialized():
            output_str += " %s%s %s" % ("@" * self._override_depth,
                                        self._operator.value,
                                        self._get_str_representation(import_tree=import_tree))

        return output_str

    def dump_short(self, import_tree=None):
        """
        Returns the nyan string representation of the member, but
        without the type definition.
        """
        return "%s %s%s %s" % (self.get_name(),
                               "@" * self._override_depth,
                               self._operator.value,
                               self._get_str_representation(import_tree=import_tree))

    def _sanity_check(self):
        """
        Check if the member conforms to nyan grammar rules. Also does
        a bunch of type checks.
        """
        # self.name must be a string
        if not isinstance(self.name, str):
            raise Exception("%s: 'name' must be a string"
                            % (self.__repr__()))

        # self.name must conform to nyan grammar rules
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", self.name[0]):
            raise Exception("%s: 'name' is not well-formed"
                            % (self.__repr__()))

        if self.is_complex():
            # if the member type is complex, then the set type needs
            # to be initialized
            if not self._set_type:
                raise Exception("%s: '_set_type' is required for complex types"
                                % (self.__repr__()))

            # set types cannot be sets
            if self._set_type in (MemberType.SET, MemberType.ORDEREDSET):
                raise Exception("%s: '_set_type' cannot be complex but is %s"
                                % (self.__repr__(), self._set_type))

        else:
            # if the member is not complex, the set type should be None
            if self._set_type:
                raise Exception("%s: member has '_set_type' but is not complex"
                                % (self.__repr__()))

        if (self.is_initialized() and not isinstance(self, InheritedNyanMember)) or\
                (isinstance(self, InheritedNyanMember) and self.has_value()):
            # Check if operator type matches with member type
            if self._member_type in (MemberType.INT, MemberType.FLOAT)\
                    and self._operator not in (MemberOperator.ASSIGN,
                                               MemberOperator.ADD,
                                               MemberOperator.SUBTRACT,
                                               MemberOperator.MULTIPLY,
                                               MemberOperator.DIVIDE):
                raise Exception("%s: %s is not a valid operator for %s member type"
                                % (self.__repr__(), self._operator,
                                   self._member_type))

            elif self._member_type is MemberType.TEXT\
                    and self._operator not in (MemberOperator.ASSIGN,
                                               MemberOperator.ADD):
                raise Exception("%s: %s is not a valid operator for %s member type"
                                % (self.__repr__(), self._operator,
                                   self._member_type))

            elif self._member_type is MemberType.FILE\
                    and self._operator is not MemberOperator.ASSIGN:
                raise Exception("%s: %s is not a valid operator for %s member type"
                                % (self.__repr__(), self._operator,
                                   self._member_type))

            elif self._member_type is MemberType.BOOLEAN\
                    and self._operator not in (MemberOperator.ASSIGN,
                                               MemberOperator.AND,
                                               MemberOperator.OR):
                raise Exception("%s: %s is not a valid operator for %s member type"
                                % (self.__repr__(), self._operator,
                                   self._member_type))

            elif self._member_type is MemberType.SET\
                    and self._operator not in (MemberOperator.ASSIGN,
                                               MemberOperator.ADD,
                                               MemberOperator.SUBTRACT,
                                               MemberOperator.AND,
                                               MemberOperator.OR):
                raise Exception("%s: %s is not a valid operator for %s member type"
                                % (self.__repr__(), self._operator,
                                   self._member_type))

            elif self._member_type is MemberType.ORDEREDSET\
                    and self._operator not in (MemberOperator.ASSIGN,
                                               MemberOperator.ADD,
                                               MemberOperator.SUBTRACT,
                                               MemberOperator.AND):
                raise Exception("%s: %s is not a valid operator for %s member type"
                                % (self.__repr__(), self._operator,
                                   self._member_type))

            # override depth must be a non-negative integer
            if not (isinstance(self._override_depth, int) and
                    self._override_depth >= 0):
                raise Exception("%s: '_override_depth' must be a non-negative integer"
                                % (self.__repr__()))

            # Member values can only be NYAN_NONE if the member is optional
            if self.value is MemberSpecialValue.NYAN_NONE and not\
                    self._optional:
                raise Exception("%s: 'value' is NYAN_NONE but member is not optional"
                                % (self.__repr__()))

            if self.value is MemberSpecialValue.NYAN_INF and\
                    self._member_type not in (MemberType.INT, MemberType.FLOAT):
                raise Exception("%s: 'value' is NYAN_INF but member type is not "
                                "INT or FLOAT" % (self.__repr__()))

            # NYAN_NONE values can only be assigned
            if self.value is MemberSpecialValue.NYAN_NONE and\
                    self._operator is not MemberOperator.ASSIGN:
                raise Exception(("%s: 'value' with NYAN_NONE can only have operator type "
                                 "MemberOperator.ASSIGN") % (self.__repr__()))

            if isinstance(self._member_type, NyanObject) and self.value\
                    and self.value is not MemberSpecialValue.NYAN_NONE:
                if not (self.value is self._member_type or
                        self.value.has_ancestor((self._member_type))):
                    raise Exception(("%s: 'value' with type NyanObject must "
                                     "have their member type as ancestor")
                                    % (self.__repr__()))

    def _type_conversion(self):
        """
        Explicit type conversion of the member value.

        This lets us convert data fields without worrying about the
        correct types too much, e.g. if a boolean is stored as uint8.
        """
        if self._member_type is MemberType.INT and\
                self._operator not in (MemberOperator.DIVIDE, MemberOperator.MULTIPLY):
            self.value = int(self.value)

        elif self._member_type is MemberType.FLOAT:
            self.value = float(self.value)

        elif self._member_type is MemberType.TEXT:
            self.value = str(self.value)

        elif self._member_type is MemberType.FILE:
            self.value = str(self.value)

        elif self._member_type is MemberType.BOOLEAN:
            self.value = bool(self.value)

        elif self._member_type is MemberType.SET:
            self.value = OrderedSet(self.value)

        elif self._member_type is MemberType.ORDEREDSET:
            self.value = OrderedSet(self.value)

    def _get_primitive_value_str(self, member_type, value, import_tree=None):
        """
        Returns the nyan string representation of primitive values.

        Subroutine of _get_str_representation()
        """
        if member_type is MemberType.FLOAT:
            return "%sf" % value

        elif member_type in (MemberType.TEXT, MemberType.FILE):
            return "\"%s\"" % (value)

        elif isinstance(member_type, NyanObject):
            if import_tree:
                sfqon = ".".join(import_tree.get_alias_fqon(value.get_fqon()))

            else:
                sfqon = ".".join(value.get_fqon())

            return sfqon

        return "%s" % value

    def _get_str_representation(self, import_tree=None):
        """
        Returns the nyan string representation of the value.
        """
        if not self.is_initialized():
            return "UNINITIALIZED VALUE %s" % self.__repr__()

        if self._optional and self.value is MemberSpecialValue.NYAN_NONE:
            return MemberSpecialValue.NYAN_NONE.value

        if self.value is MemberSpecialValue.NYAN_INF:
            return MemberSpecialValue.NYAN_INF.value

        if self._member_type in (MemberType.INT, MemberType.FLOAT,
                                 MemberType.TEXT, MemberType.FILE,
                                 MemberType.BOOLEAN):
            return self._get_primitive_value_str(self._member_type,
                                                 self.value,
                                                 import_tree=import_tree)

        elif self._member_type in (MemberType.SET, MemberType.ORDEREDSET):
            output_str = ""

            if self._member_type is MemberType.ORDEREDSET:
                output_str += "o"

            output_str += "{"

            if len(self.value) > 0:
                for val in self.value:
                    output_str += "%s, " % self._get_primitive_value_str(
                        self._set_type,
                        val,
                        import_tree=import_tree
                    )

                return output_str[:-2] + "}"

            return output_str + "}"

        elif isinstance(self._member_type, NyanObject):
            if import_tree:
                sfqon = ".".join(import_tree.get_alias_fqon(self.value.get_fqon()))

            else:
                sfqon = ".".join(self.value.get_fqon())

            return sfqon

        else:
            raise Exception("%s has no valid type" % self.__repr__())

    def __str__(self):
        return self._get_str_representation()

    def __repr__(self):
        return "NyanMember<%s: %s>" % (self.name, self._member_type)


class NyanPatchMember(NyanMember):
    """
    Nyan members for patches.
    """

    __slots__ = ('_patch_target', '_member_origin')

    def __init__(self, name, patch_target, member_origin, value,
                 operator, override_depth=0):
        """
        Initializes the member and does some correctness checks,
        for your convenience. Other than the normal members,
        patch members must initialize all values in the constructor
        """
        # the target object of the patch
        self._patch_target = patch_target

        # the origin of the patched member from the patch target
        self._member_origin = member_origin

        target_member_type, target_set_type = self._get_target_member_type(name, member_origin)

        super().__init__(name, target_member_type, value, operator,
                         override_depth, target_set_type, False)

    def get_name_with_origin(self):
        """
        Returns the name of the member in <member_origin>.<name> form.
        """
        return "%s.%s" % (self._member_origin.name, self.name)

    def dump(self, import_tree=None):
        """
        Returns the string representation of the member.
        """
        return self.dump_short(import_tree=import_tree)

    def dump_short(self, import_tree=None):
        """
        Returns the nyan string representation of the member, but
        without the type definition.
        """
        return "%s %s%s %s" % (self.get_name_with_origin(),
                               "@" * self._override_depth,
                               self._operator.value,
                               self._get_str_representation(import_tree=import_tree))

    def _sanity_check(self):
        """
        Check if the member conforms to nyan grammar rules. Also does
        a bunch of type checks.
        """
        super()._sanity_check()

        # patch target must be a nyan object
        if not isinstance(self._patch_target, NyanObject):
            raise Exception("%s: '_patch_target' must have NyanObject type"
                            % (self))

        # member origin must be a nyan object
        if not isinstance(self._member_origin, NyanObject):
            raise Exception("%s: '_member_origin' must have NyanObject type"
                            % (self))

    def _get_target_member_type(self, name, origin):
        """
        Retrieves the type of the patched member.
        """
        target_member = self._member_origin.get_member_by_name(name, origin)

        return target_member.get_member_type(), target_member.get_set_type()

    def __repr__(self):
        return "NyanPatchMember<%s: %s>" % (self.name, self._member_type)


class InheritedNyanMember(NyanMember):
    """
    Nyan members inherited from other objects.
    """

    __slots__ = ('_parent', '_origin')

    def __init__(self, name, member_type, parent, origin, value=None,
                 set_type=None, operator=None, override_depth=0, optional=False):
        """
        Initializes the member and does some correctness
        checks, for your convenience.
        """

        self._parent = parent               # the direct parent of the object which contains the member

        self._origin = origin               # nyan object which originally defined the member

        super().__init__(name, member_type, value, operator,
                         override_depth, set_type, optional)

    def get_name_with_origin(self):
        """
        Returns the name of the member in <origin>.<name> form.
        """
        return "%s.%s" % (self._origin.name, self.name)

    def get_origin(self):
        """
        Returns the origin of the member.
        """
        return self._origin

    def get_parent(self):
        """
        Returns the direct parent of the member.
        """
        return self._parent

    def is_inherited(self):
        """
        Returns True if the member is inherited from another object.
        """
        return True

    def is_initialized(self):
        """
        Returns True if self or the parent is initialized.
        """
        return super().is_initialized() or\
            self._parent.get_member_by_name(self.name, self._origin).is_initialized()

    def has_value(self):
        """
        Returns True if the inherited member has a value
        """
        return self.value is not None

    def dump(self, import_tree=None):
        """
        Returns the string representation of the member.
        """
        return self.dump_short(import_tree=import_tree)

    def dump_short(self, import_tree=None):
        """
        Returns the nyan string representation of the member, but
        without the type definition.
        """
        return "%s %s%s %s" % (self.get_name_with_origin(),
                               "@" * self._override_depth,
                               self._operator.value,
                               self._get_str_representation(import_tree=import_tree))

    def _sanity_check(self):
        """
        Check if the member conforms to nyan grammar rules. Also does
        a bunch of type checks.
        """
        super()._sanity_check()

        # parent must be a nyan object
        if not isinstance(self._parent, NyanObject):
            raise Exception("%s: '_parent' must have NyanObject type"
                            % (self.__repr__()))

        # origin must be a nyan object
        if not isinstance(self._origin, NyanObject):
            raise Exception("%s: '_origin' must have NyanObject type"
                            % (self.__repr__()))

    def __repr__(self):
        return "InheritedNyanMember<%s: %s>" % (self.name, self._member_type)


class MemberType(Enum):
    """
    Symbols for nyan member types.
    """

    # Primitive types
    INT = "int"
    FLOAT = "float"
    TEXT = "text"
    FILE = "file"
    BOOLEAN = "bool"

    # Complex types
    SET = "set"
    ORDEREDSET = "orderedset"


class MemberSpecialValue(Enum):
    """
    Symbols for special nyan values.
    """
    # nyan none type
    NYAN_NONE = "None"

    # infinite value for float and int
    NYAN_INF = "inf"


class MemberOperator(Enum):
    """
    Symbols for nyan member operators.
    """

    ASSIGN = "="        # assignment
    ADD = "+="          # addition, append, insertion, union
    SUBTRACT = "-="     # subtraction, remove
    MULTIPLY = "*="     # multiplication
    DIVIDE = "/="       # division
    AND = "&="          # logical AND, intersect
    OR = "|="           # logical OR, union
