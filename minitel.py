#!/usr/bin/env python

import time
import sys
import threading

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


# Global flag to control stdin thread
stdin_thread_running = True

def stdin_reader_thread(terminal):
    """Thread function to read from stdin and put characters into terminal input queue"""
    global stdin_thread_running
    myLogger.log("Stdin reader thread started")
    
    while stdin_thread_running:
        try:
            # Read a single character from stdin
            char = sys.stdin.read(1)
            if char:
                # Convert character to bytes and put in the input queue
                char_bytes = char.encode('latin-1')
                for byte_val in char_bytes:
                    terminal.input_queue.put(bytes([byte_val]))
        except (EOFError, KeyboardInterrupt):
            # Handle end of input or Ctrl+C
            break
        except Exception as e:
            myLogger.log(f"Error in stdin reader thread: {e}")
            break
    
    myLogger.log("Stdin reader thread stopped")


def main():
    dev = "COM3"
    if len(sys.argv) > 1:
        dev = sys.argv[1]

    framebuffer = FrameBuffer()
    terminal = Minitel(framebuffer, device=dev)
    terminal.guess_speed()
    terminal.identify()
    terminal.set_speed(1200)
    terminal.set_mode(0)
    terminal.configure_keyboard(extended = True, cursor = False, lowercase = True)
    terminal.echo(False)
    terminal.video.clear()
    terminal.cursor(False)
    engine = Engine(framebuffer, terminal)

    pagea: Page = PageA(framebuffer, "PageA")
    pageb: Page = PageB(framebuffer, "PageB")
    pageoverview: Page = PageOverview(framebuffer, "Overview")
    pagemeditations: Page = PageMeditations(framebuffer, "Meditations")
    pagerss: Page = PageRss(framebuffer, "RSS")
    page80read: Page = Page80Read(framebuffer, "80Read")

    engine.pageManager.add_page(pageoverview)
    engine.pageManager.add_page(pagea)
    engine.pageManager.add_page(pageb)
    engine.pageManager.add_page(pagemeditations)
    engine.pageManager.add_page(pagerss)
    engine.pageManager.add_page(page80read)

    engine.pageManager.set_current_page("Overview")

    # Start the stdin reader thread
    stdin_thread = threading.Thread(target=stdin_reader_thread, args=(terminal,), daemon=True)
    stdin_thread.start()
    myLogger.log("Started stdin reader thread")

    try:
        while True:
            engine.Tick()
            time.sleep(REFRESH_TIME)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        myLogger.log("Received KeyboardInterrupt, shutting down...")
    finally:
        # Clean shutdown
        global stdin_thread_running
        stdin_thread_running = False
        terminal.close() 

if __name__ == "__main__":
  main()
