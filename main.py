from pymem import Pymem
from ctypes import *
import threading
from pynput import keyboard
import time
from helper import *
from offset_loader import load_offsets
from esp import ESP
from godmode import GodMode
from gui import start_gui  # Import function from the GUI file

# ---------------------- GLOBAL ---------------------------
esp_enabled = [False]
godmode_enabled = [False]
entity_list = []
matrix = None
lock = threading.Lock()
local_team = [0]  # Local player team
esp_settings = {}  # <-- Empty dictionary for ESP settings
gui_visible = [False]
# ---------------------- SETUP ---------------------------
window_info = get_window_info("AssaultCube")
proc = Pymem("ac_client.exe")
base = proc.base_address  # DYNAMIC BASE!
offsets = load_offsets()
local_player_addr = lambda: proc.read_int(base + offsets['local_player'])  # Local player function

# ---------------------- DATA UPDATE ---------------------------
def update_game_data():
    global entity_list, matrix, local_team
    while True:
        if esp_enabled[0]:  # Only run when ESP is enabled
            try:
                temp_entities = []
                # Matrix retrieval
                temp_matrix = proc.read_ctype(base + offsets['view_matrix'], (16 * c_float)())[:]
                # Player count
                player_count = proc.read_int(base + offsets['player_count'])

                # Local player check
                local_player = proc.read_int(base + offsets['local_player'])
                if local_player:
                    try:
                        local_player_obj = proc.read_ctype(local_player, Entity())
                        local_team[0] = local_player_obj.team
                    except:
                        local_team[0] = 0
                        print("[WARNING] Local player could not be read, skipped.")
                else:
                    local_team[0] = 0  # Reset if not found

                # Entity list reading (controlled)
                if player_count > 1:
                    ents_addr = proc.read_int(base + offsets['entity_list'])
                    if ents_addr:  # Is entity list address valid?
                        ents = proc.read_ctype(ents_addr, (player_count * c_int)())[1:]  # Skip the first index, local player might be there
                        for ent_addr in ents:
                            if ent_addr:  # Is it valid?
                                try:
                                    ent_obj = proc.read_ctype(ent_addr, Entity())
                                    if ent_obj.health > 0:  # Is health > 0?
                                        temp_entities.append(ent_obj)
                                except Exception as e:
                                    print(f"[WARNING] Entity reading error: {e}")
                                    continue

                # Update global data
                with lock:
                    entity_list[:] = temp_entities
                    matrix = temp_matrix

            except Exception as e:
                print(f"[ERROR] General data reading error: {e}")
        time.sleep(0.05)  # Sleep for performance

# ---------------------- KEY PRESS ---------------------------
def on_press(key):
    if key == keyboard.Key.insert:
        gui_visible[0] = not gui_visible[0]
        print(f"[+] GUI {'opened' if gui_visible[0] else 'closed'}.")

def start_keyboard_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# ---------------------- GUI LOOP ---------------------------
def gui_loop():
    while True:
        if gui_visible[0]:  # Only show when GUI is visible
            start_gui(esp_enabled, godmode_enabled, esp_settings, gui_visible)
        time.sleep(0.5)  # Control interval

# ---------------------- MAIN ---------------------------
if __name__ == '__main__':
    print("[+] Starting...")

    start_keyboard_listener()  # Start key listener
    threading.Thread(target=update_game_data, daemon=True).start()  # Data update thread

    time.sleep(1)  # Small delay for initialization

    # --- Start ESP and Godmode
    esp = ESP(
        window_info,
        lock,
        lambda: entity_list,  # entity_list_ref
        lambda: matrix,       # matrix_ref
        esp_enabled,
        godmode_enabled,
        lambda: local_team[0],  # get_local_team
        esp_settings
    )
    threading.Thread(target=esp.esp_loop, daemon=True).start()  # ESP thread

    godmode = GodMode(proc, local_player_addr, lock, lambda: godmode_enabled[0])
    threading.Thread(target=godmode.loop, daemon=True).start()  # Godmode thread

    print("[+] Starting GUI...")
    # GUI will only start once
    start_gui(esp_enabled, godmode_enabled, esp_settings, gui_visible)  # Runs indefinitely!

    # Keep the main thread running indefinitely
    while True:
        time.sleep(1)
