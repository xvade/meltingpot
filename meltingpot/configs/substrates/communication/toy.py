# Copyright 2022 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Configuration for our toy communication example. Both agents have access to
binary cheap talk communication. One spawns in a room that either contains an
apple or doesn't (50/50 chance), the other spawns in a room with a green square
and a blue square. The green square is correct if the apple exists, otherwise
the blue square is correct. Stepping on either square ends the scenario.
Stepping on the correct square gives both agents a reward."""


from typing import Any, Dict, Mapping, Sequence

from meltingpot.utils.substrates import colors
from meltingpot.utils.substrates import shapes
from meltingpot.utils.substrates import specs
from ml_collections import config_dict
import numpy as np

# Warning: setting `_ENABLE_DEBUG_OBSERVATIONS = True` may cause slowdown.
_ENABLE_DEBUG_OBSERVATIONS = False

ASCII_MAP = """
*******      *******
*  a  *      *  u  *
*  _  *      *  _  *
*     *      *     *
*     *      *  l  *
*******      *******
"""

# `prefab` determines which prefab game object to use for each `char` in the
# ascii map.
CHAR_PREFAB_MAP = {"_":  "spawn_point", "*": "wall", "a": "apple", "u": "upper_pad", "l": "lower_pad"}

_COMPASS = ["N", "E", "S", "W"]

SPAWN_POINT = {
    "name": "spawn_point",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "spawnPoint",
                "stateConfigs": [{
                    "state": "spawnPoint",
                    "groups": ["spawnPoints"],
                }],
            }
        },
        {
            "component": "Transform",
        },
    ]
}



APPLE = {
    "name": "apple",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "apple",
                "stateConfigs": [{
                    "state": "apple",
                    "layer": "lowerPhysical",
                    "sprite": "Apple",
                }, {
                    "state": "appleWait",
                }],
            }
        },
        {
            "component": "Transform",
        },
        {
            "component": "Appearance",
            "kwargs": {
                "renderMode": "ascii_shape",
                "spriteNames": ["Apple",],
                "spriteShapes": [shapes.LEGACY_APPLE],
                "palettes": [shapes.GREEN_COIN_PALETTE],
                "noRotates": [True],
            }
        },
        {
            "component": "DisappearingApple",
            "kwargs": {
                "liveState": "apple",
                "waitState": "appleWait",
                "existsProb": 0.5,
                "upperPadName": "upper_pad",
                "lowerPadName": "lower_pad",
                "padWaitState": "inactive"
            }
        },
    ]
}

UPPER_PAD = {
    "name": "upper_pad",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "active",
                "stateConfigs": [{
                    "state": "active",
                    "layer": "lowerPhysical",
                    "sprite": "UpperPad",
                },
                {
                    "state": "inactive",
                    "layer": "lowerPhysical",
                    "sprite": "UpperPad",
                }]
            } 
        },
        {
            "component": "Transform",
        },
        {
            "component": "Appearance",
            "kwargs": {
                "spriteNames": ["UpperPad",],
                "spriteRGBColors": [(0, 128, 0)],
                "palettes": [{}],
            },
        },
        {
            "component": "RewardWhenActiveAndEnd",
            "kwargs": {
                "reward": 1,
                "liveState": "active",
                "waitState": "inactive",
            }
        },
    ]
}


LOWER_PAD = {
    "name": "lower_pad",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "active",
                "stateConfigs": [{
                    "state": "active",
                    "layer": "lowerPhysical",
                    "sprite": "LowerPad",
                },
                {
                    "state": "inactive",
                    "layer": "lowerPhysical",
                    "sprite": "LowerPad",
                }]
            }
        },   
        {
            "component": "Transform",
        },
        {
            "component": "Appearance",
            "kwargs": {
                "spriteNames": ["LowerPad",],
                "spriteRGBColors": [(0, 0, 128)],
                "palettes": [{}],
            },
        },        
        {
            "component": "RewardWhenActiveAndEnd",
            "kwargs": {
                "reward": 1,
                "liveState": "active",
                "waitState": "inactive",
            }
        },
    ]
}

WALL = {
    "name": "wall",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "wall",
                "stateConfigs": [{
                    "state": "wall",
                    "layer": "upperPhysical",
                    "sprite": "Wall",
                }],
            }
        },
        {
            "component": "Transform",
        },
        {
            "component": "Appearance",
            "kwargs": {
                "renderMode": "ascii_shape",
                "spriteNames": ["Wall",],
                "spriteShapes": [shapes.WALL],
                "palettes": [shapes.WALL_PALETTE],
                "noRotates": [True],
            }
        },
        {
            "component": "BeamBlocker",
            "kwargs": {
                "beamType": "gift"
            }
        },
        {
            "component": "BeamBlocker",
            "kwargs": {
                "beamType": "zap"
            }
        },
    ]
}




# Primitive action components.
# pylint: disable=bad-whitespace
# pyformat: disable
NOOP       = {"move": 0, "turn":  0, "binaryComms": 0}
FORWARD    = {"move": 1, "turn":  0, "binaryComms": 0}
STEP_RIGHT = {"move": 2, "turn":  0, "binaryComms": 0}
BACKWARD   = {"move": 3, "turn":  0, "binaryComms": 0}
STEP_LEFT  = {"move": 4, "turn":  0, "binaryComms": 0}
TURN_LEFT  = {"move": 0, "turn": -1, "binaryComms": 0}
TURN_RIGHT = {"move": 0, "turn":  1, "binaryComms": 0}
COMMUNICATE= {"move": 0, "turn":  0, "binaryComms": 1}
# pyformat: enablebinaryComms# pylint: enable=bad-whitespace

ACTION_SET = (
    NOOP,
    FORWARD,
    BACKWARD,
    STEP_LEFT,
    STEP_RIGHT,
    TURN_LEFT,
    TURN_RIGHT,
    COMMUNICATE,
)

TARGET_SPRITE_SELF = {
    "name": "Self",
    "shape": shapes.CUTE_AVATAR,
    "palette": shapes.get_palette((50, 100, 200)),
    "noRotate": True,
}


def create_scene():
  """Creates the scene."""
  scene = {
      "name": "scene",
      "components": [
          {
              "component": "StateManager",
              "kwargs": {
                  "initialState": "scene",
                  "stateConfigs": [{
                      "state": "scene",
                  }],
              }
          },
          {
              "component": "Transform",
          },
      ]
  }

  return scene

def create_binary_communication_manager():
    """Creates the binary communication manager."""
    quiet_state_name = "quiet"
    loud_state_name = "loud"
    binary_communication_manager = {
        "name": "binary_communication_manager",
        "components": [
            {
                "component": "StateManager",
                "kwargs": {
                    "initialState": quiet_state_name,
                    "stateConfigs": [
                        {"state": quiet_state_name},
                        {"state": loud_state_name}
                    ]
                }
            },
            {
                "component": "Transform",
            },
            {
                "component": "BinaryCommunicationManager",
                "kwargs": {
                    "quietState": quiet_state_name,
                    "loudState": loud_state_name
                }
            }
        ]
    }
    return binary_communication_manager


def create_prefabs():
  """Returns a dictionary mapping names to template game objects."""
  prefabs = {
    "wall": WALL,
    "lower_pad": LOWER_PAD,
    "upper_pad": UPPER_PAD,
    "apple": APPLE,
    "spawn_point": SPAWN_POINT,
  }
  return prefabs


def create_avatar_object(player_idx: int,
                         target_sprite_self: Dict[str, Any],
                         spawn_group: str) -> Dict[str, Any]:
  """Create an avatar object that always sees itself as blue."""
  # Lua is 1-indexed.
  lua_index = player_idx + 1

  # Setup the self vs other sprite mapping.
  source_sprite_self = "Avatar" + str(lua_index)
  custom_sprite_map = {source_sprite_self: target_sprite_self["name"]}

  live_state_name = "player{}".format(lua_index)
  avatar_object = {
      "name": "avatar",
      "components": [
          {
              "component": "StateManager",
              "kwargs": {
                  "initialState": live_state_name,
                  "stateConfigs": [
                      {"state": live_state_name,
                       "layer": "upperPhysical",
                       "sprite": source_sprite_self,
                       "contact": "avatar",
                       "groups": ["players"]},

                      {"state": "playerWait",
                       "groups": ["playerWaits"]},
                  ]
              }
          },
          {
              "component": "Transform",
          },
          {
              "component": "Appearance",
              "kwargs": {
                  "renderMode": "ascii_shape",
                  "spriteNames": [source_sprite_self],
                  "spriteShapes": [shapes.CUTE_AVATAR],
                  "palettes": [shapes.get_palette(
                      colors.human_readable[player_idx])],
                  "noRotates": [True]
              }
          },
          {
              "component": "AdditionalSprites",
              "kwargs": {
                  "renderMode": "ascii_shape",
                  "customSpriteNames": [target_sprite_self["name"]],
                  "customSpriteShapes": [target_sprite_self["shape"]],
                  "customPalettes": [target_sprite_self["palette"]],
                  "customNoRotates": [target_sprite_self["noRotate"]],
              }
          },
          {
              "component": "Avatar",
              "kwargs": {
                  "index": lua_index,
                  "aliveState": live_state_name,
                  "waitState": "playerWait",
                  "speed": 1.0,
                  "spawnGroup": spawn_group,
                  "actionOrder": ["move", "turn", "binaryComms"],
                  "actionSpec": {
                      "move": {"default": 0, "min": 0, "max": len(_COMPASS)},
                      "turn": {"default": 0, "min": -1, "max": 1},
                      "binaryComms": {"default": 0, "min": 0, "max": 1},
                  },
                  "view": {
                      "left": 5,
                      "right": 5,
                      "forward": 5,
                      "backward": 5,
                      "centered": True
                  },
                  # "spriteMap": custom_sprite_map,
              }
          },
          {
              "component": "BinaryCommunicationObservation",
              "kwargs": {
                  "binaryCommunicationManagerName": "binary_communication_manager",
              }
          },
      ]
  }
  if _ENABLE_DEBUG_OBSERVATIONS:
    avatar_object["components"].append({
        "component": "LocationObserver",
        "kwargs": {"objectIsAvatar": True, "alsoReportOrientation": True},
    })

  return avatar_object


def create_avatar_objects(num_players):
  """Returns list of avatar objects of length 'num_players'."""
  avatar_objects = []
  for player_idx in range(0, num_players):
    spawn_group = "spawnPoints"
    game_object = create_avatar_object(player_idx,
                                       TARGET_SPRITE_SELF,
                                       spawn_group=spawn_group)
    avatar_objects.append(game_object)

  return avatar_objects


def create_game_objects(num_players):
    """Returns list of game objects including the players."""
    objects = create_avatar_objects(num_players)
    objects.append(create_binary_communication_manager())
    return objects


def get_config():
  """Default configuration for training on the commons_harvest level."""
  config = config_dict.ConfigDict()

  # Action set configuration.
  config.action_set = ACTION_SET
  # Observation format configuration.
  config.individual_observation_names = [
      "RGB",
      "BINARY_COMMS",
  ]
  config.global_observation_names = [
      "WORLD.RGB",
  ]

  # The specs of the environment (from a single-agent perspective).
  config.action_spec = specs.action(len(ACTION_SET))
  config.timestep_spec = specs.timestep({
      "RGB": specs.OBSERVATION["RGB"],
      "BINARY_COMMS": specs.binary_communication(),
      # Debug only (do not use the following observations in policies).
      "WORLD.RGB": specs.rgb(48, 160),
  })

  # The roles assigned to each player.
  config.valid_roles = frozenset({"default"})
  config.default_player_roles = ("default",) * 2

  return config


def build(
    roles: Sequence[str],
    config: config_dict.ConfigDict,
) -> Mapping[str, Any]:
  """Build substrate definition given player roles."""
  del config
  num_players = len(roles) # This should be 2.
  # Build the rest of the substrate definition.
  substrate_definition = dict(
      levelName="toy",
      levelDirectory="meltingpot/lua/levels/communication",
      numPlayers=num_players,
      # Define upper bound of episode length since episodes end stochastically.
      maxEpisodeLengthFrames=100,
      spriteSize=8,
      topology="BOUNDED",  # Choose from ["BOUNDED", "TORUS"],
      simulation={
          "map": ASCII_MAP,
          "gameObjects": create_game_objects(num_players),
          "prefabs": create_prefabs(),
          "charPrefabMap": CHAR_PREFAB_MAP,
          "scene": create_scene(),
      },
  )
  return substrate_definition
