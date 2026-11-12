"""
Lightweight floating toast notification for Windows.
Displays a non-stealing, modern dark notification card in the bottom-right corner.
"""

import sys
import os
import subprocess
from pathlib import Path
import tkinter as tk


def show_toast(title, message, file_to_reveal=None, duration_ms=3000, is_success=True):
    """
    Display a sleek floating notification in bottom right of primary screen.
    Runs non-blocking or standalone.
    """
    try:
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.attributes('-alpha', 0.0)  # Start transparent for fade-in

        bg_color = "#18181b"  # Zinc 900
        border_color = "#22c55e" if is_success else "#ef4444"
        text_color = "#f4f4f5"
        sub_color = "#a1a1aa"

        root.configure(bg=border_color)

        outer_frame = tk.Frame(root, bg=border_color, padx=1, pady=1)
        outer_frame.pack(fill="both", expand=True)

        inner_frame = tk.Frame(outer_frame, bg=bg_color, padx=14, pady=12)
        inner_frame.pack(fill="both", expand=True)

        # Header with icon and title
        header_frame = tk.Frame(inner_frame, bg=bg_color)
        header_frame.pack(fill="x", anchor="w")

        icon_char = "✨" if is_success else "⚠️"
        icon_lbl = tk.Label(header_frame, text=icon_char, font=("Segoe UI Emoji", 11), bg=bg_color, fg="#22c55e" if is_success else "#ef4444")
        icon_lbl.pack(side="left", padx=(0, 6))

        title_lbl = tk.Label(header_frame, text=title, font=("Segoe UI", 10, "bold"), bg=bg_color, fg=text_color)
        title_lbl.pack(side="left")

        # Close button
        def on_close(event=None):
            fade_out_and_close()

        close_btn = tk.Label(header_frame, text="✕", font=("Segoe UI", 9), bg=bg_color, fg="#71717a", cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", on_close)

        # Message body
        msg_lbl = tk.Label(inner_frame, text=message, font=("Segoe UI", 9), bg=bg_color, fg=sub_color, wraplength=270, justify="left")
        msg_lbl.pack(fill="x", pady=(6, 4), anchor="w")

        # Action button to open folder / select file
        if file_to_reveal and os.path.exists(file_to_reveal):
            def open_in_explorer(event=None):
                try:
                    subprocess.Popen(f'explorer.exe /select,"{os.path.abspath(file_to_reveal)}"')
                except Exception:
                    pass
                fade_out_and_close()

            action_lbl = tk.Label(
                inner_frame,
                text="📂 View in Explorer",
                font=("Segoe UI", 9, "underline"),
                bg=bg_color,
                fg="#38bdf8",
                cursor="hand2"
            )
            action_lbl.pack(anchor="w", pady=(2, 0))
            action_lbl.bind("<Button-1>", open_in_explorer)

        # Calculate position (bottom-right above taskbar)
        root.update_idletasks()
        w = max(310, inner_frame.winfo_reqwidth() + 10)
        h = max(75, inner_frame.winfo_reqheight() + 10)
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        x = screen_w - w - 24
        y = screen_h - h - 56  # Leave room for Windows taskbar

        root.geometry(f"{w}x{h}+{x}+{y}")

        # Smooth fade-in
        alpha = 0.0
        def fade_in():
            nonlocal alpha
            if alpha < 0.95:
                alpha = min(0.95, alpha + 0.15)
                root.attributes('-alpha', alpha)
                root.after(20, fade_in)
        fade_in()

        # Fade-out and close
        def fade_out_and_close():
            nonlocal alpha
            if alpha > 0.05:
                alpha = max(0.0, alpha - 0.15)
                root.attributes('-alpha', alpha)
                root.after(20, fade_out_and_close)
            else:
                root.destroy()

        # Auto dismiss
        root.after(duration_ms, fade_out_and_close)

        root.mainloop()
    except Exception:
        pass


if __name__ == '__main__':
    # Test CLI call: python toast.py "Title" "Message" [file_path]
    title = sys.argv[1] if len(sys.argv) > 1 else "Syed's Image Convertor"
    msg = sys.argv[2] if len(sys.argv) > 2 else "Test notification message"
    reveal = sys.argv[3] if len(sys.argv) > 3 else None
    show_toast(title, msg, file_to_reveal=reveal)
