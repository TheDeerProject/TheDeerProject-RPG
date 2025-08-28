# THIS CODE IS NOT TO BE USED FOR PROFITS,
# This code belongs to @TheDeerProject on www.github.com
#!/usr/bin/env python3
import os
import platform
import random
import time
import json

# ---------- Config ----------
SAVE_FILE = "bramblesong_save.json"
TEXT_SPEED = 0.04  # slower text

# ---------- Utilities ----------
def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def slow_print(text, delay=TEXT_SPEED):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def show_controls():
    print("\nControls: 1=Attack 2=Flee 3=Use Item 4=Special save=Save load=Load restart=Restart clear=Clear q=Quit")
    print("-" * 60)

class RestartGame(Exception):
    pass

def safe_input(prompt=""):
    try:
        user_input = input(prompt).strip()
        if user_input.lower() == "restart":
            raise RestartGame()
        elif user_input.lower() == "clear":
            clear_screen()
            show_controls()
            return safe_input(prompt)
        elif user_input.lower() == "q":
            slow_print("\nGoodbye, forest hero.")
            raise SystemExit
        elif user_input.lower() == "save":
            save_all(player)
            return safe_input(prompt)
        elif user_input.lower() == "load":
            if load_all():
                return "loaded"
            else:
                return safe_input(prompt)
        return user_input
    except (KeyboardInterrupt, EOFError):
        slow_print("\nExiting...")
        raise SystemExit

# ---------- Game Data ----------
base_characters = {
    "Fawn": {"hp": 10, "attack": 2, "speed": 2, "special": "Leap (evade next attack)"},
    "Stag": {"hp": 12, "attack": 3, "speed": 1, "special": "Antler Charge (extra damage)"},
    "Doe": {"hp": 11, "attack": 2, "speed": 3, "special": "Healing Aura (heal 2 HP)"},
}

unlockable_characters = {
    "Elderhart": {"hp": 15, "attack": 4, "speed": 1, "special": "Nature's Wrath (pierce attack)", "unlock_boss": "Bramblehart"},
    "Spirit Fawn": {"hp": 14, "attack": 3, "speed": 2, "special": "Ethereal Step (evade all attacks once)", "unlock_boss": "Mistbuck"},
    "Storm Stag": {"hp": 16, "attack": 4, "speed": 1, "special": "Thunder Charge (stuns enemy)", "unlock_boss": "Stormantler"},
}

enemies_list = [
    {"name": "Iron Antler", "hp": 5, "attack": 2},
    {"name": "Shadow Elk", "hp": 4, "attack": 1},
    {"name": "Feral Wolf", "hp": 6, "attack": 2},
    {"name": "Forest Spider", "hp": 3, "attack": 2},
    {"name": "Vengeful Crow", "hp": 4, "attack": 2},
    {"name": "Cave Bat", "hp": 2, "attack": 3},
    {"name": "Thornling", "hp": 3, "attack": 2},
    {"name": "Swamp Croaker", "hp": 4, "attack": 2},
    {"name": "Ash Hound", "hp": 5, "attack": 3},
    {"name": "Wind Howler", "hp": 5, "attack": 2},
]

# Bosses are now weaker baseline
bosses_list = [
    {"name": "Bloodhorn", "hp": 12, "attack": 3},
    {"name": "Moonfawn", "hp": 10, "attack": 2},
    {"name": "Bramblehart", "hp": 14, "attack": 4},
    {"name": "Ironhoof", "hp": 16, "attack": 4},
    {"name": "Nightstalker", "hp": 13, "attack": 3},
    {"name": "Stormantler", "hp": 18, "attack": 4},
    {"name": "Shadowhorn", "hp": 15, "attack": 4},
    {"name": "Mistbuck", "hp": 12, "attack": 3},
    {"name": "Crystalhorn", "hp": 20, "attack": 5},
]

items_list = [
    {"name": "Healing Herb", "heal": 3},
    {"name": "Sacred Water", "heal": 5},
    {"name": "Golden Acorn", "heal": 4},
    {"name": "Forest Mushroom", "heal": 2},
]

rare_items_list = [
    {"name": "Moonlit Leaf", "heal": 6},
    {"name": "Horn of Anguish", "heal": 0, "special": "Next attack critical"},
    {"name": "Ethereal Hoof", "heal": 0, "special": "Evade all attacks once"},
    {"name": "Crown of Brambles", "heal": 0, "special": "Reflect 1 damage each turn"},
]

# ---------- Save / Load ----------
def save_all(player):
    try:
        data = {
            "player": player,
            "unlocked": unlocked_bosses
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
        slow_print("✅ Game saved.")
    except Exception as e:
        slow_print(f"Failed to save: {e}")

def load_all():
    global player, unlocked_bosses
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                player.update(data["player"])
                unlocked_bosses = data.get("unlocked", [])
            slow_print("✅ Save loaded.")
            return True
        except:
            slow_print("Failed to load save.")
            return False
    else:
        slow_print("No save file found.")
        return False

unlocked_bosses = []

# ---------- Character Selection ----------
def choose_character():
    characters = base_characters.copy()
    for name, stats in unlockable_characters.items():
        if stats["unlock_boss"] in unlocked_bosses:
            characters[name] = stats

    slow_print("Who am I right now?")
    for name, stats in characters.items():
        slow_print(f"{name} (HP: {stats['hp']}, ATK: {stats['attack']}, SPD: {stats['speed']}, Special: {stats['special']})")
    while True:
        choice = safe_input("> ").title()
        if choice in characters:
            stats = characters[choice].copy()
            stats["name"] = choice
            stats["items"] = ["Healing Herb"]
            stats["floor"] = 1
            stats["map"] = []
            stats["_crit_next"] = False
            return stats
        slow_print("Invalid choice, try again.")

# ---------- Combat Scaling ----------
def scale_enemy(enemy, floor):
    enemy = enemy.copy()
    enemy["hp"] += floor // 2
    enemy["attack"] += floor // 4
    return enemy

def scale_boss(boss, floor):
    boss = boss.copy()
    boss["hp"] += floor   # weaker scaling
    boss["attack"] += floor // 3
    return boss

# ---------- Specials ----------
def use_special(player, enemy):
    name = player["name"]
    if name == "Fawn":
        slow_print("You leap to evade next attack!")
        enemy["_miss_next"] = True
    elif name == "Stag":
        slow_print("Antler Charge hits with extra damage!")
        enemy["hp"] -= player["attack"] + 1
    elif name == "Doe":
        slow_print("Healing Aura restores 2 HP!")
        player["hp"] += 2
    elif name == "Elderhart":
        slow_print("Nature's Wrath pierces the enemy!")
        enemy["hp"] -= player["attack"] + 2
    elif name == "Spirit Fawn":
        slow_print("Ethereal Step! You cannot be hit next turn!")
        enemy["_miss_next"] = True
    elif name == "Storm Stag":
        slow_print("Thunder Charge stuns the enemy!")
        enemy["_stunned"] = True

# ---------- Battle ----------
def battle(player, enemy):
    while enemy["hp"] > 0 and player["hp"] > 0:
        slow_print(f"\nYour HP: {player['hp']} | {enemy['name']} HP: {enemy['hp']}")
        slow_print("1) Attack  2) Flee  3) Use Item  4) Special")
        choice = safe_input("> ")
        if choice=="1":
            dmg = player["attack"]
            if player.get("_crit_next"):
                dmg*=2
                player["_crit_next"]=False
                slow_print("Critical hit!")
            enemy["hp"] -= dmg
            slow_print(f"You attack {enemy['name']} for {dmg} damage!")
        elif choice=="2":
            if random.random()<0.5:
                slow_print("Failed to flee!")
            else:
                slow_print("Fled successfully.")
                return True
        elif choice=="3":
            if not player["items"]:
                slow_print("No items!")
                continue
            slow_print(f"Items: {', '.join(player['items'])}")
            item_choice = safe_input("Use which item? > ")
            item = next((i for i in items_list+rare_items_list if i["name"]==item_choice),None)
            if item and item_choice in player["items"]:
                player["hp"]+=item.get("heal",0)
                if "special" in item:
                    slow_print(f"Special: {item['special']}")
                    if "critical" in item.get("special",""):
                        player["_crit_next"]=True
                slow_print(f"Used {item_choice}. HP now {player['hp']}")
                player["items"].remove(item_choice)
            else:
                slow_print("Invalid item.")
        elif choice=="4":
            use_special(player, enemy)
        else:
            slow_print("Invalid choice.")
        # Enemy turn
        if enemy["hp"]>0 and not enemy.get("_stunned"):
            if enemy.get("_miss_next"):
                slow_print(f"{enemy['name']} misses!")
                enemy["_miss_next"]=False
            else:
                slow_print(f"{enemy['name']} attacks for {enemy['attack']} damage!")
                player["hp"]-=enemy["attack"]
        enemy["_stunned"] = False
    return player["hp"]>0

# ---------- Room Exploration ----------
def random_room(player):
    r=random.random()
    if r<0.5:
        enemy = scale_enemy(random.choice(enemies_list), player["floor"])
        slow_print(f"You encounter {enemy['name']}!")
        alive=battle(player,enemy)
        return alive
    elif r<0.8:
        item=random.choice(items_list+rare_items_list)
        slow_print(f"You found {item['name']}!")
        player["items"].append(item['name'])
    else:
        slow_print("The room is empty...")
    return True

# ---------- Floor ----------
def play_floor(player):
    rooms = random.randint(5,8)
    player["map"] = [-1]*rooms
    i = 0
    while i < rooms:
        slow_print(f"\n--- Room {i+1} of floor {player['floor']} ---")
        cont=random_room(player)
        if not cont:
            return False
        player["map"][i]=1
        if i < rooms-1:
            slow_print("Move to next room? (y/n)")
            move = safe_input("> ").lower()
            if move != "y":
                slow_print("You rest for a moment...")
                continue
        i+=1
    boss = scale_boss(random.choice(bosses_list), player["floor"])
    slow_print(f"\nBoss Encounter: {boss['name']} (HP {boss['hp']})")
    alive = battle(player,boss)
    if alive:
        if boss["name"] not in unlocked_bosses:
            unlocked_bosses.append(boss["name"])
            slow_print(f"✨ Defeating {boss['name']} may unlock new characters!")
        save_all(player)
    return alive

# ---------- Main Game ----------
def play_game():
    global player
    clear_screen()
    show_controls()
    slow_print("Welcome to BrambleSong - The Lost Worlds!")
    player = choose_character()
    while player["hp"]>0:
        slow_print(f"\n--- Floor {player['floor']} ---")
        alive = play_floor(player)
        if not alive:
            slow_print("💀 You have perished...")
            choice = safe_input("Type 'restart' to try again, or 'q' to quit: ")
            continue
        player["floor"]+=1
        slow_print(f"🌿 You cleared Floor {player['floor']-1}!")
    slow_print("Game Over.")

if __name__=="__main__":
    while True:
        try:
            play_game()
        except RestartGame:
            slow_print("🔄 Restarting game...")
            continue
        except SystemExit:
            break
