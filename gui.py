"""
AnyWebP Local - Modern Desktop Image Converter GUI.
Features batch image conversion, drag-and-drop, format selection, quality slider,
image resizing, single-instance socket IPC, and right-click Explorer integration.
"""

import sys
import os
import json
import socket
import threading
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# Attempt drag-and-drop support
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except Exception:
    HAS_DND = False

from converter import (
    convert_image,
    get_image_info,
    format_bytes,
    is_image_file,
    SUPPORTED_FORMATS
)

IPC_PORT = 48721


def send_to_existing_instance(file_paths):
    """Check if another instance is running; if so, pass paths and return True."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(('127.0.0.1', IPC_PORT))
        payload = json.dumps(file_paths).encode('utf-8')
        s.sendall(payload)
        s.close()
        return True
    except Exception:
        return False


class AnyWebPApp:
    def __init__(self, root, initial_files=None):
        self.root = root
        self.root.title("Syed's Image Convertor")
        self.root.geometry("980x720")
        self.root.minsize(860, 620)

        # Set window icon if available
        app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        ico_file = app_dir / "app_icon.ico"
        if ico_file.exists():
            try:
                self.root.iconbitmap(str(ico_file))
            except Exception:
                pass

        # Apply dark theme styling
        self.bg_main = "#0f172a"      # Slate 900
        self.bg_card = "#1e293b"      # Slate 800
        self.bg_card_hover = "#334155"# Slate 700
        self.accent = "#38bdf8"       # Sky 400
        self.accent_btn = "#0284c7"   # Sky 600
        self.accent_hover = "#0369a1" # Sky 700
        self.text_main = "#f8fafc"    # Slate 50
        self.text_muted = "#94a3b8"   # Slate 400
        self.border = "#334155"       # Slate 700
        self.green = "#10b981"        # Emerald 500

        self.root.configure(bg=self.bg_main)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Custom.Horizontal.TProgressbar",
                             troughcolor=self.bg_card,
                             background=self.accent,
                             bordercolor=self.bg_card,
                             lightcolor=self.accent,
                             darkcolor=self.accent)

        # State
        self.file_items = []  # list of dicts with file info & UI references
        self.target_format = tk.StringVar(value="WEBP")
        self.quality = tk.IntVar(value=85)
        self.lossless = tk.BooleanVar(value=False)
        self.resize_mode = tk.StringVar(value="original")  # original, scale, custom
        self.resize_scale = tk.IntVar(value=100)
        self.custom_width = tk.StringVar(value="")
        self.custom_height = tk.StringVar(value="")
        self.keep_aspect = tk.BooleanVar(value=True)
        self.output_mode = tk.StringVar(value="same")      # same, custom
        self.custom_output_dir = tk.StringVar(value="")
        self.overwrite = tk.BooleanVar(value=False)
        self.is_converting = False
        self.format_buttons = {}

        self._build_ui()

        # Handle initial files
        if initial_files:
            self.add_files(initial_files)

        # Start IPC socket listener
        self._start_ipc_server()

        # Enable Drag and Drop if available
        if HAS_DND and isinstance(self.root, TkinterDnD.Tk):
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)

    def _start_ipc_server(self):
        """Listen on IPC port for new files opened while app is already running."""
        def listen():
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(('127.0.0.1', IPC_PORT))
                server.listen(5)
                while True:
                    conn, _ = server.accept()
                    data = conn.recv(65536)
                    conn.close()
                    if data:
                        try:
                            paths = json.loads(data.decode('utf-8'))
                            if paths:
                                self.root.after(0, lambda p=paths: self._handle_remote_paths(p))
                        except Exception:
                            pass
            except Exception:
                pass

        t = threading.Thread(target=listen, daemon=True)
        t.start()

    def _handle_remote_paths(self, paths):
        """Bring window to front and add incoming files."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.add_files(paths)

    def _on_drop(self, event):
        """Handle drag-and-dropped files/folders."""
        raw_data = event.data
        if not raw_data:
            return
        # Windows TkinterDnD can wrap paths with spaces in curly braces {}
        paths = []
        in_curly = False
        current_token = ""
        for char in raw_data:
            if char == '{':
                in_curly = True
            elif char == '}':
                in_curly = False
                if current_token:
                    paths.append(current_token.strip())
                    current_token = ""
            elif char == ' ' and not in_curly:
                if current_token:
                    paths.append(current_token.strip())
                    current_token = ""
            else:
                current_token += char
        if current_token:
            paths.append(current_token.strip())

        self.add_files(paths)

    def _build_ui(self):
        # 1. Header Frame
        header = tk.Frame(self.root, bg=self.bg_main, height=64)
        header.pack(fill="x", padx=24, pady=(16, 8))

        # Title and branding
        title_box = tk.Frame(header, bg=self.bg_main)
        title_box.pack(side="left")

        # Logo image
        app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        png_logo = app_dir / "app_icon.png"
        self.logo_img = None
        if png_logo.exists():
            try:
                with Image.open(png_logo) as img:
                    img = img.resize((38, 38), Image.Resampling.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(img)
            except Exception:
                pass

        if self.logo_img:
            logo_lbl = tk.Label(title_box, image=self.logo_img, bg=self.bg_main, borderwidth=0)
        else:
            logo_lbl = tk.Label(title_box, text="⚡", font=("Segoe UI Emoji", 20), bg=self.bg_main, fg=self.accent)
        logo_lbl.pack(side="left", padx=(0, 10))

        text_box = tk.Frame(title_box, bg=self.bg_main)
        text_box.pack(side="left")

        app_title = tk.Label(text_box, text="SYED'S IMAGE CONVERTOR", font=("Segoe UI", 15, "bold"), bg=self.bg_main, fg=self.text_main)
        app_title.pack(anchor="w")

        app_sub = tk.Label(text_box, text="Created by Syed Riyazuddin • Fast, Offline & Privacy-First", font=("Segoe UI", 8), bg=self.bg_main, fg=self.text_muted)
        app_sub.pack(anchor="w")

        # Top Right Actions
        top_actions = tk.Frame(header, bg=self.bg_main)
        top_actions.pack(side="right")

        about_btn = tk.Button(
            top_actions,
            text="ℹ️ About",
            font=("Segoe UI", 9),
            bg=self.bg_card,
            fg=self.text_main,
            activebackground=self.bg_card_hover,
            activeforeground=self.text_main,
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._open_about_dialog
        )
        about_btn.pack(side="right", padx=(8, 0))

        menu_btn = tk.Button(
            top_actions,
            text="⚙️ Context Menu Setup",
            font=("Segoe UI", 9),
            bg=self.bg_card,
            fg=self.text_main,
            activebackground=self.bg_card_hover,
            activeforeground=self.text_main,
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._open_context_menu_dialog
        )
        menu_btn.pack(side="right", padx=(8, 0))

        # 2. Main Container (Left: Settings Panel, Right: Queue List)
        main_content = tk.Frame(self.root, bg=self.bg_main)
        main_content.pack(fill="both", expand=True, padx=24, pady=8)

        # --- LEFT PANEL: Settings Card ---
        left_panel = tk.Frame(main_content, bg=self.bg_card, width=320, padx=18, pady=18)
        left_panel.pack(side="left", fill="y", padx=(0, 16))
        left_panel.pack_propagate(False)

        settings_title = tk.Label(left_panel, text="CONVERSION SETTINGS", font=("Segoe UI", 10, "bold"), bg=self.bg_card, fg=self.accent)
        settings_title.pack(anchor="w", pady=(0, 14))

        # Output Format Pills
        fmt_lbl = tk.Label(left_panel, text="Target Format", font=("Segoe UI", 9, "bold"), bg=self.bg_card, fg=self.text_main)
        fmt_lbl.pack(anchor="w", pady=(0, 6))

        fmt_grid = tk.Frame(left_panel, bg=self.bg_card)
        fmt_grid.pack(fill="x", pady=(0, 14))

        formats = ['WEBP', 'PNG', 'JPG', 'AVIF', 'GIF', 'ICO', 'BMP', 'TIFF', 'PDF']
        for i, fmt in enumerate(formats):
            row = i // 3
            col = i % 3
            btn = tk.Button(
                fmt_grid,
                text=fmt,
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda f=fmt: self._set_format(f)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            fmt_grid.columnconfigure(col, weight=1)
            self.format_buttons[fmt] = btn

        self._refresh_format_buttons()

        # Quality Control
        self.quality_frame = tk.Frame(left_panel, bg=self.bg_card)
        self.quality_frame.pack(fill="x", pady=(0, 14))

        q_head = tk.Frame(self.quality_frame, bg=self.bg_card)
        q_head.pack(fill="x")
        q_lbl = tk.Label(q_head, text="Quality / Compression", font=("Segoe UI", 9, "bold"), bg=self.bg_card, fg=self.text_main)
        q_lbl.pack(side="left")
        self.q_val_lbl = tk.Label(q_head, text="85%", font=("Segoe UI", 9), bg=self.bg_card, fg=self.accent)
        self.q_val_lbl.pack(side="right")

        self.q_slider = tk.Scale(
            self.quality_frame,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.quality,
            bg=self.bg_card,
            fg=self.text_main,
            highlightthickness=0,
            troughcolor="#0f172a",
            activebackground=self.accent,
            showvalue=0,
            command=self._on_quality_slider
        )
        self.q_slider.pack(fill="x", pady=(4, 6))

        self.lossless_chk = tk.Checkbutton(
            self.quality_frame,
            text="Lossless Mode (WebP/PNG)",
            variable=self.lossless,
            font=("Segoe UI", 8),
            bg=self.bg_card,
            fg=self.text_main,
            selectcolor="#0f172a",
            activebackground=self.bg_card,
            activeforeground=self.text_main,
            command=self._on_lossless_toggle
        )
        self.lossless_chk.pack(anchor="w")

        # Resize Options
        resize_frame = tk.Frame(left_panel, bg=self.bg_card)
        resize_frame.pack(fill="x", pady=(0, 14))

        r_lbl = tk.Label(resize_frame, text="Image Resizing", font=("Segoe UI", 9, "bold"), bg=self.bg_card, fg=self.text_main)
        r_lbl.pack(anchor="w", pady=(0, 6))

        r_modes = [("Original Size", "original"), ("Scale %", "scale"), ("Custom W × H", "custom")]
        r_radio_box = tk.Frame(resize_frame, bg=self.bg_card)
        r_radio_box.pack(fill="x")
        for text, mode in r_modes:
            rb = tk.Radiobutton(
                r_radio_box,
                text=text,
                value=mode,
                variable=self.resize_mode,
                font=("Segoe UI", 8),
                bg=self.bg_card,
                fg=self.text_main,
                selectcolor="#0f172a",
                activebackground=self.bg_card,
                activeforeground=self.text_main,
                command=self._on_resize_mode_change
            )
            rb.pack(anchor="w", pady=1)

        # Scale options container
        self.scale_box = tk.Frame(resize_frame, bg=self.bg_card)
        scale_pills = [("25%", 25), ("50%", 50), ("75%", 75), ("150%", 150), ("200%", 200)]
        for label, val in scale_pills:
            sp_btn = tk.Button(
                self.scale_box,
                text=label,
                font=("Segoe UI", 8),
                bg=self.bg_main,
                fg=self.text_main,
                relief="flat",
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda v=val: self._set_scale(v)
            )
            sp_btn.pack(side="left", padx=2, pady=4)

        # Custom dimensions container
        self.custom_dim_box = tk.Frame(resize_frame, bg=self.bg_card)
        tk.Label(self.custom_dim_box, text="W:", font=("Segoe UI", 8), bg=self.bg_card, fg=self.text_muted).pack(side="left")
        self.w_entry = tk.Entry(self.custom_dim_box, textvariable=self.custom_width, width=6, bg=self.bg_main, fg=self.text_main, insertbackground="white", relief="flat")
        self.w_entry.pack(side="left", padx=(2, 6))
        tk.Label(self.custom_dim_box, text="H:", font=("Segoe UI", 8), bg=self.bg_card, fg=self.text_muted).pack(side="left")
        self.h_entry = tk.Entry(self.custom_dim_box, textvariable=self.custom_height, width=6, bg=self.bg_main, fg=self.text_main, insertbackground="white", relief="flat")
        self.h_entry.pack(side="left", padx=(2, 6))

        self.aspect_chk = tk.Checkbutton(
            self.custom_dim_box,
            text="Lock Ratio",
            variable=self.keep_aspect,
            font=("Segoe UI", 8),
            bg=self.bg_card,
            fg=self.text_main,
            selectcolor="#0f172a",
            activebackground=self.bg_card,
            activeforeground=self.text_main
        )
        self.aspect_chk.pack(side="left")

        # Destination Folder
        dest_frame = tk.Frame(left_panel, bg=self.bg_card)
        dest_frame.pack(fill="x", pady=(0, 10))

        dest_lbl = tk.Label(dest_frame, text="Output Location", font=("Segoe UI", 9, "bold"), bg=self.bg_card, fg=self.text_main)
        dest_lbl.pack(anchor="w", pady=(0, 4))

        same_rb = tk.Radiobutton(
            dest_frame,
            text="Same as original file",
            value="same",
            variable=self.output_mode,
            font=("Segoe UI", 8),
            bg=self.bg_card,
            fg=self.text_main,
            selectcolor="#0f172a",
            activebackground=self.bg_card,
            activeforeground=self.text_main,
            command=self._on_dest_mode_change
        )
        same_rb.pack(anchor="w", pady=1)

        custom_dest_rb = tk.Radiobutton(
            dest_frame,
            text="Custom folder:",
            value="custom",
            variable=self.output_mode,
            font=("Segoe UI", 8),
            bg=self.bg_card,
            fg=self.text_main,
            selectcolor="#0f172a",
            activebackground=self.bg_card,
            activeforeground=self.text_main,
            command=self._on_dest_mode_change
        )
        custom_dest_rb.pack(anchor="w", pady=1)

        self.custom_dir_box = tk.Frame(dest_frame, bg=self.bg_card)
        self.dir_entry = tk.Entry(self.custom_dir_box, textvariable=self.custom_output_dir, font=("Segoe UI", 8), bg=self.bg_main, fg=self.text_main, relief="flat")
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        browse_btn = tk.Button(self.custom_dir_box, text="...", font=("Segoe UI", 8), bg=self.bg_main, fg=self.text_main, relief="flat", command=self._browse_output_dir)
        browse_btn.pack(side="right")

        self.overwrite_chk = tk.Checkbutton(
            dest_frame,
            text="Overwrite existing files",
            variable=self.overwrite,
            font=("Segoe UI", 8),
            bg=self.bg_card,
            fg=self.text_main,
            selectcolor="#0f172a",
            activebackground=self.bg_card,
            activeforeground=self.text_main
        )
        self.overwrite_chk.pack(anchor="w", pady=(4, 0))

        # --- RIGHT PANEL: Queue / List & Actions ---
        right_panel = tk.Frame(main_content, bg=self.bg_main)
        right_panel.pack(side="right", fill="both", expand=True)

        # Action Bar above queue
        action_bar = tk.Frame(right_panel, bg=self.bg_main)
        action_bar.pack(fill="x", pady=(0, 10))

        add_files_btn = tk.Button(
            action_bar,
            text="+ Add Images",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_card,
            fg=self.text_main,
            activebackground=self.bg_card_hover,
            activeforeground=self.text_main,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._browse_images
        )
        add_files_btn.pack(side="left", padx=(0, 8))

        add_folder_btn = tk.Button(
            action_bar,
            text="+ Add Folder",
            font=("Segoe UI", 9),
            bg=self.bg_card,
            fg=self.text_main,
            activebackground=self.bg_card_hover,
            activeforeground=self.text_main,
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._browse_folder
        )
        add_folder_btn.pack(side="left", padx=(0, 8))

        clear_btn = tk.Button(
            action_bar,
            text="🗑️ Clear List",
            font=("Segoe UI", 9),
            bg=self.bg_card,
            fg=self.text_muted,
            activebackground=self.bg_card_hover,
            activeforeground=self.text_main,
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.clear_all
        )
        clear_btn.pack(side="left")

        self.count_lbl = tk.Label(action_bar, text="0 images loaded", font=("Segoe UI", 9), bg=self.bg_main, fg=self.text_muted)
        self.count_lbl.pack(side="right", padx=4)

        # File List Container (Card with Scrollbar)
        list_card = tk.Frame(right_panel, bg=self.bg_card)
        list_card.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(list_card, bg=self.bg_card, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(list_card, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_card)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.scrollbar.pack(side="right", fill="y", pady=6)

        # Handle mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfig(self.canvas_window, width=event.width))

        # Empty state prompt
        self.empty_lbl = tk.Label(
            self.scrollable_frame,
            text="📥 Drag and drop images here\nor click '+ Add Images' above\nor right-click images in Windows Explorer",
            font=("Segoe UI", 12),
            bg=self.bg_card,
            fg=self.text_muted,
            pady=80
        )
        self.empty_lbl.pack(fill="both", expand=True)

        # 3. Bottom Footer Action Bar
        footer = tk.Frame(self.root, bg=self.bg_card, height=72, padx=24, pady=12)
        footer.pack(fill="x", side="bottom")

        # Stats summary on left
        self.stats_summary = tk.Label(footer, text="Select images to begin", font=("Segoe UI", 10), bg=self.bg_card, fg=self.text_main)
        self.stats_summary.pack(side="left")

        # Convert All Button on right
        self.convert_btn = tk.Button(
            footer,
            text="⚡ Convert All",
            font=("Segoe UI", 11, "bold"),
            bg=self.accent_btn,
            fg="white",
            activebackground=self.accent_hover,
            activeforeground="white",
            relief="flat",
            padx=28,
            pady=8,
            cursor="hand2",
            command=self.start_conversion
        )
        self.convert_btn.pack(side="right", padx=(12, 0))

        self.open_out_btn = tk.Button(
            footer,
            text="📂 Open Output Folder",
            font=("Segoe UI", 9),
            bg=self.bg_main,
            fg=self.text_main,
            activebackground=self.bg_card_hover,
            activeforeground=self.text_main,
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
            command=self._open_output_folder
        )
        self.open_out_btn.pack(side="right")

        # Progress bar (placed between list and footer)
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", mode="determinate", style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", side="bottom", padx=24, pady=(0, 2))
        self.progress_bar['value'] = 0

    def _set_format(self, fmt):
        self.target_format.set(fmt)
        self._refresh_format_buttons()
        # Toggle lossless availability
        if fmt == 'WEBP':
            self.lossless_chk.config(state="normal")
            self.q_slider.config(state="disabled" if self.lossless.get() else "normal")
        elif fmt in ('JPG', 'AVIF'):
            self.lossless_chk.config(state="disabled")
            self.q_slider.config(state="normal")
        else:
            self.lossless_chk.config(state="disabled")
            self.q_slider.config(state="disabled")

    def _refresh_format_buttons(self):
        curr = self.target_format.get()
        for fmt, btn in self.format_buttons.items():
            if fmt == curr:
                btn.configure(bg=self.accent_btn, fg="white")
            else:
                btn.configure(bg=self.bg_main, fg=self.text_muted)

    def _on_quality_slider(self, val):
        self.q_val_lbl.config(text=f"{int(val)}%")

    def _on_lossless_toggle(self):
        if self.target_format.get() == 'WEBP':
            self.q_slider.config(state="disabled" if self.lossless.get() else "normal")

    def _on_resize_mode_change(self):
        mode = self.resize_mode.get()
        self.scale_box.pack_forget()
        self.custom_dim_box.pack_forget()
        if mode == 'scale':
            self.scale_box.pack(fill="x", pady=(4, 0))
        elif mode == 'custom':
            self.custom_dim_box.pack(fill="x", pady=(4, 0))

    def _set_scale(self, val):
        self.resize_scale.set(val)
        messagebox.showinfo("Scale Set", f"Resize scale set to {val}%")

    def _on_dest_mode_change(self):
        if self.output_mode.get() == 'custom':
            self.custom_dir_box.pack(fill="x", pady=(4, 0))
        else:
            self.custom_dir_box.pack_forget()

    def _browse_output_dir(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.custom_output_dir.set(folder)

    def _open_output_folder(self):
        if self.output_mode.get() == 'custom' and self.custom_output_dir.get():
            out_p = self.custom_output_dir.get()
        elif self.file_items:
            # Open directory of the first file or last converted output
            out_p = Path(self.file_items[0]['info']['path']).parent
        else:
            out_p = Path.home()
        try:
            subprocess.Popen(f'explorer.exe "{os.path.abspath(out_p)}"')
        except Exception:
            pass

    def _browse_images(self):
        filetypes = [
            ("All Image Files", "*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.gif;*.tiff;*.avif;*.heic;*.ico"),
            ("WebP Images", "*.webp"),
            ("PNG Images", "*.png"),
            ("JPEG Images", "*.jpg;*.jpeg"),
            ("All Files", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Select Images to Convert", filetypes=filetypes)
        if files:
            self.add_files(files)

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Images")
        if folder:
            self.add_files([folder])

    def add_files(self, paths):
        """Add image files or all images from a folder to the queue."""
        expanded_files = []
        for p_str in paths:
            p = Path(p_str)
            if p.is_file() and is_image_file(p):
                expanded_files.append(p)
            elif p.is_dir():
                for sub in p.rglob("*"):
                    if sub.is_file() and is_image_file(sub):
                        expanded_files.append(sub)

        # Filter out duplicates already in file_items
        existing_paths = {item['info']['path'] for item in self.file_items}
        new_items = []
        for file_p in expanded_files:
            abs_path = str(file_p.resolve())
            if abs_path not in existing_paths:
                info = get_image_info(abs_path)
                if info:
                    new_items.append(info)
                    existing_paths.add(abs_path)

        if not new_items:
            return

        if self.empty_lbl:
            self.empty_lbl.pack_forget()

        for info in new_items:
            self._render_file_row(info)

        self._update_summary()

    def _render_file_row(self, info):
        row_frame = tk.Frame(self.scrollable_frame, bg=self.bg_main, padx=10, pady=8)
        row_frame.pack(fill="x", pady=3)

        # Thumbnail
        thumb_lbl = tk.Label(row_frame, bg=self.bg_main, width=48, height=48)
        thumb_lbl.pack(side="left", padx=(0, 10))

        # Load thumbnail in background or fast resize
        try:
            with Image.open(info['path']) as img:
                img.thumbnail((44, 44))
                photo = ImageTk.PhotoImage(img)
                thumb_lbl.config(image=photo)
                thumb_lbl.image = photo  # keep reference
        except Exception:
            thumb_lbl.config(text="🖼️", fg=self.text_muted, font=("Segoe UI Emoji", 14))

        # File details
        info_box = tk.Frame(row_frame, bg=self.bg_main)
        info_box.pack(side="left", fill="x", expand=True)

        name_lbl = tk.Label(info_box, text=info['name'], font=("Segoe UI", 9, "bold"), bg=self.bg_main, fg=self.text_main, anchor="w")
        name_lbl.pack(fill="x")

        meta_text = f"{info['format']} • {info['dimensions_str']} • {info['size_str']}"
        meta_lbl = tk.Label(info_box, text=meta_text, font=("Segoe UI", 8), bg=self.bg_main, fg=self.text_muted, anchor="w")
        meta_lbl.pack(fill="x")

        # Status badge
        status_lbl = tk.Label(row_frame, text="Ready", font=("Segoe UI", 8, "bold"), bg=self.bg_card, fg=self.accent, padx=8, pady=3)
        status_lbl.pack(side="left", padx=10)

        # Delete button
        del_btn = tk.Button(
            row_frame,
            text="✕",
            font=("Segoe UI", 8, "bold"),
            bg=self.bg_main,
            fg=self.text_muted,
            activebackground=self.bg_card,
            activeforeground="#ef4444",
            relief="flat",
            cursor="hand2"
        )
        del_btn.pack(side="right")

        item_data = {
            'info': info,
            'row_frame': row_frame,
            'status_lbl': status_lbl,
            'meta_lbl': meta_lbl,
            'thumb_lbl': thumb_lbl,
            'converted': False,
            'output_path': None
        }

        def remove_row():
            row_frame.destroy()
            if item_data in self.file_items:
                self.file_items.remove(item_data)
            self._update_summary()
            if not self.file_items and self.empty_lbl:
                self.empty_lbl.pack(fill="both", expand=True)

        del_btn.config(command=remove_row)
        self.file_items.append(item_data)

    def _update_summary(self):
        count = len(self.file_items)
        self.count_lbl.config(text=f"{count} image{'s' if count != 1 else ''} loaded")
        if count == 0:
            self.stats_summary.config(text="Select images to begin")
            self.convert_btn.config(text="⚡ Convert All")
        else:
            total_bytes = sum(item['info']['size'] for item in self.file_items)
            self.stats_summary.config(text=f"{count} files • Total Size: {format_bytes(total_bytes)}")
            self.convert_btn.config(text=f"⚡ Convert All ({count})")

    def clear_all(self):
        for item in self.file_items:
            item['row_frame'].destroy()
        self.file_items.clear()
        self.progress_bar['value'] = 0
        if self.empty_lbl:
            self.empty_lbl.pack(fill="both", expand=True)
        self._update_summary()

    def start_conversion(self):
        if not self.file_items:
            messagebox.showinfo("No Images", "Please add images to convert first.")
            return

        if self.is_converting:
            return

        self.is_converting = True
        self.convert_btn.config(state="disabled", text="⏳ Converting...")

        # Run conversion loop in worker thread
        threading.Thread(target=self._run_conversion_worker, daemon=True).start()

    def _run_conversion_worker(self):
        fmt = self.target_format.get()
        quality_val = self.quality.get()
        lossless_val = self.lossless.get()
        res_mode = self.resize_mode.get()
        res_scale = self.resize_scale.get()
        tw = self.custom_width.get().strip()
        th = self.custom_height.get().strip()
        keep_asp = self.keep_aspect.get()
        ovr = self.overwrite.get()

        out_dir = None
        if self.output_mode.get() == 'custom' and self.custom_output_dir.get():
            out_dir = self.custom_output_dir.get()

        total = len(self.file_items)
        success_count = 0
        total_orig_bytes = 0
        total_new_bytes = 0

        for i, item in enumerate(self.file_items):
            info = item['info']
            # Update UI to Converting
            self.root.after(0, lambda it=item: it['status_lbl'].config(text="Converting...", fg=self.accent))

            res = convert_image(
                input_path=info['path'],
                output_format=fmt,
                output_dir=out_dir,
                quality=quality_val,
                lossless=lossless_val,
                resize_mode=res_mode,
                resize_scale=res_scale,
                custom_width=tw if tw else None,
                custom_height=th if th else None,
                keep_aspect_ratio=keep_asp,
                overwrite=ovr
            )

            if res['success']:
                success_count += 1
                total_orig_bytes += res['original_size']
                total_new_bytes += res['new_size']
                savings = res['savings_percent']
                item['converted'] = True
                item['output_path'] = res['output_path']

                sav_str = f"Done ({savings}% smaller)" if savings > 0 else f"Done ({res['new_size_str']})"

                def update_done(it=item, s=sav_str, res_obj=res):
                    it['status_lbl'].config(text=s, fg=self.green)
                    it['meta_lbl'].config(text=f"➔ {res_obj['format']} • {res_obj['new_dims'][0]}×{res_obj['new_dims'][1]} • {res_obj['new_size_str']}")

                self.root.after(0, update_done)
            else:
                err_msg = res.get('error', 'Error')
                self.root.after(0, lambda it=item, e=err_msg: it['status_lbl'].config(text=f"Failed: {e[:20]}", fg="#ef4444"))

            # Update progress
            pct = int(((i + 1) / total) * 100)
            self.root.after(0, lambda p=pct: self.progress_bar.configure(value=p))

        # Conversion complete
        def on_complete():
            self.is_converting = False
            self.convert_btn.config(state="normal", text=f"⚡ Convert All ({total})")
            savings_pct = 0.0
            if total_orig_bytes > 0:
                savings_pct = round(((total_orig_bytes - total_new_bytes) / total_orig_bytes) * 100.0, 1)

            summary = f"Converted {success_count}/{total} images to {fmt} • Saved {savings_pct}% space ({format_bytes(total_orig_bytes)} ➔ {format_bytes(total_new_bytes)})"
            self.stats_summary.config(text=summary)

            # Show floating toast
            from toast import show_toast
            first_out = self.file_items[0]['output_path'] if self.file_items else None
            show_toast("Syed's Image Convertor", summary, file_to_reveal=first_out, is_success=(success_count > 0))

        self.root.after(0, on_complete)

    def _open_context_menu_dialog(self):
        """Dialog to install or uninstall Windows Explorer context menu."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Context Menu Integration")
        dlg.geometry("450x300")
        dlg.configure(bg=self.bg_card)
        dlg.transient(self.root)
        dlg.grab_set()

        lbl_title = tk.Label(dlg, text="Windows Explorer Context Menu", font=("Segoe UI", 11, "bold"), bg=self.bg_card, fg=self.text_main)
        lbl_title.pack(pady=(16, 8))

        desc_text = (
            "Add 'Syed's Image Convertor' directly into your Windows right-click menu.\n\n"
            "• Right-click any image ➔ Instant 1-click convert to WebP, PNG, JPG, AVIF\n"
            "• Right-click any image ➔ Open here with custom options\n"
            "• Adds 'Send to' shortcut for maximum compatibility\n"
            "• Installs locally in your user profile (No Admin rights required!)"
        )
        lbl_desc = tk.Label(dlg, text=desc_text, font=("Segoe UI", 9), bg=self.bg_card, fg=self.text_muted, justify="left")
        lbl_desc.pack(padx=20, pady=(0, 16))

        btn_box = tk.Frame(dlg, bg=self.bg_card)
        btn_box.pack(pady=8)

        def install_menu():
            app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
            ps_script = app_dir / "install_context_menu.ps1"
            res = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)], capture_output=True, text=True)
            if res.returncode == 0:
                messagebox.showinfo("Success", "Context menu installed successfully!\nRight-click any image in Explorer to test.", parent=dlg)
                dlg.destroy()
            else:
                messagebox.showerror("Error", f"Failed to install context menu:\n{res.stderr}", parent=dlg)

        def uninstall_menu():
            app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
            ps_script = app_dir / "uninstall_context_menu.ps1"
            res = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)], capture_output=True, text=True)
            if res.returncode == 0:
                messagebox.showinfo("Removed", "Context menu removed cleanly.", parent=dlg)
                dlg.destroy()
            else:
                messagebox.showerror("Error", f"Failed to remove context menu:\n{res.stderr}", parent=dlg)

        in_btn = tk.Button(btn_box, text="✅ Install Context Menu", font=("Segoe UI", 9, "bold"), bg=self.accent_btn, fg="white", relief="flat", padx=12, pady=6, cursor="hand2", command=install_menu)
        in_btn.pack(side="left", padx=6)

        un_btn = tk.Button(btn_box, text="❌ Uninstall", font=("Segoe UI", 9), bg=self.bg_main, fg=self.text_muted, relief="flat", padx=12, pady=6, cursor="hand2", command=uninstall_menu)
        un_btn.pack(side="left", padx=6)

    def _open_about_dialog(self):
        """Dialog showing detailed description, features, and creator credits."""
        dlg = tk.Toplevel(self.root)
        dlg.title("About Syed's Image Convertor")
        dlg.geometry("540x530")
        dlg.minsize(500, 480)
        dlg.configure(bg=self.bg_card)
        dlg.transient(self.root)
        dlg.grab_set()

        # Set icon
        app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        ico_file = app_dir / "app_icon.ico"
        if ico_file.exists():
            try:
                dlg.iconbitmap(str(ico_file))
            except Exception:
                pass

        # Header Frame
        hdr_frame = tk.Frame(dlg, bg=self.bg_main, padx=20, pady=16)
        hdr_frame.pack(fill="x")

        dlg.about_logo = None
        png_logo = app_dir / "app_icon.png"
        if png_logo.exists():
            try:
                with Image.open(png_logo) as img:
                    img = img.resize((48, 48), Image.Resampling.LANCZOS)
                    dlg.about_logo = ImageTk.PhotoImage(img)
            except Exception:
                pass

        if dlg.about_logo:
            about_logo_lbl = tk.Label(hdr_frame, image=dlg.about_logo, bg=self.bg_main, borderwidth=0)
            about_logo_lbl.pack(side="left", padx=(0, 12))

        hdr_text = tk.Frame(hdr_frame, bg=self.bg_main)
        hdr_text.pack(side="left", fill="both", expand=True)

        title_lbl = tk.Label(hdr_text, text="SYED'S IMAGE CONVERTOR", font=("Segoe UI", 13, "bold"), bg=self.bg_main, fg=self.accent)
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(hdr_text, text="Version 1.0.0 • Created by Syed Riyazuddin • 100% Offline & Private", font=("Segoe UI", 9), bg=self.bg_main, fg=self.text_muted)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Body container
        body = tk.Frame(dlg, bg=self.bg_card, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        # Short description
        desc_title = tk.Label(body, text="📌 About The App:", font=("Segoe UI", 10, "bold"), bg=self.bg_card, fg=self.text_main)
        desc_title.pack(anchor="w", pady=(0, 4))

        desc_text = (
            "Syed's Image Convertor is a high-speed, offline desktop image converter and compressor. "
            "It gives you instant 1-click conversions directly from your Windows Explorer right-click menu, "
            "as well as a rich batch-processing interface with custom quality and resizing controls. "
            "All conversions run 100% locally on your computer—no internet connection, cloud upload, or tracking."
        )
        desc_lbl = tk.Label(body, text=desc_text, font=("Segoe UI", 9), bg=self.bg_card, fg=self.text_muted, justify="left", wraplength=480)
        desc_lbl.pack(anchor="w", pady=(0, 14))

        # What the app does
        feat_title = tk.Label(body, text="✨ What The App Does:", font=("Segoe UI", 10, "bold"), bg=self.bg_card, fg=self.text_main)
        feat_title.pack(anchor="w", pady=(0, 6))

        features = [
            ("🖱️ Right-Click Explorer Menu", "Right-click any image on your PC to instantly convert to WebP, PNG, JPG, or AVIF."),
            ("🔄 Multi-Format Batch Conversion", "Convert WebP, PNG, JPG, AVIF, HEIC/HEIF, GIF, BMP, TIFF, ICO, and PDF in batches."),
            ("🎚️ Compression & Quality Control", "Lossy compression slider (1-100) or pure Lossless compression for WebP and PNG."),
            ("📐 Smart Image Resizing", "Proportional scaling (25%, 50%, 75%, 200%) or custom dimensions with locked aspect ratio."),
            ("🛡️ 100% Private & Standalone", "Runs completely offline without needing Python or internet access on any PC.")
        ]

        for f_title, f_desc in features:
            f_row = tk.Frame(body, bg=self.bg_card)
            f_row.pack(fill="x", pady=2)
            tk.Label(f_row, text=f_title, font=("Segoe UI", 9, "bold"), bg=self.bg_card, fg=self.text_main).pack(anchor="w")
            tk.Label(f_row, text=f_desc, font=("Segoe UI", 8), bg=self.bg_card, fg=self.text_muted, justify="left", wraplength=470).pack(anchor="w", padx=(16, 0))

        # Close button
        close_btn = tk.Button(dlg, text="Close", font=("Segoe UI", 9, "bold"), bg=self.accent_btn, fg="white", activebackground=self.accent_hover, activeforeground="white", relief="flat", padx=24, pady=6, cursor="hand2", command=dlg.destroy)
        close_btn.pack(pady=(0, 16))


def main():
    initial_files = sys.argv[1:] if len(sys.argv) > 1 else []

    # If another instance of the GUI is running, forward the files and exit
    if initial_files and send_to_existing_instance(initial_files):
        sys.exit(0)

    # Initialize root window with TkinterDnD if present
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = AnyWebPApp(root, initial_files=initial_files)
    root.mainloop()


if __name__ == '__main__':
    main()
