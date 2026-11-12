local args = require 'common.args'
local class = require 'common.class'
local helpers = require 'common.helpers'
local log = require 'common.log'
local random = require 'system.random'
local meltingpot = 'meltingpot.lua.modules.'
local component = require(meltingpot .. 'component')
local component_registry = require(meltingpot .. 'component_registry')


-- DensityRegrow makes the containing GameObject switch from `waitState` to
-- `liveState` at a rate based on the number of surrounding objects in
-- `liveState` and the configured `baseRate`.
local DisappearingApple = class.Class(component.Component)

function DisappearingApple:__init__(kwargs)
    kwargs = args.parse(kwargs, {
        {'name', args.default("DisappearingApple")},
        {'liveState', args.stringType},
        {'waitState', args.stringType},
        {'existsProb', args.numberType},
        {'upperPadName', args.stringType},
        {'lowerPadName', args.stringType},
        {'padWaitState', args.stringType}
    })

    DisappearingApple.Base.__init__(self, kwargs)

    self._config.liveState = kwargs.liveState
    self._config.waitState = kwargs.waitState
    self._config.existsProb = kwargs.existsProb
    self._config.upperPadName = kwargs.upperPadName
    self._config.lowerPadName = kwargs.lowerPadName
    self._config.padWaitState = kwargs.padWaitState
end

function DisappearingApple:randomizeExistance()
    local simulation = self.gameObject.simulation
    if random:uniformReal(0, 1) > self._existsProb then
        self.gameObject:setState(self._waitState)
        local upperPad = simulation:getGameObjectsByName(self._config.upperPadName)[1]
        upperPad:setState(self._config.padWaitState)
    else
        local lowerPad = simulation:getGameObjectsByName(self._config.lowerPadName)[1]
        lowerPad:setState(self._config.padWaitState)
    end
end  

function DisappearingApple:reset()
    self._liveState = self._config.liveState
    self._waitState = self._config.waitState
    self._existsProb = self._config.existsProb
end

function DisappearingApple:postStart()
    self:randomizeExistance()
end


local RewardWhenActiveAndEnd = class.Class(component.Component)

function RewardWhenActiveAndEnd:__init__(kwargs)
    kwargs = args.parse(kwargs, {
        {'name', args.default("RewardWhenActiveAndEnd")},
        {'liveState', args.stringType},
        {'waitState', args.stringType},
        {'reward', args.numberType}
    })

    RewardWhenActiveAndEnd.Base.__init__(self, kwargs)

    self._config.liveState = kwargs.liveState
    self._config.waitState = kwargs.waitState
    self._config.reward = kwargs.reward
end

function RewardWhenActiveAndEnd:onEnter(enteringGameObject, contactName)
    if contactName == "avatar" then
        local simulation = self.gameObject.simulation
        if self.gameObject:getState() == self._config.liveState then
            local avatars = simulation:getAllGameObjectsWithComponent("Avatar")
            for _, avatar in ipairs(avatars) do
                avatar:getComponent("Avatar"):addReward(self._config.reward)
            end
        end
        simulation:endEpisode()
    end
end


local allComponents = {
    DisappearingApple = DisappearingApple,
    RewardWhenActiveAndEnd = RewardWhenActiveAndEnd,
}



component_registry.registerAllComponents(allComponents)

return allComponents
