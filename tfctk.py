import tkinter as tk
from collections import deque
from pathlib import Path
from tkinter import Menu, messagebox, ttk

from PIL import Image, ImageTk

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# (значение действия, подпись, файл иконки, колонка, строка)
ACTIONS = [
    (-3, "Лёгкий удар", "light_hit.png", 0, 2),
    (-6, "Средний удар", "medium_hit.png", 1, 2),
    (-9, "Тяжёлый удар", "heavy_hit.png", 0, 3),
    (-15, "Волочение", "draw.png", 1, 3),
    (2, "Пробивание", "punch.png", 3, 2),
    (7, "Сгибание", "bend.png", 4, 2),
    (13, "Осаживание", "upset.png", 3, 3),
    (16, "Усадка", "shrink.png", 4, 3),
]

ACTION_BY_VALUE = {value: name for value, name, _, _, _ in ACTIONS}
ICON_PATH_BY_VALUE = {
    value: ASSETS_DIR / filename for value, _, filename, _, _ in ACTIONS
}

BUTTON_ICON_SIZE = 64
RESULT_ICON_SIZE = 30

button_icons = {}
result_icons = {}

pbl = [0, 0, 0]
pbl2 = []
queued_images = []


def load_icon(value, size):
    image = Image.open(ICON_PATH_BY_VALUE[value])
    image = image.resize((size, size), Image.LANCZOS)
    return ImageTk.PhotoImage(image)


def find_path(target):
    """Кратчайшая последовательность действий, дающая в сумме target."""
    if target == 0:
        return []

    # Оптимальный путь не уходит далеко от цели: ограничиваем область поиска.
    limit = abs(target) + 64
    low, high = -limit, limit
    previous = {0: None}
    queue = deque([0])

    while queue:
        current = queue.popleft()
        for value in ACTION_BY_VALUE:
            nxt = current + value
            if nxt in previous or not low <= nxt <= high:
                continue
            previous[nxt] = (current, value)
            if nxt == target:
                queue.clear()
                break
            queue.append(nxt)

    if target not in previous:
        return None

    path = []
    node = target
    while previous[node] is not None:
        node, value = previous[node]
        path.append(value)
    path.reverse()
    return path


def update_pbl(value):
    global pbl
    pbl = [value] + pbl[:2]
    update_label()
    add_image_to_queue(value)


def update_pbl2(value):
    pbl2.append(value)
    update_label2()
    add_image_to_queue(value)


def update_label():
    pressedL.config(text=pbl)


def update_label2():
    pressedL2.config(text=pbl2)


def add_image_to_queue(value):
    queued_images.append(result_icons[value])
    display_queue()


def display_queue():
    for widget in queue_frame.winfo_children():
        widget.destroy()
    for img in queued_images:
        lbl = tk.Label(queue_frame, image=img)
        lbl.image = img
        lbl.pack(side=tk.LEFT, padx=5)


def reset_queue():
    global queued_images
    queued_images = []
    display_queue()
    reset_path()
    clear_result()


def reset_path():
    global pbl, pbl2
    pbl = [0, 0, 0]
    pbl2 = []
    update_label()
    update_label2()


def reset_pbl2():
    global pbl2
    pbl2 = []
    pressedL2.config(text="")


def clear_result():
    for widget in result_frame.winfo_children():
        widget.destroy()
    resultP.config(text="")


def calce():
    coord = sum(pbl2)
    pressedL2.config(text=f"Конечная координата: {coord}")


def calculatepath():
    try:
        target = int(cente.get())
    except ValueError:
        resultP.config(text="Ошибка! Введите конечную координату в поле ввода.")
        return

    a, b, c = pbl[2], pbl[1], pbl[0]
    remainder = target - (a + b + c)
    path = find_path(remainder)
    if path is None:
        resultP.config(text="Не удалось рассчитать путь.")
        return

    newlst = path + [a, b, c]

    resultP.config(text="")
    for widget in result_frame.winfo_children():
        widget.destroy()

    result_frame.columnconfigure(0, weight=1)
    result_frame.rowconfigure(0, weight=1)

    container = tk.Frame(result_frame)
    container.grid(row=0, column=0, sticky="nsew")
    container.columnconfigure(0, weight=1)

    for index, action in enumerate(newlst):
        action_name = ACTION_BY_VALUE[action]
        img = result_icons[action]
        lbl = tk.Label(
            container, text=action_name, compound=tk.TOP, image=img
        )
        lbl.image = img
        lbl.grid(row=0, column=index, padx=5, sticky="w")


def about():
    messagebox.showinfo(
        title="О программе",
        message="""Это программа-помощник для мини-игры с наковальней в TerraFirmaCraft — моде для Minecraft от Robert "Bioxx" Anthony, Amanda "Kittychanley" Halek и других.

Автор программы: dzhemvrot (доработал Taeko-ar)
Версия программы: 2.0
Программа распространяется по лицензии GPL-3.0""",
    )


def quitting():
    root.destroy()


def build_action_buttons(parent, handler):
    for value, _name, _filename, column, row in ACTIONS:
        ttk.Button(
            parent,
            image=button_icons[value],
            command=lambda v=value: handler(v),
        ).grid(column=column, row=row, padx=10, pady=10)


root = tk.Tk()
root.title("Помощник наковальни TFC")
root.minsize(560, 420)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

button_icons = {
    value: load_icon(value, BUTTON_ICON_SIZE) for value in ACTION_BY_VALUE
}
result_icons = {
    value: load_icon(value, RESULT_ICON_SIZE) for value in ACTION_BY_VALUE
}

tabControl = ttk.Notebook(root)
tabControl.grid(row=0, column=0, sticky="nsew")

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text="Путь")
tabControl.add(tab2, text="Конец")

tab1.rowconfigure(0, weight=1)
tab1.columnconfigure(0, weight=1)
tab2.rowconfigure(0, weight=1)
tab2.columnconfigure(0, weight=1)

menubar = Menu(root)
root.config(menu=menubar)

file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Выход", command=quitting)
menubar.add_cascade(label="Файл", menu=file_menu)
menubar.add_command(label="О программе", command=about)

ttk.Label(tab1, text="Расчёт пути").grid(column=2, row=0, padx=30, pady=0)
pressedL = ttk.Label(tab1, text=pbl)
pressedL.grid(column=2, row=1, padx=0, pady=0)

queue_frame = ttk.Frame(tab1)
queue_frame.grid(column=2, row=6, padx=10, pady=10, sticky="nsew")

result_frame = ttk.Frame(tab1)
result_frame.grid(column=2, row=8, padx=10, pady=10, sticky="nsew")

for i in range(5):
    tab1.columnconfigure(i, weight=1)
    tab1.rowconfigure(i, weight=1)

build_action_buttons(tab1, update_pbl)

cente = ttk.Entry(tab1)
cente.grid(column=2, row=3)
ttk.Button(tab1, text="Рассчитать", command=calculatepath).grid(
    column=2, row=4, padx=10, pady=10
)
ttk.Button(tab1, text="Сбросить очередь", command=reset_queue).grid(
    column=2, row=5, padx=10, pady=10
)

resultP = ttk.Label(tab1, text="")
resultP.grid(column=2, row=7, padx=0, pady=0)

# Вкладка 2 (Конец)
ttk.Label(tab2, text="Расчёт конечной координаты").grid(
    column=2, row=0, padx=30, pady=0
)
pressedL2 = ttk.Label(tab2, text="")
pressedL2.grid(column=2, row=1, padx=0, pady=0)

tab2.columnconfigure(0, weight=1)
tab2.rowconfigure(0, weight=1)
tab2.columnconfigure(4, weight=1)

build_action_buttons(tab2, update_pbl2)

ttk.Button(tab2, text="Сброс", command=reset_pbl2).grid(
    column=2, row=5, padx=10, pady=10
)
ttk.Button(tab2, text="Рассчитать", command=calce).grid(
    column=2, row=4, padx=10, pady=10
)

root.mainloop()
