import tkinter as tk

from src.services.history_service import HistoryService
from src.services.selection_service import SelectionService
from src.storage.database import initialize_database
from src.ui.main_window import MainWindow



def create_app() -> MainWindow:
    initialize_database()
    root = tk.Tk()
    selection_service = SelectionService()
    history_service = HistoryService(selection_service)
    return MainWindow(root, selection_service, history_service)



def main() -> None:
    app = create_app()
    app.run()


if __name__ == "__main__":
    main()
