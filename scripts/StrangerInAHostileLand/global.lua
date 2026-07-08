---@omw-context global
local types = require("openmw.types")
local world = require("openmw.world")

local dispositions = require("scripts.StrangerInAHostileLand.dispositions")

local modifiedNPCs = {}
local playerRaces = {}

---@param playerRace string
---@param npcRace string
---@return number offset defaults to 0 if not configured
local function getOffset(playerRace, npcRace)
    local playerTable = dispositions[playerRace]
    if not playerTable then
        return 0
    end
    return playerTable[npcRace] or 0
end

local function onActorActive(actor)
    if not types.NPC.objectIsInstance(actor) or modifiedNPCs[actor.id] then
        return
    end

    local npcRace = actor.type.records[actor.recordId].race
    modifiedNPCs[actor.id] = true

    for _, player in ipairs(world.players) do
        local offset = getOffset(playerRaces[player.id], npcRace)
        if offset ~= 0 then
            types.NPC.modifyBaseDisposition(actor, player, offset)
        end
    end
end

local function onPlayerAdded(player)
    local playerRace = player.type.records[player.recordId].race
    if dispositions[playerRace] then
        -- we don't care for players with non-registered races
        playerRaces[player.id] = playerRace
        for _, actor in ipairs(world.activeActors) do
            onActorActive(actor)
        end
    end
end

local function onSave()
    return {
        modifiedNPCs = modifiedNPCs,
    }
end

local function onLoad(data)
    if not data then return end
    modifiedNPCs = data.modifiedNPCs or modifiedNPCs
    
    -- has to be done after modifiedNPCs is initialized
    for _, player in ipairs(world.players) do
        onPlayerAdded(player)
    end
end

return {
    engineHandlers = {
        onSave = onSave,
        onLoad = onLoad,
        onActorActive = onActorActive,
        onPlayerAdded = onPlayerAdded,
    },
}
