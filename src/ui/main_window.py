import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from config import WINDOW_HEIGHT, WINDOW_WIDTH
from src.core.formatter import format_groups, format_samples
from src.core.generator import generate_random_samples, parse_manual_samples
from src.core.models import SelectionResult
from src.services.history_service import HistoryService
from src.services.selection_service import SelectionService
from src.ui.history_panel import HistoryPanel
from src.ui.input_panel import InputPanel
from src.ui.result_panel import ResultPanel


class MainWindow:
    def __init__(self, root: tk.Tk, selection_service: SelectionService, history_service: HistoryService) -> None:
        self.root = root
        self.selection_service = selection_service
        self.history_service = history_service
        self.current_result: SelectionResult | None = None
        self.generated_random_samples: list[int] | None = None
        self.is_running = False
        self.run_start_time = 0.0
        self.timer_job_id: str | None = None
        self.timeout_timer: str | None = None
        self.root.title("An optimal Samples selection System")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.input_panel: InputPanel | None = None
        self.result_panel: ResultPanel | None = None
        self.history_panel: HistoryPanel | None = None
        self.build_layout()
        self.bind_events()
        self.refresh_history()

    def build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=2)
        container.columnconfigure(2, weight=1)
        container.rowconfigure(1, weight=1)

        title = ttk.Label(container, text="An optimal Samples selection System", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        self.input_panel = InputPanel(container)
        self.input_panel.frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

        self.result_panel = ResultPanel(container)
        self.result_panel.frame.grid(row=1, column=1, sticky="nsew", padx=8)

        self.history_panel = HistoryPanel(container)
        self.history_panel.frame.grid(row=1, column=2, sticky="nsew", padx=(8, 0))

    def bind_events(self) -> None:
        assert self.input_panel is not None
        assert self.result_panel is not None
        assert self.history_panel is not None
        self.input_panel.bind_generate_samples(self.handle_generate_samples)
        self.input_panel.bind_run(self.handle_run_selection)
        self.input_panel.bind_save(self.handle_save_result)
        self.input_panel.bind_clear(self.handle_clear)
        self.result_panel.bind_print(self.handle_print_current_result)
        self.result_panel.bind_next(self.handle_clear)
        self.history_panel.bind_view(self.handle_view_history)
        self.history_panel.bind_reload(self.handle_reload_history)
        self.history_panel.bind_delete(self.handle_delete_history)
        self.history_panel.bind_print(self.handle_print_history)

    def show_message(self, title: str, message: str) -> None:
        messagebox.showinfo(title, message)

    def show_error(self, message: str) -> None:
        messagebox.showerror("Error", message)

    def refresh_history(self) -> None:
        assert self.history_panel is not None
        self.history_panel.load_runs(self.history_service.list_runs())

    def build_parameter_label(self, result: SelectionResult) -> str:
        threshold = result.rule.threshold if result.rule else 1
        return f"{result.params.m}-{result.params.n}-{result.params.k}-{result.params.j}-{result.params.s}-{threshold}-{result.result_count()}"

    def display_result(self, result: SelectionResult) -> None:
        assert self.result_panel is not None
        self.current_result = result
        self.result_panel.show_run_label(self.build_parameter_label(result))
        self.result_panel.show_selected_samples(result.selected_samples)
        self.result_panel.show_result_stats(result)
        self.result_panel.show_full_result_details(result)
        self.result_panel.show_coverage_report(result.coverage_report)
        self.root.title(f"An optimal Samples selection System - {result.rule.to_display_text() if result.rule else 'No rule'}")

    def set_running(self, is_running: bool) -> None:
        self.is_running = is_running
        assert self.input_panel is not None
        self.input_panel.set_running(is_running)
        if is_running:
            self.run_start_time = time.time()
            self.update_timer()
        else:
            self.stop_timer()

    def update_timer(self) -> None:
        if not self.is_running:
            return
        elapsed = time.time() - self.run_start_time
        remaining = max(0, 120 - int(elapsed))
        status = f"Running optimization... Time: {elapsed:.1f}s / 120s (remaining: {remaining}s)"
        if remaining < 30:
            status += " [Approaching limit]"
        if self.result_panel:
            self.result_panel.show_status_text(status)
        self.timer_job_id = self.root.after(500, self.update_timer)

    def stop_timer(self) -> None:
        if self.timer_job_id is not None:
            self.root.after_cancel(self.timer_job_id)
            self.timer_job_id = None

    def _handle_timeout(self) -> None:
        """Enforce 2-minute hard limit on optimization."""
        if not self.is_running:
            return
        self.set_running(False)
        self.show_error("Optimization exceeded the 2-minute (120s) time limit.\nPlease try with smaller parameters (e.g. smaller n or k).")
        if self.result_panel:
            self.result_panel.show_status_text("Timeout: 2-minute limit reached")
        self.timeout_timer = None

    def validate_samples_input(self, mode: str, manual_text: str, expected_n: int) -> None:
        """Validate that User Input box contains valid samples, for both Random n and Input n modes."""
        if mode == "random":
            if self.generated_random_samples is None:
                raise ValueError("Please click Random n first so the generated samples can be used for execution.")
            if len(self.generated_random_samples) != expected_n:
                raise ValueError("Generated random samples do not match the current n value. Please click Random n again.")
            return

        if not manual_text or not manual_text.strip():
            raise ValueError("User Input box cannot be empty. Please generate samples using Random n button first, or enter numbers manually.")
        samples = parse_manual_samples(manual_text)
        if not samples:
            raise ValueError("No valid numbers found in User Input. Please ensure numbers are entered (separated by spaces or commas).")
        if len(samples) != expected_n:
            raise ValueError(f"Input n requires exactly {expected_n} values, but you entered {len(samples)}. Please re-enter input.")

    def handle_generate_samples(self) -> None:
        try:
            assert self.input_panel is not None
            params = self.input_panel.get_params()
            samples = generate_random_samples(params.m, params.n)
            self.generated_random_samples = samples
            self.input_panel.set_samples_text(format_samples(samples))
            self.show_message(
                "Samples Generated",
                "Random samples generated and shown in User Input. Choose n remains Random n, and Execute will use exactly these generated samples.",
            )
        except Exception as exc:
            self.show_error(str(exc))

    def handle_run_selection(self) -> None:
        if self.is_running:
            return
        try:
            assert self.input_panel is not None
            params = self.input_panel.get_params()
            mode = self.input_panel.get_mode()
            manual_text = self.input_panel.get_manual_samples_text()
            self.validate_samples_input(mode, manual_text, params.n)
            execution_mode = mode
            execution_manual_text = manual_text
            if mode == "random" and self.generated_random_samples is not None:
                execution_mode = "manual"
                execution_manual_text = format_samples(self.generated_random_samples)
            rule_name = self.input_panel.get_rule_name()
            rule_threshold = self.input_panel.get_rule_threshold()
            if self.result_panel:
                self.result_panel.clear()
            self.current_result = None
            self.set_running(True)
            self.timeout_timer = None
            worker = threading.Thread(
                target=self._run_selection_worker,
                args=(params, execution_mode, execution_manual_text, rule_name, rule_threshold),
                daemon=True,
            )
            worker.start()
            # 2-minute hard timeout
            self.timeout_timer = self.root.after(120000, self._handle_timeout)
        except Exception as exc:
            self.set_running(False)
            self.show_error(str(exc))

    def _run_selection_worker(self, params, mode: str, manual_text: str, rule_name: str, rule_threshold: int) -> None:
        try:
            result = self.selection_service.run_selection(params, mode, manual_text, rule_name, rule_threshold)
            self.root.after(0, lambda result=result: self._finish_selection(result, None))
        except Exception as exc:
            error = exc
            self.root.after(0, lambda error=error: self._finish_selection(None, error))
        finally:
            if self.timeout_timer is not None:
                try:
                    self.root.after_cancel(self.timeout_timer)
                except:
                    pass
                self.timeout_timer = None

    def _finish_selection(self, result: SelectionResult | None, error: Exception | None) -> None:
        elapsed = time.time() - self.run_start_time if self.run_start_time else 0.0
        if self.timeout_timer is not None:
            try:
                self.root.after_cancel(self.timeout_timer)
            except:
                pass
            self.timeout_timer = None
        self.set_running(False)
        if error is not None:
            self.show_error(str(error))
            return
        if result is not None:
            result.runtime_seconds = elapsed
            self.display_result(result)
            if self.result_panel:
                self.result_panel.show_status_text(f"{result.coverage_report.to_display_text()} | Runtime: {elapsed:.2f}s")

    def handle_save_result(self) -> None:
        try:
            if self.current_result is None:
                raise ValueError("No current result to store.")
            run_id = self.history_service.save_run(self.current_result)
            self.refresh_history()
            self.show_message("Stored", f"Current result stored successfully with ID {run_id}.")
        except Exception as exc:
            self.show_error(str(exc))

    def handle_view_history(self) -> None:
        try:
            assert self.history_panel is not None
            run_id = self.history_panel.get_selected_run_id()
            if run_id is None:
                raise ValueError("Please select a database record.")
            details = self.history_service.get_run_details(run_id)
            run = details["run"]
            groups = details["groups"]
            params = run.params
            label = f"{params.m}-{params.n}-{params.k}-{params.j}-{params.s}-{run.rule_threshold}-{run.result_count}"
            lines = [
                f"Runtime: {run.runtime_seconds:.2f}s",
                f"Created: {run.created_at}",
                f"Coverage: {run.coverage_summary}",
                "",
            ]
            lines.extend(f"{index}. {group}" for index, group in enumerate(format_groups(groups), start=1))
            self.history_panel.set_detail(label, lines)
        except Exception as exc:
            self.show_error(str(exc))

    def handle_reload_history(self) -> None:
        try:
            assert self.history_panel is not None
            run_id = self.history_panel.get_selected_run_id()
            if run_id is None:
                raise ValueError("Please select a database record.")
            result = self.history_service.rerun_saved_record(run_id)
            self.display_result(result)
        except Exception as exc:
            self.show_error(str(exc))

    def handle_delete_history(self) -> None:
        try:
            assert self.history_panel is not None
            run_id = self.history_panel.get_selected_run_id()
            if run_id is None:
                raise ValueError("Please select a database record.")
            self.history_service.delete_run(run_id)
            self.refresh_history()
            self.show_message("Deleted", "Database record deleted successfully.")
        except Exception as exc:
            self.show_error(str(exc))

    def handle_clear(self) -> None:
        assert self.input_panel is not None
        assert self.result_panel is not None
        self.generated_random_samples = None
        self.input_panel.clear()
        self.result_panel.clear()
        self.current_result = None

    def handle_print_current_result(self) -> None:
        if self.current_result is None:
            self.show_message("Print", "No current result to print.")
            return
        self.show_message("Print", "Print function is represented by this preview in the course demo version.")

    def handle_print_history(self) -> None:
        self.show_message("Print", "History print function is represented by this preview in the course demo version.")

    def run(self) -> None:
        self.root.mainloop()
