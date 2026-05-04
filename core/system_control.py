"""System controls: real/fallback volume and safe mouse control."""

import time
import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0


class VolumeController:
    """
    Real volume controller.

    First tries pycaw exact dB control. If pycaw fails, it still controls the
    laptop volume using Windows media keys: volumeup / volumedown.
    """

    def __init__(self):
        self.mode = "media_keys"
        self.simulated = 50
        self._last_key_time = 0.0
        self._key_delay = 0.06
        self._volume_ctrl = None
        self._vol_range = (-65.25, 0.0, 0.03125)
        self._init_pycaw()

    def _init_pycaw(self):
        """Try pycaw initialization, with safe fallback to media keys."""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            speakers = AudioUtilities.GetSpeakers()
            interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
            self._vol_range = self._volume_ctrl.GetVolumeRange()
            self.mode = "pycaw"
            print("[Volume] Real pycaw volume enabled.")
        except Exception as exc:
            self.mode = "media_keys"
            self._volume_ctrl = None
            print(f"[Volume] pycaw unavailable: {exc}")
            print("[Volume] Using real Windows media keys fallback.")

    def set_percent(self, percent):
        """Set volume percentage. Uses exact pycaw or real media keys fallback."""
        percent = int(max(0, min(100, percent)))

        if self.mode == "pycaw" and self._volume_ctrl:
            try:
                min_db, max_db, _ = self._vol_range
                db = min_db + (max_db - min_db) * (percent / 100.0)
                self._volume_ctrl.SetMasterVolumeLevel(db, None)
                self.simulated = percent
                return
            except Exception as exc:
                print(f"[Volume] pycaw set failed, switching to media keys: {exc}")
                self.mode = "media_keys"

        # Fallback: real OS media keys. It is less exact but changes laptop volume.
        now = time.time()
        if now - self._last_key_time < self._key_delay:
            return

        diff = percent - self.simulated
        if abs(diff) >= 3:
            key = "volumeup" if diff > 0 else "volumedown"
            presses = min(3, max(1, abs(diff) // 8))
            for _ in range(int(presses)):
                pyautogui.press(key)
            self.simulated += presses * (4 if diff > 0 else -4)
            self.simulated = int(max(0, min(100, self.simulated)))
            self._last_key_time = now

    def get_percent(self):
        """Return current or simulated volume percentage."""
        if self.mode == "pycaw" and self._volume_ctrl:
            try:
                db = self._volume_ctrl.GetMasterVolumeLevel()
                min_db, max_db, _ = self._vol_range
                self.simulated = int((db - min_db) / (max_db - min_db) * 100)
            except Exception:
                pass
        return int(max(0, min(100, self.simulated)))


class MouseController:
    """Safe and smooth cursor control using hand landmark coordinates."""

    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self.prev_x = None
        self.prev_y = None
        self.smoothing = 0.22
        self.last_click = 0.0
        self.click_delay = 0.45

    def reset(self):
        """Reset smoothing state."""
        self.prev_x = None
        self.prev_y = None

    def move(self, x, y, frame_w, frame_h):
        """Map hand position to screen position with safe borders."""
        margin_x = int(frame_w * 0.20)
        margin_y = int(frame_h * 0.20)
        active_w = max(1, frame_w - 2 * margin_x)
        active_h = max(1, frame_h - 2 * margin_y)

        nx = (x - margin_x) / active_w
        ny = (y - margin_y) / active_h
        nx = max(0.02, min(0.98, nx))
        ny = max(0.02, min(0.98, ny))

        target_x = nx * self.screen_w
        target_y = ny * self.screen_h

        if self.prev_x is None:
            self.prev_x, self.prev_y = target_x, target_y
        else:
            self.prev_x = self.prev_x * (1 - self.smoothing) + target_x * self.smoothing
            self.prev_y = self.prev_y * (1 - self.smoothing) + target_y * self.smoothing

        border = 25
        sx = int(max(border, min(self.screen_w - border, self.prev_x)))
        sy = int(max(border, min(self.screen_h - border, self.prev_y)))
        pyautogui.moveTo(sx, sy)

    def click(self):
        """Debounced left click."""
        now = time.time()
        if now - self.last_click > self.click_delay:
            pyautogui.click()
            self.last_click = now
