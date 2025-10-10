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

    pagea: Page = PageA(framebuffer, "PageA")
    pageb: Page = PageB(framebuffer, "PageB")
    pageoverview: Page = PageOverview(framebuffer, "Overview")
    pagemeditations: Page = PageMeditations(framebuffer, "Meditations")
    pagerss: Page = PageRss(framebuffer, "RSS")
    page80read: Page = Page80Read(framebuffer, "80-Column")

    engine.pageManager.add_page(pageoverview)
    engine.pageManager.add_page(pagea)
    engine.pageManager.add_page(pageb)
    engine.pageManager.add_page(pagemeditations)
    engine.pageManager.add_page(pagerss)
    engine.pageManager.add_page(page80read)

    engine.pageManager.set_current_page("Overview")

    while True:
        engine.Tick()
        time.sleep(REFRESH_TIME)

    terminal.close() 

if __name__ == "__main__":
  main()
