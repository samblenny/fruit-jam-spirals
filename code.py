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


def draw_spiral(a, b, h, cycles=64, oversample=2, delay_ms=1):
    """Draw a Hypotrochoid spiral
    a: outer circle radius in pixels
    b: inner circle radius in pixels
    h: drawing pen radius in pixels from center of inner circle
    cycles: how many 360 degree cycles to run the equations through
    oversample: increase this to make the pixel density higher
    delay_ms: increase this to draw slower (unit: ms)
    """
    global bitmap
    global display
    global palette
    # Alias trig functions with short names to improve equation readability
    rad = math.radians
    sin = math.sin
    cos = math.cos
    # Translate origin of graph to center of the display
    (x0, y0) = (width / 2, height / 2)
    # Clear the bitmap, then start drawing the hypotrochoid spiral
    bitmap.fill(0)
    max_color = len(palette)
    for t in range(cycles * 360 * oversample):
        color = (t // oversample) % max_color  # Cycle through all colors
        tr = rad(t/oversample)
        x = round(x0 + (a - b) * cos(tr) + h * cos((a - b) / b * tr))
        y = round(y0 + (a - b) * sin(tr) - h * sin((a - b) / b * tr))
        if (0 <= x < width) and (0 <= y < height):
            bitmap[x, y] = color
            display.refresh()
        # This delay controls the pen movement speed
        sleep(0.001 * delay_ms)
    # This delay pauses at the end so you can see the final image
    sleep(5)

def init_display(width, height, color_depth):
    """Initialize the picodvi display
    Video mode compatibility (only tested these--unsure about other boards):
    | Video Mode     | Fruit Jam | Metro RP2350 No PSRAM    |
    | -------------- | --------- | ------------------------ |
    | 320x240, 8-bit | Yes!      | Yes!                     |
    | 640x480, 8-bit | Yes!      | MemoryError exception :( |
    """
    displayio.release_displays()
    gc.collect()
    fb = picodvi.Framebuffer(width, height, clk_dp=CKP, clk_dn=CKN,
        red_dp=D0P, red_dn=D0N, green_dp=D1P, green_dn=D1N,
        blue_dp=D2P, blue_dn=D2N, color_depth=color_depth)
    display = framebufferio.FramebufferDisplay(fb)
    supervisor.runtime.display = display
    return display


# Pick a video mode (comment out the one you don't want):
(width, height, color_depth) = (320, 240, 8)
#(width, height, color_depth) = (640, 480, 8)    # This needs board with PSRAM

# Detect if an existing display matches requested video mode
display = supervisor.runtime.display
if (display is None) or (width, height) != (display.width, display.height):
    # Didn't find a display configured as we need, so initialize a new one
    try:
        display = init_display(width, height, color_depth)
    except MemoryError as e:
        # Fall back to low resolution so the error message will be readable
        display = init_display(320, 240, 8)
        print("---\nREQUESTED VIDEO MODE NEEDS A BOARD WITH PSRAM\n---")
        raise e
# Use manual refresh for better performance
display.auto_refresh = False
grp = Group(scale=1)
display.root_group = grp

# Arrange a bitmap + palette + tilegrid so we have a canvas to draw on. The
# pallet gets initialized with all 256 of the RGB332 colors.
palette = Palette(256)
bitmap = Bitmap(width, height, 256)
for i in range(256):
    # Expand 8-bit RGB332 (i) into a 24-bit RGB888 tuple (r, g, b)
    r = i & 0xE0
    g = (i & 0x1C) << 3
    b = (i & 0x03) << 6
    palette[i] = (r, g, b)
tilegrid = TileGrid(bitmap, pixel_shader=palette)
grp.append(tilegrid)

# Draw stuff (includes a brief pause after each spiral is done)
while True:
    draw_spiral(a=110, b=12, h=11, cycles=6, oversample=3, delay_ms=3)
    draw_spiral(a=111, b=25, h=9, cycles=6, delay_ms=3)
    draw_spiral(a=111, b=25, h=29, cycles=27, oversample=3)
