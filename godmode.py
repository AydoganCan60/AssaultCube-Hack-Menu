from helper import get_offset
import time
from ctypes import *

class GodMode:
    def __init__(self, proc, local_player_func, lock, toggle_func):
        self.proc = proc
        self.get_local_player = local_player_func
        self.lock = lock
        self.toggle = toggle_func

        # Offsets (all from offsets.json)
        self.health_offset = get_offset("health_offset")  # Example: 0xEC
        self.armor_offset = get_offset("armor_offset")  # Example: 0xF0

        self.ammo_offsets = {
            "assault_rifle": get_offset("assault_rifle_offset"),  # Example: 0x140
            "submachine_gun": get_offset("submachine_gun_offset"),  # Example: 0x138
            "sniper": get_offset("sniper_offset"),  # Example: 0x13C
            "shotgun": get_offset("shotgun_offset"),  # Example: 0x134
            "pistol": get_offset("pistol_offset"),  # Example: 0x12C
            "grenade": get_offset("grenade_offset")  # Example: 0x144
        }

    def loop(self):
        while True:
            try:
                local_player_addr = self.get_local_player()  # Get the local player address
                if not local_player_addr:
                    time.sleep(0.1)
                    continue  # Wait if no local player is found

                if self.toggle():  # If GodMode is active
                    with self.lock:
                        # HEALTH and ARMOR
                        self.proc.write_int(local_player_addr + self.health_offset, 9999)  # Health
                        self.proc.write_int(local_player_addr + self.armor_offset, 9999)  # Armor

                        # Infinite ammo
                        for ammo_name, ammo_offset in self.ammo_offsets.items():
                            self.proc.write_int(local_player_addr + ammo_offset, 999)  # Infinite ammo

                else:  # If GodMode is disabled
                    with self.lock:
                        # Set health to 100 if it's above 100
                        current_health = self.proc.read_int(local_player_addr + self.health_offset)
                        if current_health > 100:
                            self.proc.write_int(local_player_addr + self.health_offset, 100)

                        # Set armor to 100 if it's above 100
                        current_armor = self.proc.read_int(local_player_addr + self.armor_offset)
                        if current_armor > 100:
                            self.proc.write_int(local_player_addr + self.armor_offset, 100)

                        # Set ammo to default (e.g., 30)
                        for ammo_name, ammo_offset in self.ammo_offsets.items():
                            current_ammo = self.proc.read_int(local_player_addr + ammo_offset)
                            if current_ammo > 30:  # If greater than 30
                                self.proc.write_int(local_player_addr + ammo_offset, 30)  # Set to 30

                time.sleep(0.05)  # Loop speed
            except Exception as e:
                print(f"[ERROR] GodMode: {e}")
                time.sleep(1)  # Wait if an error occurs
