import os
import tarfile
import tempfile
from pathlib import Path
from PIL import Image, ImageTk
from PIL.Image import Resampling
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

HEADER_SIZE = 2
WIDTH = 135
HEIGHT = 240

MODES = {
    "Clockface": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "space", "colon", "am", "pm"],
    "Weatherface": [
        "01d", "01n", "02d", "02n", "03d", "03n",
        "04d", "04n", "09d", "09n", "10d", "10n",
        "11d", "11n", "13d", "13n", "50d", "50n"
    ],
    "Staticface": ["1", "2", "3", "4", "5", "6"]
}

DESCRIPTIONS = {
    "Weatherface": {
        "01d": "Klarer Himmel - Tag",
        "01n": "Klarer Himmel - Nacht",
        "02d": "Wenige Wolken - Tag",
        "02n": "Wenige Wolken - Nacht",
        "03d": "Überwiegend bewölkt - Tag",
        "03n": "Überwiegend bewölkt - Nacht",
        "04d": "Bedeckt - Tag",
        "04n": "Bedeckt - Nacht",
        "09d": "Nieselregen - Tag",
        "09n": "Nieselregen - Nacht",
        "10d": "Regen (normal) - Tag",
        "10n": "Regen (normal) - Nacht",
        "11d": "Gewitter - Tag",
        "11n": "Gewitter - Nacht",
        "13d": "Schnee - Tag",
        "13n": "Schnee - Nacht",
        "50d": "Nebel / Dunst - Tag",
        "50n": "Nebel / Dunst - Nacht"
    }
}

DESCRIPTIONS_English = {
    "Weatherface": {
        "01d": "Clear sky - Day",
        "01n": "Clear sky - Night",
        "02d": "Few clouds - Day",
        "02n": "Few clouds - Night",
        "03d": "Partly cloudy - Day",
        "03n": "Partly cloudy - Night",
        "04d": "Overcast - Day",
        "04n": "Overcast - Night",
        "09d": "Drizzle - Day",
        "09n": "Drizzle - Night",
        "10d": "Rain (normal) - Day",
        "10n": "Rain (normal) - Night",
        "11d": "Thunderstorm - Day",
        "11n": "Thunderstorm - Night",
        "13d": "Snow - Day",
        "13n": "Snow - Night",
        "50d": "Fog / Haze - Day",
        "50n": "Fog / Haze - Night"
    }
}

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + 40
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify="left",
            background="#111", foreground="white",
            relief="solid", borderwidth=1,
            font=("Arial", 10)
        )
        label.pack(ipadx=6, ipady=3)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ImageFrame(ctk.CTkFrame):
    def __init__(self, master, label, index):
        super().__init__(master, width=WIDTH, height=HEIGHT+20)
        self.grid_propagate(False)
        self.index = index
        self.label_text = label

        self.canvas = ctk.CTkCanvas(self, width=WIDTH, height=HEIGHT, bg="gray20", highlightthickness=0)
        self.canvas.pack()
        self.name_label = ctk.CTkLabel(self, text=label, width=WIDTH)
        self.name_label.pack()

        self.original = None
        self.tk_image = None
        self.img_path = None
        self.scale = 1.0
        self.offset = [0, 0]
        self.drag_start = None

        self.canvas.bind("<Button-1>", self.on_click_or_drag_start)
        self.canvas.bind("<Button-3>", self.reset_event)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<MouseWheel>", self.on_scroll_zoom)
        self.canvas.bind("<Configure>", self.redraw)

        self.draw_placeholder()

    def reset_event(self, event=None):
        self.original = None
        self.tk_image = None
        self.img_path = None
        self.scale = 1.0
        self.offset = [0, 0]
        self.drag_start = None
        self.draw_placeholder()

    def draw_placeholder(self):
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH//2, HEIGHT//2, text="Click to load", fill="white")

    def on_click_or_drag_start(self, event):
        if not self.original:
            file_path = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg")])
            if file_path:
                self.load_image(file_path)
        else:
            self.drag_start = (event.x, event.y)

    def on_drag_motion(self, event):
        if self.original and self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.offset[0] += dx
            self.offset[1] += dy
            self.drag_start = (event.x, event.y)
            self.redraw()

    def on_drag_end(self, event):
        self.drag_start = None

    def on_scroll_zoom(self, event):
        if self.original:
            zoom_factor = 1.1 if event.delta > 0 else 0.9
            self.scale *= zoom_factor
            self.redraw()

    def load_image(self, path):
        self.img_path = path
        self.original = Image.open(path).convert("RGB")
        self.scale = 1.0
        self.offset = [0, 0]
        self.redraw()

    def load_bmp_with_header(self, bmp_path):
        with open(bmp_path, "rb") as f:
            #f.read(HEADER_SIZE)
            f.read()
            image = Image.open(f)
            self.original = image.convert("RGB")
            self.scale = 1.0
            self.offset = [0, 0]
            self.redraw()

    def redraw(self, event=None):
        self.canvas.delete("all")
        if not self.original:
            self.draw_placeholder()
            return
        img = self.original.copy()
        new_size = [int(s * self.scale) for s in img.size]
        img = img.resize(new_size, Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(WIDTH//2 + self.offset[0], HEIGHT//2 + self.offset[1], image=self.tk_image)

    def export_bmp(self, output_path):
        if not self.original:
            return
        img = self.original.copy()
        new_size = [int(s * self.scale) for s in img.size]
        img = img.resize(new_size, Resampling.LANCZOS)
        canvas = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        paste_pos = (
            (WIDTH - new_size[0]) // 2 + self.offset[0],
            (HEIGHT - new_size[1]) // 2 + self.offset[1]
        )
        canvas.paste(img, paste_pos)
        bmp_path = output_path / f"{self.label_text}.bmp"
        #header = b'\x56\x65'
        temp = bmp_path.with_suffix(".tmp")
        canvas.save(temp, format="BMP")
        with open(temp, "rb") as f:
            bmp_data = f.read()
        with open(bmp_path, "wb") as f:
            #f.write(header)
            f.write(bmp_data)
        temp.unlink()

class ImageApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IPSTube face set package generator. RGB565.")
        self.geometry("1350x500")
        self.mode = tk.StringVar(value="Staticface")
        self.frames = []

        # Mode selector
        mode_menu = ctk.CTkOptionMenu(self, values=list(MODES.keys()), command=self.change_mode, variable=self.mode)
        mode_menu.pack(pady=10)

        # Frame container
        self.container = ctk.CTkFrame(self)
        self.container.pack()

        # Button bar
        btn_bar = ctk.CTkFrame(self)
        btn_bar.pack(pady=10)

        ctk.CTkButton(btn_bar, text="Export set", command=self.export_set).pack(side="left", padx=10)
        ctk.CTkButton(btn_bar, text="Load from .tar.gz", command=self.import_set).pack(side="left", padx=10)
        ctk.CTkButton(btn_bar, text="Reset all", command=self.reset_all).pack(side="left", padx=10)
        ctk.CTkButton(btn_bar, text="6-Image row load", command=self.load_split_image_to_staticface).pack(side="left", padx=10)
        self.build_frames("Staticface")

    def build_frames_older(self, mode):
        for child in self.container.winfo_children():
            child.destroy()
        self.frames.clear()
        labels = MODES[mode]
        for i, label in enumerate(labels):
            f = ImageFrame(self.container, label, i)
            f.grid(row=0, column=i, padx=5)
            self.frames.append(f)

    def build_frames(self, mode):
        for child in self.container.winfo_children():
            child.destroy()
        self.frames.clear()

        labels = MODES[mode]
        max_per_row = 6  # Anzahl Bilder pro Zeile

        for i, label in enumerate(labels):
            row = i // max_per_row
            col = i % max_per_row
            f = ImageFrame(self.container, label, i)
            f.grid(row=row, column=col, padx=5, pady=5)
            self.frames.append(f)

            # Tooltip nur für Weatherface
            if mode == "Weatherface":
                tiptext = DESCRIPTIONS["Weatherface"].get(label, "")
                Tooltip(f.canvas, tiptext)    

    def change_mode(self, mode):
        self.build_frames(mode)

    def reset_all(self):
        for f in self.frames:
            f.reset_event()

    def export_set(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".tar.gz",
            filetypes=[("tar.gz Archive", "*.tar.gz")],
            title="Store set as..."
        )
        if not file_path:
            return
        output_dir = Path(tempfile.mkdtemp())
        for f in self.frames:
            f.export_bmp(output_dir)
        with tarfile.open(file_path, "w:gz") as tar:
            for bmp in output_dir.glob("*.bmp"):
                tar.add(bmp, arcname=bmp.name)
        messagebox.showinfo("Export done", f"Stored:\n{file_path}")

    def import_set(self):
        file_path = filedialog.askopenfilename(filetypes=[("tar.gz Archive", "*.tar.gz")])
        if not file_path:
            return
        with tempfile.TemporaryDirectory() as tmpdir:
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(tmpdir)
            for f in self.frames:
                bmp_file = Path(tmpdir) / f"{f.label_text}.bmp"
                if bmp_file.exists():
                    f.load_bmp_with_header(bmp_file)
    
    def load_split_image_to_staticface(self):
        if self.mode.get() != "Staticface":
            messagebox.showwarning("Wrong mode", "Please select 'Staticface'-mode.")
            return

        file_path = filedialog.askopenfilename(filetypes=[("Imagefiles", "*.jpg;*.png;*.bmp")])
        if not file_path:
            return

        #full_image = Image.open(file_path).convert("RGB")
        full_image = Image.open(file_path).convert("RGB").resize((WIDTH * 6, HEIGHT), Resampling.LANCZOS)
        img_width, img_height = full_image.size
        parts = 6
        part_width = img_width // parts

        for i in range(parts):
            left = i * part_width
            right = (i + 1) * part_width
            cropped = full_image.crop((left, 0, right, img_height))
            self.frames[i].original = cropped
            self.frames[i].scale = 1.0
            self.frames[i].offset = [0, 0]
            self.frames[i].redraw()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ImageApp()
    app.mainloop()
