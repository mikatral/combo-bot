import threading
import time
import json
import os
import win32gui

class SupliesManager:
    def __init__(self, config_path='config.json', profile_name='elite_knight', hotkey_queue=None):
        self.event = threading.Event()
        self.thread = None
        self.profile_name = profile_name
        self.hotkey_queue = hotkey_queue
        self.WIDTH = 89

        self.load_config(config_path)

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
            print(f"[ERRO] Falha ao carregar o config: {e}")
            raise

    def start(self):
        if self.thread and self.thread.is_alive():
            print("SUPORTES já estão ativos.")
            return
        self.event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("SUPORTES ATIVOS")

    def stop(self):
        if not self.thread or not self.thread.is_alive():
            print("SUPORTES já estão desativados.")
            return
        self.event.set()
        self.thread.join()
        print("SUPORTES DESATIVADOS")

    def toggle(self):
        if not self.thread or not self.thread.is_alive():
            self.start()
        else:
            self.stop()

    def _run(self):
        while not self.event.is_set():
            if self.profile_name == 'elite_knight':
                self._run_elite_knight()
            elif self.profile_name == 'royal_paladin':
                self._run_royal_paladin()
            time.sleep(0.5)

    def _run_elite_knight(self):
        if not self.pixel_matches_color(self.LIFE_REGION, 60, self.LIFE_COLOR):
            self._enqueue_key('F12')
            time.sleep(0.1)
            self._enqueue_key('F1')
        else:
            if not self.pixel_matches_color(self.LIFE_REGION, 80, self.LIFE_COLOR):
                self._enqueue_key('F1')
                time.sleep(0.1)
            if not self.pixel_matches_color(self.MANA_REGION, 80, self.MANA_COLOR):
                self._enqueue_key('F2')

    def _run_royal_paladin(self):
        if not self.pixel_matches_color(self.LIFE_REGION, 60, self.LIFE_COLOR):
            self._enqueue_key('F1')
            time.sleep(0.2)
            self._enqueue_key('F3')
        else:
            if not self.pixel_matches_color(self.LIFE_REGION, 80, self.LIFE_COLOR):
                self._enqueue_key('F2')
            if not self.pixel_matches_color(self.MANA_REGION, 80, self.MANA_COLOR):
                self._enqueue_key('F4')

    def calculate_width(self, percent):
        return int(self.LIFE_REGION[2] * percent / 100)

    def pixel_matches_color(self, region, percent, color, tolerance=10):
        result_percent = self.calculate_width(percent)
        x = region[0] + result_percent
        y = region[1] + region[3]
        pixel_color = win32gui.GetPixel(win32gui.GetDC(0), x, y)
        return self.color_matches_with_tolerance(pixel_color, self.rgb_to_bgr(color), tolerance)

    def color_matches_with_tolerance(self, pixel, expected_bgr, tolerance):
        r1 = pixel & 0xff
        g1 = (pixel >> 8) & 0xff
        b1 = (pixel >> 16) & 0xff

        r2 = expected_bgr & 0xff
        g2 = (expected_bgr >> 8) & 0xff
        b2 = (expected_bgr >> 16) & 0xff

        return all(abs(a - b) <= tolerance for a, b in zip((r1, g1, b1), (r2, g2, b2)))

    def _enqueue_key(self, key):
        try:
            if self.hotkey_queue:
                self.hotkey_queue.put(key)
                print(f"[SUPPORT] Enfileirado: {key}")
            else:
                print("[ERRO] hotkey_queue não está configurada.")
        except Exception as e:
            print(f"[ERRO] ao enfileirar tecla {key}: {e}")

    def rgb_to_bgr(self, color):
        r, g, b = color
        return b << 16 | g << 8 | r
