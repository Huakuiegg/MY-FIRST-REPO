import tkinter as tk
from tkinter import ttk

from src.core.formatter import format_groups, format_samples
from src.core.models import CoverageReport, SelectionResult


class ResultPanel:
    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent
        self.frame = ttk.LabelFrame(parent, text="Results", padding=10)
        self.samples_var = tk.StringVar(value="")
        self.stats_var = tk.StringVar(value="")
        self.coverage_var = tk.StringVar(value="")
        self.run_label_var = tk.StringVar(value="")
        self.groups_text: tk.Text | None = None
        self.next_button: ttk.Button | None = None
        self.print_button: ttk.Button | None = None
        self.build()

    def build(self) -> None:
        ttk.Label(self.frame, textvariable=self.run_label_var, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))

        input_frame = ttk.LabelFrame(self.frame, text="Value Input", padding=6)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(input_frame, text="Selected Samples:").grid(row=0, column=0, sticky="w")
        ttk.Label(input_frame, textvariable=self.samples_var, wraplength=750).grid(row=1, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        result_frame = ttk.LabelFrame(self.frame, text="Results", padding=6)
        result_frame.grid(row=2, column=0, sticky="nsew")
        ttk.Label(result_frame, textvariable=self.stats_var, wraplength=750).grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(result_frame, textvariable=self.coverage_var, wraplength=750).grid(row=1, column=0, sticky="ew", pady=(0, 6))

        groups_label = ttk.Label(result_frame, text="FINAL COVERAGE GROUPS", font=("Segoe UI", 10, "bold"))
        groups_label.grid(row=2, column=0, sticky="w", pady=(0, 4))

        # Text must be a child of result_frame so it shares the same grid as the scrollbar;
        # parenting it to self.frame placed the box on the wrong row and hid the data.
        self.groups_text = tk.Text(result_frame, height=12, width=64, state="disabled", wrap="word")
        y_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.groups_text.yview)
        self.groups_text.configure(yscrollcommand=y_scroll.set)
        self.groups_text.grid(row=3, column=0, sticky="nsew")
        y_scroll.grid(row=3, column=1, sticky="ns")

        button_frame = ttk.Frame(result_frame)
        button_frame.grid(row=4, column=0, sticky="e", pady=(6, 0))
        self.print_button = ttk.Button(button_frame, text="Print")
        self.print_button.pack(side="left", padx=4)
        self.next_button = ttk.Button(button_frame, text="Next")
        self.next_button.pack(side="left", padx=4)

        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)

    def show_run_label(self, label: str) -> None:
        self.run_label_var.set(label)

    def show_selected_samples(self, samples: list[int]) -> None:
        self.samples_var.set(format_samples(samples))

    def show_result_stats(self, result: SelectionResult) -> None:
        self.stats_var.set(
            f"Candidate groups: {result.candidate_count()} | "
            f"Coverage targets: {result.target_count} | "
            f"Final result groups: {result.result_count()}"
        )

    def show_full_result_details(self, result: SelectionResult) -> None:
        formatted_groups = format_groups(result.optimized_groups)
        if formatted_groups:
            lines = [f"Result {index}: {group}" for index, group in enumerate(formatted_groups, start=1)]
            self.set_groups_text("\n".join(lines))
        else:
            self.set_groups_text("No result groups generated.")

    def set_groups_text(self, text: str) -> None:
        assert self.groups_text is not None
        self.groups_text.configure(state="normal")
        self.groups_text.delete("1.0", "end")
        self.groups_text.insert("1.0", text)
        self.groups_text.configure(state="disabled")

    def show_coverage_report(self, report: CoverageReport) -> None:
        status = "Satisfied" if report.is_satisfied else "Not satisfied"
        self.coverage_var.set(
            f"Final coverage: {report.covered_targets}/{report.total_targets} | "
            f"Coverage ratio: {report.coverage_ratio:.2%} | Rule: {status}"
        )

    def show_status_text(self, text: str) -> None:
        # Ensure long status text (including runtime) is fully visible
        self.coverage_var.set(text)

    def clear(self) -> None:
        self.run_label_var.set("")
        self.samples_var.set("")
        self.stats_var.set("")
        self.coverage_var.set("")
        self.set_groups_text("")

    def bind_print(self, callback) -> None:
        if self.print_button:
            self.print_button.configure(command=callback)

    def bind_next(self, callback) -> None:
        if self.next_button:
            self.next_button.configure(command=callback)
