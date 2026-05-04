"""DSP Project GUI: Filters, Move Mouse, and Volume Control only."""

import time
import threading
import cv2
import customtkinter as ctk
from PIL import Image, ImageTk

from core.camera import Camera
from core.hand_tracking import HandTracker
from core.dsp_filters import DSPFilters, FILTERS
from core.system_control import VolumeController, MouseController
from core.gesture import normalized_pinch, is_mouse_move_gesture, is_click_gesture, pinch_distance, fingers_up
from core.overlay import draw_hud

MODE_DSP = "Filters"
MODE_MOUSE = "Move Mouse"
MODE_VOLUME = "Volume Control"
MODES = [MODE_DSP, MODE_MOUSE, MODE_VOLUME]

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """Main desktop application."""

    def __init__(self):
        super().__init__()
        self.title("DSP Project | Filters / Move Mouse / Volume Control")
        self.geometry("1280x780")
        self.minsize(1050, 650)
        self.configure(fg_color="#070914")

        self.camera = Camera(camera_index=0)
        self.hand_tracker = HandTracker()
        self.dsp = DSPFilters()
        self.volume = VolumeController()
        self.mouse = MouseController()

        self.mode = ctk.StringVar(value=MODE_DSP)
        self.dsp_filter = ctk.StringVar(value="None")
        self.show_landmarks = ctk.BooleanVar(value=True)
        self.mirror_view = ctk.BooleanVar(value=True)
        self.camera_index = ctk.IntVar(value=0)

        self.running = False
        self.current_frame = None
        self.last_frame_time = time.time()
        self.fps = 0.0
        self.status = "Ready"

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        """Create all GUI widgets."""
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, width=245, corner_radius=0, fg_color="#0f1424")
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)

        ctk.CTkLabel(left, text="DSP Project", font=ctk.CTkFont(size=24, weight="bold"), text_color="#4dd8ff").pack(anchor="w", padx=18, pady=(18, 2))
        ctk.CTkLabel(left, text="Filters • Move Mouse • Volume", font=ctk.CTkFont(size=12), text_color="#8290aa").pack(anchor="w", padx=18, pady=(0, 14))

        self.btn_start = ctk.CTkButton(left, text="▶ Start Camera", command=self.start_camera, fg_color="#167a4a")
        self.btn_start.pack(fill="x", padx=18, pady=5)
        self.btn_stop = ctk.CTkButton(left, text="■ Stop Camera", command=self.stop_camera, fg_color="#8a2525", state="disabled")
        self.btn_stop.pack(fill="x", padx=18, pady=5)
        ctk.CTkLabel(left, text="Camera Index", text_color="#aab6d6").pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkSegmentedButton(left, values=["0", "1", "2"], command=self._set_camera_index).pack(fill="x", padx=18, pady=4)

        ctk.CTkLabel(left, text="MODE", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8fa6ff").pack(anchor="w", padx=18, pady=(20, 5))
        for m in MODES:
            ctk.CTkRadioButton(left, text=m, variable=self.mode, value=m, command=self._mode_changed).pack(anchor="w", padx=24, pady=6)

        ctk.CTkCheckBox(left, text="Mirror View", variable=self.mirror_view).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkCheckBox(left, text="Show Hand Landmarks", variable=self.show_landmarks).pack(anchor="w", padx=24, pady=4)

        center = ctk.CTkFrame(self, fg_color="#070914", corner_radius=0)
        center.grid(row=0, column=1, sticky="nsew")
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=1)
        self.preview = ctk.CTkLabel(center, text="\n\nCamera Preview\nPress Start Camera", font=ctk.CTkFont(size=24, weight="bold"), text_color="#4c5b7a", fg_color="#050713")
        self.preview.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        right = ctk.CTkFrame(self, width=290, corner_radius=0, fg_color="#0f1424")
        right.grid(row=0, column=2, sticky="nsew")
        right.grid_propagate(False)

        ctk.CTkLabel(right, text="FILTERS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8fa6ff").pack(anchor="w", padx=18, pady=(18, 5))
        ctk.CTkOptionMenu(right, values=FILTERS, variable=self.dsp_filter).pack(fill="x", padx=18, pady=5)

        ctk.CTkLabel(right, text="How To Use", font=ctk.CTkFont(size=15, weight="bold"), text_color="#4dd8ff").pack(anchor="w", padx=18, pady=(24, 8))
        help_text = (
            "Filters:\n"
            "• Choose any DSP filter from dropdown.\n"
            "• Includes resize, crop, rotate, flip, HSV, noise, Pillow filters, edges, brightness, and contrast.\n\n"
            "Move Mouse:\n"
            "• Raise index finger to move.\n"
            "• Index + middle close = click.\n\n"
            "Volume Control:\n"
            "• Move thumb and index apart.\n"
            "• Close = low volume.\n"
            "• Far = high volume."
        )
        ctk.CTkLabel(right, text=help_text, justify="left", anchor="w", text_color="#c8d4ee", font=ctk.CTkFont(size=13)).pack(fill="x", padx=18, pady=5)

        self.status_box = ctk.CTkTextbox(right, height=170, fg_color="#070914", text_color="#dce8ff")
        self.status_box.pack(fill="x", padx=18, pady=(18, 5))
        self._update_status_box()

    def _set_camera_index(self, value):
        """Change camera index from segmented button."""
        try:
            self.camera_index.set(int(value))
        except Exception:
            self.camera_index.set(0)

    def _mode_changed(self):
        """Reset state when switching modes."""
        self.mouse.reset()
        self.status = f"Mode changed to {self.mode.get()}"

    def start_camera(self):
        """Start camera loop in a background thread."""
        if self.running:
            return
        self.camera.camera_index = self.camera_index.get()
        if not self.camera.open():
            self.status = "Camera failed. Try index 1 or 2."
            self._update_status_box()
            return
        self.running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        threading.Thread(target=self._loop, daemon=True).start()

    def stop_camera(self):
        """Stop camera loop."""
        self.running = False
        self.camera.release()
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.status = "Camera stopped"
        self._update_status_box()

    def _loop(self):
        """Read, process, and display frames."""
        while self.running:
            ok, frame = self.camera.read()
            if not ok or frame is None:
                self.status = "Frame read failed"
                break

            if self.mirror_view.get():
                frame = cv2.flip(frame, 1)

            now = time.time()
            self.fps = 1.0 / max(now - self.last_frame_time, 1e-6)
            self.last_frame_time = now

            mode = self.mode.get()
            status = "No hand detected"
            volume_percent = None

            if mode == MODE_DSP:
                frame = self.dsp.apply(frame, self.dsp_filter.get())
                status = "DSP filter applied"

            else:
                frame, hands = self.hand_tracker.process(frame, draw=self.show_landmarks.get())
                if hands:
                    pts = hands[0]
                    h, w = frame.shape[:2]

                    if mode == MODE_VOLUME:
                        ratio = normalized_pinch(pts)
                        # Practical mapping after testing: 0.25 close, 1.9 far.
                        percent = int(max(0, min(100, (ratio - 0.25) / (1.9 - 0.25) * 100)))
                        self.volume.set_percent(percent)
                        volume_percent = self.volume.get_percent()
                        pd = pinch_distance(pts)
                        cv2.line(frame, (pts[4]["x"], pts[4]["y"]), (pts[8]["x"], pts[8]["y"]), (0, 220, 255), 4)
                        cv2.circle(frame, (pts[4]["x"], pts[4]["y"]), 10, (0, 220, 255), -1)
                        cv2.circle(frame, (pts[8]["x"], pts[8]["y"]), 10, (0, 220, 255), -1)
                        status = f"Pinch distance: {int(pd)} | Volume backend: {self.volume.mode}"

                    elif mode == MODE_MOUSE:
                        f = fingers_up(pts)
                        if is_mouse_move_gesture(pts):
                            self.mouse.move(pts[8]["x"], pts[8]["y"], w, h)
                            status = "Moving mouse"
                        else:
                            status = "Raise index only to move"

                        if is_click_gesture(pts):
                            self.mouse.click()
                            status = "Click"

                        cv2.circle(frame, (pts[8]["x"], pts[8]["y"]), 12, (60, 255, 100), -1)
                        cv2.putText(frame, f"Fingers: {f}", (20, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            frame = draw_hud(frame, mode, status, self.fps, volume=volume_percent, filter_name=self.dsp_filter.get() if mode == MODE_DSP else None)
            self.current_frame = frame.copy()
            self._display(frame)
            self.status = status
            self._update_status_box()

        self.stop_camera()

    def _display(self, frame_bgr):
        """Display OpenCV BGR frame in CustomTkinter."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        max_w = max(640, self.preview.winfo_width())
        max_h = max(480, self.preview.winfo_height())
        img.thumbnail((max_w, max_h))
        imgtk = ImageTk.PhotoImage(img)
        self.preview.configure(image=imgtk, text="")
        self.preview.image = imgtk

    def _update_status_box(self):
        """Update side status text."""
        if not hasattr(self, "status_box"):
            return
        text = (
            f"Mode: {self.mode.get()}\n"
            f"Status: {self.status}\n"
            f"FPS: {self.fps:.1f}\n"
            f"Selected Filter: {self.dsp_filter.get()}\n"
            f"Volume Backend: {self.volume.mode}\n"
            f"Volume: {self.volume.get_percent()}%\n"
        )
        self.status_box.delete("1.0", "end")
        self.status_box.insert("1.0", text)

    def on_close(self):
        """Close safely."""
        self.running = False
        self.camera.release()
        self.destroy()
