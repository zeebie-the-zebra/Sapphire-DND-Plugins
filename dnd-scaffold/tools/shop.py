"""
dnd-shop — tools

Persistent shop inventory manager. Generate and save shop stock so
merchants stay consistent across visits. Tracks markup, haggling DC,
and a restock interval (in in-game days).

Storage key scheme:
  shop:{shop_key}  →  JSON shop record
  shop_index       →  JSON list of all shop keys
"""

from core.plugin_loader import plugin_loader
import json
import random

# Default shop templates by shop_type
SHOP_TEMPLATES = {
    "general": {
        "items": [
            {"name": "Rope (50ft)", "price_gp": 1, "qty": 5},
            {"name": "Torches (10)", "price_gp": 0.1, "qty": 10},
            {"name": "Rations (1 day)", "price_gp": 0.5, "qty": 20},
            {"name": "Lantern (hooded)", "price_gp": 5, "qty": 3},
            {"name": "Oil (flask)", "price_gp": 0.1, "qty": 15},
            {"name": "Backpack", "price_gp": 2, "qty": 4},
            {"name": "Bedroll", "price_gp": 1, "qty": 4},
            {"name": "Crowbar", "price_gp": 2, "qty": 2},
            {"name": "Waterskin", "price_gp": 0.2, "qty": 6},
            {"name": "Tinderbox", "price_gp": 0.5, "qty": 5},
        ],
        "haggle_dc": 12,
        "markup_percent": 10,
        "restock_days": 7,
    },
    "blacksmith": {
        "items": [
            {"name": "Shortsword", "price_gp": 10, "qty": 2},
            {"name": "Handaxe", "price_gp": 5, "qty": 3},
            {"name": "Dagger", "price_gp": 2, "qty": 5},
            {"name": "Spear", "price_gp": 1, "qty": 3},
            {"name": "Shield (wooden)", "price_gp": 10, "qty": 2},
            {"name": "Leather armour", "price_gp": 10, "qty": 2},
            {"name": "Chain shirt", "price_gp": 50, "qty": 1},
            {"name": "Arrows (20)", "price_gp": 1, "qty": 5},
            {"name": "Bolts (20)", "price_gp": 1, "qty": 3},
            {"name": "Ball bearings (1000)", "price_gp": 1, "qty": 2},
        ],
        "haggle_dc": 14,
        "markup_percent": 15,
        "restock_days": 14,
    },
    "apothecary": {
        "items": [
            {"name": "Healing potion", "price_gp": 50, "qty": 2},
            {"name": "Antitoxin (vial)", "price_gp": 50, "qty": 1},
            {"name": "Healer's kit", "price_gp": 5, "qty": 3},
            {"name": "Herbalism kit", "price_gp": 5, "qty": 2},
            {"name": "Poisons antidote (weak)", "price_gp": 20, "qty": 2},
            {"name": "Candle (10)", "price_gp": 0.1, "qty": 10},
            {"name": "Incense (block)", "price_gp": 2, "qty": 5},
            {"name": "Alchemist's fire (flask)", "price_gp": 50, "qty": 1},
            {"name": "Holy water (flask)", "price_gp": 25, "qty": 2},
            {"name": "Potion of climbing", "price_gp": 75, "qty": 1},
        ],
        "haggle_dc": 13,
        "markup_percent": 20,
        "restock_days": 10,
    },
    "magic": {
        "items": [
            {"name": "Spell component pouch", "price_gp": 25, "qty": 2},
            {"name": "Arcane focus (crystal)", "price_gp": 10, "qty": 2},
            {"name": "Scroll: Mage Armor", "price_gp": 75, "qty": 1},
            {"name": "Scroll: Detect Magic", "price_gp": 50, "qty": 2},
            {"name": "Scroll: Identify", "price_gp": 50, "qty": 1},
            {"name": "Scroll: Cure Wounds", "price_gp": 50, "qty": 2},
            {"name": "Bag of holding", "price_gp": 500, "qty": 1},
            {"name": "Rope of climbing", "price_gp": 300, "qty": 1},
        ],
        "haggle_dc": 16,
        "markup_percent": 30,
        "restock_days": 21,
    },
    "fence": {
        "items": [
            {"name": "Thieves' tools", "price_gp": 20, "qty": 2},
            {"name": "Forgery kit", "price_gp": 10, "qty": 1},
            {"name": "Disguise kit", "price_gp": 15, "qty": 1},
            {"name": "Poisoner's kit", "price_gp": 35, "qty": 1},
            {"name": "Stolen goods (misc)", "price_gp": 5, "qty": 4},
            {"name": "Lockpicks (set)", "price_gp": 15, "qty": 2},
            {"name": "Dark lantern (collapsible)", "price_gp": 10, "qty": 2},
        ],
        "haggle_dc": 10,
        "markup_percent": 5,
        "restock_days": 3,
    },
}


DEFAULT_CAMPAIGN_ID = "default"


def _get_campaign_id(config=None) -> str:
    from core.plugin_loader import plugin_loader
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        return campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
    except Exception:
        return DEFAULT_CAMPAIGN_ID


def _state():
    return plugin_loader.get_plugin_state("dnd-shop")


def _key(shop_name: str, config=None) -> str:
    campaign_id = _get_campaign_id(config)
    return f"shop:{campaign_id}:{shop_name.strip().lower().replace(' ', '_')}"


def _load_index(config=None):
    campaign_id = _get_campaign_id(config)
    raw = _state().get(f"shop_index:{campaign_id}")
    if not raw:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


def _save_index(index: list, config=None):
    campaign_id = _get_campaign_id(config)
    _state().save(f"shop_index:{campaign_id}", json.dumps(index))


def shop_create(
    name: str,
    owner: str = "",
    location: str = "",
    shop_type: str = "general",
    custom_items: str = "",
    notes: str = ""
) -> str:
    """
    Create a new shop with generated or custom inventory.

    Args:
        name: Shop name (e.g. "Petra's General Store", "The Dented Anvil")
        owner: Owner NPC name (optional, for cross-reference with dnd-npcs)
        location: Location name this shop is in (e.g. "Village of Barovia")
        shop_type: Template to seed inventory — general | blacksmith (weapons, armour, ammo) | apothecary (potions, antitoxin) | magic (scrolls, wands) | fence (stolen goods)
        custom_items: JSON string of custom items to ADD to template stock.
                      Format: [{"name": "Item", "price_gp": 10, "qty": 2}]
                      Or plain text list for DM notes only.
        notes: Freeform notes (e.g. "Won't sell to elves", "Closed on Sundays")

    Returns:
        Created shop summary.
    """
    if shop_type not in SHOP_TEMPLATES:
        return f"ERROR: shop_type must be one of: {', '.join(SHOP_TEMPLATES.keys())}"

    template = SHOP_TEMPLATES[shop_type]
    items = [dict(i) for i in template["items"]]  # deep copy

    # Parse and append custom items if provided
    if custom_items:
        try:
            extra = json.loads(custom_items)
            if isinstance(extra, list):
                items.extend(extra)
        except Exception:
            pass  # treat as freeform note if not valid JSON

    k = _key(name)
    shop_data = {
        "name": name,
        "owner": owner,
        "location": location,
        "shop_type": shop_type,
        "items": items,
        "haggle_dc": template["haggle_dc"],
        "markup_percent": template["markup_percent"],
        "restock_days": template["restock_days"],
        "notes": notes,
        "last_restock_day": 0,
    }

    _state().save(k, json.dumps(shop_data))
    index = _load_index()
    if k not in index:
        index.append(k)
        _save_index(index)

    return (
        f"🏪 Shop created: {name}\n"
        f"  Type: {shop_type} | Owner: {owner or '(unset)'} | Location: {location or '(unset)'}\n"
        f"  Items: {len(items)} | Haggle DC: {template['haggle_dc']} | "
        f"Markup: {template['markup_percent']}% | Restocks every {template['restock_days']} days\n"
        f"  Notes: {notes or '(none)'}"
    )


def shop_get(name: str) -> str:
    """
    Get the full inventory and details for a shop.

    Args:
        name: Shop name

    Returns:
        Full shop inventory formatted for display.
    """
    k = _key(name)
    raw = _state().get(k)
    if not raw:
        return f"Shop '{name}' not found. Use shop_list to see all shops, or shop_create to add it."

    shop = json.loads(raw) if isinstance(raw, str) else raw
    items = shop.get("items", [])

    lines = [
        f"🏪 {shop['name']} ({shop['shop_type']})",
        f"  Owner: {shop.get('owner') or '(unknown)'} | Location: {shop.get('location') or '(unset)'}",
        f"  Haggle DC: {shop['haggle_dc']} | Markup: {shop['markup_percent']}% | "
        f"Restock: every {shop['restock_days']} days",
    ]
    if shop.get("notes"):
        lines.append(f"  Notes: {shop['notes']}")
    lines.append(f"\n  Inventory ({len(items)} items):")

    for item in items:
        qty = item.get("qty", 0)
        stock_str = f"×{qty}" if qty > 0 else "OUT OF STOCK"
        price = item.get("price_gp", 0)
        price_str = f"{price} gp" if price >= 1 else f"{int(price*100)} cp"
        lines.append(f"    • {item['name']} — {price_str} [{stock_str}]")

    return "\n".join(lines)


def shop_sell(name: str, item_name: str, qty: int = 1) -> str:
    """
    Record a sale — reduces item quantity in the shop's stock.

    Args:
        name: Shop name
        item_name: Exact item name as it appears in inventory
        qty: Quantity being purchased (default 1)

    Returns:
        Sale result and remaining stock.
    """
    k = _key(name)
    raw = _state().get(k)
    if not raw:
        return f"Shop '{name}' not found."

    shop = json.loads(raw) if isinstance(raw, str) else raw
    items = shop.get("items", [])

    # Find item (case-insensitive)
    target = None
    for item in items:
        if item["name"].lower() == item_name.lower():
            target = item
            break

    if not target:
        return f"Item '{item_name}' not found in {name}. Use shop_get to see available stock."

    current_qty = target.get("qty", 0)
    if current_qty == 0:
        return f"'{item_name}' is out of stock at {name}."
    if qty > current_qty:
        return f"Only {current_qty}× '{item_name}' in stock. Cannot sell {qty}."

    target["qty"] -= qty
    shop["items"] = items
    _state().save(k, json.dumps(shop))

    remaining = target["qty"]
    price = target.get("price_gp", 0) * qty
    price_str = f"{price:.1f} gp" if price >= 1 else f"{int(price*100)} cp"
    return (
        f"💰 Sold {qty}× {item_name} for {price_str}. "
        f"Remaining stock: {remaining}{'× (last one!)' if remaining == 1 else '×' if remaining > 0 else ' — OUT OF STOCK'}"
    )


def shop_restock(name: str, current_day: int = 0) -> str:
    """
    Restock a shop if enough in-game days have passed since last restock.
    Call this when the party returns to a shop after time has passed.

    Args:
        name: Shop name
        current_day: Current in-game day number (from dnd-time)

    Returns:
        Restock result — what was replenished or how many days remain.
    """
    k = _key(name)
    raw = _state().get(k)
    if not raw:
        return f"Shop '{name}' not found."

    shop = json.loads(raw) if isinstance(raw, str) else raw
    last_restock = shop.get("last_restock_day", 0)
    restock_interval = shop.get("restock_days", 7)
    days_since = current_day - last_restock

    if days_since < restock_interval:
        days_remaining = restock_interval - days_since
        return (
            f"{name} hasn't restocked yet. "
            f"{days_remaining} more day(s) until restock (every {restock_interval} days)."
        )

    # Restore all items to template quantities
    template = SHOP_TEMPLATES.get(shop.get("shop_type", "general"), SHOP_TEMPLATES["general"])
    template_map = {i["name"]: i["qty"] for i in template["items"]}
    restocked = []

    for item in shop["items"]:
        orig_qty = template_map.get(item["name"])
        if orig_qty is not None and item.get("qty", 0) < orig_qty:
            restocked.append(f"{item['name']} (→ {orig_qty}×)")
            item["qty"] = orig_qty

    shop["last_restock_day"] = current_day
    _state().save(k, json.dumps(shop))

    if restocked:
        return f"🔄 {name} restocked on day {current_day}:\n  " + "\n  ".join(restocked)
    return f"🔄 {name} restocked on day {current_day} — all items were already at full stock."


def shop_update(name: str, item_name: str, price_gp: float = None, qty: int = None, add: bool = False) -> str:
    """
    Manually update an item's price or quantity, or add a new item to a shop.

    Args:
        name: Shop name
        item_name: Item to update or add
        price_gp: New price in gold pieces (optional)
        qty: New quantity (optional)
        add: If True, adds item_name as a new item if it doesn't exist

    Returns:
        Update confirmation.
    """
    k = _key(name)
    raw = _state().get(k)
    if not raw:
        return f"Shop '{name}' not found."

    shop = json.loads(raw) if isinstance(raw, str) else raw
    items = shop.get("items", [])

    target = next((i for i in items if i["name"].lower() == item_name.lower()), None)

    if target is None:
        if add:
            new_item = {"name": item_name, "price_gp": price_gp or 1.0, "qty": qty or 1}
            items.append(new_item)
            shop["items"] = items
            _state().save(k, json.dumps(shop))
            return f"✅ Added '{item_name}' to {name} — {new_item['price_gp']} gp × {new_item['qty']}"
        return f"Item '{item_name}' not found. Set add=True to create it."

    if price_gp is not None:
        target["price_gp"] = price_gp
    if qty is not None:
        target["qty"] = qty

    _state().save(k, json.dumps(shop))
    return f"✅ Updated '{item_name}' in {name}: {target['price_gp']} gp × {target['qty']}"


def shop_list(location: str = "") -> str:
    """
    List all saved shops, optionally filtered by location.

    Args:
        location: Filter by location name (optional)

    Returns:
        List of all matching shops.
    """
    index = _load_index()
    if not index:
        return "No shops saved yet. Use shop_create to add one."

    lines = ["🏪 Saved shops:"]
    for k in index:
        raw = _state().get(k)
        if not raw:
            continue
        shop = json.loads(raw) if isinstance(raw, str) else raw
        if location and location.lower() not in shop.get("location", "").lower():
            continue
        owner_str = f" (run by {shop['owner']})" if shop.get("owner") else ""
        loc_str = f" — {shop['location']}" if shop.get("location") else ""
        lines.append(f"  {shop['name']}{owner_str}{loc_str} [{shop['shop_type']}]")

    return "\n".join(lines)


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "shop_create",
            "description": "Create a new shop with generated or custom inventory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Shop name (e.g. 'Petra's General Store', 'The Dented Anvil')"},
                    "owner": {"type": "string", "description": "Owner NPC name. Default: ''"},
                    "location": {"type": "string", "description": "Location name this shop is in. Default: ''"},
                    "shop_type": {"type": "string", "description": "Template: general | blacksmith (weapons, armour, ammunition) | apothecary (potions, poisons) | magic (scrolls, wands, wondrous items) | fence (stolen goods, illicit items). Default: general"},
                    "custom_items": {"type": "string", "description": "JSON string of custom items to add to template stock. Default: ''"},
                    "notes": {"type": "string", "description": "Freeform notes. Default: ''"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "shop_get",
            "description": "Get the full inventory and details for a shop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Shop name"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "shop_sell",
            "description": "Record a sale — reduces item quantity in the shop's stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Shop name"},
                    "item_name": {"type": "string", "description": "Exact item name as it appears in inventory"},
                    "qty": {"type": "integer", "description": "Quantity being purchased. Default: 1"}
                },
                "required": ["name", "item_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "shop_restock",
            "description": "Restock a shop if enough in-game days have passed since last restock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Shop name"},
                    "current_day": {"type": "integer", "description": "Current in-game day number (from dnd-time). Default: 0"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "shop_update",
            "description": "Manually update an item's price or quantity, or add a new item to a shop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Shop name"},
                    "item_name": {"type": "string", "description": "Item to update or add"},
                    "price_gp": {"type": "number", "description": "New price in gold pieces"},
                    "qty": {"type": "integer", "description": "New quantity"},
                    "add": {"type": "boolean", "description": "If True, adds item_name as a new item if it doesn't exist. Default: False"}
                },
                "required": ["name", "item_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "shop_list",
            "description": "List all saved shops, optionally filtered by location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Filter by location name. Default: ''"}
                },
                "required": []
            }
        }
    },
]


def execute(function_name, arguments, config):
    if function_name == 'shop_create':
        result = shop_create(
            name=arguments.get('name', ''),
            owner=arguments.get('owner', ''),
            location=arguments.get('location', ''),
            shop_type=arguments.get('shop_type', 'general'),
            custom_items=arguments.get('custom_items', ''),
            notes=arguments.get('notes', '')
        )
        return result, not result.startswith("ERROR:")

    if function_name == 'shop_get':
        return shop_get(name=arguments.get('name', '')), True

    if function_name == 'shop_sell':
        return shop_sell(
            name=arguments.get('name', ''),
            item_name=arguments.get('item_name', ''),
            qty=arguments.get('qty', 1)
        ), True

    if function_name == 'shop_restock':
        return shop_restock(
            name=arguments.get('name', ''),
            current_day=arguments.get('current_day', 0)
        ), True

    if function_name == 'shop_update':
        return shop_update(
            name=arguments.get('name', ''),
            item_name=arguments.get('item_name', ''),
            price_gp=arguments.get('price_gp'),
            qty=arguments.get('qty'),
            add=arguments.get('add', False)
        ), True

    if function_name == 'shop_list':
        return shop_list(location=arguments.get('location', '')), True

    return f"Unknown function: {function_name}", False
