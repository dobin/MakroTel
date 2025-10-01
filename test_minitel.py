#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
import sys

from config import *
config_set_mode("minitel")

from terminals.terminal_minitel import Minitel
from mylogger import myLogger
from terminals.terminal import Terminal
from pages.page import Page
from pages.page_a import PageA
from components.sequence import Sequence


def main():
    dev = "COM3"
    if len(sys.argv) > 1:
        dev = sys.argv[1]

    terminal = Minitel(device=dev)
    terminal.guess_speed()
    terminal.identify()
    terminal.set_speed(1200)
    terminal.set_mode('VIDEOTEX')
    terminal.configure_keyboard(extended = True, cursor = False, lowercase = True)
    terminal.echo(False)
    terminal.clear()
    terminal.cursor(False)

    page: Page = PageA(terminal.framebuffer)
    page.initial()

    while True:
        page.Tick()
        keySequence = terminal.get_input_key()
        if keySequence is not None:
            page.KeyPressed(keySequence)
        time.sleep(REFRESH_TIME)

    terminal.close() 

if __name__ == "__main__":
  main()
