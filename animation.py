#!/usr/bin/env python3
"""ASHIF - animated ASCII AK-47 with muzzle flash, bullets and sparks.
Run in a terminal at least 100 columns wide:  python3 animation.py
Ctrl+C to quit."""
import random, sys, time

W, H = 100, 14
GUN = [
    r"        __________________________________",
    r" ______/____|______________________|=====|=====o==",
    r"|_____________|  _____  |===========|__|",
    r" \__   ____/ |_/     \_|_|_|_|_|_|_|_|",
    r"    / /\ \    \_____/",
    r"   / /  \ \ ",
    r"  /_/    \_\ ",
]
FONT = {
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #"],
    "I": ["###", " # ", " # ", " # ", "###"],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
    "H": ["#   #", "#   #", "#####", "#   #", "#   #"],
    "U": ["#   #", "#   #", "#   #", "#   #", " ### "],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #"],
    "A": [" ### ", "#   #", "#####", "#   #", "#   #"],
    "S": [" ####", "#    ", " ### ", "    #", "#### "],
    "F": ["#####", "#    ", "#### ", "#    ", "#    "],
}
NAME = "ASHIF"
GX, GY = 1, 2            # gun position
BX, BY = 64, 1           # banner position
FIRE_EVERY = 14
COLORS = {"g": "37", "b": "36", "y": "93", "r": "91", "w": "97", "o": "33"}

# letter x offsets inside the banner
offs, x = [], 0
for ch in NAME:
    offs.append(x)
    x += len(FONT[ch][0]) + 1

def run(max_frames=None):
    bullets, sparks = [], []
    flash = recoil = tick = hits = 0
    glow = [0] * len(NAME)
    muzzle_x = GX + len(GUN[1])
    barrel_y = GY + 1
    while max_frames is None or tick < max_frames:
        # --- fire ---
        if tick % FIRE_EVERY == 0:
            flash, recoil = 3, 2
            bullets.append([muzzle_x + 1, barrel_y])
            sparks.append([GX + 22, GY, 0.4, -0.5, 6, ","])   # shell casing
        # --- update ---
        for b in bullets[:]:
            b[0] += 4
            if b[0] >= BX:
                bullets.remove(b)
                glow[hits % len(NAME)] = 10
                hits += 1
                for _ in range(14):
                    sparks.append([BX, b[1], random.uniform(-1.8, 0.2),
                                   random.uniform(-1.2, 1.2), random.randint(5, 11),
                                   random.choice("*+.'`x")])
        for s in sparks[:]:
            s[0] += s[2]; s[1] += s[3]; s[3] += 0.12; s[4] -= 1
            if s[4] <= 0 or not (0 <= s[0] < W and 0 <= s[1] < H):
                sparks.remove(s)
        glow = [max(0, g - 1) for g in glow]
        # --- draw ---
        grid = [[(" ", "g")] * W for _ in range(H)]
        def put(px, py, ch, col):
            px, py = int(round(px)), int(round(py))
            if 0 <= px < W and 0 <= py < H and ch != " ":
                grid[py][px] = (ch, col)
        ox = GX - (1 if recoil else 0)
        for r, line in enumerate(GUN):
            for c, ch in enumerate(line):
                put(ox + c, GY + r, ch, "g")
        for i, ch in enumerate(NAME):
            for r, line in enumerate(FONT[ch]):
                for c, p in enumerate(line):
                    if p == "#":
                        put(BX + offs[i] + c, BY + r, "@" if glow[i] else "#",
                            "y" if glow[i] else "b")
        if flash:
            mx, my = muzzle_x + 1, barrel_y
            for dx, dy, ch in [(0, 0, "*"), (1, 0, "*"), (2, 0, "-"), (1, -1, "\\"),
                               (1, 1, "/"), (3, 0, "="), (0, -1, "'"), (0, 1, ".")]:
                put(mx + dx, my + dy, ch, "r" if dx < 2 else "y")
        for b in bullets:
            put(b[0], b[1], "=", "w"); put(b[0] - 1, b[1], "-", "w")
        for s in sparks:
            put(s[0], s[1], s[5], "y" if s[4] > 3 else "o")
        title = f"- {NAME.lower()} -   hits: {hits}"
        for i, ch in enumerate(title):
            put(BX + 3 + i, BY + 7, ch, "w")
        out, cur = ["\033[H"], None
        for row in grid:
            for ch, col in row:
                if col != cur:
                    out.append(f"\033[{COLORS[col]}m"); cur = col
                out.append(ch)
            out.append("\033[0m\n"); cur = None
        sys.stdout.write("".join(out)); sys.stdout.flush()
        flash = max(0, flash - 1); recoil = max(0, recoil - 1); tick += 1
        if max_frames is None:
            time.sleep(0.05)

if __name__ == "__main__":
    n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--frames" else None
    sys.stdout.write("\033[2J\033[?25l")
    try:
        run(n)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[0m\033[?25h\n")
