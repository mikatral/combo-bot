from classes.combat_manager import CombatManager
from classes.item_manager import ItemManager
import pynput
import subprocess
import keyboard

# Escolha de classe antes de iniciar
def escolher_classe():
    print("Selecione sua classe:")
    print("[1] Elite Knight")
    print("[2] Royal Paladin")
    while True:
        escolha = input("Digite 1 ou 2: ").strip()
        if escolha == "1":
            return "elite_knight"
        elif escolha == "2":
            return "royal_paladin"
        else:
            print("Opção inválida. Tente novamente.")

# Carregar perfil selecionado
perfil_escolhido = escolher_classe()

# Instâncias dos controladores
tasks = {
    "combat": CombatManager(profile_name=perfil_escolhido),
    "items": ItemManager()
}

def key_code(key):
    if key == pynput.keyboard.Key.delete:
        print("Encerrando o bot...")
        tasks["combat"].stop_all()
        return False

    if hasattr(key, 'char'):
        match key.char:
            case 'f':
                tasks["combat"].toggle_combo()
                if tasks["combat"].combo_running:
                    tasks["items"].use_offensive_sequence()
                else:
                    tasks["items"].use_defensive_sequence()
            case 'h':
                tasks["combat"].toggle_heal()
            case '':
                print("Coletando loot...")

def calibrar_regioes():
    print("[CALIBRAÇÃO] Iniciando calibrador de região e cor...")
    subprocess.run(['python', 'config_calibrator.py'])
    print("[CALIBRAÇÃO] Finalizada. Arquivo config.json atualizado.")
    try:
        tasks["combat"] = CombatManager(profile_name=perfil_escolhido)
        print("[OK] CombatManager recarregado com nova configuração.")
    except Exception as e:
        print(f"[ERRO] Após calibração: {e}")

keyboard.add_hotkey('end', calibrar_regioes)

print(f"[BOT] Classe selecionada: {perfil_escolhido.replace('_', ' ').title()}")
print("Bot iniciado. Use: f=combo, h=cura, End=calibrar, Delete=encerra")

# Listener de teclado (em segundo plano)
listener = pynput.keyboard.Listener(on_press=key_code)
listener.start()

# Abrir HUD com interface gráfica
if __name__ == "__main__":
    import tkinter as tk
    from hud import BotHUD

    root = tk.Tk()
    app = BotHUD(root, tasks["combat"])
    root.mainloop()
