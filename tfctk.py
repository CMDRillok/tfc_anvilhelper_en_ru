import os
import tkinter as tk
from collections import deque
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageTk

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# (значение действия, ключ перевода, файл иконки, колонка, строка)
ACTIONS = [
    (-3, "action_light", "light_hit.png", 0, 2),
    (-6, "action_medium", "medium_hit.png", 1, 2),
    (-9, "action_heavy", "heavy_hit.png", 0, 3),
    (-15, "action_draw", "draw.png", 1, 3),
    (2, "action_punch", "punch.png", 3, 2),
    (7, "action_bend", "bend.png", 4, 2),
    (13, "action_upset", "upset.png", 3, 3),
    (16, "action_shrink", "shrink.png", 4, 3),
]

ACTION_KEY_BY_VALUE = {value: key for value, key, _, _, _ in ACTIONS}
ICON_PATH_BY_VALUE = {
    value: ASSETS_DIR / filename for value, _, filename, _, _ in ACTIONS
}

TRANSLATIONS = {
    "en": {
        "title": "TFC Anvil Helper",
        "language": "Language:",
        "tab_path": "Path",
        "tab_end": "End",
        "path_title": "Calculate the path",
        "end_title": "Calculate the end coordinate",
        "calculate": "Calculate",
        "reset_queue": "Reset queue",
        "reset": "Reset",
        "error_invalid": "Error! Enter the end coordinate in the input field.",
        "error_no_path": "Could not calculate the path.",
        "end_coordinate": "End coordinate: {coord}",
        "action_light": "Light Hit",
        "action_medium": "Medium Hit",
        "action_heavy": "Heavy Hit",
        "action_draw": "Draw",
        "action_punch": "Punch",
        "action_bend": "Bend",
        "action_upset": "Upset",
        "action_shrink": "Shrink",
    },
    "ru": {
        "title": "Помощник наковальни TFC",
        "language": "Язык:",
        "tab_path": "Путь",
        "tab_end": "Конец",
        "path_title": "Расчёт пути",
        "end_title": "Расчёт конечной координаты",
        "calculate": "Рассчитать",
        "reset_queue": "Сбросить очередь",
        "reset": "Сброс",
        "error_invalid": "Ошибка! Введите конечную координату в поле ввода.",
        "error_no_path": "Не удалось рассчитать путь.",
        "end_coordinate": "Конечная координата: {coord}",
        "action_light": "Лёгкий удар",
        "action_medium": "Средний удар",
        "action_heavy": "Тяжёлый удар",
        "action_draw": "Волочение",
        "action_punch": "Пробивание",
        "action_bend": "Сгибание",
        "action_upset": "Осаживание",
        "action_shrink": "Усадка",
    },
}

LANGUAGE_NAMES = {"English": "en", "Русский": "ru"}
LANGUAGE_BY_CODE = {code: name for name, code in LANGUAGE_NAMES.items()}

LANG = os.environ.get("TFC_LANG", "en")
if LANG not in TRANSLATIONS:
    LANG = "en"
BUTTON_ICON_SIZE = 44
RESULT_ICON_SIZE = 30

button_icons = {}
result_icons = {}

pbl = [0, 0, 0]
pbl2 = []
queued_images = []
last_result = []
result_message = None
end_result = None


def t(key, **kwargs):
    text = TRANSLATIONS[LANG].get(key, key)
    return text.format(**kwargs) if kwargs else text


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
        for value in ACTION_KEY_BY_VALUE:
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
    global end_result
    pbl2.append(value)
    end_result = None
    update_label2()
    add_image_to_queue(value)


def update_label():
    pressedL.config(text=pbl)


def update_label2():
    if end_result is None:
        pressedL2.config(text=pbl2)
    else:
        pressedL2.config(text=t("end_coordinate", coord=end_result))


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
    global pbl, pbl2, end_result
    pbl = [0, 0, 0]
    pbl2 = []
    end_result = None
    update_label()
    update_label2()


def reset_pbl2():
    global pbl2, end_result
    pbl2 = []
    end_result = None
    update_label2()


def clear_result():
    global last_result, result_message
    last_result = []
    result_message = None
    for widget in result_frame.winfo_children():
        widget.destroy()
    render_result_message()


def render_result_message():
    resultP.config(text=t(result_message) if result_message else "")


def render_result_icons():
    for widget in result_frame.winfo_children():
        widget.destroy()
    if not last_result:
        return

    result_frame.columnconfigure(0, weight=1)
    result_frame.rowconfigure(0, weight=1)

    container = tk.Frame(result_frame)
    container.grid(row=0, column=0, sticky="nsew")
    container.columnconfigure(0, weight=1)

    for index, action in enumerate(last_result):
        img = result_icons[action]
        lbl = tk.Label(
            container, text=t(ACTION_KEY_BY_VALUE[action]), compound=tk.TOP, image=img
        )
        lbl.image = img
        lbl.grid(row=0, column=index, padx=5, sticky="w")


def calce():
    global end_result
    end_result = sum(pbl2)
    update_label2()


def calculatepath():
    global last_result, result_message
    try:
        target = int(cente.get())
    except ValueError:
        result_message = "error_invalid"
        render_result_message()
        return

    a, b, c = pbl[2], pbl[1], pbl[0]
    remainder = target - (a + b + c)
    path = find_path(remainder)
    if path is None:
        result_message = "error_no_path"
        render_result_message()
        return

    last_result = path + [a, b, c]
    result_message = None
    render_result_message()
    render_result_icons()


def build_action_buttons(parent, handler):
    for value, _key, _filename, column, row in ACTIONS:
        ttk.Button(
            parent,
            image=button_icons[value],
            command=lambda v=value: handler(v),
        ).grid(column=column, row=row, padx=6, pady=6)


def apply_language():
    root.title(t("title"))
    tabControl.tab(tab1, text=t("tab_path"))
    tabControl.tab(tab2, text=t("tab_end"))
    language_label.config(text=t("language"))
    path_title.config(text=t("path_title"))
    end_title.config(text=t("end_title"))
    calculate_button.config(text=t("calculate"))
    reset_queue_button.config(text=t("reset_queue"))
    end_calculate_button.config(text=t("calculate"))
    end_reset_button.config(text=t("reset"))
    update_label()
    update_label2()
    render_result_message()
    render_result_icons()


def change_language(_event=None):
    global LANG
    LANG = LANGUAGE_NAMES.get(language_var.get(), "en")
    apply_language()


root = tk.Tk()
root.title(t("title"))
root.minsize(560, 460)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

button_icons = {
    value: load_icon(value, BUTTON_ICON_SIZE) for value in ACTION_KEY_BY_VALUE
}
result_icons = {
    value: load_icon(value, RESULT_ICON_SIZE) for value in ACTION_KEY_BY_VALUE
}

header = ttk.Frame(root)
header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
header.columnconfigure(0, weight=1)

language_label = ttk.Label(header, text=t("language"))
language_label.grid(row=0, column=1, padx=(0, 6))

language_var = tk.StringVar(value=LANGUAGE_BY_CODE[LANG])
language_box = ttk.Combobox(
    header,
    textvariable=language_var,
    values=list(LANGUAGE_NAMES),
    state="readonly",
    width=10,
)
language_box.grid(row=0, column=2, sticky="e")
language_box.bind("<<ComboboxSelected>>", change_language)

tabControl = ttk.Notebook(root)
tabControl.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text=t("tab_path"))
tabControl.add(tab2, text=t("tab_end"))

tab1.rowconfigure(0, weight=1)
tab1.columnconfigure(0, weight=1)
tab2.rowconfigure(0, weight=1)
tab2.columnconfigure(0, weight=1)

path_title = ttk.Label(tab1, text=t("path_title"))
path_title.grid(column=2, row=0, padx=30, pady=0)
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
calculate_button = ttk.Button(tab1, text=t("calculate"), command=calculatepath)
calculate_button.grid(column=2, row=4, padx=10, pady=10)
reset_queue_button = ttk.Button(tab1, text=t("reset_queue"), command=reset_queue)
reset_queue_button.grid(column=2, row=5, padx=10, pady=10)

resultP = ttk.Label(tab1, text="")
resultP.grid(column=2, row=7, padx=0, pady=0)

# Вкладка 2 (Конец)
end_title = ttk.Label(tab2, text=t("end_title"))
end_title.grid(column=2, row=0, padx=30, pady=0)
pressedL2 = ttk.Label(tab2, text="")
pressedL2.grid(column=2, row=1, padx=0, pady=0)

tab2.columnconfigure(0, weight=1)
tab2.rowconfigure(0, weight=1)
tab2.columnconfigure(4, weight=1)

build_action_buttons(tab2, update_pbl2)

end_reset_button = ttk.Button(tab2, text=t("reset"), command=reset_pbl2)
end_reset_button.grid(column=2, row=5, padx=10, pady=10)
end_calculate_button = ttk.Button(tab2, text=t("calculate"), command=calce)
end_calculate_button.grid(column=2, row=4, padx=10, pady=10)

apply_language()
root.mainloop()
