import random
from dataclasses import dataclass, field
from typing import Callable

from enums import FillStrategy


@dataclass
class Scenario:
    id: str
    name: str
    suggested_players: int
    min_players: int
    max_players: int
    base_roles: list[str]
    fill_strategy: FillStrategy
    custom_rules: dict = field(default_factory=dict)
    win_condition_fn: Callable | None = None
    allow_role_edit: bool = True


CLASSIC = Scenario(
    id="classic",
    name="Classic",
    suggested_players=9,
    min_players=6,
    max_players=15,
    base_roles=["werewolf", "werewolf", "seer", "guard", "witch", "hunter"]
    + ["villager", "villager", "villager"],
    fill_strategy=FillStrategy.PROPORTIONAL,
)

# Other scenarios (Fairy-Tale Village, Mystery Village, Massacre Village,
# Twin Villages, Chaos Slums, Medieval Village, Full Chaos) follow the same
# Scenario shape — add them here once their supporting roles/rules exist.
SCENARIOS: dict[str, Scenario] = {
    CLASSIC.id: CLASSIC,
}


def get_scenario(scenario_id: str) -> Scenario:
    return SCENARIOS[scenario_id]


class ScenarioFiller:
    @staticmethod
    def fill(scenario: Scenario, target_count: int) -> list[str]:
        if scenario.fill_strategy == FillStrategy.PROPORTIONAL:
            return ScenarioFiller._fill_proportional(scenario, target_count)
        if scenario.fill_strategy == FillStrategy.VILLAGER_FIRST:
            return ScenarioFiller._fill_villager_first(scenario, target_count)
        if scenario.fill_strategy == FillStrategy.RANDOM:
            return ScenarioFiller._fill_random(scenario, target_count)
        # THEMATIC needs a per-scenario role pool; fall back to proportional
        # until that pool is defined for the scenario in question.
        return ScenarioFiller._fill_proportional(scenario, target_count)

    @staticmethod
    def _fill_proportional(scenario: Scenario, target_count: int) -> list[str]:
        roles = list(scenario.base_roles)
        wolf_count = sum(1 for r in roles if r == "werewolf")
        villager_count = len(roles) - wolf_count
        base_ratio = villager_count / wolf_count if wolf_count else float("inf")

        while len(roles) < target_count:
            current_wolves = sum(1 for r in roles if r == "werewolf")
            current_villagers = len(roles) - current_wolves
            current_ratio = current_villagers / current_wolves if current_wolves else float("inf")
            roles.append("werewolf" if current_ratio > base_ratio else "villager")

        while len(roles) > target_count:
            roles.pop()

        return roles

    @staticmethod
    def _fill_villager_first(scenario: Scenario, target_count: int) -> list[str]:
        roles = list(scenario.base_roles)
        while len(roles) < target_count:
            roles.append("villager")
        return roles[:target_count]

    @staticmethod
    def _fill_random(scenario: Scenario, target_count: int) -> list[str]:
        from roles import ROLE_REGISTRY

        pool = list(ROLE_REGISTRY.keys())
        roles = [random.choice(pool) for _ in range(target_count)]
        return roles
