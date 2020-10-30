# Copyright 2019-2020 the openage authors. See copying.md for legal info.
#
# pylint: disable=too-many-instance-attributes,too-few-public-methods

"""
Object for comparing and passing around data from a dataset.
"""

from ..converter_object import ConverterObjectContainer


class GenieObjectContainer(ConverterObjectContainer):
    """
    Contains everything from the dat file, sorted into several
    categories.
    """

    def __init__(self):

        # Game version
        self.game_version = None

        # API reference
        self.nyan_api_objects = None

        # Things that don't exist in the game, e.g. Attributes
        # saved as RawAPIObjects
        self.pregen_nyan_objects = {}

        # Auxiliary
        self.strings = None
        self.existing_graphics = None

        # Phase 1: Genie-like objects
        # ConverterObject types (the data from the game)
        # key: obj_id; value: ConverterObject instance
        self.genie_units = {}
        self.genie_techs = {}
        self.genie_effect_bundles = {}
        self.genie_civs = {}
        self.age_connections = {}
        self.building_connections = {}
        self.unit_connections = {}
        self.tech_connections = {}
        self.genie_graphics = {}
        self.genie_sounds = {}
        self.genie_terrains = {}

        # Phase 2: API-like objects
        # ConverterObjectGroup types (things that will become
        # nyan objects)
        # key: group_id; value: ConverterObjectGroup instance
        self.unit_lines = {}                        # Keys are the ID of the first unit in line
        self.unit_lines_vertical_ref = {}           # Keys are the line ID of the unit connection
        self.building_lines = {}
        self.task_groups = {}
        self.transform_groups = {}
        self.villager_groups = {}
        self.monk_groups = {}
        self.ambient_groups = {}
        self.variant_groups = {}

        self.civ_groups = {}

        self.tech_groups = {}
        self.age_upgrades = {}
        self.unit_upgrades = {}
        self.building_upgrades = {}
        self.stat_upgrades = {}
        self.unit_unlocks = {}
        self.building_unlocks = {}
        self.civ_boni = {}
        self.initiated_techs = {}
        self.node_techs = {}

        self.terrain_groups = {}

        # Stores which line a unit is part of
        # key: unit id; value: ConverterObjectGroup
        self.unit_ref = {}

        # Phase 3: sprites, sounds
        self.combined_sprites = {}          # Animation or Terrain graphics
        self.combined_sounds = {}
        self.combined_terrains = {}

        self.graphics_exports = {}
        self.sound_exports = {}
        self.metadata_exports = []

    def __repr__(self):
        return "GenieObjectContainer"
