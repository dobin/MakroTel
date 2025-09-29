#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading

from config import *
config_set_mode("minitel")

from terminals.terminal_minitel import Minitel
from mylogger import myLogger
from terminals.terminal import Terminal
from pages.page import Page
from pages.page_a import PageA

#from components.component_menu import ComponentMenu
from components.component_text import ComponentText
from components.component_textfield import ComponentTextField



def main():
  terminal = Minitel(device="COM3")
  terminal.guess_speed()
  terminal.identify()
  terminal.set_speed(1200)
  terminal.set_mode('VIDEOTEX')
  terminal.configure_keyboard(extended = True, cursor = False, lowercase = True)
  terminal.echo(False)
  terminal.clear()
  terminal.cursor(False)

  def draw_loop():
      while True:
          terminal.draw_buffer()
          time.sleep(0.1)
  threading.Thread(target=draw_loop, daemon=True).start()

  page: Page = PageA(terminal)
  page.initial()

  while True:
      page.Tick()
      try:
        sequence = terminal.receive_sequence(blocking=False)
        myLogger.log(f"Got char: {sequence}")
        page.KeyPressed(0x41)
      except:
        pass
      time.sleep(REFRESH_TIME)

  terminal.close() 

if __name__ == "__main__":
  main()
