from enum import Enum


class Faction(str, Enum):
    VILLAGER = "villager"
    WOLF = "wolf"
    NEUTRAL = "neutral"


class Phase(str, Enum):
    LOBBY = "lobby"
    NIGHT = "night"
    MORNING = "morning"
    DISCUSSION = "discussion"
    VOTE = "vote"
    ENDED = "ended"


class DeathCause(str, Enum):
    WOLF_BITE = "wolf_bite"
    LYNCH = "lynch"
    WITCH_POISON = "witch_poison"
    HUNTER_MARK = "hunter_mark"
    TERRORIST = "terrorist"
    CUPID_LINK = "cupid_link"
    SOLO_KILLER = "solo_killer"
    VAMPIRE = "vampire"
    HUNTRESS = "huntress"
    GAMBLER_MISS = "gambler_miss"


class RoomStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class FillStrategy(str, Enum):
    PROPORTIONAL = "proportional"
    VILLAGER_FIRST = "villager_first"
    THEMATIC = "thematic"
    RANDOM = "random"


AFK_TIMEOUT_SECONDS = 30
HOST_RECONNECT_TIMEOUT_SECONDS = 300
MIN_RECONNECT_RATIO = 0.5

DISCUSSION_DEFAULT_SECONDS = 5 * 60
DISCUSSION_MIN_SECONDS = 2 * 60
DISCUSSION_MAX_SECONDS = 10 * 60

EARLY_VOTE_DEFAULT_SECONDS = 3 * 60
EARLY_VOTE_MIN_SECONDS = 60

VOTE_DEFAULT_SECONDS = 60
VOTE_MIN_SECONDS = 30
VOTE_MAX_SECONDS = 120

NIGHT_DEFAULT_SECONDS = 60
NIGHT_MIN_SECONDS = 30
NIGHT_MAX_SECONDS = 120

SKIP_DISCUSSION_RATIO = 0.5
