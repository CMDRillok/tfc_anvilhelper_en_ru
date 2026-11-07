"""Helper for the TerraFirmaCraft anvil minigame.

The player strikes the workpiece, which moves it along a 1D axis.  This tool
either (a) calculates the strikes needed to finish at a given coordinate, or
(b) sums up a sequence of strikes to show the resulting coordinate.

The anvil has a limited set of moves:

    positive (right):  +2, +7, +13, +16
    negative (left):   -3, -6, -9, -15
"""

import tkinter as tk
from collections import deque
from tkinter import Menu, messagebox, ttk

# Move -> name shown to the player.
MOVE_NAMES = {
    16: "Усадить",
    13: "Обжать",
    7: "Изогнуть",
    2: "Штамповать",
    -3: "Слабо ударить",
    -6: "Ударить",
    -9: "Сильно ударить",
    -15: "Протянуть",
}

# Ordered so that stronger strikes are preferred when several shortest paths
# exist.
MOVES = (16, 13, 7, 2, -3, -6, -9, -15)

MAX_TARGET = 1000  # guard against absurd input / huge search space


def find_strikes(target):
    """Return the shortest list of strikes that moves from 0 to ``target``.

    Uses breadth-first search, so the result always contains the minimum
    possible number of strikes.  Returns ``None`` if the target is
    unreachable (it never is for integer targets, but the check is cheap).
    """
    if target == 0:
        return []

    max_step = max(abs(m) for m in MOVES)
    low = min(0, target) - max_step
    high = max(0, target) + max_step

    # prev[position] = (previous_position, move_used)
    prev = {0: None}
    queue = deque([0])

    while queue:
        position = queue.popleft()
        if position == target:
            path = []
            while prev[position] is not None:
                position, move = prev[position]
                path.append(move)
            path.reverse()
            return path

        for move in MOVES:
            nxt = position + move
            if low <= nxt <= high and nxt not in prev:
                prev[nxt] = (position, move)
                queue.append(nxt)

    return None


def format_moves(moves):
    """Render a list of move values as human readable names."""
    return " → ".join(MOVE_NAMES.get(move, str(move)) for move in moves)


class ForgeApp:
    def __init__(self, root):
        self.root = root

        # Last three strikes on the "Path" tab, most recent first.
        self.recent = [0, 0, 0]
        # Sequence of strikes on the "End" tab.
        self.strikes = []

        self.notebook = ttk.Notebook(root)
        path_tab = ttk.Frame(self.notebook)
        end_tab = ttk.Frame(self.notebook)
        self.notebook.add(path_tab, text="Path")
        self.notebook.add(end_tab, text="End")
        self.notebook.pack(expand=1, fill="both")

        self._build_menu()
        self._build_path_tab(path_tab)
        self._build_end_tab(end_tab)

    # ------------------------------------------------------------------ UI --
    def _build_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_command(label="About", command=self.about)

    @staticmethod
    def _add_move_buttons(tab, callback):
        """Create the 8 strike buttons in the shared 2x2+2x2 layout."""
        layout = (
            (-3, 0, 2),
            (-6, 1, 2),
            (-9, 0, 3),
            (-15, 1, 3),
            (2, 3, 2),
            (7, 4, 2),
            (13, 3, 3),
            (16, 4, 3),
        )
        for move, column, row in layout:
            ttk.Button(
                tab, text=MOVE_NAMES[move], command=lambda m=move: callback(m)
            ).grid(column=column, row=row, padx=10, pady=10)

    def _build_path_tab(self, tab):
        ttk.Label(tab, text="Calculate the path").grid(
            column=2, row=0, padx=30
        )
        self.recent_label = ttk.Label(tab, text=self._recent_text())
        self.recent_label.grid(column=2, row=1)

        self._add_move_buttons(tab, self.record_recent)

        self.target_entry = ttk.Entry(tab)
        self.target_entry.grid(column=2, row=3)
        self.target_entry.bind("<Return>", lambda _event: self.calculate_path())

        ttk.Button(tab, text="Высчитать", command=self.calculate_path).grid(
            column=2, row=4, padx=10, pady=10
        )

        self.result_label = ttk.Label(tab, text="", wraplength=600)
        self.result_label.grid(column=2, row=5)

    def _build_end_tab(self, tab):
        ttk.Label(tab, text="Calculate the end coordinate").grid(
            column=2, row=0, padx=30
        )
        self.strikes_label = ttk.Label(tab, text="", wraplength=600)
        self.strikes_label.grid(column=2, row=1)

        self._add_move_buttons(tab, self.record_strike)

        ttk.Button(tab, text="Calculate", command=self.calculate_end).grid(
            column=2, row=4, padx=10, pady=10
        )
        ttk.Button(tab, text="Reset", command=self.reset_strikes).grid(
            column=2, row=5, padx=10, pady=10
        )

        self.end_label = ttk.Label(tab, text="")
        self.end_label.grid(column=2, row=6)

    # -------------------------------------------------------------- actions --
    def _recent_text(self):
        return f"Последние удары: {self.recent}"

    def record_recent(self, move):
        """Shift the new strike into the last-three history."""
        self.recent = [move, self.recent[0], self.recent[1]]
        self.recent_label.config(text=self._recent_text())

    def record_strike(self, move):
        self.strikes.append(move)
        self.strikes_label.config(text=format_moves(self.strikes))

    def reset_strikes(self):
        self.strikes = []
        self.strikes_label.config(text="")
        self.end_label.config(text="")

    def calculate_end(self):
        if not self.strikes:
            self.end_label.config(text="Сначала нажмите хотя бы один удар.")
            return
        coordinate = sum(self.strikes)
        self.end_label.config(
            text=f"The end coordinate is {coordinate}"
        )

    def calculate_path(self):
        raw = self.target_entry.get().strip()
        try:
            target = int(raw)
        except ValueError:
            self.result_label.config(
                text="Ошибка! Введите конечную координату целым числом."
            )
            return

        if abs(target) > MAX_TARGET:
            self.result_label.config(
                text=f"Слишком большая координата (максимум {MAX_TARGET})."
            )
            return

        # The last three strikes are already known; find the rest.
        remaining = target - sum(self.recent)

        path = find_strikes(remaining)
        if path is None:
            self.result_label.config(
                text="Ошибка! Такой координаты достичь нельзя."
            )
            return

        # Full sequence in chronological order: the three known strikes
        # (oldest first) followed by the newly calculated ones.
        sequence = [m for m in reversed(self.recent) if m != 0] + path
        text = format_moves(sequence)
        if path:
            text = f"{text}\n(всего ударов: {len(sequence)})"
        self.result_label.config(text=text)

    def about(self):
        messagebox.showinfo(
            title="About",
            message=(
                "This is a program to help with anvil minigame in "
                'TerraFirmaCraft, a Minecraft mod made by Robert "Bioxx" '
                'Anthony, Amanda "Kittychanley" Halek, and others.\n\n'
                "Program author: dzhemvrot\n"
                "Program version: 2.0\n"
                "Program redistributed using GPL-3.0 license"
            ),
        )


def main():
    root = tk.Tk()
    root.title("TFC Anvil Calculator")

    ForgeApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
