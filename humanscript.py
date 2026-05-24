import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.system("")  # enable ANSI escape codes on Windows
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import mplcursors
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from game import Game
from player import Player

itt = "a"
path = itt + "/input.csv"

players = ["RED", "BLUE", "YELLOW", "GREEN"]

g = Game()
g.createPlayers("h", players)
g.setup(path)
g.setFestCount(4)

CAT_ORDER = ["SCRIPT", "DIRECTOR", "ACTOR", "EVENT", "DEBUFF"]

ANSI = {"RED": "\033[91m", "BLUE": "\033[94m", "YELLOW": "\033[93m", "GREEN": "\033[92m"}
RESET = "\033[0m"

def cname(player):
    name = player.name if hasattr(player, "name") else str(player)
    return f"{ANSI.get(name, '')}{name}{RESET}"

def print_hand(player: Player, max_name_len: int):
    cats = [cat for cat in CAT_ORDER if cat in player.table]
    padding = " " * (max_name_len - len(player.name) + 2)
    colored_prefix = f"{cname(player)}:{padding}"
    indent = " " * (max_name_len + 3)  # name + colon + 2 spaces
    for i, cat in enumerate(cats):
        names = ", ".join(player.hand[j].name for j in player.table[cat])
        leader = colored_prefix if i == 0 else indent
        print(f"{leader}{cat}S: {names}")
    print()

def print_hands():
    max_name_len = max(len(p.name) for p in g.players)
    for player in g.players:
        print_hand(player, max_name_len)

def print_balances():
    print("  |  ".join(f"{cname(p)}: £{p.balance}" for p in g.players) + f"  |  DEBUFF: {g.debuff.name}")

def pick_card(player: Player, cat):
    indices = player.table[cat]
    if len(indices) == 1:
        return player.hand[indices[0]]
    print(f"  Choose a {cat}:")
    print(f"    [0] Cancel")
    for i, idx in enumerate(indices):
        print(f"    [{i+1}] {player.hand[idx].name}")
    while True:
        choice = input("  > ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(indices):
            return player.hand[indices[int(choice)-1]]
        print(f"  Invalid — enter 0–{len(indices)}")

def prompt_movie(player: Player):
    has = lambda cat: cat in player.table and len(player.table[cat]) > 0
    if not (has("SCRIPT") and has("DIRECTOR") and has("ACTOR")):
        return

    one_of_each = all(len(player.table[c]) == 1 for c in ("SCRIPT", "DIRECTOR", "ACTOR"))
    if one_of_each:
        s = player.hand[player.table["SCRIPT"][0]]
        d = player.hand[player.table["DIRECTOR"][0]]
        a = player.hand[player.table["ACTOR"][0]]
        answer = input(f"  Would {cname(player)} like to play a film ({s.name}, {d.name}, {a.name})? (y/n): ").strip().lower()
    else:
        answer = input(f"  Would {cname(player)} like to play a film? (y/n): ").strip().lower()

    if answer != "y":
        return

    if not one_of_each:
        s = pick_card(player, "SCRIPT")
        if s is None:
            print("  Film cancelled.")
            return
        d = pick_card(player, "DIRECTOR")
        if d is None:
            print("  Film cancelled.")
            return
        a = pick_card(player, "ACTOR")
        if a is None:
            print("  Film cancelled.")
            return

    print(f"\n  Film: {s.name} | {d.name} | {a.name}")
    confirm = input("  Confirm release? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Film cancelled.")
        return

    movie = player.makeMovie(s, d, a)
    movie.modify(g.fest.name)
    movie.modify(g.debuff.name)
    player.changeBalance(movie.value, 0)
    g.movies.append(movie)

    film_log.append({
        "turn":     turn_number,
        "player":   player.name,
        "value":    movie.value,
        "festival": g.fest.name,
        "script":   {"name": s.name, "qtyDice": s.qtyDice, "dice": s.dice, "roll": movie.rolls[s.name]},
        "director": {"name": d.name, "qtyDice": d.qtyDice, "dice": d.dice, "roll": movie.rolls[d.name]},
        "actor":    {"name": a.name, "qtyDice": a.qtyDice, "dice": a.dice, "roll": movie.rolls[a.name]},
        "applied_mods": list(movie.applied_mods),
    })

    print(f"\n  Rolls:")
    for card, roll_val in zip([s, d, a], movie.rolls.values()):
        print(f"    {card.name} ({card.qtyDice}d{card.dice}): {roll_val}")
    if movie.applied_mods:
        print(f"  Modifiers:")
        for trigger, mod in movie.applied_mods:
            print(f"    {trigger}: {mod}")
    print(f"  Total: £{movie.value}")
    print(f"  → {cname(player)} released film for £{movie.value}")
    input("Press ENTER to move to next turn")

# build single-key shortcuts: r=RED, b=BLUE etc.
shortcuts = {p.name[0].lower(): p for p in g.players}
shortcut_hint = ", ".join(f"{k}={cname(p)}" for k, p in shortcuts.items())

PLAYER_COLORS = {"RED": "red", "BLUE": "royalblue", "YELLOW": "gold", "GREEN": "green"}
FEST_SHADE_COLORS = ["#fce4ec", "#e8eaf6", "#e8f5e9", "#fff9c4"]

plt.ion()
fig, ax = plt.subplots(figsize=(8, 5))
ax.set_xlabel("Turn")
ax.set_ylabel("Balance (£)")
ax.set_title("Player Balances Over Time")
ax.grid(True, alpha=0.3)

turn_history = [0]
balance_history = {p.name: [p.balance] for p in g.players}
plot_lines = {
    p.name: ax.plot([0], [p.balance], label=p.name,
                    color=PLAYER_COLORS.get(p.name, None), linewidth=2)[0]
    for p in g.players
}
ax.legend()
plt.tight_layout()
plt.show()

fig_s, ax_s = plt.subplots(figsize=(10, 6))
fig_s.canvas.manager.set_window_title("Films Released")
plt.tight_layout()
plt.show()

film_log = []
festival_log = [(g.fest.name, 0)]
_scatter_cursor = [None]  # list so inner function can rebind

def update_scatter(current_turn):
    if _scatter_cursor[0] is not None:
        _scatter_cursor[0].remove()
        _scatter_cursor[0] = None

    ax_s.cla()
    ax_s.set_xlabel("Turn")
    ax_s.set_ylabel("Box Office (£)")
    ax_s.set_title("Films Released")
    ax_s.grid(True, alpha=0.3)

    fest_handles = []
    for i, (fest_name, start) in enumerate(festival_log):
        end = festival_log[i + 1][1] if i + 1 < len(festival_log) else current_turn + 1
        color = FEST_SHADE_COLORS[i % len(FEST_SHADE_COLORS)]
        ax_s.axvspan(start - 0.5, end - 0.5, alpha=0.4, color=color, zorder=0)
        fest_handles.append(Patch(facecolor=color, alpha=0.6, label=fest_name))

    player_handles = [
        Line2D([0], [0], marker="o", color="w",
               markerfacecolor=PLAYER_COLORS.get(p.name, "gray"),
               markersize=8, label=p.name)
        for p in g.players
    ]
    ax_s.legend(handles=fest_handles + player_handles, loc="upper left", fontsize=8)

    if film_log:
        x      = [f["turn"]  for f in film_log]
        y      = [f["value"] for f in film_log]
        colors = [mcolors.to_rgba(PLAYER_COLORS.get(f["player"], "gray")) for f in film_log]
        sc = ax_s.scatter(x, y, c=colors, s=100, zorder=5,
                          edgecolors="white", linewidths=0.5)

        cur = mplcursors.cursor(sc, hover=True)

        @cur.connect("add")
        def on_add(sel):
            film = film_log[sel.index]
            si, di, ai = film["script"], film["director"], film["actor"]
            rows = [
                f"Festival: {film['festival']}",
                "",
                f"Script:   {si['name']}  ({si['qtyDice']}d{si['dice']}) → {si['roll']}",
                f"Director: {di['name']}  ({di['qtyDice']}d{di['dice']}) → {di['roll']}",
                f"Actor:    {ai['name']}  ({ai['qtyDice']}d{ai['dice']}) → {ai['roll']}",
            ]
            if film["applied_mods"]:
                rows += ["", "Modifiers:"]
                for trigger, mod in film["applied_mods"]:
                    rows.append(f"  {trigger}: {mod}")
            rows += ["", f"Total: £{film['value']}"]
            sel.annotation.set_text("\n".join(rows))
            sel.annotation.get_bbox_patch().set(fc="white", alpha=0.92)

        _scatter_cursor[0] = cur

        y_max = max(y)
        y_pad = max(5, y_max * 0.15)
        ax_s.set_ylim(0, y_max + y_pad)

    ax_s.set_xlim(-0.5, current_turn + 0.5)
    fig_s.canvas.draw()
    fig_s.canvas.flush_events()

def update_plot(turn):
    turn_history.append(turn)
    for p in g.players:
        balance_history[p.name].append(p.balance)
        plot_lines[p.name].set_xdata(turn_history)
        plot_lines[p.name].set_ydata(balance_history[p.name])
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()
    fig.canvas.flush_events()

print(f"\n=== FESTIVAL: {g.fest.name} ===\n")
print_balances()
print()

turn_number = 1
while not g.endGame:
    print_hands()
    input(f"Press ENTER for {cname(g.players[g.pIndex])} to reveal next card...")

    # handle empty deck
    if g.deck.tpleng == 0:
        g.startEndGame()
        print("\n=== DECK EXHAUSTED — FINAL ROUND ===")
        break

    g.turnNo += 1
    print()
    print_balances()

    card = g.deck.reveal()
    mods = ", ".join(f"{k} {v}" for k, v in card.modifiers.items()) if card.modifiers else ""
    mod_str = f" ({mods})" if mods else ""
    print(f"\n{cname(g.players[g.pIndex])} reveals Card: {card.name}  [{card.cat}]{mod_str}")

    if card.cat == "DEBUFF":
        g.replaceDebuff(card)
        print(f"  → Debuff active: {card.name}")

    elif card.cat == "EVENT":
        # log current balances first — applyAction reads actionlog[-1][5:]
        g.log(f"EVENT: {card.name}")
        if card.name == "POACH TALENT":
            active = g.players[g.pIndex]
            others = {k: p for k, p in shortcuts.items() if p != active}
            others_hint = ", ".join(f"{k}={cname(p)}" for k, p in others.items())
            print(f"  POACH TALENT: pick a player to steal a card from ({others_hint}):")
            key = input("  Steal from > ").strip().lower()
            victim = others.get(key)
            if victim and len(victim.hand) > 0:
                print(f"  {cname(victim)}'s cards:")
                for i, c in enumerate(victim.hand):
                    print(f"    [{i}] {c.name} ({c.cat})")
                idx = int(input("  Card index > ").strip())
                stolen = victim.hand[idx]
                victim.removeCard(stolen)
                g.players[g.pIndex].giveCard(stolen)
                print(f"  → {cname(g.players[g.pIndex])} stole {stolen.name} from {cname(victim)}")
        else:
            result = g.applyAction(card, g.players[g.pIndex])
            if card.name == "TAX SCANDAL" and result is not None:
                rolled, target = result
                print(f"  → TAX SCANDAL applied to {cname(target)} — rolled {rolled}")
            elif card.name == "STRIKE ACTION":
                print(f"  → STRIKE ACTION applied to all players")
            elif card.name == "PLANTED PR PIECE" and result is not None:
                print(f"  → PLANTED PR PIECE: {cname(result)} gets £{list(card.modifiers.values())[0][1:]} — debuff cleared")
            elif result is not None:
                print(f"  → {card.name} applied to {cname(result)}")
            elif card.name == "TAX CREDIT":
                print(f"  → TAX CREDIT not applied — no one has purchased a card yet")
            elif card.name == "TOURISM":
                print(f"  → TOURISM not applied — no films have been released yet")
            elif card.name == "LIFETIME ACHIEVEMENT":
                print(f"  → LIFETIME ACHIEVEMENT not applied — no films have been released yet")
            elif card.name == "AARP AWARD":
                print(f"  → AARP AWARD not applied — no films featuring a VETERAN director have been released yet")
            else:
                print(f"  → {card.name} applied")

    elif card.cat == "FESTIVAL":
        if g.fest != g.deck.null:
            g.awardsVote()
        g.fest = card
        festival_log.append((g.fest.name, turn_number))
        g.log("NEW FESTIVAL! - " + str(g.fest))
        print(f"\n=== NEW FESTIVAL: {g.fest.name} ===\n")

    elif card.cat in ("SCRIPT", "DIRECTOR", "ACTOR"):
        while True:
            key = input(f"  Who bought it? ({shortcut_hint}): ").strip().lower()
            if key in shortcuts:
                break
            print(f"  Invalid — enter one of: {', '.join(shortcuts)}")
        buyer = shortcuts[key]
        price = int(input(f"  Price paid by {cname(buyer)}? £"))
        g.lastBuyer = buyer
        buyer.giveCard(card)
        buyer.changeBalance(price, 1)
        print(f"  → {cname(buyer)} bought {card.name} for £{price}")

    prompt_movie(g.players[g.pIndex])

    g.pIndex = (g.pIndex + 1) % g.noPlayers
    turn_number += 1
    update_plot(turn_number)
    update_scatter(turn_number)
    fest_mods = ", ".join(f"{k} {v}" for k, v in g.fest.modifiers.items()) if g.fest.modifiers else ""
    fest_str = f"{g.fest.name} ({fest_mods})" if fest_mods else g.fest.name
    next_fest_idx = next((i for i, c in enumerate(g.deck.toplay) if c.cat == "FESTIVAL"), None)
    if next_fest_idx == 0:
        fest_countdown = " — FESTIVAL NEXT TURN"
    elif next_fest_idx is not None:
        fest_countdown = f" — NEXT FEST IN {next_fest_idx} TURNS"
    else:
        fest_countdown = " — NO MORE FESTIVALS"
    print(f"\n=============================== TURN {turn_number} - {fest_str}{fest_countdown} ===============================\n")

print(f"\n=== FINAL ROUND ===\n")
for _ in range(g.noPlayers):
    print_hands()
    print_balances()
    prompt_movie(g.players[g.pIndex])
    g.pIndex = (g.pIndex + 1) % g.noPlayers
    turn_number += 1
    update_plot(turn_number)
    update_scatter(turn_number)

print("\n=== GAME OVER ===")
print_balances()
plt.ioff()
plt.show(block=True)

