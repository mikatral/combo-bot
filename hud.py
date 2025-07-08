import tkinter as tk
from tkinter import ttk
import time
import ctypes
import pygetwindow as gw
import keyboard
import subprocess

# ================= CONFIG OPACIDADE DO TIBIA =================
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002
WINDOW_TITLE = "Tibia"
OPACITY_STATES = [255, 1]
current_opacity_index = 0

def toggle_opacity(hud_instance=None):
    global current_opacity_index
    try:
        target_window = gw.getWindowsWithTitle(WINDOW_TITLE)[0]
        target_hwnd = target_window._hWnd
        ex_style = ctypes.windll.user32.GetWindowLongA(target_hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongA(target_hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
        opacity = OPACITY_STATES[current_opacity_index]
        ctypes.windll.user32.SetLayeredWindowAttributes(target_hwnd, 0, opacity, LWA_ALPHA)
        status_text = "Normal" if opacity == 255 else "Invisível"
        print(f"[TIBIA] Opacidade ajustada para {opacity} ({status_text})")
        if hud_instance:
            hud_instance.opacity_label.config(text=f"Opacidade: {status_text}")
        current_opacity_index = (current_opacity_index + 1) % len(OPACITY_STATES)
    except IndexError:
        print(f"[ERRO] Janela '{WINDOW_TITLE}' não encontrada.")
        if hud_instance:
            hud_instance.opacity_label.config(text="Opacidade: ERRO")

# ================= HUD =================
class BotHUD:
    def __init__(self, root, combat_manager):
        self.root = root
        self.root.title("System Assistant")  # ou Monitor Helper, Service Watcher, etc.
        self.root.geometry("300x360")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)

        self.start_time = time.time()
        self.combat = combat_manager

        self.combo_on = False
        self.heal_on = False
        self.vocation = tk.StringVar(value=self.combat.profile_name.replace("_", " ").title())
        self.life_percent = tk.IntVar(value=self.combat.life_threshold)
        self.mana_percent = tk.IntVar(value=self.combat.mana_threshold)

        self.create_widgets()
        self.update_timer()
        self.update_status()

        keyboard.add_hotkey('f', self.toggle_combo)
        keyboard.add_hotkey('h', self.toggle_heal)
        keyboard.add_hotkey('home', lambda: toggle_opacity(self))
        keyboard.add_hotkey('end', self.run_calibration)

    def create_widgets(self):
        ttk.Label(self.root, text="Vocação:").pack()
        voc_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.vocation,
            values=["Elite Knight", "Royal Paladin"],
            state="readonly"
        )
        voc_dropdown.pack()
        voc_dropdown.bind("<<ComboboxSelected>>", self.on_vocation_change)

        ttk.Label(self.root, text="Vida % para curar:").pack()
        ttk.Entry(self.root, textvariable=self.life_percent).pack()

        ttk.Label(self.root, text="Mana % para curar:").pack()
        ttk.Entry(self.root, textvariable=self.mana_percent).pack()

        ttk.Label(self.root, text="Tempo de execução:").pack()
        self.timer_label = ttk.Label(self.root, text="00:00")
        self.timer_label.pack()

        self.combo_label = ttk.Label(self.root, text="Combo: OFF", background="red", foreground="white")
        self.combo_label.pack(pady=5, fill="x")

        self.heal_label = ttk.Label(self.root, text="Cura: OFF", background="red", foreground="white")
        self.heal_label.pack(pady=5, fill="x")

        self.opacity_label = ttk.Label(self.root, text="Opacidade: Normal", foreground="blue")
        self.opacity_label.pack(pady=2)

        ttk.Button(self.root, text="Ativar/Desativar Combo [F]", command=self.toggle_combo).pack(pady=2)
        ttk.Button(self.root, text="Ativar/Desativar Cura [H]", command=self.toggle_heal).pack(pady=2)

        ttk.Button(self.root, text="Calibrar Vida/Mana [End]", command=self.run_calibration).pack(pady=4)

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)
        self.timer_label.config(text=f"{mins:02}:{secs:02}")
        self.root.after(1000, self.update_timer)

    def update_status(self):
        self.combat.set_thresholds(self.life_percent.get(), self.mana_percent.get())

        self.combo_label.config(
            text=f"Combo: {'ON' if self.combo_on else 'OFF'}",
            background="green" if self.combo_on else "red"
        )
        self.heal_label.config(
            text=f"Cura: {'ON' if self.heal_on else 'OFF'}",
            background="green" if self.heal_on else "red"
        )
        self.root.after(500, self.update_status)

    def toggle_combo(self):
        self.combo_on = not self.combo_on
        self.combat.toggle_combo()
        print(f"[HUD] Combo {'ativado' if self.combo_on else 'desativado'}")

    def toggle_heal(self):
        self.heal_on = not self.heal_on
        self.combat.toggle_heal()
        print(f"[HUD] Cura {'ativada' if self.heal_on else 'desativada'}")

    def on_vocation_change(self, event=None):
        voc = self.vocation.get().lower().replace(" ", "_")

        if self.combo_on:
            self.toggle_combo()
        if self.heal_on:
            self.toggle_heal()

        print(f"[HUD] Mudando vocação para: {voc.replace('_', ' ').title()}")

        from classes.combat_manager import CombatManager
        self.combat = CombatManager(profile_name=voc)
        self.combat.set_thresholds(self.life_percent.get(), self.mana_percent.get())

    def run_calibration(self):
        print("[HUD] Iniciando calibrador...")
        subprocess.run(["python", "config_calibrator.py"])
        print("[HUD] Calibração finalizada.")

        voc = self.vocation.get().lower().replace(" ", "_")

        from classes.combat_manager import CombatManager
        self.combat = CombatManager(profile_name=voc)
        self.combat.set_thresholds(self.life_percent.get(), self.mana_percent.get())

        if self.combo_on:
            self.toggle_combo()
        if self.heal_on:
            self.toggle_heal()

        print(f"[HUD] Novo CombatManager carregado com configuração calibrada.")

# ================= EXECUÇÃO DIRETA =================
if __name__ == "__main__":
    from classes.combat_manager import CombatManager

    combat = CombatManager(profile_name="Royal Paladin")
    root = tk.Tk()
    app = BotHUD(root, combat)
    root.mainloop()
