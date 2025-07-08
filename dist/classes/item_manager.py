import win32api
import win32con
import time

class ItemManager:
    def __init__(self):
        self.OFFENSIVE_SEQUENCE = ['F10']
        self.DEFENSIVE_SEQUENCE = ['F10']
        self.delay_between_keys = 0.1

    def _press_key(self, key):
        vk_codes = {
                'F1': 0x70,
                'F2': 0x71,
                'F3': 0x72,
                'F4': 0x73,
                'F5': 0x74,
                'F6': 0x75,
                'F7': 0x76,
                'F8': 0x77,
                'F9': 0x78,
                'F10': 0x79,
                'F11': 0x7A,
                'F12': 0x7B,
                'space': 0x20
        }
        if key in vk_codes:
            vk = vk_codes[key]
            win32api.keybd_event(vk, 0, 0, 0)
            time.sleep(0.2)
            win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            print(f"[WARN] Tecla '{key}' sem suporte no win32api")

    def use_offensive_sequence(self):
        print("Ativando itens ofensivos...")
        for key in self.OFFENSIVE_SEQUENCE:
            self._press_key(key)
            time.sleep(self.delay_between_keys)

    def use_defensive_sequence(self):
        print("Ativando itens defensivos...")
        for key in self.DEFENSIVE_SEQUENCE:
            self._press_key(key)
            time.sleep(self.delay_between_keys)
