import customtkinter
import sys

def start_gui(esp_enabled, godmode_enabled, esp_settings, gui_visible):
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("dark-blue")

    app = customtkinter.CTk()
    app.geometry("700x500")
    app.title("💀 AssaultCube Hack Menu 💀")

    # Tab Panel
    tabview = customtkinter.CTkTabview(app, width=680, height=400)
    tabview.pack(padx=10, pady=10, fill="both", expand=True)

    tab_esp = tabview.add("ESP")
    tab_godmode = tabview.add("GodMode")
    tab_misc = tabview.add("Misc")
    tab_settings = tabview.add("Settings")

    # ------------------- ESP Settings -------------------
    customtkinter.CTkLabel(tab_esp, text="ESP Settings", font=("Arial", 18)).pack(pady=10)

    def toggle_esp():
        esp_enabled[0] = not esp_enabled[0]
        esp_button.configure(text=f"ESP {'On' if esp_enabled[0] else 'Off'}")

    esp_button = customtkinter.CTkButton(tab_esp, text="Toggle ESP", command=toggle_esp, width=200)
    esp_button.pack(pady=10)

    esp_settings['box'] = customtkinter.BooleanVar(value=False)
    esp_box_checkbox = customtkinter.CTkCheckBox(tab_esp, text="Show Box", variable=esp_settings['box'])
    esp_box_checkbox.pack(pady=5)

    esp_settings['name'] = customtkinter.BooleanVar(value=False)
    esp_name_checkbox = customtkinter.CTkCheckBox(tab_esp, text="Show Name", variable=esp_settings['name'])
    esp_name_checkbox.pack(pady=5)

    esp_settings['health'] = customtkinter.BooleanVar(value=False)
    esp_health_checkbox = customtkinter.CTkCheckBox(tab_esp, text="Show Health Bar", variable=esp_settings['health'])
    esp_health_checkbox.pack(pady=5)

    # ------------------- GodMode Settings -------------------
    customtkinter.CTkLabel(tab_godmode, text="GodMode Settings", font=("Arial", 18)).pack(pady=10)

    def toggle_godmode():
        godmode_enabled[0] = not godmode_enabled[0]
        godmode_button.configure(text=f"GODMODE {'On' if godmode_enabled[0] else 'Off'}")

    godmode_button = customtkinter.CTkButton(tab_godmode, text="Toggle GodMode", command=toggle_godmode, width=200)
    godmode_button.pack(pady=20)

    # ------------------- Exit Button -------------------
    exit_button = customtkinter.CTkButton(
        app,
        text="❌ EXIT ❌",
        command=sys.exit,
        fg_color="red",
        hover_color="#8B0000",
        width=250,
        height=50,
        font=("Arial", 18, "bold"),
        corner_radius=20
    )
    exit_button.pack(pady=10)

    # ------------------- GUI Visibility Control -------------------
    def check_gui_visibility():
        if gui_visible[0]:
            app.deiconify()           # Show
            app.lift()                # Bring to front
            app.focus_force()         # Focus (automatically clickable)
            app.attributes('-topmost', True)   # Bring to front
            app.after(200, lambda: app.attributes('-topmost', False))  # Release after 200ms
        else:
            app.withdraw()            # Hide
        app.after(100, check_gui_visibility)  # Check again after 0.1s





    check_gui_visibility()  # Initial start

    # Run the GUI
    app.mainloop()
