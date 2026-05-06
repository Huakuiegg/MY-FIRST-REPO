import tkinter as tk
from tkinter import ttk

from config import get_default_params
from src.core.models import SelectionParams
from src.utils.helpers import safe_int


class InputPanel:
    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent
        defaults = get_default_params()
        self.frame = ttk.LabelFrame(parent, text="Value Input", padding=10)
        self.entries: dict[str, ttk.Entry] = {}
        self.mode_var = tk.StringVar(value="random")
        self.rule_threshold_var = tk.StringVar(value="1")
        self.manual_text = tk.Text(self.frame, height=5, width=34)
        self.generate_button: ttk.Button | None = None
        self.run_button: ttk.Button | None = None
        self.save_button: ttk.Button | None = None
        self.clear_button: ttk.Button | None = None
        self._defaults = defaults
        self.build()

    def build(self) -> None:
        constraints = {
            "m": "45 ≤ m ≤ 54",
            "n": "7 ≤ n ≤ 25, n ≤ m",
            "k": "4 ≤ k ≤ 7, k ≤ n",
            "j": "s ≤ j ≤ k",
            "s": "3 ≤ s ≤ 7",
        }
        fields = ["m", "n", "k", "j", "s"]
        for index, field in enumerate(fields):
            ttk.Label(self.frame, text=field.upper()).grid(row=index, column=0, sticky="w", padx=4, pady=3)
            entry = ttk.Entry(self.frame, width=8)
            entry.insert(0, str(self._defaults[field]))
            entry.grid(row=index, column=1, sticky="ew", padx=4, pady=3)
            ttk.Label(self.frame, text=constraints[field], foreground="#666666").grid(row=index, column=2, sticky="w", padx=4, pady=3)
            self.entries[field] = entry

        ttk.Label(self.frame, text="Choose n").grid(row=5, column=0, sticky="w", padx=4, pady=4)
        mode_frame = ttk.Frame(self.frame)
        mode_frame.grid(row=5, column=1, columnspan=2, sticky="w", padx=4, pady=4)
        ttk.Radiobutton(mode_frame, text="Random n", variable=self.mode_var, value="random").pack(side="left", padx=(0, 8))
        ttk.Radiobutton(mode_frame, text="Input n", variable=self.mode_var, value="manual").pack(side="left")

        ttk.Label(self.frame, text="Rule").grid(row=6, column=0, sticky="w", padx=4, pady=4)
        rule_frame = ttk.Frame(self.frame)
        rule_frame.grid(row=6, column=1, columnspan=2, sticky="w", padx=4, pady=4)
        ttk.Label(rule_frame, text="at least").pack(side="left")
        ttk.Entry(rule_frame, textvariable=self.rule_threshold_var, width=5).pack(side="left", padx=4)
        ttk.Label(rule_frame, text="S sample").pack(side="left")

        ttk.Label(self.frame, text="User Input").grid(row=7, column=0, sticky="nw", padx=4, pady=4)
        self.manual_text.grid(row=7, column=1, columnspan=2, sticky="nsew", padx=4, pady=4)

        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=8, column=0, columnspan=3, sticky="ew", padx=4, pady=8)
        self.generate_button = ttk.Button(button_frame, text="Random n")
        self.generate_button.pack(side="left", padx=4)
        self.run_button = ttk.Button(button_frame, text="Execute")
        self.run_button.pack(side="left", padx=4)
        self.save_button = ttk.Button(button_frame, text="Store")
        self.save_button.pack(side="left", padx=4)
        self.clear_button = ttk.Button(button_frame, text="Clear")
        self.clear_button.pack(side="left", padx=4)

        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(7, weight=1)

    def get_params(self) -> SelectionParams:
        return SelectionParams(
            m=int(self.entries["m"].get()),
            n=int(self.entries["n"].get()),
            k=int(self.entries["k"].get()),
            j=int(self.entries["j"].get()),
            s=int(self.entries["s"].get()),
        )

    def get_mode(self) -> str:
        return self.mode_var.get()

    def set_mode(self, mode: str) -> None:
        self.mode_var.set(mode)

    def get_rule_name(self) -> str:
        params = self.get_params()
        threshold = self.get_rule_threshold()
        if params.j == params.s:
            return "all"
        if threshold <= 1:
            return "at_least_one"
        return "at_least_n"

    def get_rule_threshold(self) -> int:
        return max(1, safe_int(self.rule_threshold_var.get(), 1) or 1)

    def get_manual_samples_text(self) -> str:
        return self.manual_text.get("1.0", "end").strip()

    def set_samples_text(self, text: str) -> None:
        self.manual_text.delete("1.0", "end")
        self.manual_text.insert("1.0", text)

    def clear(self) -> None:
        self.manual_text.delete("1.0", "end")

    def set_running(self, is_running: bool) -> None:
        state = "disabled" if is_running else "normal"
        for button in [self.generate_button, self.run_button, self.save_button, self.clear_button]:
            if button:
                button.configure(state=state)

    def bind_generate_samples(self, callback) -> None:
        if self.generate_button:
            self.generate_button.configure(command=callback)

    def bind_run(self, callback) -> None:
        if self.run_button:
            self.run_button.configure(command=callback)

    def bind_save(self, callback) -> None:
        if self.save_button:
            self.save_button.configure(command=callback)

    def bind_clear(self, callback) -> None:
        if self.clear_button:
            self.clear_button.configure(command=callback)
