--[[ Copyright 2022 DeepMind Technologies Limited.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
]]

local helpers = require 'common.helpers'
local log = require 'common.log'
local args = require 'common.args'
local class = require 'common.class'
local set = require 'common.set'
local tensor = require 'system.tensor'

local meltingpot = 'meltingpot.lua.modules.'
local component = require(meltingpot .. 'component')
local component_registry = require(meltingpot .. 'component_registry')

local _DIRECTION = {
    N = tensor.Tensor({0, -1}),
    E = tensor.Tensor({1, 0}),
    S = tensor.Tensor({0, 1}),
    W = tensor.Tensor({-1, 0}),
}


local BinaryCommunicationManager = class.Class(component.Component)

function BinaryCommunicationManager:__init__(kwargs)
    kwargs = args.parse(kwargs, {
        {'name', args.default('BinaryCommunicationManager')},
        {'loudState', args.default('loud')},
        {'quietState', args.default('quiet')},
    })
    BinaryCommunicationManager.Base.__init__(self, kwargs)
    self._config.loudState = kwargs.loudState
    self._config.quietState = kwargs.quietState
end

function BinaryCommunicationManager:getLoudState()
    return self._config.loudState
end

function BinaryCommunicationManager:postStart()
    local simulation = self.gameObject.simulation
    self._config.avatars = simulation:getAllGameObjectsWithComponent("Avatar")
end
    

function BinaryCommunicationManager:registerUpdaters(updaterRegistry)
    local updateFn = function()
        for _, avatar in ipairs(self._config.avatars) do
            local playerVolatileVariables = (
            avatar:getComponent('Avatar'):getVolatileData())
            local actions = playerVolatileVariables.actions
            if actions["binaryComms"] == 1 then
                self.gameObject:setState(self._config.loudState)
                return
            end
        end
        self.gameObject:setState(self._config.quietState)
    end
    updaterRegistry:registerUpdater{
        updateFn = updateFn,
        priority = 0,
    }
end 


local BinaryCommunicationObservation = class.Class(component.Component)

function BinaryCommunicationObservation:__init__(kwargs)
  kwargs = args.parse(kwargs, {
      {'name', args.default('BinaryCommunicationObservation')},
      {'binaryCommunicationManagerName', args.stringType},
  })
  BinaryCommunicationObservation.Base.__init__(self, kwargs)

  self._config.binaryCommunicationManagerName = kwargs.binaryCommunicationManagerName
end

function BinaryCommunicationObservation:addObservations(tileSet, world, observations)
  local playerIndex = self.gameObject:getComponent('Avatar'):getIndex()

  observations[#observations + 1] = {
      name = tostring(playerIndex) .. '.BINARY_COMMS',
      type = 'Int32s',
      shape = {},
      func = function(grid)
           local simulation = self.gameObject.simulation
           local binaryCommunicationManager = simulation:getGameObjectsByName(self._config.binaryCommunicationManagerName)[1]
           local binaryCommunicationManagerComponent = binaryCommunicationManager:getComponent("BinaryCommunicationManager")
           if binaryCommunicationManager:getState() == binaryCommunicationManagerComponent:getLoudState() then
               return 1
           else
                return 0
           end
      end
  }
end



local OpenChannelSender = class.Class(component.Component)

function OpenChannelSender:__init__(kwargs)
    kwargs = args.parse(kwargs, {
        {'name', args.stringType},           -- Names should be formatted as OpenChannelSender<recipientIndex> by convention
        {'recipientIndex', args.numberType}, -- The avatar index of the recipient
        {'actionName', args.stringType}      -- The name of the action the sender will look for
    })

    OpenChannelSender.Base.__init__(self, kwargs)

    self._config.recipientIndex = kwargs.recipientIndex
    self._config.actionName = kwargs.actionName
end


function OpenChannelSender:postStart()
    local simulation = self.gameObject.simulation
    local avatarComp = self.gameObject:getComponent("Avatar")
    self._config.recipient = simulation:getAvatarFromIndex(self._config.recipientIndex)
    self._config.reciever = recipient:getComponent("OpenChannelReciever" .. avatarComp:getIndex()) -- Assumes uniqueness of the componenet
end


function OpenChannelSender:registerUpdaters()
    local avatarComp = self.gameObject:getComponent("Avatar")
    local updateFn = function()
        local playerVolatileVariables = avatarComp:getVolatileData()
        local actions = playerVolatileVariables.actions
        self._config.reciever:recieveMessage(actions[self._config.actionName])
    end
    updaterRegistry:registerUpdater{
        updateFn = updateFn,
        priority = 10,
    }
end



local OpenChannelReciever = class.Class(component.Component)

function OpenChannelReciever:__init__(kwargs)
    kwargs = args.parse(kwargs, {
        {'name', args.stringType},           -- Names should be formatted as OpenChannelReciever<originIndex> by convention
        {'originIndex', args.numberType},    -- The avatar index of the origin (opposite of the recipient)
        {'type', args.stringType},           -- The type of the communication tensor, eg Int32
        {'shape', args.dictType},            -- The shape of the communication tensor, eg {}
        {'silentMessage'}                    -- What will be observed if no message is recieved. Should have type and shape as specified.
    })

    OpenChannelReciever.Base.__init__(self, kwargs)

    self._config.originIndex = kwargs.originIndex
    self._config.type = kwargs.type
    self._config.shape = kwargs.shape
    self._config.observationName = kwargs.observationName
end


function OpenChannelReciever:postStart()
end


function OpenChannelReciever:recieveMessage(message)
    self._variables.lastMessage = message
end


function OpenChannelReciever:registerUpdaters()
    updaterRegistry:registerUpdaters{
        updateFn = function() self._variables.lastMessage = self._config.silentMessage end,
        priority = 11,
    }
end


function OpenChannelReciever:addObservations(tileSet, world, observations)
  local playerIndex = self.gameObject:getComponent('Avatar'):getIndex()

  observations[#observations + 1] = {
      name = tostring(playerIndex) .. '.OPEN_COMMS' .. self._config.originIndex,
      type = self._config.type,
      shape = self._config.shape,
      func = function(grid)
          return self._variables.lastMessage
      end
  }
end

-- TODO: Implement proximity chat
-- TODO: Implement DMs
-- TODO: Do I need something more efficient than O(n^2)?
-- TODO: Implement deliberate message passing
-- TODO: Implement memmory (maybe just self DMs?)


local allComponents = {
    BinaryCommunicationManager = BinaryCommunicationManager,
    BinaryCommunicationObservation = BinaryCommunicationObservation,
    OpenChannelSender = OpenChannelSender,
    OpenChannelReciever = OpenChannelReciever,
}


-- Register all components from this module in the component registry.
component_registry.registerAllComponents(allComponents)

