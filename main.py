import tkinter as tk
from ui.gui import App
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
