# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2025 Sam Blenny
from board import CKP, CKN, D0P, D0N, D1P, D1N, D2P, D2N
import displayio
from displayio import Bitmap, Group, Palette, TileGrid
import framebufferio
import gc
import math
import picodvi
import supervisor
from time import sleep


# Set LOWRES to True for 320x240 RGB332 or False for 640x480 RGB332
LOWRES = True
if LOWRES:
    (width, height, color_depth) = (320, 240, 8)
else:
    (width, height, color_depth) = (640, 480, 8)
# Make sure display is initialized for the requested video mode
display = supervisor.runtime.display
if (width, height) != (display.width, display.height):
    print("re-initializing display")
    displayio.release_displays()
    gc.collect()
    fb = picodvi.Framebuffer(width, height, clk_dp=CKP, clk_dn=CKN,
        red_dp=D0P, red_dn=D0N, green_dp=D1P, green_dn=D1N,
        blue_dp=D2P, blue_dn=D2N, color_depth=color_depth)
    display = framebufferio.FramebufferDisplay(fb)
    supervisor.runtime.display = display
else:
    print("using existing display")
display.auto_refresh = False
grp = Group(scale=1)
display.root_group = grp

# Make bitmap + palette + tilegrid so we have a canvas to draw on
palette_size = 1 << color_depth
bitmap = Bitmap(width, height, palette_size)
palette = Palette(palette_size)
for i in range(palette_size):
    # Expand 8-bit RGB332 (i) into a 24-bit RGB888 tuple (r, g, b)
    r = i & 0xE0
    g = (i & 0x1C) << 3
    b = (i & 0x03) << 6
    palette[i] = (r, g, b)
tilegrid = TileGrid(bitmap, pixel_shader=palette)
grp.append(tilegrid)

def draw_spiral(a, b, h, cycles=64, oversample=2, delay_ms=1, end_pause_s=5):
    """Draw a Hypotrochoid spiral
    a: outer circle radius in pixels
    b: inner circle radius in pixels
    h: drawing pen radius in pixels from center of inner circle
    cycles: how many 360 degree cycles to run the equations through
    oversample: increase this to make the pixel density higher
    delay_ms: increase this to draw slower (unit: ms)
    end_pause_s: increase this to pause for longer at the end (unit: seconds)
    """
    global bitmap
    global display
    # Cache functions as local vars with short names to improve readability
    rad = math.radians
    sin = math.sin
    cos = math.cos
    # Translate origin of graph to center of the display
    (x0, y0) = (width / 2, height / 2)
    # Clear the bitmap, then start drawing the hypotrochoid spiral
    bitmap.fill(0)
    for t in range(cycles * 360 * oversample):
        color = (t >> 1) & 0xff  # this cycles through all the palette colors
        tr = rad(t/oversample)
        x = round(x0 + (a - b) * cos(tr) + h * cos((a - b) / b * tr))
        y = round(y0 + (a - b) * sin(tr) - h * sin((a - b) / b * tr))
        if (0 <= x < width) and (0 <= y < height):
            bitmap[x, y] = color
            display.refresh()
        # This delay controls the pen movement speed
        sleep(0.001 * delay_ms)
    # This delay pauses at the end so you can see the final image
    sleep(end_pause_s)

# Sleep after drawing is done to prevent supervisor from erasing display
while True:
    draw_spiral(a=110, b=12, h=11, cycles=6, delay_ms=3)
    draw_spiral(a=160, b=80, h=10, cycles=1, delay_ms=3)
    draw_spiral(a=111, b=25, h=9, cycles=6, delay_ms=3)
    draw_spiral(a=111, b=25, h=29, cycles=27)
