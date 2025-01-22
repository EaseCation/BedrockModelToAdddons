entityDemo = {
            "format_version": "1.14.0",
            "minecraft:entity": {
                "component_groups": {
                },
                "components": {
                    "minecraft:attack": {
                        "damage": 1
                    },
                    "minecraft:behavior.delayed_attack": {
                        "attack_duration": 1.9,
                        "attack_once": False,
                        "hit_delay_pct": 0.5,
                        "priority": 0,
                        "reach_multiplier": 5.0,
                        "require_complete_path": True,
                        "speed_multiplier": 1.0,
                        "track_target": False
                    },
                    "minecraft:behavior.float": {
                        "priority": 6
                    },
                    "minecraft:behavior.hurt_by_target": {
                        "priority": 1
                    },
                    "minecraft:behavior.nearest_attackable_target": {
                        "must_see": False,
                        "priority": 2,
                        "reselect_targets": True,
                        "within_radius": 25.0
                    },
                    "minecraft:behavior.random_look_around": {
                        "priority": 8
                    },
                    "minecraft:behavior.random_stroll": {
                        "priority": 6,
                        "speed_multiplier": 0.5
                    },
                    "minecraft:can_climb": {
                    },
                    "minecraft:collision_box": {
                        "height": 1.0,
                        "width": 1.0
                    },
                    "minecraft:floats_in_liquid": {
                    },
                    "minecraft:health": {
                        "max": 41.67,
                        "value": 41.67
                    },
                    "minecraft:jump.static": {
                    },
                    "minecraft:knockback_resistance": {
                        "value": 0
                    },
                    "minecraft:movement": {
                        "value": 0.4
                    },
                    "minecraft:movement.basic": {
                    },
                    "minecraft:nameable": {
                    },
                    "minecraft:navigation.walk": {
                        "avoid_damage_blocks": True,
                        "can_path_over_water": True
                    },
                    "minecraft:persistent": {

                    },
                    "minecraft:physics": {

                    },
                    "minecraft:pushable": {
                        "is_pushable": False,
                        "is_pushable_by_piston": False
                    },
                    "minecraft:scale": {
                        "value": 1
                    }
                },
                "description": {
                    "identifier": "",
                    "is_experimental": False,
                    "is_spawnable": True,
                    "is_summonable": True
                },
                "events": {
                }
            }
        }

blockDemo = {
            "format_version": "1.10.0",
            "minecraft:block": {
                "components": {
                    "minecraft:block_light_absorption": {"value": 0},
                    "minecraft:block_light_emission": {"emission": 1.0},
                    "minecraft:destroy_time": {"value": 5.0},
                    "netease:aabb": {
                        "clip": {"max": [1.0, 1.0, 1.0], "min": [0.0, 0.0, 0.0]},
                        "collision": {"max": [1.0, 1.0, 1.0], "min": [0.0, 0.0, 0.0]}
                    },
                    "netease:block_entity": {"client_tick": False, "movable": False, "tick": False},
                    "netease:face_directional": {"type": "facing_direction"},
                    "netease:listen_block_remove": {"value": True},
                    "netease:render_layer": {"value": "alpha"},
                    "netease:solid": {"value": True},
                    "netease:tier": {"digger": "pickaxe"}
                },
                "description": {
                    "identifier": "",
                    "register_to_creative_menu": True
                }
            }
        }