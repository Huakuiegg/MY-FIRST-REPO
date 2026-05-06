from __future__ import annotations

from pathlib import Path
import sys
import threading
import time

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager

from mobile_app.services.mobile_facade import MobileAppFacade

KV = """
#:import dp kivy.metrics.dp

<PrimaryButton@Button>:
    size_hint_y: None
    height: dp(48)

<SecondaryButton@Button>:
    size_hint_y: None
    height: dp(42)

<SectionLabel@Label>:
    size_hint_y: None
    height: self.texture_size[1] + dp(8)
    bold: True
    halign: "left"
    text_size: self.width, None

<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(12)

        Label:
            text: app.title_text
            font_size: "24sp"
            size_hint_y: None
            height: dp(72)
            bold: True
            halign: "center"
            valign: "middle"
            text_size: self.size

        Label:
            text: "Offline mobile optimizer"
            size_hint_y: None
            height: dp(40)
            halign: "center"
            text_size: self.size

        Widget:

        PrimaryButton:
            text: "Start New Optimization"
            disabled: app.is_busy
            on_release: app.open_form_screen()

        PrimaryButton:
            text: "View History"
            disabled: app.is_busy
            on_release: app.open_history_screen()

        Widget:

<FormScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(14)
        spacing: dp(10)

        Label:
            text: "Parameters"
            font_size: "22sp"
            size_hint_y: None
            height: dp(44)
            bold: True

        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: form_grid
                cols: 1
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height
                disabled: app.is_busy

                SectionLabel:
                    text: "Basic Parameters"
                TextInput:
                    id: field_m
                    hint_text: "m"
                    multiline: False
                    input_filter: "int"
                    size_hint_y: None
                    height: dp(42)
                TextInput:
                    id: field_n
                    hint_text: "n"
                    multiline: False
                    input_filter: "int"
                    size_hint_y: None
                    height: dp(42)
                TextInput:
                    id: field_k
                    hint_text: "k"
                    multiline: False
                    input_filter: "int"
                    size_hint_y: None
                    height: dp(42)
                TextInput:
                    id: field_j
                    hint_text: "j"
                    multiline: False
                    input_filter: "int"
                    size_hint_y: None
                    height: dp(42)
                TextInput:
                    id: field_s
                    hint_text: "s"
                    multiline: False
                    input_filter: "int"
                    size_hint_y: None
                    height: dp(42)

                SectionLabel:
                    text: "Sample Mode"
                Spinner:
                    id: sample_mode_spinner
                    text: "random"
                    values: ["random", "manual"]
                    size_hint_y: None
                    height: dp(42)
                    on_text: root.on_sample_mode_changed(self.text)

                TextInput:
                    id: manual_samples_input
                    hint_text: "Manual samples, e.g. 1 2 3 4 5 6 7 8"
                    multiline: True
                    readonly: sample_mode_spinner.text != "manual" or app.is_busy
                    size_hint_y: None
                    height: dp(92)

                SectionLabel:
                    text: "Rule"
                Spinner:
                    id: rule_mode_spinner
                    text: "auto"
                    values: ["auto", "all", "at_least_one", "at_least_n"]
                    size_hint_y: None
                    height: dp(42)
                    on_text: root.on_rule_mode_changed(self.text)

                TextInput:
                    id: threshold_input
                    hint_text: "Threshold for at_least_n"
                    multiline: False
                    input_filter: "int"
                    readonly: rule_mode_spinner.text != "at_least_n" or app.is_busy
                    size_hint_y: None
                    height: dp(42)

                Label:
                    id: form_message
                    text: root.message
                    color: 1, 0.2, 0.2, 1
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)
                    halign: "left"
                    valign: "middle"
                    text_size: self.width, None

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(10)
            SecondaryButton:
                text: "Back"
                disabled: app.is_busy
                on_release: app.go_home()
            PrimaryButton:
                text: "Running..." if app.is_busy else "Run"
                disabled: app.is_busy
                on_release: root.submit()

<LoadingScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(16)

        Widget:

        Label:
            text: "正在计算，请稍候..."
            font_size: "24sp"
            bold: True
            size_hint_y: None
            height: dp(40)

        Label:
            text: root.loading_message
            halign: "center"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(50)

        Label:
            text: root.elapsed_text
            font_size: "20sp"
            size_hint_y: None
            height: dp(36)

        ProgressBar:
            max: 1
            value: 1 if app.is_busy else 0
            size_hint_y: None
            height: dp(10)

        Widget:

<ResultScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(14)
        spacing: dp(10)

        Label:
            text: root.title_text
            font_size: "22sp"
            size_hint_y: None
            height: dp(44)
            bold: True

        ScrollView:
            do_scroll_x: False
            GridLayout:
                cols: 1
                spacing: dp(8)
                size_hint_y: None
                height: self.minimum_height

                Label:
                    text: root.summary_text
                    halign: "left"
                    valign: "top"
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)
                Label:
                    text: root.detail_text
                    halign: "left"
                    valign: "top"
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)
                Label:
                    text: root.groups_text
                    halign: "left"
                    valign: "top"
                    text_size: self.width, None
                    size_hint_y: None
                    height: max(self.texture_size[1] + dp(10), dp(120))

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(10)
            SecondaryButton:
                text: "Back"
                disabled: app.is_busy
                on_release: app.open_form_screen()
            PrimaryButton:
                text: "Save"
                disabled: app.is_busy
                on_release: root.save_current_result()
            PrimaryButton:
                text: "Home"
                disabled: app.is_busy
                on_release: app.go_home()

<HistoryScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(14)
        spacing: dp(10)

        Label:
            text: "History"
            font_size: "22sp"
            size_hint_y: None
            height: dp(44)
            bold: True

        BoxLayout:
            size_hint_y: None
            height: dp(42)
            spacing: dp(8)
            Spinner:
                id: history_spinner
                text: root.selected_history_text
                values: root.history_titles
                disabled: app.is_busy
                on_text: root.on_history_selected(self.text)
            SecondaryButton:
                text: "Refresh"
                disabled: app.is_busy
                on_release: root.refresh_history()

        ScrollView:
            do_scroll_x: False
            GridLayout:
                cols: 1
                spacing: dp(8)
                size_hint_y: None
                height: self.minimum_height

                Label:
                    text: root.history_detail_text
                    halign: "left"
                    valign: "top"
                    text_size: self.width, None
                    size_hint_y: None
                    height: max(self.texture_size[1] + dp(10), dp(200))

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(10)
            SecondaryButton:
                text: "Back"
                disabled: app.is_busy
                on_release: app.go_home()
            PrimaryButton:
                text: "Rerun"
                disabled: app.is_busy
                on_release: root.rerun_selected()
            PrimaryButton:
                text: "Delete"
                disabled: app.is_busy
                on_release: root.delete_selected()
"""


class HomeScreen(Screen):
    pass


class FormScreen(Screen):
    message = StringProperty("")

    def on_pre_enter(self, *args) -> None:
        self.populate_form(self.manager.app_ref.form_data)

    def populate_form(self, form_data: dict[str, str]) -> None:
        self.ids.field_m.text = form_data.get("m", "")
        self.ids.field_n.text = form_data.get("n", "")
        self.ids.field_k.text = form_data.get("k", "")
        self.ids.field_j.text = form_data.get("j", "")
        self.ids.field_s.text = form_data.get("s", "")
        self.ids.sample_mode_spinner.text = form_data.get("sample_mode", "random")
        self.ids.manual_samples_input.text = form_data.get("manual_samples", "")
        self.ids.rule_mode_spinner.text = form_data.get("rule_mode", "auto")
        self.ids.threshold_input.text = form_data.get("rule_threshold", "1")
        self.on_sample_mode_changed(self.ids.sample_mode_spinner.text)
        self.on_rule_mode_changed(self.ids.rule_mode_spinner.text)
        self.message = ""

    def collect_form_data(self) -> dict[str, str]:
        return {
            "m": self.ids.field_m.text.strip(),
            "n": self.ids.field_n.text.strip(),
            "k": self.ids.field_k.text.strip(),
            "j": self.ids.field_j.text.strip(),
            "s": self.ids.field_s.text.strip(),
            "sample_mode": self.ids.sample_mode_spinner.text.strip(),
            "manual_samples": self.ids.manual_samples_input.text.strip(),
            "rule_mode": self.ids.rule_mode_spinner.text.strip(),
            "rule_threshold": self.ids.threshold_input.text.strip() or "1",
        }

    def on_sample_mode_changed(self, mode: str) -> None:
        if mode != "manual":
            self.ids.manual_samples_input.text = ""

    def on_rule_mode_changed(self, rule_mode: str) -> None:
        if rule_mode != "at_least_n":
            self.ids.threshold_input.text = "1"

    def submit(self) -> None:
        app = self.manager.app_ref
        self.message = ""
        form_data = self.collect_form_data()
        app.run_optimization(form_data)

    def show_error(self, message: str) -> None:
        self.message = message


class LoadingScreen(Screen):
    loading_message = StringProperty("正在准备任务...")
    elapsed_text = StringProperty("已用时: 0.0 秒")


class ResultScreen(Screen):
    title_text = StringProperty("Optimization Result")
    summary_text = StringProperty("No result yet.")
    detail_text = StringProperty("")
    groups_text = StringProperty("")

    def update_content(self, view_model: dict[str, object]) -> None:
        self.title_text = str(view_model.get("title", "Optimization Result"))
        detail_lines = [
            f"Params: {view_model.get('params', '')}",
            f"Mode: {view_model.get('sample_mode', '')}",
            f"Rule: {view_model.get('rule', '')}",
            f"Samples: {view_model.get('samples', '')}",
            f"Coverage: {view_model.get('coverage_summary', '')}",
            f"Candidates: {view_model.get('candidate_count', 0)}",
            f"Targets: {view_model.get('target_count', 0)}",
            f"Results: {view_model.get('result_count', 0)}",
            f"Runtime: {view_model.get('runtime_seconds', 0)}s",
        ]
        groups = list(view_model.get("groups", []))
        self.summary_text = str(view_model.get("summary", ""))
        self.detail_text = "\n".join(detail_lines)
        self.groups_text = "Selected Groups:\n" + "\n".join(
            f"{index + 1}. {group_text}" for index, group_text in enumerate(groups)
        )

    def save_current_result(self) -> None:
        app = self.manager.app_ref
        app.save_current_result()


class HistoryScreen(Screen):
    selected_history_text = StringProperty("No history")
    history_titles = ListProperty([])
    history_detail_text = StringProperty("No saved history.")

    def on_pre_enter(self, *args) -> None:
        self.refresh_history()

    def refresh_history(self) -> None:
        app = self.manager.app_ref
        app.refresh_history_cache()
        titles = [item["text"] for item in app.history_index]
        self.history_titles = titles or ["No history"]
        self.selected_history_text = self.history_titles[0]
        self.on_history_selected(self.selected_history_text)

    def on_history_selected(self, text: str) -> None:
        app = self.manager.app_ref
        item = next((entry for entry in app.history_index if entry["text"] == text), None)
        if item is None:
            self.history_detail_text = "No saved history."
            return
        details = app.facade.get_run_details(int(item["run_id"]))
        view_model = app.facade.history_details_to_view_model(details)
        groups = list(view_model.get("groups", []))
        self.history_detail_text = "\n".join(
            [
                str(view_model.get("title", "")),
                str(view_model.get("created_at", "")),
                str(view_model.get("summary", "")),
                f"Params: {view_model.get('params', '')}",
                f"Mode: {view_model.get('sample_mode', '')}",
                f"Rule: {view_model.get('rule', '')}",
                f"Samples: {view_model.get('samples', '')}",
                f"Results: {view_model.get('result_count', 0)}",
                f"Runtime: {view_model.get('runtime_seconds', 0)}s",
                "Groups:",
                *[f"{index + 1}. {group_text}" for index, group_text in enumerate(groups)],
            ]
        )

    def rerun_selected(self) -> None:
        app = self.manager.app_ref
        item = next((entry for entry in app.history_index if entry["text"] == self.selected_history_text), None)
        if item is None:
            self.history_detail_text = "No history selected."
            return
        app.rerun_history(int(item["run_id"]))

    def delete_selected(self) -> None:
        app = self.manager.app_ref
        item = next((entry for entry in app.history_index if entry["text"] == self.selected_history_text), None)
        if item is None:
            self.history_detail_text = "No history selected."
            return
        app.delete_history(int(item["run_id"]))
        self.refresh_history()


class MobileRoot(ScreenManager):
    app_ref = ObjectProperty(None)


class MobileOptimizerApp(App):
    title_text = StringProperty("Optimal Samples Selection")
    is_busy = BooleanProperty(False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.facade = MobileAppFacade()
        self.form_data = self.facade.get_default_form_data()
        self.current_result = None
        self.history_index: list[dict[str, object]] = []
        self._task_started_at = 0.0
        self._timer_event = None

    def build(self) -> MobileRoot:
        Builder.load_string(KV)
        root = MobileRoot()
        root.app_ref = self
        root.add_widget(HomeScreen(name="home"))
        root.add_widget(FormScreen(name="form"))
        root.add_widget(LoadingScreen(name="loading"))
        root.add_widget(ResultScreen(name="result"))
        root.add_widget(HistoryScreen(name="history"))
        return root

    def go_home(self) -> None:
        if not self.is_busy:
            self.root.current = "home"

    def open_form_screen(self) -> None:
        if not self.is_busy:
            self.root.current = "form"

    def open_history_screen(self) -> None:
        if not self.is_busy:
            self.root.current = "history"

    def run_optimization(self, form_data: dict[str, str]) -> None:
        if self.is_busy:
            return
        self.form_data = form_data
        self._start_loading("正在执行组合优化计算...")
        worker = threading.Thread(target=self._run_optimization_worker, args=(form_data,), daemon=True)
        worker.start()

    def _run_optimization_worker(self, form_data: dict[str, str]) -> None:
        try:
            result = self.facade.run_selection(form_data)
        except Exception as exc:
            Clock.schedule_once(lambda _dt: self._handle_task_error(str(exc)), 0)
            return
        Clock.schedule_once(lambda _dt: self._handle_optimization_success(result), 0)

    def _handle_optimization_success(self, result) -> None:
        self.current_result = result
        view_model = self.facade.selection_result_to_view_model(result)
        result_screen = self.root.get_screen("result")
        result_screen.update_content(view_model)
        self._stop_loading()
        self.root.current = "result"

    def _handle_task_error(self, message: str) -> None:
        self._stop_loading()
        form_screen = self.root.get_screen("form")
        form_screen.show_error(message)
        self.root.current = "form"

    def _start_loading(self, message: str) -> None:
        self.is_busy = True
        self._task_started_at = time.perf_counter()
        loading_screen = self.root.get_screen("loading")
        loading_screen.loading_message = message
        loading_screen.elapsed_text = "已用时: 0.0 秒"
        self.root.current = "loading"
        if self._timer_event is not None:
            self._timer_event.cancel()
        self._timer_event = Clock.schedule_interval(self._update_loading_timer, 0.1)

    def _stop_loading(self) -> None:
        self.is_busy = False
        if self._timer_event is not None:
            self._timer_event.cancel()
            self._timer_event = None

    def _update_loading_timer(self, _dt: float) -> None:
        elapsed = time.perf_counter() - self._task_started_at
        loading_screen = self.root.get_screen("loading")
        loading_screen.elapsed_text = f"已用时: {elapsed:.1f} 秒"

    def save_current_result(self) -> None:
        if self.current_result is None or self.is_busy:
            return
        run_id = self.facade.save_result(self.current_result)
        result_screen = self.root.get_screen("result")
        result_screen.summary_text = f"Saved successfully. Run ID: {run_id}\n\n" + result_screen.summary_text
        self.refresh_history_cache()

    def refresh_history_cache(self) -> None:
        summaries = self.facade.list_run_summaries()
        self.history_index = [
            {"run_id": item.run_id, "text": f"{item.title} | {item.subtitle}"}
            for item in summaries
        ]

    def rerun_history(self, run_id: int) -> None:
        if self.is_busy:
            return
        self._start_loading("正在基于历史记录重新计算...")
        worker = threading.Thread(target=self._rerun_history_worker, args=(run_id,), daemon=True)
        worker.start()

    def _rerun_history_worker(self, run_id: int) -> None:
        try:
            result = self.facade.rerun_saved_record(run_id)
        except Exception as exc:
            Clock.schedule_once(lambda _dt: self._handle_history_error(str(exc)), 0)
            return
        Clock.schedule_once(lambda _dt: self._handle_optimization_success(result), 0)

    def _handle_history_error(self, message: str) -> None:
        self._stop_loading()
        history_screen = self.root.get_screen("history")
        history_screen.history_detail_text = message
        self.root.current = "history"

    def delete_history(self, run_id: int) -> None:
        if self.is_busy:
            return
        self.facade.delete_run(run_id)
        self.refresh_history_cache()


if __name__ == "__main__":
    MobileOptimizerApp().run()
