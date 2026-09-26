"""A colorful particle heart animation inspired by the Douyin video.

Run with: python particle_heart.py
Press Esc to quit, Space to pause, or F11 to toggle fullscreen.
"""

from __future__ import annotations

import math
import random
import tkinter as tk


BACKGROUND = "#000000"
PALETTE = ("#ff78a8", "#ff9ec2", "#ffd7e5", "#fff2f7", "#cfb4ff", "#a8c8ff")


class ParticleHeart:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Particle Heart")
        self.root.configure(bg=BACKGROUND)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.canvas = tk.Canvas(self.root, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.center_x = self.width * 0.62
        self.center_y = self.height * 0.32
        self.scale = min(self.width * 0.011, self.height * 0.0164)
        self.basin_x = self.center_x
        self.basin_y = self.height * 0.79
        self.text_x = self.width * 0.22
        self.text_y = self.height * 0.5
        self.paused = False
        self.started = False
        self.frame = 0
        self.text_duration = 90
        self.heart_duration = self.text_duration + 100
        self.random = random.Random()
        self.glyphs: list[dict[str, object]] = []
        self.particles = self.make_particles(3000)
        self.drift = self.make_drift(150)
        self.basin = self.make_basin(800)
        self.text_sparks = self.make_text_sparks(48)
        self.show_start_button()

    def show_start_button(self) -> None:
        button = tk.Button(
            self.root,
            text="开始",
            command=self.start,
            font=("Microsoft YaHei UI", 25, "bold"),
            bg="#ff78a8",
            fg="#180912",
            activebackground="#ffd7e5",
            activeforeground="#180912",
            bd=0,
            relief="flat",
            padx=58,
            pady=18,
            cursor="hand2",
            takefocus=True,
        )
        self.start_button = button
        self.canvas.create_window(self.width / 2, self.height / 2,
                                  window=button, tags="start-button")
        self.root.bind("<Return>", lambda _event: self.start())

    def start(self) -> None:
        if self.started:
            return
        self.started = True
        self.start_button.destroy()
        self.canvas.delete("start-button")
        self.draw_slogan()
        self.prepare_particle_items()
        self.animate()

    def draw_slogan(self) -> None:
        columns = ("心之所向", "爱之所往")
        column_gap = min(190, max(120, self.width * 0.13))
        row_gap = min(170, max(115, self.height * 0.16))
        reveal_order = 0
        for column_index, column in enumerate(columns):
            x = self.text_x + (0.5 - column_index) * column_gap
            for row, char in enumerate(column):
                y = self.text_y + (row - 1.5) * row_gap
                shadow = self.canvas.create_text(
                    x + 2, y + 52, text=char, fill="#762c53",
                    font=("Microsoft YaHei UI", 28, "bold"), tags="slogan",
                )
                text = self.canvas.create_text(
                    x, y + 52, text=char, fill="#ff78a8",
                    font=("Microsoft YaHei UI", 28, "bold"), tags="slogan",
                )
                self.glyphs.append({
                    "char": char, "x": x, "y": y, "shadow": shadow, "text": text,
                    "delay": (self.text_duration - 20) * reveal_order / 7,
                    "bursts": [
                        self.canvas.create_line(0, 0, 0, 0, fill=PALETTE[ray],
                                                width=1, state="hidden", tags="burst")
                        for ray in range(4)
                    ],
                })
                reveal_order += 1

    def update_slogan(self) -> None:
        for glyph in self.glyphs:
            age = self.frame - float(glyph["delay"])
            if age < 0:
                for item in glyph["bursts"]:
                    self.canvas.itemconfigure(int(item), state="hidden")
                continue
            progress = min(1.0, age / 16)
            eased = 1 - (1 - progress) ** 3
            bounce = math.sin(progress * math.pi) * (1 - progress)
            target_y = float(glyph["y"])
            y = target_y + (1 - eased) * 52 - bounce * 16
            size = int(28 + 48 * eased + 14 * bounce)
            color_mix = min(1.0, progress * 1.4)
            color = self.mix_color("#ff78a8", "#fff0f6", color_mix)
            font = ("Microsoft YaHei UI", max(28, size), "bold")
            self.canvas.coords(int(glyph["shadow"]), float(glyph["x"]) + 1, y + 2)
            self.canvas.coords(int(glyph["text"]), float(glyph["x"]), y)
            self.canvas.itemconfigure(int(glyph["shadow"]), font=font)
            self.canvas.itemconfigure(int(glyph["text"]), font=font, fill=color)
            # Each arriving character throws a small, short-lived particle burst.
            if 1 <= age <= 7:
                radius = 8 + age * 3
                for ray in range(4):
                    angle = ray * math.tau / 4 + int(glyph["delay"]) * 0.7
                    x1 = float(glyph["x"]) + math.cos(angle) * radius * 0.35
                    y1 = y + math.sin(angle) * radius * 0.35
                    x2 = float(glyph["x"]) + math.cos(angle) * radius
                    y2 = y + math.sin(angle) * radius
                    color_index = (ray + int(age)) % len(PALETTE)
                    item = int(glyph["bursts"][ray])
                    self.canvas.coords(item, x1, y1, x2, y2)
                    self.canvas.itemconfigure(item, fill=PALETTE[color_index], state="normal")
            else:
                for item in glyph["bursts"]:
                    self.canvas.itemconfigure(int(item), state="hidden")

    @staticmethod
    def mix_color(start: str, end: str, amount: float) -> str:
        channels = [
            round(int(start[index:index + 2], 16) * (1 - amount)
                  + int(end[index:index + 2], 16) * amount)
            for index in (1, 3, 5)
        ]
        return "#" + "".join(f"{channel:02x}" for channel in channels)

    def make_text_sparks(self, count: int) -> list[dict[str, float | str]]:
        return [{
            "x": self.random.uniform(self.width * 0.055, self.width * 0.355),
            "y": self.text_y + self.random.choice((-1, 1)) * self.random.uniform(22, 47),
            "speed": self.random.uniform(0.25, 1.1),
            "phase": self.random.random() * math.tau,
            "size": self.random.uniform(0.6, 1.5),
            "color": self.random.choice(PALETTE),
        } for _ in range(count)]

    def make_particles(self, count: int) -> list[dict[str, float | str]]:
        particles = []
        for index in range(count):
            # Sample the classic heart curve, then fill its interior.
            t = self.random.random() * math.tau
            fill = math.sqrt(self.random.random())
            x = 16 * math.sin(t) ** 3 * fill
            y = (13 * math.cos(t) - 5 * math.cos(2 * t)
                 - 2 * math.cos(3 * t) - math.cos(4 * t)) * fill
            depth = self.random.uniform(-1, 1) * math.sqrt(max(0.04, 1 - fill * fill))
            perspective = 1 + depth * 0.13
            tx = self.center_x + x * self.scale * perspective
            ty = self.center_y - y * self.scale * perspective
            particles.append({
                # Gather the cloud at the lower particle band before it rises into a heart.
                "x": self.basin_x + self.random.uniform(-self.scale * 20, self.scale * 20),
                "y": self.basin_y + self.random.gauss(0, self.scale * 2.4),
                "tx": tx,
                "ty": ty,
                "depth": depth,
                "vx": 0.0,
                "vy": 0.0,
                "size": self.random.uniform(0.7, 2.0) * (0.78 + (depth + 1) * 0.22),
                "color": PALETTE[(index + int((depth + 1) * 2)) % len(PALETTE)],
                "phase": self.random.random() * math.tau,
                "orbit": self.random.uniform(0.7, 2.6),
                "shard": self.random.random() < 0.38,
            })
        return particles

    def make_drift(self, count: int) -> list[dict[str, float | str]]:
        return [{
            "x": self.random.uniform(self.center_x - self.scale * 13, self.center_x + self.scale * 13),
            "y": self.random.uniform(self.center_y + self.scale * 10, self.basin_y),
            "speed": self.random.uniform(0.7, 2.5),
            "size": self.random.uniform(0.7, 1.8),
            "phase": self.random.random() * math.tau,
            "color": self.random.choice(PALETTE),
            "shard": self.random.random() < 0.45,
        } for _ in range(count)]

    def make_basin(self, count: int) -> list[dict[str, float | str]]:
        return [{
            "angle": self.random.random() * math.tau,
            "radius": self.random.uniform(0.76, 1.08),
            "speed": self.random.uniform(0.003, 0.009) * self.random.choice((-1, 1)),
            "phase": self.random.random() * math.tau,
            "size": self.random.uniform(0.7, 1.8),
            "color": self.random.choice(PALETTE),
            "shard": self.random.random() < 0.5,
        } for _ in range(count)]

    def prepare_particle_items(self) -> None:
        for particle in (*self.particles, *self.drift, *self.basin, *self.text_sparks):
            color = str(particle["color"])
            shard = bool(particle.get("shard", True))
            if shard:
                particle["item"] = self.canvas.create_line(
                    0, 0, 0, 0, fill=color, width=1, tags="particle"
                )
            else:
                particle["item"] = self.canvas.create_oval(
                    0, 0, 0, 0, fill=color, outline="", tags="particle"
                )

    def draw_speck(self, particle: dict[str, float | str], x: float, y: float,
                   size: float, phase: float, shard: bool) -> None:
        item = int(particle["item"])
        if shard:
            angle = phase + self.frame * 0.012
            dx = math.cos(angle) * size * 2.4
            dy = math.sin(angle) * size * 2.4
            self.canvas.coords(item, x - dx, y - dy, x + dx, y + dy)
        else:
            self.canvas.coords(item, x-size, y-size, x+size, y+size)

    def animate(self) -> None:
        if self.frame >= self.heart_duration:
            return
        if not self.paused:
            self.frame += 1
            motion = max(0.0, 1 - self.frame / self.heart_duration)
            text_motion = max(0.0, 1 - self.frame / self.text_duration)
            pulse = 1 + 0.028 * math.sin(self.frame * 0.035) * motion
            for particle in self.particles:
                x, y = float(particle["x"]), float(particle["y"])
                phase = self.frame * 0.025 + float(particle["phase"])
                depth = float(particle["depth"])
                orbit = float(particle["orbit"])
                tx = self.center_x + (float(particle["tx"]) - self.center_x) * pulse
                ty = self.center_y + (float(particle["ty"]) - self.center_y) * pulse
                # Parallax makes the near and far layers shift independently.
                tx += depth * self.scale * 2.2 * math.sin(self.frame * 0.018) * motion
                ty += depth * self.scale * 1.1 * math.cos(self.frame * 0.018) * motion
                tx += math.sin(phase * 0.8) * orbit * (0.6 + depth * 0.25) * motion
                ty += math.cos(phase) * orbit * 0.65 * motion
                vx = (float(particle["vx"]) + (tx - x) * 0.012) * 0.94
                vy = (float(particle["vy"]) + (ty - y) * 0.012) * 0.94
                x += vx
                y += vy
                particle["x"], particle["y"] = x, y
                particle["vx"], particle["vy"] = vx, vy
                twinkle = 0.68 + 0.32 * math.sin(self.frame * 0.075 + float(particle["phase"]))
                radius = float(particle["size"]) * twinkle
                self.draw_speck(particle, x, y, radius,
                                float(particle["phase"]), bool(particle["shard"]))

            for particle in self.drift:
                particle["y"] = float(particle["y"]) + float(particle["speed"]) * motion
                particle["x"] = float(particle["x"]) + math.sin(self.frame * 0.025 + float(particle["phase"])) * 0.65 * motion
                if float(particle["y"]) > self.height:
                    particle["y"] = self.center_y + self.scale * self.random.uniform(8, 14)
                    particle["x"] = self.center_x + self.random.uniform(-self.scale * 12, self.scale * 12)
                x, y = float(particle["x"]), float(particle["y"])
                r = float(particle["size"])
                self.draw_speck(particle, x, y, r,
                                float(particle["phase"]), bool(particle["shard"]))

            for particle in self.basin:
                angle = float(particle["angle"]) + self.frame * float(particle["speed"]) * motion
                radius = float(particle["radius"])
                wobble = math.sin(self.frame * 0.035 + float(particle["phase"]))
                x = self.basin_x + math.cos(angle) * self.scale * 19 * radius
                y = self.basin_y + math.sin(angle) * self.scale * 4.2 * radius + wobble * 4 * motion
                # The center catches falling fragments like a shallow particle vortex.
                x += math.sin(self.frame * 0.018 + float(particle["phase"])) * 2.5 * motion
                self.draw_speck(particle, x, y, float(particle["size"]),
                                angle, bool(particle["shard"]))
            for particle in self.text_sparks:
                particle["x"] = float(particle["x"]) + float(particle["speed"]) * text_motion
                if float(particle["x"]) > self.width * 0.37:
                    particle["x"] = self.width * 0.05
                y = float(particle["y"]) + math.sin(
                    self.frame * 0.045 + float(particle["phase"])
                ) * 2 * text_motion
                self.draw_speck(particle, float(particle["x"]), y, float(particle["size"]),
                                float(particle["phase"]), True)
            self.update_slogan()
            self.canvas.tag_raise("slogan")
        self.root.after(50, self.animate)

    def toggle_pause(self, _event: tk.Event) -> None:
        self.paused = not self.paused

    def toggle_fullscreen(self, _event: tk.Event) -> None:
        current = bool(self.root.attributes("-fullscreen"))
        self.root.attributes("-fullscreen", not current)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    ParticleHeart().run()
