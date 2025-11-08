#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ساعت تمام‌صفحه با ۴ مود:
1️⃣ Analog Clock
2️⃣ Digital Orange
3️⃣ Digital Green
4️⃣ Timer Mode (با کنترل کلیدها)

کلیدها:
- M : تغییر مود
- ↑ ↓ ← → : تنظیم تایمر
- Space : شروع/توقف تایمر
- R : ریست تایمر
- Esc : خروج
"""

import tkinter as tk
import time
import math

class ClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clock + Timer")
        self.attributes("-fullscreen", True)
        self.configure(bg="black")

        # کلیدها
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<m>", self.toggle_mode)
        self.bind("<Up>", lambda e: self.adjust_timer(minutes=1))
        self.bind("<Down>", lambda e: self.adjust_timer(minutes=-1))
        self.bind("<Left>", lambda e: self.adjust_timer(seconds=-10))
        self.bind("<Right>", lambda e: self.adjust_timer(seconds=10))
        self.bind("<space>", lambda e: self.toggle_timer())
        self.bind("<r>", lambda e: self.reset_timer())

        # Canvas
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # حالت‌ها
        self.modes = ["analog", "digital_orange", "digital_green", "timer"]
        self.mode_index = 0
        self.mode = self.modes[self.mode_index]

        self.cx = self.cy = self.radius = 0
        self.digital_label = None

        # تایمر
        self.timer_seconds = 0
        self.timer_running = False
        self.timer_text = None
        self.timer_flash = False

        self.canvas.bind("<Configure>", self.on_resize)
        self.on_resize(None)
        self.update_clock()

    # 🔄 تغییر مود
    def toggle_mode(self, event=None):
        self.mode_index = (self.mode_index + 1) % len(self.modes)
        self.mode = self.modes[self.mode_index]
        self.on_resize(None)

    # 🎨 تنظیم اندازه
    def on_resize(self, event):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.width, self.height = max(200, w), max(200, h)
        self.radius = int(min(self.width, self.height) * 0.42)
        self.cx, self.cy = self.width // 2, self.height // 2

        if self.mode == "analog":
            self.draw_face()
        elif self.mode.startswith("digital"):
            self.draw_digital()
        else:
            self.draw_timer()

    # ================= حالت آنالوگ =================
    def draw_face(self):
        c = self.canvas
        cx, cy, r = self.cx, self.cy, self.radius
        # قاب
        c.create_oval(cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10,
                      outline="#444444", width=4)
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill="#f8f5e6", outline="#222222", width=2)
        # خطوط دقیقه و ساعت
        for i in range(60):
            a = math.radians(i * 6 - 90)
            x1 = cx + math.cos(a) * (r * (0.9 if i % 5 else 0.8))
            y1 = cy + math.sin(a) * (r * (0.9 if i % 5 else 0.8))
            x2 = cx + math.cos(a) * r
            y2 = cy + math.sin(a) * r
            c.create_line(x1, y1, x2, y2, width=3 if i % 5 == 0 else 1)
        # اعداد
        fnt = ("Times New Roman", int(r * 0.13), "bold")
        for h in range(1, 13):
            a = math.radians(h * 30 - 90)
            x = cx + math.cos(a) * (r * 0.72)
            y = cy + math.sin(a) * (r * 0.72)
            c.create_text(x, y, text=str(h), font=fnt)
        c.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill="#111111")

    def update_analog(self):
        now = time.localtime()
        h, m, s = now.tm_hour % 12, now.tm_min, now.tm_sec
        def ang_to_xy(a, l):
            a = math.radians(a - 90)
            return self.cx + math.cos(a)*l, self.cy + math.sin(a)*l

        self.canvas.delete("hands")
        # ساعت
        hx, hy = ang_to_xy(h*30 + m*0.5, self.radius*0.5)
        self.canvas.create_line(self.cx, self.cy, hx, hy, width=8,
                                fill="#222222", capstyle=tk.ROUND, tags="hands")
        # دقیقه
        mx, my = ang_to_xy(m*6 + s*0.1, self.radius*0.75)
        self.canvas.create_line(self.cx, self.cy, mx, my, width=5,
                                fill="#111111", capstyle=tk.ROUND, tags="hands")
        # ثانیه
        sx, sy = ang_to_xy(s*6, self.radius*0.85)
        self.canvas.create_line(self.cx, self.cy, sx, sy, width=2,
                                fill="#b30000", capstyle=tk.ROUND, tags="hands")

    # ================= حالت دیجیتال =================
    def draw_digital(self):
        color = "#ff6600" if self.mode == "digital_orange" else "#00ff00"
        self.canvas.delete("all")
        font_size = int(self.height * 0.25)
        self.digital_label = self.canvas.create_text(
            self.width // 2, self.height // 2,
            text="--:--:--",
            fill=color,
            font=("Courier", font_size, "bold")
        )

    def update_digital(self):
        now = time.strftime("%H:%M:%S")
        if self.digital_label:
            self.canvas.itemconfigure(self.digital_label, text=now)

    # ================= حالت تایمر =================
    def draw_timer(self):
        self.canvas.delete("all")
        self.timer_text = self.canvas.create_text(
            self.width // 2, self.height // 2,
            text="00:00",
            fill="#00bfff",  # آبی نئون
            font=("Courier", int(self.height * 0.25), "bold")
        )
        # راهنما
        self.canvas.create_text(
            self.width // 2, self.height * 0.8,
            text="↑↓ دقیقه | ←→ ثانیه | Space شروع/توقف | R ریست",
            fill="#0099ff", font=("Arial", 18)
        )

    def adjust_timer(self, minutes=0, seconds=0):
        if self.mode != "timer" or self.timer_running:
            return
        self.timer_seconds = max(0, self.timer_seconds + minutes*60 + seconds)
        self.update_timer_display()

    def toggle_timer(self):
        if self.mode == "timer":
            self.timer_running = not self.timer_running

    def reset_timer(self):
        if self.mode == "timer":
            self.timer_running = False
            self.timer_seconds = 0
            self.update_timer_display()

    def update_timer_display(self):
        mins, secs = divmod(self.timer_seconds, 60)
        t = f"{mins:02}:{secs:02}"
        self.canvas.itemconfigure(self.timer_text, text=t)

    def update_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_display()
        elif self.timer_running and self.timer_seconds == 0:
            # هشدار پایان
            self.timer_running = False
            self.flash_timer()

    def flash_timer(self):
        # افکت چشمک برای اتمام تایمر
        if self.mode != "timer":
            return
        self.timer_flash = not self.timer_flash
        color = "#ff0000" if self.timer_flash else "#000000"
        self.canvas.itemconfigure(self.timer_text, fill=color)
        if not self.timer_running:
            self.after(400, self.flash_timer)

    # ================= بروزرسانی کلی =================
    def update_clock(self):
        if self.mode == "analog":
            self.update_analog()
        elif self.mode.startswith("digital"):
            self.update_digital()
        else:
            self.update_timer()
        self.after(1000, self.update_clock)


if __name__ == "__main__":
    ClockApp().mainloop()

