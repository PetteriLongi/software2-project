import shutil

# ==========================================
# INVENTORY RENDERING (ASCII FALLBACK)
# ==========================================
def _render_inventory_ascii(player, weapons_list, consumables_list):
    """Plain-text inventory rendering used when Rich is unavailable.

    Matches ordering and numbering expected by combat_actions.handle_inventory().
    """
    print("\n=== Inventory ===")

    markka_amount = getattr(player, "markka", 0)
    try:
        markka_display = f"{markka_amount:,}"
    except ValueError:
        markka_display = str(markka_amount)
    print(f"Markka: {markka_display}")

    # Ammo reserves
    print("Ammo reserves:")
    if getattr(player, "ammo", None):
        for k, v in player.ammo.items():
            print(f"  - {k}: {v}")
    else:
        print("  (none)")

    index = 1
    # Weapons section
    print("\nWeapons:")
    if weapons_list:
        for w in weapons_list:
            equipped = (player.weapon is w)
            badge = " (equipped)" if equipped else ""
            if getattr(w, "weapon_type", "melee") == "gun":
                mag = f" [{w.current_mag}/{w.mag_size}]"
            else:
                mag = ""
            print(f"  {index}. {w.name}{badge}{mag} - {w.description}")
            index += 1
    else:
        print("  (none)")

    # Consumables section
    print("\nConsumables:")
    if consumables_list:
        for c in consumables_list:
            qty = getattr(c, "quantity", None)
            qty_str = f" x{qty}" if isinstance(qty, int) else ""
            print(f"  {index}. {getattr(c, 'name', str(c))}{qty_str} - {getattr(c, 'description', '')}")
            index += 1
    else:
        print("  (none)")

    print("\n0. Back to action menu")
    print("Type 'u' to unequip current weapon")
    print("Choose an item to equip/use (0 to back):")


# ==========================================
# COMBAT STATUS BARS (ASCII FALLBACK)
# ==========================================
def draw_status_bars_ascii(player, enemies_list):
    """Print classic ASCII status bars for player and enemies.

    Mirrors the original layout from combat.py, used when Rich is unavailable.
    """
    # Determine max name width for alignment on the right side
    max_name_length = max(len(e.name) for e in enemies_list) if enemies_list else 12

    def draw_bar(label, current, maximum, bar_length=20, color="default", name_width=12):
        ratio = current / maximum if maximum > 0 else 0
        filled = int(ratio * bar_length)
        empty = bar_length - filled
        if color == "hp":
            col = "\033[92m" if ratio > 0.6 else "\033[93m" if ratio > 0.3 else "\033[91m"
        elif color == "sanity":
            col = "\033[95m"
        else:
            col = "\033[0m"
        reset = "\033[0m"
        bar = f"{col}{'#' * filled}{'-' * empty}{reset}"
        return f"{label:<{name_width}}: [{bar}] {current}/{maximum}"

    # Build enemy bars
    enemy_bars = []
    for enemy in enemies_list:
        if enemy.hp > 0:
            enemy_bars.append(draw_bar(enemy.name, enemy.hp, enemy.max_hp, color="hp", name_width=max_name_length))
        else:
            enemy_bars.append(f"{enemy.name}: [\033[91mDEFEATED\033[0m]")

    player_lines = 2  # HP + Sanity
    total_lines = max(len(enemy_bars), player_lines)

    for i in range(total_lines):
        left = (
            draw_bar("Your HP", player.hp, player.max_hp, color="hp") if i == 0 else
            draw_bar("Sanity ", player.sanity, player.max_sanity, color="sanity") if i == 1 else
            " " * 42
        )
        right = enemy_bars[i] if i < len(enemy_bars) else ""
        print(f"{left:<40} || {right}")


def display_hud(player, doom_clock):
    """Display persistent hud with Doomclock"""
    term_width = shutil.get_terminal_size(fallback=(80, 24)).columns
    separator = "=" * min(60, term_width - 4)
    # center and print status
    def center_text(text):
        padding = (term_width - len(text)) // 2
        return " " * padding + text

    print(center_text(separator))
    print(center_text(f"Sanity: {player.sanity}/{player.max_sanity}"))
    print(center_text(f"HP: {player.hp}/{player.max_hp}"))
    print(center_text(f"Doom Clock: {doom_clock.ticks}/{doom_clock.start}"))
    print(center_text(f"Level: {player.level}"))
    print(center_text(separator))