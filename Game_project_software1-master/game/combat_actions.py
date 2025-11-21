import random
from .items import Weapon, Item, Consumable
from .ui import render_inventory, colouring
from .music import play_sfx

# ========================================
# COMBAT FUNCTIONS
# ========================================

# ---Target selection function---
def select_target(enemies_list, player_log):
    """
    Prompts the player to select a living enemy target.
    Returns the selected enemy or None if no valid selection.
    """
    living = [enemy for enemy in enemies_list if enemy.hp > 0]
    if not living:
        player_log.append(colouring("There are no living enemies!", "yellow"))
        player_log.append("")
        return None
    
    print("\nChoose a target:")
    for i, enemy in enumerate(living, 1):
        print(f"{i}. {enemy.name} ({enemy.hp}/{enemy.max_hp} HP)")

    pick = input("> ")
    if not pick.isdigit():
        player_log.append(colouring("You hesitate and do nothing!", "yellow"))
        player_log.append("")
        return None
    
    index = int(pick)
    if not (1 <= index <= len(living)):
        player_log.append(colouring("You hesitate and do nothing!", "yellow"))
        player_log.append("")
        return None
    
    return living[index - 1]


# ---Reload Gun Function---        
def reload_gun(player, weapon=None, ammo=None, consume_turn=True):
    """
    Reload the player's current (or provided) firearm.

    Returns:
        (turn_consumed: bool, messages: list[str])

    Usage:
        # Inside combat:
        turn_consumed, msgs = reload_gun(player, consume_turn=True)
        player_log.extend(msgs)

        # Outside combat (e.g., resting/menu):
        _, msgs = reload_gun(player, consume_turn=False)
        for m in msgs:
            print(m)
    """

    msgs = []
    weapon = weapon if weapon is not None else player.weapon
    ammo = ammo if ammo is not None else player.ammo
    
    if not weapon or getattr(weapon, "weapon_type", "melee") != "gun":
        msgs.append(colouring("You are not wielding a firearm.", "yellow"))
        msgs.append("")
        return (consume_turn, msgs)
    
    sfx = getattr(weapon, "sfx_reload", None)
    if sfx:
        try:
            play_sfx(sfx)
        except Exception:
            # Fail silently if audio unavailable
            pass

    needed = max(0, weapon.mag_size - weapon.current_mag)
    if needed == 0:
        msgs.append(colouring(f"{weapon.name}'s magazine is already full.", "blue"))
        msgs.append("")
        return (consume_turn, msgs)

    ammo_type = getattr(weapon, 'ammo_type', 'bullets')
    reserve = ammo.get(ammo_type, 0) #read straight from ammo
    if reserve <= 0:
        msgs.append(colouring(f"No {ammo_type} ammo in reserve to reload!", "red"))
        msgs.append("")
        return (consume_turn, msgs)

    to_load = min(needed, reserve)
    weapon.current_mag += to_load
    ammo[ammo_type] = reserve - to_load

    msgs.append(colouring(f"You reload {weapon.name}: +{to_load} rounds ({weapon.current_mag}/{weapon.mag_size}).", "green"))
    msgs.append(colouring(f"Reserve left: {ammo[ammo_type]}", "green"))

    if to_load < needed:
        msgs.append(colouring(f"Partial reload: not enough {ammo_type} to fill the magazine.", "yellow"))
    if ammo[ammo_type] == 0:
        msgs.append(colouring(f"You're out of {ammo_type} after reloading.", "yellow"))
    msgs.append("")
    return (consume_turn, msgs)

# ---Handle Inventory Function---
def handle_inventory(player):

    msgs = []
    turn_consumed = False

    if not player.inventory:
        msgs.append(colouring("Your inventory is empty!", "yellow"))
        msgs.append("")
        return (turn_consumed, msgs)

    total_items = []
    weapons_list = []
    consumables_list = []

    # Migrate any lingering ammo-type consumables into the ammo pool
    # This prevents showing stale ammo quantities as inventory items.
    to_remove = []
    for it in list(player.inventory):
        if isinstance(it, Consumable) and getattr(it, "type", None) and str(getattr(it, "type")).lower() == "ammo":
                ammo_key = getattr(it, "name", None) or "ammo"
                qty = getattr(it, "quantity", 0) or 0
                if qty > 0:
                    player.ammo[ammo_key] = player.ammo.get(ammo_key, 0) + qty
                to_remove.append(it)
    for it in to_remove:
        player.inventory.remove(it)

    for it in player.inventory:
        match it:
            case Weapon():
                weapons_list.append(it)
            case Consumable():
                # Skip ammo-type consumables from being displayed/selected
                if not (getattr(it, "type", None) and str(getattr(it, "type")).lower() == "ammo"):
                    consumables_list.append(it)
            case _:
                consumables_list.append(it)

    render_inventory(player, weapons_list, consumables_list)

    total_items.extend(weapons_list)
    total_items.extend(consumables_list)

    while True:
        pick = input("> ").strip()

        if pick == "0":
            msgs.append(colouring("You leave your inventory.", "blue"))
            msgs.append("")
            return turn_consumed, msgs

        if pick.lower() == "u":
            if player.weapon is not None:
                player.weapon = None
                turn_consumed = True
                msgs.append(colouring("You unequip your weapon.", "blue"))
                msgs.append("")
                return turn_consumed, msgs
            else: 
                msgs.append(colouring("You have no weapon equipped!", "yellow"))
                msgs.append("")
                return turn_consumed, msgs

        if pick.isdigit():
            index = int(pick)
            if 1 <= index <= len(total_items):
                turn_consumed = True
                selected = total_items[index - 1]
                break
            else:
                print(colouring("Invalid selection. Please choose a number from the available options.", "yellow"))
        else:
            print(colouring("Invalid input. Please enter a number.", "yellow"))
            
    match selected:
        case Weapon():
            player.weapon = selected
            msgs.append(colouring(f"You equipped {selected.name}", "green"))
            msgs.append("")
        case Consumable():
            msg = selected.use(player)
            if msg:
                msgs.append(msg)
            if selected.quantity <= 0:
                msgs.append(colouring(f"{selected.name} is depleted!", "red"))
                player.inventory.remove(selected)
                msgs.append("")
        case Item():
            msg = selected.use(player)
            if msg:
                msgs.append(msg)
            msgs.append("")
        case _:
            msgs.append(colouring("Invalid item action...", "yellow"))
            msgs.append("")

    return (turn_consumed, msgs)

# --- Handle Manifestations ---
def handle_manifestations(player, enemies_list, player_log):
    if not player.manifestations:
        player_log.append(colouring("You have no manifestations unlocked yet!", "yellow"))
        player_log.append("")
        return False # no turn consumed if no manifestations

    print("\nChoose a manifestation to use:")
    for i, manifestation in enumerate(player.manifestations, 1):
        print(f"{i}. {manifestation.name} (Cost: {manifestation.sanity_cost}) - {manifestation.description}")

    pick = input("> ")
    if not pick.isdigit():
        player_log.append(colouring("You hesitate and do nothing!", "yellow"))
        player_log.append("")
        return True
    
    index = int(pick)
    if not (1 <= index <= len(player.manifestations)):
        player_log.append(colouring("You hesitate and do nothing!", "yellow"))
        player_log.append("")
        return True
    
    chosen = player.manifestations[index - 1]

    # If the manifestation targets self (e.g., Hope), skip enemy selection
    if getattr(chosen, "target_type", "enemy") == "self":
        result = chosen.use_skill(player, None)
        match result:
            case list():
                for r in result:
                    player_log.append(colouring(r, "magenta"))
            case str():
                player_log.append(colouring(result, "magenta"))
            case _ if result:
                player_log.append(colouring(str(result), "magenta"))
        player_log.append("")
        return True

    # Collect living enemies
    living = [e for e in enemies_list if e.hp > 0]
    if not living:
        player_log.append(colouring("There are no valid targets!", "yellow"))
        player_log.append("")
        return True
    
    # Target selection
    print("\nChoose a target:")
    for i, enemies in enumerate(living, 1):
        print(f"{i}. {enemies.name} ({enemies.hp}/{enemies.max_hp} HP)")

    target_pick = input("> ")
    if not target_pick.isdigit():
        player_log.append(colouring("You hesitate and do nothing!", "yellow"))
        player_log.append("")
        return True
    
    t_index = int(target_pick)
    if not (1 <= t_index <= len(living)):
        player_log.append(colouring("You hesitate and do nothing!", "yellow"))
        player_log.append("")
        return True
    
    target = living[t_index - 1]

    # Use the chosen manifestation
    result = chosen.use_skill(player, target)
    match result:
        case list():
            for r in result:
                player_log.append(colouring(r, "magenta"))
        case str():
            player_log.append(colouring(result, "magenta"))
        case _ if result:
            player_log.append(colouring(str(result), "magenta"))

    player_log.append("")
    return True


# ---Attack resolution---
def resolve_attack(player, target, player_log):
    """
    Handles the attack logic (melee or gun), applies damage, and logs messages.
    """
    weapon = player.weapon
    if weapon:
        weapon_name = weapon.name
        if getattr(weapon, "weapon_type", "melee") == "gun":
            # Check Mag first
            if getattr(weapon, "current_mag", 0) > 0:
                dmg = random.randint(*weapon.attack_range)
                weapon.current_mag -= 1
                reserve = player.ammo.get(getattr(weapon, "ammo_type", "bullets"), 0)
                player_log.append(colouring(
                    f"You fire {weapon.name}! ({weapon.current_mag}/{weapon.mag_size} in mag, {reserve} in reserve)",
                    "green"
                ))
            else:
                reserve = player.ammo.get(getattr(weapon, "ammo_type", "bullets"), 0)
                if reserve > 0:
                    player_log.append(colouring("Click! Your magazine is empty. Reload first.", "yellow"))
                else:
                    player_log.append(colouring("Click! You have no ammo left.", "red"))
                dmg = 0
        else:
            # Melee attack
            dmg = random.randint(*weapon.attack_range)
    else:
        # No weapon, fists
        dmg = random.randint(*player.base_attack)
        weapon_name = "your fists"
  
    if dmg > 0 and getattr(player, "weapon", None):
        sfx = getattr(player.weapon, "sfx_attack", None)
        if sfx:
            try:
                play_sfx(sfx)
            except Exception:
                # Fail silently if audio unavailable
                pass
        
    #apply damage
    target.hp -= dmg
    if dmg > 0:
        player_log.append(colouring(f"You strike {target.name} with {weapon_name} for {dmg} damage!", "green"))
    player_log.append("")