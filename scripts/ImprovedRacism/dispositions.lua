---@omw-context global|local
local dispositions = {
    -- races must match Lua API standards
    -- player race
    dunmer = {
        -- npc race
        argonian = -10,
        redguard = -5,
        imperial = -5,
        nord = 5,
    },

    nord = {
        dunmer = -5,
        orc = 5,
    },

    orc = {
        nord = 5,
        dunmer = -10,
    },
}

return dispositions
