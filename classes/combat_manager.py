import threading
import time
import json
import os
import random
import pyautogui
import win32gui

class CombatManager:
    def __init__(self, profile_name='elite_knight', config_path='config.json'):
        self.combo_running = False
        self.combo_event = threading.Event()
        self.combo_thread = None

        self.heal_event = threading.Event()
        self.heal_thread = None
        self.heal_running = False  # controle da cura ligado/desligado

        self.profile_name = profile_name
        self.WIDTH = 89

        self.LIST_HOTKEY_ATTACKS = []
        self.before_hotkeys = []
        self.after_hotkeys = []

        self.RANDOM_MIN_DELAY = 0.05
        self.RANDOM_MAX_DELAY = 0.1

        self.life_threshold = 80
        self.mana_threshold = 80

        self.load_profile(profile_name)
        self.load_config(config_path)

        

    def load_profile(self, profile_name):
        path = os.path.join('profiles', f'{profile_name}.json')
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self.LIST_HOTKEY_ATTACKS = data.get("combo", [])
                self.before_hotkeys = data.get("before_hotkeys", [])
                self.after_hotkeys = data.get("after_hotkeys", [])
                print(f"[OK] Perfil '{profile_name}' carregado.")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar perfil '{profile_name}': {e}")

    def load_config(self, path):
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                self.LIFE_REGION = tuple(config['LIFE_REGION'])
                self.LIFE_COLOR = tuple(config['LIFE_COLOR'])
                self.MANA_REGION = tuple(config['MANA_REGION'])
                self.MANA_COLOR = tuple(config['MANA_COLOR'])
                print("[OK] Configuração de suporte carregada.")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar config: {e}")
            raise

    def toggle_combo(self):
        if not self.combo_running:
            self.start_combo()
        else:
            self.stop_combo()

    def toggle_heal(self):
        self.heal_running = not self.heal_running
        if not hasattr(self, 'heal_thread') or not self.heal_thread:
            self._start_healing()  # inicia a thread na primeira vez que ativar
        print(f"[BOT] Cura {'ativada' if self.heal_running else 'desativada'}")

    def set_thresholds(self, life_percent, mana_percent):
        self.life_threshold = life_percent
        self.mana_threshold = mana_percent

    def start_combo(self):
        self.combo_running = True
        self.combo_event.clear()
        self.combo_thread = threading.Thread(target=self._run_combo, daemon=True)

        for hotkey in self.before_hotkeys:
            self._press_key(hotkey)

        self.combo_thread.start()
        print("[BOT] Combo iniciado.")

    def stop_combo(self):
        self.combo_running = False
        self.combo_event.set()

        for hotkey in self.after_hotkeys:
            self._press_key(hotkey)

        if self.combo_thread and self.combo_thread.is_alive():
            self.combo_thread.join()
        print("[BOT] Combo parado.")

    def _start_healing(self):
        self.heal_event.clear()
        self.heal_thread = threading.Thread(target=self._run_healing, daemon=True)
        self.heal_thread.start()
        print("[BOT] Cura contínua iniciada.")

    def stop_all(self):
        self.stop_combo()
        self.heal_event.set()
        if self.heal_thread and self.heal_thread.is_alive():
            self.heal_thread.join()
        print("[BOT] Cura parada.")

    def _run_combo(self):
        i = 0
        while not self.combo_event.is_set():
            if not self.LIST_HOTKEY_ATTACKS:
                time.sleep(0.3)
                continue
            attack = self.LIST_HOTKEY_ATTACKS[i % len(self.LIST_HOTKEY_ATTACKS)]
            self._press_key(attack["hotkey"])
            delay = max(0.08, attack["delay"] + random.uniform(self.RANDOM_MIN_DELAY, self.RANDOM_MAX_DELAY))
            time.sleep(delay)
            i += 1

    def _run_healing(self):
        while not self.heal_event.is_set():
            if not self.heal_running:
                time.sleep(0.1)
                continue

            if self.profile_name == 'elite_knight':
                if not self._pixel_matches(self.LIFE_REGION, 60, self.LIFE_COLOR):
                    self._press_key('F12')
                    self._press_key('F1')
                    time.sleep(0.05)
                    continue
                    
                elif not self._pixel_matches(self.LIFE_REGION, self.life_threshold, self.LIFE_COLOR):
                    self._press_key('F1')
                    time.sleep(0.1)
                if not self._pixel_matches(self.MANA_REGION, self.mana_threshold, self.MANA_COLOR):
                    self._press_key('F2')

            elif self.profile_name == 'royal_paladin':
                if not self._pixel_matches(self.LIFE_REGION, 60, self.LIFE_COLOR):
                    self._press_key('F1')
                    time.sleep(0.2)
                    self._press_key('F3')
                elif not self._pixel_matches(self.LIFE_REGION, self.life_threshold, self.LIFE_COLOR):
                    self._press_key('F2')
                if not self._pixel_matches(self.MANA_REGION, self.mana_threshold, self.MANA_COLOR):
                    self._press_key('F4')

            time.sleep(0.1)

    def _press_key(self, key):
        pyautogui.press(key)
        print(f"[KEY] {key}")

    def calculate_width(self, percent):
        return int(self.LIFE_REGION[2] * percent / 100)

    def _pixel_matches(self, region, percent, color, tolerance=10):
        result_percent = self.calculate_width(percent)
        x = region[0] + result_percent
        y = region[1] + region[3]
        pixel_color = win32gui.GetPixel(win32gui.GetDC(0), x, y)
        return self._color_match(pixel_color, self.rgb_to_bgr(color), tolerance)

    def _color_match(self, pixel, expected_bgr, tolerance):
        r1 = pixel & 0xff
        g1 = (pixel >> 8) & 0xff
        b1 = (pixel >> 16) & 0xff
        r2 = expected_bgr & 0xff
        g2 = (expected_bgr >> 8) & 0xff
        b2 = (expected_bgr >> 16) & 0xff
        return all(abs(a - b) <= tolerance for a, b in zip((r1, g1, b1), (r2, g2, b2)))

    def rgb_to_bgr(self, color):
        r, g, b = color
        return b << 16 | g << 8 | r
