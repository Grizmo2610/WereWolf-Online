# Game Engine & Mechanics — Werewolf Online

## 1. Core Game Loop

1. **Night Phase (Max 60s):**
   - Characters with night abilities (Werewolves, Seer, Bodyguard, Witch, etc.) perform actions simultaneously.
   - Werewolves coordinate to select a victim.
   - Seer checks a player's alignment.
   - Bodyguard protects a target.
   - Witch uses healing or poison potions.

2. **Day Discussion Phase (5 min):**
   - Morning briefing reveals who died during the night (if any).
   - Surviving players discuss events publicly.
   - Early vote/skip discussion is enabled after 3 minutes if consensus is reached.

3. **Voting Phase (Max 60s):**
   - Players cast exile votes against suspected werewolves.
   - Majority vote eliminates the target. Ties result in no exile.

4. **Win Conditions:**
   - **Villagers Win:** All werewolves are eliminated.
   - **Werewolves Win:** Werewolf count equals or exceeds village count.
   - **Neutral Faction:** Achieves independent win condition.

---

## 2. Character Roles

- **Villager (Dân làng):** No special abilities; relies on deduction and voting.
- **Werewolf (Ma Sói):** Hunts villagers each night and blends in during the day.
- **Seer (Tiên tri):** Inspects one player each night to learn their true alignment.
- **Bodyguard (Bảo vệ):** Protects one player from werewolf attacks each night (cannot protect the same person twice in a row).
- **Witch (Phù thủy):** Holds a Healing potion (saves night victim) and a Poison potion (eliminates a player). Each can be used once per game.

---

## 3. Scenarios & Customization

Hosts can customize game scenarios in the room lobby before starting:
- Player count (typically 5 to 16 players).
- Role composition ratios (number of werewolves vs villagers vs special roles).
- Timing rules (night duration, discussion duration, voting duration).
- Imposter / Special mode rules.
