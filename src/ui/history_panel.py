import tkinter as tk
from tkinter import ttk

from src.core.models import RunRecord


class HistoryPanel:
    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent
        self.frame = ttk.LabelFrame(parent, text="Data Base Resource", padding=10)
        self.listbox = tk.Listbox(self.frame, height=10, width=42)
        self.detail_label_var = tk.StringVar(value="")
        self.detail_box = tk.Text(self.frame, height=14, width=42, state="disabled", wrap="none")
        self.run_ids: list[int] = []
        self.display_button: ttk.Button | None = None
        self.reload_button: ttk.Button | None = None
        self.delete_button: ttk.Button | None = None
        self.print_button: ttk.Button | None = None
        self.build()

    def build(self) -> None:
        top_button_frame = ttk.Frame(self.frame)
        top_button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(top_button_frame, text="Data Base Resource", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.delete_button = ttk.Button(top_button_frame, text="Delete")
        self.delete_button.pack(side="right", padx=3)
        self.display_button = ttk.Button(top_button_frame, text="Display")
        self.display_button.pack(side="right", padx=3)

        list_scroll = ttk.Scrollbar(self.frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=list_scroll.set)
        self.listbox.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        list_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 8))

        ttk.Label(self.frame, textvariable=self.detail_label_var, font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 2))
        y_scroll = ttk.Scrollbar(self.frame, orient="vertical", command=self.detail_box.yview)
        x_scroll = ttk.Scrollbar(self.frame, orient="horizontal", command=self.detail_box.xview)
        self.detail_box.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.detail_box.grid(row=3, column=0, sticky="nsew")
        y_scroll.grid(row=3, column=1, sticky="ns")
        x_scroll.grid(row=4, column=0, sticky="ew")

        bottom_button_frame = ttk.Frame(self.frame)
        bottom_button_frame.grid(row=5, column=0, sticky="e", pady=(6, 0))
        self.reload_button = ttk.Button(bottom_button_frame, text="Back")
        self.reload_button.pack(side="left", padx=3)
        self.print_button = ttk.Button(bottom_button_frame, text="Print")
        self.print_button.pack(side="left", padx=3)

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(3, weight=2)

    def format_run_label(self, run: RunRecord) -> str:
        group_count = run.result_count or 0
        params = run.params
        return f"{params.m}-{params.n}-{params.k}-{params.j}-{params.s}-{run.rule_threshold}-{group_count}"

    def load_runs(self, runs: list[RunRecord]) -> None:
        self.clear()
        for run in runs:
            self.run_ids.append(run.id or -1)
            self.listbox.insert("end", self.format_run_label(run))

    def get_selected_run_id(self) -> int | None:
        selection = self.listbox.curselection()
        if not selection:
            return None
        index = selection[0]
        return self.run_ids[index] if 0 <= index < len(self.run_ids) else None

    def set_detail(self, label: str, groups: list[str]) -> None:
        self.detail_label_var.set(label)
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")
        self.detail_box.insert("1.0", "\n".join(groups) if groups else "No stored groups.")
        self.detail_box.configure(state="disabled")

    def clear_detail(self) -> None:
        self.detail_label_var.set("")
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")
        self.detail_box.configure(state="disabled")

    def clear(self) -> None:
        self.run_ids = []
        self.listbox.delete(0, "end")
        self.clear_detail()

    def bind_view(self, callback) -> None:
        if self.display_button:
            self.display_button.configure(command=callback)
        self.listbox.bind("<Double-Button-1>", lambda _event: callback())

    def bind_reload(self, callback) -> None:
        if self.reload_button:
            self.reload_button.configure(command=callback)

    def bind_delete(self, callback) -> None:
        if self.delete_button:
            self.delete_button.configure(command=callback)

    def bind_print(self, callback) -> None:
        if self.print_button:
            self.print_button.configure(command=callback)
