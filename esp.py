from raylibpy import *
from helper import world_to_screen
import win32gui, win32con
import math

# Color settings
TEAM_FRIEND_COLOR = BLUE
TEAM_ENEMY_COLOR = RED
ESP_HEALTH_COLOR = GREEN


class ESP:
    def __init__(self, window_info, lock, entity_list_ref, matrix_ref, esp_enabled_ref, godmode_enabled_ref, get_local_team, esp_settings_ref):
        self.window_info = window_info
        self.lock = lock
        self.entity_list_ref = entity_list_ref  # Lambda
        self.matrix_ref = matrix_ref  # Lambda
        self.esp_enabled = esp_enabled_ref
        self.godmode_enabled = godmode_enabled_ref
        self.get_local_team = get_local_team  # Lambda
        self.esp_settings = esp_settings_ref  # ESP settings reference

    def draw_box_with_health(self, pos, health, name, screen_width, screen_height, box_color):
        box_width = 50
        box_height = 100

        x = pos.x - box_width / 2
        y = pos.y - box_height / 2

        # Draw box if active
        if self.esp_settings['box'].get():
            draw_rectangle_lines(int(x), int(y), box_width, box_height, box_color)

        # Draw health bar if active
        if self.esp_settings['health'].get():
            max_health = 100
            health_height = box_height * (health / max_health)
            health_bar_x = x - 8
            health_bar_y = y + (box_height - health_height)

            draw_rectangle(int(health_bar_x), int(y), 5, box_height, DARKGRAY)  # Background
            draw_rectangle(int(health_bar_x), int(health_bar_y), 5, int(health_height), ESP_HEALTH_COLOR)  # Health

        # Draw name if active
        if self.esp_settings['name'].get():
            name = name[:12]  # Truncate long names
            text_width = measure_text(name, 12)
            draw_text(name, int(pos.x - text_width / 2), int(y - 15), 12, WHITE)

    def set_window_mouse_passthrough(self, enable):
        hwnd = win32gui.FindWindow(None, "AssaultCube ESP")
        if hwnd:
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if enable:
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
            else:
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style & ~win32con.WS_EX_TRANSPARENT)

    def init_esp(self):
        set_target_fps(60)
        set_config_flags(
            ConfigFlags.FLAG_WINDOW_UNDECORATED |
            ConfigFlags.FLAG_WINDOW_TRANSPARENT |
            ConfigFlags.FLAG_WINDOW_TOPMOST
        )
        init_window(self.window_info[2], self.window_info[3], "AssaultCube ESP")
        set_window_position(self.window_info[0], self.window_info[1])
        self.set_window_mouse_passthrough(True)

    def esp_loop(self):
        self.init_esp()

        while not window_should_close():
            begin_drawing()
            clear_background(BLANK)

            screen_width = get_screen_width()
            screen_height = get_screen_height()

            # Status indicators
            if self.esp_enabled[0]:
                draw_text("ESP ACTIVE", (screen_width - measure_text("ESP ACTIVE", 20)) // 2, 10, 20, GREEN)
            if self.godmode_enabled[0]:
                draw_text("GOD MODE ACTIVE", (screen_width - measure_text("GOD MODE ACTIVE", 20)) // 2, 40, 20, RED)

            # When ESP is enabled
            if self.esp_enabled[0]:
                with self.lock:
                    current_entities = self.entity_list_ref()
                    current_matrix = self.matrix_ref()
                
                if current_matrix is None:
                    end_drawing()
                    continue

                local_team = self.get_local_team()

                for ent in current_entities:
                    if (ent.pos.x, ent.pos.y, ent.pos.z) == (0, 0, 0) or ent.health <= 0:
                        continue
                    try:
                        wts = world_to_screen(current_matrix, ent.pos)
                        if math.isnan(wts.x) or math.isnan(wts.y):
                            continue
                        if not (0 <= wts.x <= screen_width and 0 <= wts.y <= screen_height):
                            continue

                        name = ent.name.decode('utf-8', 'ignore').strip()
                        box_color = TEAM_FRIEND_COLOR if ent.team == local_team else TEAM_ENEMY_COLOR

                        # You can add a distance filter here:
                        # distance = math.sqrt((ent.pos.x - local_player.x) ** 2 + (ent.pos.y - local_player.y) ** 2 + (ent.pos.z - local_player.z) ** 2)
                        # if distance > 500: continue  # Skip if greater than 500 units

                        # Combined drawing for all features
                        self.draw_box_with_health(wts, ent.health, name, screen_width, screen_height, box_color)

                    except Exception as e:
                        if "Out of bounds" not in str(e):
                            print(f"[ERROR] ESP drawing: {e}")

            end_drawing()

        close_window()
