#!/usr/bin/env python

import time
import sys
import threading

from config import *
config_set_mode("minitel")

from terminals.terminal_minitel import Minitel
from mylogger import myLogger
from engine import Engine
from framebuffer import FrameBuffer
from terminals.minitel_model import MinitelVideoMode

from pages.page import Page
from pages.page_a import PageA
from pages.page_b import PageB
from pages.page_meditations import PageMeditations
from pages.page_rss import PageRss
from pages.page_overview import PageOverview
from pages.page_80_read import Page80Read
from pages.page_filebrowser import PageFileBrowser
from pages.page_ezines_list import PageEzinesList
from pages.page_ezines_issues import PageEzinesIssues
from pages.page_ezines_articles import PageEzinesArticles
from pages.page_ezines_article_detail import PageEzinesArticleDetail


# Global flag to control stdin thread
stdin_thread_running = True

def stdin_reader_thread(terminal):
    """Thread function to read from stdin and put characters into terminal input queue"""
    global stdin_thread_running
    myLogger.log("Makrotel: Stdin reader thread started")
    
    while stdin_thread_running:
        try:
            # Read a single character from stdin
            char = sys.stdin.read(1)
            if char and char != 0x0A:
                # Convert character to bytes and put in the input queue
                char_bytes = char.encode('latin-1')
                for byte_val in char_bytes:
                    terminal.input_queue.put(bytes([byte_val]))
        except (EOFError, KeyboardInterrupt):
            # Handle end of input or Ctrl+C
            break
        except Exception as e:
            myLogger.log(f"Makrotel: Error in stdin reader thread: {e}")
            break
    
    myLogger.log("Makrotel: Stdin reader thread stopped")


def main():
    dev = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        dev = sys.argv[1]

    framebuffer = FrameBuffer()
    terminal = Minitel(framebuffer, device=dev)
    terminal.set_speed(4800)  # full speed ahead
    terminal.identify_capabilities()  # mostly nice to have information
    #terminal.identify_mode()  # check in which video mode the terminal is
    # just assume videotex mode for now
    terminal.terminal_init_videotex()
    
    # Mark terminal as connected at startup
    with terminal.connection_lock:
        terminal.is_connected = True
    
    engine = Engine(framebuffer, terminal)

    pagea: Page = PageA(framebuffer, "PageA")
    pageb: Page = PageB(framebuffer, "PageB")
    pageoverview: Page = PageOverview(framebuffer, "Overview")
    pagemeditations: Page = PageMeditations(framebuffer, "Meditations")
    pageRssBbc: Page = PageRss(framebuffer, "RSS_BBC", "https://feeds.bbci.co.uk/news/rss.xml")
    pageRssArs: Page = PageRss(framebuffer, "RSS_ARS", "https://feeds.arstechnica.com/arstechnica/index/")
    page80read: Page = Page80Read(framebuffer, "80Read")
    pagefilebrowser: Page = PageFileBrowser(framebuffer, "FileBrowser", "data")
    pageEzinesList: Page = PageEzinesList(framebuffer, "EzinesList")
    pageEzinesIssues: Page = PageEzinesIssues(framebuffer, "EzinesIssues")
    pageEzinesArticles: Page = PageEzinesArticles(framebuffer, "EzinesArticles")
    pageEzinesArticleDetail: Page = PageEzinesArticleDetail(framebuffer, "EzinesArticleDetail")

    #pageZinesList: Page = PageZinesList(framebuffer, "ZinesList", dir="data/zines")
    #pageZine: Page = PageZine(framebuffer, "Zine")
    #pageZineArticle: Page = PageZineArticle(framebuffer, "ZineArticle")

    engine.pageManager.add_page(pageoverview)
    engine.pageManager.add_page(pagea)
    engine.pageManager.add_page(pageb)
    engine.pageManager.add_page(pagemeditations)
    engine.pageManager.add_page(pageRssArs)
    engine.pageManager.add_page(pageRssBbc)
    engine.pageManager.add_page(page80read)
    engine.pageManager.add_page(pagefilebrowser)
    engine.pageManager.add_page(pageEzinesList)
    engine.pageManager.add_page(pageEzinesIssues)
    engine.pageManager.add_page(pageEzinesArticles)
    engine.pageManager.add_page(pageEzinesArticleDetail)

    engine.pageManager.set_current_page("Overview")

    # Configure page rotation
    rotation_pages = ["Overview", "RSS_BBC", "RSS_ARS", "Meditations", "EzinesList"]
    engine.pageManager.set_rotation_pages(rotation_pages)
    engine.pageManager.enable_rotation()

    # Start the stdin reader thread
    stdin_thread = threading.Thread(target=stdin_reader_thread, args=(terminal,), daemon=True)
    stdin_thread.start()

    try:
        while True:
            engine.Tick()
            time.sleep(REFRESH_TIME)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        myLogger.log("MakroTel: Received KeyboardInterrupt, shutting down...")
    finally:
        # Clean shutdown
        global stdin_thread_running
        stdin_thread_running = False
        terminal.close() 

if __name__ == "__main__":
  main()
