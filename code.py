# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2025 Sam Blenny
#
# Fruit Jam Spirals
#
from board import CKP, CKN, D0P, D0N, D1P, D1N, D2P, D2N
import displayio
from displayio import Bitmap, Group, Palette, TileGrid
import framebufferio
import gc
import picodvi
import supervisor
from time import sleep


# Make sure display is initialized for the video mode
width = 320
height = 240
color_depth = 8
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
bitmap = Bitmap(width, height, 256)
palette = Palette(256)
for i in range(len(palette)):
    palette[i] = i
tilegrid = TileGrid(bitmap, pixel_shader=palette)
grp.append(tilegrid)

# TODO: DRAW SPIRALS
