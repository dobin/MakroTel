#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
import sys

from config import *
config_set_mode("minitel")

from terminals.terminal_minitel import Minitel
from mylogger import myLogger
from pages.page import Page
from pages.page_a import PageA
from pages.page_b import PageB
from engine import Engine
from framebuffer import FrameBuffer


def main():
    dev = "COM3"
    if len(sys.argv) > 1:
        dev = sys.argv[1]

    framebuffer = FrameBuffer()
    terminal = Minitel(framebuffer, device=dev)
    terminal.guess_speed()
    terminal.identify()
    terminal.set_speed(1200)
    terminal.set_mode('VIDEOTEX')
    terminal.configure_keyboard(extended = True, cursor = False, lowercase = True)
    terminal.echo(False)
    terminal.clear()
    terminal.cursor(False)
    engine = Engine(framebuffer, terminal)

    pagea: Page = PageA(framebuffer)
    pageb: Page = PageB(framebuffer)
    engine.pageManager.add_page("PageA", pagea)
    engine.pageManager.add_page("PageB", pageb)
    engine.pageManager.set_current_page("PageA")

    while True:
        engine.Tick()
        time.sleep(REFRESH_TIME)

    terminal.close() 

if __name__ == "__main__":
  main()
