# Copyright 2015-2020 the openage authors. See copying.md for legal info.

# TODO pylint: disable=C,R

from .....entity_object.conversion.genie_structure import GenieStructure
from ....read.member_access import READ, SKIP
from ....read.read_members import SubdataMember
from ....read.value_members import MemberTypes as StorageType


class MapInfo(GenieStructure):
    name_struct_file   = "randommap"
    name_struct        = "map_header"
    struct_description = "random map information header"

    @classmethod
    def get_data_format_members(cls, game_version):
        """
        Return the members in this struct.
        """
        data_format = [
            (READ, "map_id", StorageType.ID_MEMBER, "int32_t"),
            (READ, "border_south_west", StorageType.INT_MEMBER, "int32_t"),
            (READ, "border_north_west", StorageType.INT_MEMBER, "int32_t"),
            (READ, "border_north_east", StorageType.INT_MEMBER, "int32_t"),
            (READ, "border_south_east", StorageType.INT_MEMBER, "int32_t"),
            (READ, "border_usage", StorageType.INT_MEMBER, "int32_t"),
            (READ, "water_shape", StorageType.INT_MEMBER, "int32_t"),
            (READ, "base_terrain", StorageType.INT_MEMBER, "int32_t"),
            (READ, "land_coverage", StorageType.INT_MEMBER, "int32_t"),
            (SKIP, "unused_id", StorageType.ID_MEMBER, "int32_t"),
            (READ, "base_zone_count", StorageType.INT_MEMBER, "uint32_t"),
            (READ, "base_zone_ptr", StorageType.ID_MEMBER, "int32_t"),
            (READ, "map_terrain_count", StorageType.INT_MEMBER, "uint32_t"),
            (READ, "map_terrain_ptr", StorageType.ID_MEMBER, "int32_t"),
            (READ, "map_unit_count", StorageType.INT_MEMBER, "uint32_t"),
            (READ, "map_unit_ptr", StorageType.ID_MEMBER, "int32_t"),
            (READ, "map_elevation_count", StorageType.INT_MEMBER, "uint32_t"),
            (READ, "map_elevation_ptr", StorageType.ID_MEMBER, "int32_t"),
        ]

        return data_format


class MapLand(GenieStructure):
    name_struct_file   = "randommap"
    name_struct        = "map"
    struct_description = "random map information data"

    @classmethod
    def get_data_format_members(cls, game_version):
        """
        Return the members in this struct.
        """
        data_format = [
            (READ, "land_id", StorageType.ID_MEMBER, "int32_t"),
            (READ, "terrain", StorageType.ID_MEMBER, "int32_t"),
            (READ, "land_spacing", StorageType.INT_MEMBER, "int32_t"),
            (READ, "base_size", StorageType.INT_MEMBER, "int32_t"),
            (READ, "zone", StorageType.INT_MEMBER, "int8_t"),
            (READ, "placement_type", StorageType.ID_MEMBER, "int8_t"),
            (SKIP, "padding1", StorageType.INT_MEMBER, "int16_t"),
            (READ, "base_x", StorageType.INT_MEMBER, "int32_t"),
            (READ, "base_y", StorageType.INT_MEMBER, "int32_t"),
            (READ, "land_proportion", StorageType.INT_MEMBER, "int8_t"),
            (READ, "by_player_flag", StorageType.ID_MEMBER, "int8_t"),
            (SKIP, "padding2", StorageType.INT_MEMBER, "int16_t"),
            (READ, "start_area_radius", StorageType.INT_MEMBER, "int32_t"),
            (READ, "terrain_edge_fade", StorageType.INT_MEMBER, "int32_t"),
            (READ, "clumpiness", StorageType.INT_MEMBER, "int32_t"),
        ]

        return data_format


class MapTerrain(GenieStructure):
    name_struct_file   = "randommap"
    name_struct        = "map_terrain"
    struct_description = "random map terrain information data"

    @classmethod
    def get_data_format_members(cls, game_version):
        """
        Return the members in this struct.
        """
        data_format = [
            (READ, "proportion", StorageType.INT_MEMBER, "int32_t"),
            (READ, "terrain_id", StorageType.ID_MEMBER, "int32_t"),
            (READ, "number_of_clumps", StorageType.INT_MEMBER, "int32_t"),
            (READ, "edge_spacing", StorageType.INT_MEMBER, "int32_t"),
            (READ, "placement_zone", StorageType.INT_MEMBER, "int32_t"),
            (READ, "clumpiness", StorageType.INT_MEMBER, "int32_t"),
        ]

        return data_format


class MapUnit(GenieStructure):
    name_struct_file   = "randommap"
    name_struct        = "map_unit"
    struct_description = "random map unit information data"

    @classmethod
    def get_data_format_members(cls, game_version):
        """
        Return the members in this struct.
        """
        data_format = [
            (READ, "unit_id", StorageType.ID_MEMBER, "int32_t"),
            (READ, "host_terrain", StorageType.ID_MEMBER, "int32_t"),   # -1 = land; 1 = water
            (READ, "group_placing", StorageType.ID_MEMBER, "int8_t"),   # 0 =
            (READ, "scale_flag", StorageType.BOOLEAN_MEMBER, "int8_t"),
            (SKIP, "padding1", StorageType.INT_MEMBER, "int16_t"),
            (READ, "objects_per_group", StorageType.INT_MEMBER, "int32_t"),
            (READ, "fluctuation", StorageType.INT_MEMBER, "int32_t"),
            (READ, "groups_per_player", StorageType.INT_MEMBER, "int32_t"),
            (READ, "group_radius", StorageType.INT_MEMBER, "int32_t"),
            (READ, "own_at_start", StorageType.INT_MEMBER, "int32_t"),  # -1 = player unit; 0 = else
            (READ, "set_place_for_all_players", StorageType.INT_MEMBER, "int32_t"),
            (READ, "min_distance_to_players", StorageType.INT_MEMBER, "int32_t"),
            (READ, "max_distance_to_players", StorageType.INT_MEMBER, "int32_t"),
        ]

        return data_format


class MapElevation(GenieStructure):
    name_struct_file   = "randommap"
    name_struct        = "map_elevation"
    struct_description = "random map elevation data"

    @classmethod
    def get_data_format_members(cls, game_version):
        """
        Return the members in this struct.
        """
        data_format = [
            (READ, "proportion", StorageType.INT_MEMBER, "int32_t"),
            (READ, "terrain", StorageType.INT_MEMBER, "int32_t"),
            (READ, "clump_count", StorageType.INT_MEMBER, "int32_t"),
            (READ, "base_terrain", StorageType.ID_MEMBER, "int32_t"),
            (READ, "base_elevation", StorageType.INT_MEMBER, "int32_t"),
            (READ, "tile_spacing", StorageType.INT_MEMBER, "int32_t"),
        ]

        return data_format


class Map(GenieStructure):
    name_struct_file   = "randommap"
    name_struct        = "map"
    struct_description = "random map information data"

    @classmethod
    def get_data_format_members(cls, game_version):
        """
        Return the members in this struct.
        """
        data_format = [
            (READ, "border_south_west", StorageType.INT_MEMBER, "int32_t"),
            (READ, "border_north_west", StorageType.INT_MEMBER, "int32_t"),
            (READ, "border_north_east", StorageType.INT_MEMBER, "int32_t"),
            (READ, "border_south_east", StorageType.INT_MEMBER, "int32_t"),
            (READ, "border_usage", StorageType.INT_MEMBER, "int32_t"),
            (READ, "water_shape", StorageType.INT_MEMBER, "int32_t"),
            (READ, "base_terrain", StorageType.INT_MEMBER, "int32_t"),
            (READ, "land_coverage", StorageType.INT_MEMBER, "int32_t"),
            (SKIP, "unused_id", StorageType.ID_MEMBER, "int32_t"),

            (READ, "base_zone_count", StorageType.INT_MEMBER, "uint32_t"),
            (READ, "base_zone_ptr", StorageType.ID_MEMBER, "int32_t"),
            (READ, "base_zones", StorageType.ARRAY_CONTAINER, SubdataMember(
                ref_type=MapLand,
                length="base_zone_count",
            )),

            (READ, "map_terrain_count", StorageType.INT_MEMBER, "uint32_t"),
            (READ, "map_terrain_ptr", StorageType.ID_MEMBER, "int32_t"),
            (READ, "map_terrains", StorageType.ARRAY_CONTAINER, SubdataMember(
                ref_type=MapTerrain,
                length="map_terrain_count",
            )),

            (READ, "map_unit_count", StorageType.INT_MEMBER, "uint32_t"),
            (READ, "map_unit_ptr", StorageType.ID_MEMBER, "int32_t"),
            (READ, "map_units", StorageType.ARRAY_CONTAINER, SubdataMember(
                ref_type=MapUnit,
                length="map_unit_count",
            )),

            (READ, "map_elevation_count", StorageType.INT_MEMBER, "uint32_t"),
            (READ, "map_elevation_ptr", StorageType.ID_MEMBER, "int32_t"),
            (READ, "map_elevations", StorageType.ARRAY_CONTAINER, SubdataMember(
                ref_type=MapElevation,
                length="map_elevation_count",
            )),
        ]

        return data_format
