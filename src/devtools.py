
import logging
import time
import tkinter as tk
from tkinter import messagebox


# Enable this during development; turn off in production
DEVMODE = True


class DebugConsole(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("🛠️ Debug Console")
        self.geometry("500x300")
        self.resizable(True, True)

        self.textbox = tk.Text(
            self,
            state="disabled",
            bg="black",
            fg="lime",
            font=("Courier", 10),
            wrap='word'
        )
        self.textbox.pack(expand=True, fill='both')

        # Don't destroy, just hide
        self.protocol("WM_DELETE_WINDOW", self.hide)
        self.visible = True

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"[{timestamp}] {msg}\n")
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

    def hide(self):
        self.visible = False
        self.withdraw()

    def show(self):
        if not self.visible:
            self.visible = True
            self.deiconify()


def not_implemented_yet(feature_name=""):
    msg = f"Feature '{feature_name}' is not implemented yet. Skipping..."
    if DEVMODE:
        print(f"⚠️ [NOTICE] {msg}")
        popup_notice("🚧 Feature Incomplete", msg)
        logging.warning(msg)


def dev_breakpoint(feature_name=""):
    if DEVMODE:
        print(f"\n[🧪 BREAKPOINT] Paused at: {feature_name}")
        input("Press Enter to continue...")


def dev_log(message):
    if DEVMODE:
        logging.info(f"[DEV LOG] {message}")


def banner(text):
    if DEVMODE:
        print("\n" + "=" * 50)
        print(f"🛠️  {text}")
        print("=" * 50)


def warn_once(msg_key, storage=None):
    if storage is None:
        storage = set()
    if msg_key not in storage:
        print(f"⚠️ [NOTICE ONCE] {msg_key}")
        storage.add(msg_key)


def popup_notice(
    title="Work in Progress",
    msg="This feature is not implemented yet."
):
    root = tk._get_default_root()
    if not root:
        # Use shared root pattern to avoid multiple Tk() instances
        from utils.window_positioning import ScreenInfo
        if not ScreenInfo._shared_root:
            ScreenInfo._shared_root = tk.Tk()
            ScreenInfo._shared_root.withdraw()  # Hide the main root
        root = ScreenInfo._shared_root
    messagebox.showinfo(title, msg)
