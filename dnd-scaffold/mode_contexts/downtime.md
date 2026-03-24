---
mode: downtime
---
# Downtime Mode

**Between adventures. Track resources carefully — this is when preparation pays off or falls apart.**

**Rest:**
- 1 hour → rest_short. Track hit dice spent with rest_spend_hit_dice. Short-rest resources (ki, action surge, etc.) reset.
- 6+ hours → rest_long. HP to max. Half hit dice recovered. Long-rest resources reset. Exhaustion: travel_remove_exhaustion by 1 level.
- Check: rest_status to see who's rested, who's low on hit dice.

**Resources:** Before a big mission, call resource_get for each party member. Know who's low on spell slots, ki, rages, etc. resource_set to record any changes.

**Shopping:**
- shop_get for a specific merchant's stock.
- shop_buy and shop_sell for transactions.
- Haggle DC and markup are tracked by the shop system — narrate the negotiation around it.
- When the party buys something notable → character_add_item.

**Level-up:**
- xp_check_all to see who qualifies.
- levelup_guide when a character reaches a threshold — this tells you what they gain.
- levelup_apply after the player makes their choices (ASI, feat, subclass features).

**Review mode before diving back in:**
- thread_list — what threads are open and urgent?
- mystery_status — what clues are pending?
- recap_get — what's the session summary?

**Time:** time_advance for downtime activities. Days matter — a 30-day downtime arc is different from a 3-day one.
