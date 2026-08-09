from roles.base import Role, RoleMeta
from roles.neutral import NEUTRAL_ROLES
from roles.villagers import VILLAGER_ROLES
from roles.wolves import WOLF_ROLES

ROLE_REGISTRY: dict[str, type[Role]] = {**VILLAGER_ROLES, **WOLF_ROLES, **NEUTRAL_ROLES}


def get_role(role_id: str) -> type[Role]:
    return ROLE_REGISTRY[role_id]


def get_role_meta(role_id: str) -> RoleMeta:
    return ROLE_REGISTRY[role_id].meta
