import tkinter as tk
from tkinter import Menu, messagebox, ttk

from PIL import Image, ImageTk

pbl = [0, 0, 0]
pbl2 = []
lstp = [2, 7, 13, 16]
lstn = [-3, -6, -9, -15]
newlst = []
queued_images = []

images = {
    "Лёгкий удар": "assets/light_hit.png",
    "Средний удар": "assets/medium_hit.png",
    "Тяжёлый удар": "assets/heavy_hit.png",
    "Волочение": "assets/draw.png",
    "Пробивание": "assets/punch.png",
    "Сгибание": "assets/bend.png",
    "Осаживание": "assets/upset.png",
    "Усадка": "assets/shrink.png",
}


def closest(lst, K):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]


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
    action_name = next(
        (name for name, val in images.items() if val == value), None
    )
    if action_name and action_name in images:
        img = ImageTk.PhotoImage(
            Image.open(images[action_name]).resize((30, 30))
        )
        queued_images.append(img)
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


def clear_result():
    for widget in result_frame.winfo_children():
        widget.destroy()


def calce():
    coord = sum(pbl2)
    pressedL2.config(text=f"Конечная координата: {coord}")


def calculatepath():
    newlst = []
    a = pbl[2]
    b = pbl[1]
    c = pbl[0]
    cn = cente.get()
    try:
        cn = int(cn)
        bf = ((cn - a) - b) - c
        fs = 0
    except ValueError:
        resultP.config(text="Ошибка! Введите конечную координату в поле ввода.")
        return

    while fs != bf:
        x = bf - fs
        if x > 0:
            dif = closest(lstp, x)
            fs += dif
            newlst.append(dif)
        if x < 0:
            dif = closest(lstn, x)
            fs += dif
            newlst.append(dif)

    newlst.append(c)
    newlst.append(b)
    newlst.append(a)

    for widget in result_frame.winfo_children():
        widget.destroy()

    result_frame.columnconfigure(0, weight=1)
    result_frame.rowconfigure(0, weight=1)

    container = tk.Frame(result_frame)
    container.grid(row=0, column=0, sticky="nsew")
    container.columnconfigure(0, weight=1)

    for index, action in enumerate(newlst):
        action_name = None
        if action == 2:
            action_name = "Пробивание"
        elif action == 7:
            action_name = "Сгибание"
        elif action == 13:
            action_name = "Осаживание"
        elif action == 16:
            action_name = "Усадка"
        elif action == -3:
            action_name = "Лёгкий удар"
        elif action == -6:
            action_name = "Средний удар"
        elif action == -9:
            action_name = "Тяжёлый удар"
        elif action == -15:
            action_name = "Волочение"

        if action_name in images:
            img = ImageTk.PhotoImage(
                Image.open(images[action_name]).resize((30, 30))
            )
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


root = tk.Tk()
root.title("Помощник наковальни TFC")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

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

ttk.Button(tab1, text="Лёгкий удар", command=lambda: update_pbl(-3)).grid(
    column=0, row=2, padx=10, pady=10
)
ttk.Button(tab1, text="Средний удар", command=lambda: update_pbl(-6)).grid(
    column=1, row=2, padx=10, pady=10
)
ttk.Button(tab1, text="Тяжёлый удар", command=lambda: update_pbl(-9)).grid(
    column=0, row=3, padx=10, pady=10
)
ttk.Button(tab1, text="Волочение", command=lambda: update_pbl(-15)).grid(
    column=1, row=3, padx=10, pady=10
)
ttk.Button(tab1, text="Пробивание", command=lambda: update_pbl(2)).grid(
    column=3, row=2, padx=10, pady=10
)
ttk.Button(tab1, text="Сгибание", command=lambda: update_pbl(7)).grid(
    column=4, row=2, padx=10, pady=10
)
ttk.Button(tab1, text="Осаживание", command=lambda: update_pbl(13)).grid(
    column=3, row=3, padx=10, pady=10
)
ttk.Button(tab1, text="Усадка", command=lambda: update_pbl(16)).grid(
    column=4, row=3, padx=10, pady=10
)

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

ttk.Button(tab2, text="Лёгкий удар", command=lambda: update_pbl2(-3)).grid(
    column=0, row=2, padx=10, pady=10
)
ttk.Button(tab2, text="Средний удар", command=lambda: update_pbl2(-6)).grid(
    column=1, row=2, padx=10, pady=10
)
ttk.Button(tab2, text="Тяжёлый удар", command=lambda: update_pbl2(-9)).grid(
    column=0, row=3, padx=10, pady=10
)
ttk.Button(tab2, text="Волочение", command=lambda: update_pbl2(-15)).grid(
    column=1, row=3, padx=10, pady=10
)
ttk.Button(tab2, text="Пробивание", command=lambda: update_pbl2(2)).grid(
    column=3, row=2, padx=10, pady=10
)
ttk.Button(tab2, text="Сгибание", command=lambda: update_pbl2(7)).grid(
    column=4, row=2, padx=10, pady=10
)
ttk.Button(tab2, text="Осаживание", command=lambda: update_pbl2(13)).grid(
    column=3, row=3, padx=10, pady=10
)
ttk.Button(tab2, text="Усадка", command=lambda: update_pbl2(16)).grid(
    column=4, row=3, padx=10, pady=10
)

resetB = ttk.Button(tab2, text="Сброс", command=lambda: reset_path()).grid(
    column=2, row=5, padx=10, pady=10
)
calceB = ttk.Button(tab2, text="Рассчитать", command=calce).grid(
    column=2, row=4, padx=10, pady=10
)

root.mainloop()
