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
from pages.page_meditations import PageMeditations
from pages.page_rss import PageRss
from pages.page_overview import PageOverview
from pages.page_80_read import Page80Read


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
    pageoverview: Page = PageOverview(framebuffer)
    pagemeditations: Page = PageMeditations(framebuffer)
    pagerss: Page = PageRss(framebuffer)
    page80read: Page = Page80Read(framebuffer)

    engine.pageManager.add_page("Overview", pageoverview)
    engine.pageManager.add_page("PageA", pagea)
    engine.pageManager.add_page("PageB", pageb)
    engine.pageManager.add_page("Meditations", pagemeditations)
    engine.pageManager.add_page("RSS", pagerss)
    engine.pageManager.add_page("80-Column", page80read)
    
    engine.pageManager.set_current_page("Overview")

    while True:
        engine.Tick()
        time.sleep(REFRESH_TIME)

    terminal.close() 

if __name__ == "__main__":
  main()
