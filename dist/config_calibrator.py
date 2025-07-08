import tkinter as tk
from PIL import ImageGrab, Image, ImageDraw, ImageTk
import pyautogui
import keyboard
import json

x_start, y_start, x_end, y_end = 0, 0, 0, 0
drawing = False
capture_result = None

def on_move(event, canvas):
    global x_end, y_end, drawing

    if drawing:
        x_end, y_end = event.x_root, event.y_root
        draw_rectangle(canvas)

def draw_rectangle(canvas):
    screen_captured = ImageGrab.grab()
    mask = Image.new('L', screen_captured.size, 50)
    draw = ImageDraw.Draw(mask)
    xmin, ymin = min(x_start, x_end), min(y_start, y_end)
    xmax, ymax = max(x_start, x_end), max(y_start, y_end)
    draw.rectangle([xmin, ymin, xmax, ymax], fill=255)
    alpha = Image.new('L', screen_captured.size, 100)
    alpha.paste(mask, (0, 0), mask=mask)
    img = Image.composite(screen_captured, Image.new('RGB', screen_captured.size, 'white'), alpha)
    img_tk = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
    canvas.img_tk = img_tk

def on_click(event):
    global x_start, y_start, drawing
    x_start, y_start = event.x_root, event.y_root
    drawing = True

def finalizar_programa(root, filename):
    global x_start, y_start, x_end, y_end, capture_result
    x1, y1 = min(x_start, x_end), min(y_start, y_end)
    x2, y2 = max(x_start, x_end), max(y_start, y_end)
    width = x2 - x1
    raw_height = y2 - y1
    height = max(1, raw_height // 2)  # Reduzido para capturar o centro vertical da barra
    print(f'Left: {x1}, Top: {y1}, Width: {width}, Height: {height}')
    
    root.withdraw()
    img = pyautogui.screenshot(region=(x1, y1, width, height))
    if filename:
        img.save(filename)
    else:
        img.save('oiaaaa.png')
    root.deiconify()
    capture_result = (x1, y1, width, height)
    root.destroy()
    return capture_result

def on_release(_, root, filename):
    global drawing
    drawing = False
    return finalizar_programa(root, filename)

def start_capture(filename=None):
    global capture_result
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    root.attributes('-alpha', 0.5)

    canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), highlightthickness=0)
    canvas.pack()

    canvas.bind("<B1-Motion>", lambda event: on_move(event, canvas))
    canvas.bind("<ButtonPress-1>", on_click)
    canvas.bind("<ButtonRelease-1>", lambda _: on_release(_, root, filename))
    root.mainloop()
    return capture_result

if __name__ == "__main__":
    print("[CAPTURA] Selecione a barra de VIDA")
    life = start_capture()
    print("[CAPTURA] Selecione a barra de MANA")
    mana = start_capture()

    # Captura a cor da esquerda (10%) da barra
    def get_color(region):
        x = region[0] + int(region[2] * 0.1)
        y = region[1] + region[3]  # Mantém como está: y = top + height
        return pyautogui.pixel(x, y)

    data = {
        "LIFE_REGION": list(life),
        "LIFE_COLOR": list(get_color(life)),
        "MANA_REGION": list(mana),
        "MANA_COLOR": list(get_color(mana))
    }

    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

    print("[OK] Arquivo 'config.json' atualizado com sucesso.")
