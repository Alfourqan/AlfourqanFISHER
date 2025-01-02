import tkinter as tk
from views.main_window import MainWindow
import logging

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and run main application window
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()
