time_group EQUS "0," ; use the nth TimeFishGroups entry

fishgroup: MACRO
; chance, old rod, good rod, super rod
	dbwww \1, \2, \3, \4
ENDM

FishGroups:
; entries correspond to FISHGROUP_* constants
	fishgroup 100 percent, .Shore_Old,            .Shore_Good,            .Shore_Super
	fishgroup 100 percent, .Ocean_Old,            .Ocean_Good,            .Ocean_Super
	fishgroup 100 percent, .Lake_Old,             .Lake_Good,             .Lake_Super
	fishgroup 100 percent, .Pond_Old,             .Pond_Good,             .Pond_Super
	fishgroup 100 percent, .Dratini_Old,          .Dratini_Good,          .Dratini_Super
	fishgroup 100 percent, .Qwilfish_Swarm_Old,   .Qwilfish_Swarm_Good,   .Qwilfish_Swarm_Super
	fishgroup 100 percent, .Remoraid_Swarm_Old,   .Remoraid_Swarm_Good,   .Remoraid_Swarm_Super
	fishgroup 100 percent, .Gyarados_Old,         .Gyarados_Good,         .Gyarados_Super
	fishgroup 100 percent, .Dratini_2_Old,        .Dratini_2_Good,        .Dratini_2_Super
	fishgroup 100 percent, .WhirlIslands_Old,     .WhirlIslands_Good,     .WhirlIslands_Super
	fishgroup 100 percent, .Qwilfish_Old,         .Qwilfish_Good,         .Qwilfish_Super
	fishgroup 100 percent, .Remoraid_Old,         .Remoraid_Good,         .Remoraid_Super
	fishgroup 100 percent, .Qwilfish_NoSwarm_Old, .Qwilfish_NoSwarm_Good, .Qwilfish_NoSwarm_Super

.Shore_Old:
	db  50 percent + 1, KRABBY,     10
	db  90 percent + 1, SEEL,       10
	db 100 percent,     HORSEA,     10
.Shore_Good:
	db  35 percent,     GYARADOS,   25
	db  70 percent,     KRABBY,     25
	db  90 percent + 1, HORSEA,     25
	db 100 percent,     time_group 0
.Shore_Super:
	db  40 percent,     KRABBY,     60
	db  70 percent,     time_group 1
	db  90 percent + 1, SEADRA,     60
	db 100 percent,     KINGLER,    60

.Ocean_Old:
	db  50 percent + 1, MAGIKARP,   10
	db  90 percent + 1, SHELLDER,   10
	db 100 percent,     CHINCHOU,   10
.Ocean_Good:
	db  35 percent,     SHELLDER,   25
	db  70 percent,     TENTACOOL,  25
	db  90 percent + 1, CHINCHOU,   25
	db 100 percent,     time_group 2
.Ocean_Super:
	db  40 percent,     CHINCHOU,   60
	db  70 percent,     time_group 3
	db  90 percent + 1, TENTACRUEL, 60
	db 100 percent,     LANTURN,    60

.Lake_Old:
	db  50 percent + 1, MAGIKARP,   10
	db  90 percent + 1, SHELLDER,   10
	db 100 percent,     REMORAID,   10
.Lake_Good:
	db  35 percent,     MAGIKARP,   25
	db  70 percent,     SHELLDER,   25
	db  90 percent + 1, REMORAID,    25
	db 100 percent,     time_group 4
.Lake_Super:
	db  40 percent,     SHELLDER,  60
	db  70 percent,     time_group 5
	db  90 percent + 1, OCTILLERY, 60
	db 100 percent,     CLOYSTER,  60

.Pond_Old:
	db  50 percent + 1, MAGIKARP,   10
	db  90 percent + 1, POLIWAG,    10
	db 100 percent,     REMORAID,   10
.Pond_Good:
	db  35 percent,     MAGIKARP,   25
	db  70 percent,     POLIWAG,    25
	db  90 percent + 1, REMORAID,   25
	db 100 percent,     time_group 6
.Pond_Super:
	db  40 percent,     POLIWHIRL,  60
	db  70 percent,     time_group 7
	db  90 percent + 1, OCTILLERY,  60
	db 100 percent,     POLITOED,   60

.Dratini_Old:
	db  50 percent + 1, DRATINI,    10
	db  90 percent + 1, DRATINI,    10
	db 100 percent,     DRATINI,    15
.Dratini_Good:
	db  35 percent,     MAGIKARP,   25
	db  70 percent,     HORSEA,     25
	db  90 percent + 1, DRATINI,    25
	db 100 percent,     time_group 8
.Dratini_Super:
	db  40 percent,     GYARADOS,   60
	db  70 percent,     time_group 9
	db  90 percent + 1, SEADRA,     60
	db 100 percent,     KINGDRA,  60

.Qwilfish_Swarm_Old:
	db  50 percent + 1, QWILFISH,   10
	db  90 percent + 1, QWILFISH,   10
	db 100 percent,     QWILFISH,   10
.Qwilfish_Swarm_Good:
	db  35 percent,     QWILFISH,   25
	db  70 percent,     QWILFISH,   25
	db  90 percent + 1, QWILFISH,   25
	db 100 percent,     time_group 10
.Qwilfish_Swarm_Super:
	db  40 percent,     QWILFISH,   60
	db  70 percent,     time_group 11
	db  90 percent + 1, QWILFISH,   60
	db 100 percent,     QWILFISH,   60

.Remoraid_Swarm_Old:
	db  50 percent + 1, REMORAID,   10
	db  90 percent + 1, REMORAID,   10
	db 100 percent,     REMORAID,   10
.Remoraid_Swarm_Good:
	db  35 percent,     REMORAID,   25
	db  70 percent,     REMORAID,   25
	db  90 percent + 1, REMORAID,   25
	db 100 percent,     time_group 12
.Remoraid_Swarm_Super:
	db  40 percent,     REMORAID,   60
	db  70 percent,     time_group 13
	db  90 percent + 1, REMORAID,   60
	db 100 percent,     REMORAID,   60

.Gyarados_Old:
	db  50 percent + 1, MAGIKARP,   10
	db  90 percent + 1, MAGIKARP,   10
	db 100 percent,     GYARADOS,   10
.Gyarados_Good:
	db  35 percent,     GYARADOS,   25
	db  70 percent,     GYARADOS,   25
	db  90 percent + 1, GYARADOS,   25
	db 100 percent,     time_group 14
.Gyarados_Super:
	db  40 percent,     GYARADOS,   60
	db  70 percent,     time_group 15
	db  90 percent + 1, GYARADOS,   60
	db 100 percent,     GYARADOS,   60

.Dratini_2_Old:
	db  50 percent + 1, DRATINI,    10
	db  90 percent + 1, DRATINI,    10
	db 100 percent,     DRATINI,    10
.Dratini_2_Good:
	db  35 percent,     DRATINI,    25
	db  70 percent,     DRATINI,    25
	db  90 percent + 1, DRATINI,    25
	db 100 percent,     time_group 16
.Dratini_2_Super:
	db  40 percent,     DRATINI,    60
	db  70 percent,     time_group 17
	db  90 percent + 1, SEADRA,     60
	db 100 percent,     DRAGONAIR,  60

.WhirlIslands_Old:
	db  50 percent + 1, SEEL,       10
	db  90 percent + 1, SHELLDER,   10
	db 100 percent,     KRABBY,     10
.WhirlIslands_Good:
	db  35 percent,     SEEL,       25
	db  70 percent,     SHELLDER,   25
	db  90 percent + 1, KRABBY,     25
	db 100 percent,     time_group 18
.WhirlIslands_Super:
	db  40 percent,     KRABBY,     60
	db  70 percent,     time_group 19
	db  90 percent + 1, KINGLER,    60
	db 100 percent,     SEADRA,     60

.Qwilfish_NoSwarm_Old:
.Qwilfish_Old:
	db  50 percent + 1, MAGIKARP,   10
	db  90 percent + 1, TENTACOOL,  10
	db 100 percent,     QWILFISH,   10
.Qwilfish_NoSwarm_Good:
.Qwilfish_Good:
	db  35 percent,     MAGIKARP,   25
	db  70 percent,     TENTACOOL,  25
	db  90 percent + 1, GOLDEEN,    25
	db 100 percent,     time_group 20
.Qwilfish_NoSwarm_Super:
.Qwilfish_Super:
	db  40 percent,     TENTACOOL,  60
	db  70 percent,     time_group 21
	db  90 percent + 1, GYARADOS,   60
	db 100 percent,     QWILFISH,   60

.Remoraid_Old:
	db  50 percent + 1, REMORAID,   10
	db  90 percent + 1, REMORAID,   10
	db 100 percent,     POLIWAG,    10
.Remoraid_Good:
	db  35 percent,     REMORAID,   25
	db  70 percent,     OCTILLERY,  25
	db  90 percent + 1, POLIWAG,    25
	db 100 percent,     time_group 6
.Remoraid_Super:
	db  40 percent,     REMORAID,    60
	db  70 percent,     time_group 7
	db  90 percent + 1, REMORAID,   60
	db 100 percent,     OCTILLERY,   60

TimeFishGroups:
	;  day              nite
	db CORSOLA,    25,  STARYU,     25 ; 0
	db CORSOLA,    60,  STARYU,     60 ; 1
	db SHELLDER,   25,  SHELLDER,   25 ; 2
	db SHELLDER,   60,  SHELLDER,   60 ; 3
	db GOLDEEN,    25,  GOLDEEN,    25 ; 4
	db GOLDEEN,    60,  GOLDEEN,    60 ; 5
	db POLIWAG,    25,  POLIWAG,    25 ; 6
	db POLIWHIRL,  60,  POLIWHIRL,  60 ; 7
	db DRATINI,    25,  DRATINI,    25 ; 8
	db DRAGONAIR,  60,  DRAGONAIR,  60 ; 9
	db QWILFISH,   25,  QWILFISH,   25 ; 10
	db QWILFISH,   60,  QWILFISH,   60 ; 11
	db REMORAID,   25,  REMORAID,   25 ; 12
	db REMORAID,   60,  REMORAID,   60 ; 13
	db GYARADOS,   25,  GYARADOS,   25 ; 14
	db GYARADOS,   60,  GYARADOS,   60 ; 15
	db DRAGONAIR,  25,  DRAGONAIR,  25 ; 16
	db DRAGONAIR,  60,  DRAGONAIR,  60 ; 17
	db HORSEA,     25,  HORSEA,     25 ; 18
	db SEADRA,     60,  SEADRA,     60 ; 19
	db QWILFISH,   25,  QWILFISH,   25 ; 20
	db TENTACRUEL, 60,  TENTACRUEL, 60 ; 21
