from typing import Any, Dict, Mapping, Sequence

from meltingpot.configs.substrates.communication import toy as base_config
from meltingpot.utils.substrates import specs
from ml_collections import config_dict
import numpy as np


COMMUNICATE = {"move": 0, "turn":  0, "openComms": 1}
NOOP        = {"move": 0, "turn":  0, "openComms": 0}
FORWARD     = {"move": 1, "turn":  0, "openComms": 0}
STEP_RIGHT  = {"move": 2, "turn":  0, "openComms": 0}
BACKWARD    = {"move": 3, "turn":  0, "openComms": 0}
STEP_LEFT   = {"move": 4, "turn":  0, "openComms": 0}
TURN_LEFT   = {"move": 0, "turn": -1, "openComms": 0}
TURN_RIGHT  = {"move": 0, "turn":  1, "openComms": 0}
# pyformat: enablebinaryComms# pylint: enable=bad-whitespace

ACTION_SET = (
    COMMUNICATE,
    NOOP,
    FORWARD,
    BACKWARD,
    STEP_LEFT,
    STEP_RIGHT,
    TURN_LEFT,
    TURN_RIGHT,
)


def create_avatar_objects(num_players):
  """Returns list of avatar objects of length 'num_players'."""
  avatar_objects = []
  for player_idx in range(0, num_players):
    lua_idx = player_idx + 1  # Lua is 1 indexed
    other_idx = 1 if lua_idx == 2 else 2  # We assume there are two players
    comm_components = [{
        "component": "OpenChannelSender",
        "kwargs": {
            "name": "OpenChannelSender" + str(other_idx),
            "recipientIndex": other_idx,
            "actionName": "openComms"
        }
    },
    {
        "component": "OpenChannelReciever",
        "kwargs": {
            "name": "OpenChannelReciever" + str(other_idx),
            "originIndex": other_idx,
            "type": "Doubles",
            "observationName": "openComms",
            "silentMessage": 0,   
        }
    }]
    spawn_group = "spawnPoints"
    game_object = base_config.create_avatar_object(player_idx,
                                       base_config.TARGET_SPRITE_SELF,
                                       spawn_group,
                                       {"openComms": {"default": 0, "min": 0, "max": 1}},
                                       comm_components
                                   )
    avatar_objects.append(game_object)

  return avatar_objects


def create_game_objects(num_players):
    """Returns list of game objects including the players."""
    objects = create_avatar_objects(num_players)
    return objects


def create_scene():
    return base_config.parameterized_create_scene()


def build(
    roles: Sequence[str],
    config: config_dict.ConfigDict,
) -> Mapping[str, Any]:
    """Build substrate definition given player roles."""
    return base_config.parameterized_build(roles, create_game_objects, create_scene)
    

def get_config():
    """Default configuration."""
    return base_config.parameterized_get_config(ACTION_SET, ["OPEN_COMMS"], {"OPEN_COMMS": specs.open_communication(1, dtype=np.float32)})

