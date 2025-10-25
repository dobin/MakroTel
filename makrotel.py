import curses
import time

from config import *
config_set_mode("curses")

from mylogger import myLogger
from terminals.terminal_curses import TerminalCurses
from terminals.terminal import Terminal
from components.sequence import Sequence
from engine import Engine
from framebuffer import FrameBuffer

from pages.page import Page
from pages.page_a import PageA
from pages.page_b import PageB
from pages.page_overview import PageOverview
from pages.page_meditations import PageMeditations
from pages.page_rss import PageRss
from pages.page_weather import PageWeather
from pages.page_80_read import Page80Read
from pages.page_filebrowser import PageFileBrowser
from pages.page_ezines_list import PageEzinesList
from pages.page_ezines_issues import PageEzinesIssues
from pages.page_ezines_articles import PageEzinesArticles
from pages.page_ezines_article_detail import PageEzinesArticleDetail


def main(stdscr):
    framebuffer = FrameBuffer()
    terminal: Terminal = TerminalCurses(framebuffer, stdscr)
    engine = Engine(framebuffer, terminal)

    pagea: Page = PageA(framebuffer, "PageA")
    pageb: Page = PageB(framebuffer, "PageB")
    pageoverview: Page = PageOverview(framebuffer, "Overview")
    pagemeditations: Page = PageMeditations(framebuffer, "Meditations")
    pageRssBbc: Page = PageRss(framebuffer, "RSS_BBC", "https://feeds.bbci.co.uk/news/rss.xml")
    pageRssArs: Page = PageRss(framebuffer, "RSS_ARS", "https://feeds.arstechnica.com/arstechnica/index/")
    pageRss0day: Page = PageRss(framebuffer, "RSS_0DAY", "https://0dayfans.com/feed.rss")
    pageRssTalk: Page = PageRss(framebuffer, "RSS_TALK", "https://talkback.sh/resources/feed/")
    pageWeather: Page = PageWeather(framebuffer, "Weather", "")
    
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
    engine.pageManager.add_page(pageRss0day)
    engine.pageManager.add_page(pageRssTalk)
    engine.pageManager.add_page(pageWeather)

    engine.pageManager.add_page(page80read)
    engine.pageManager.add_page(pagefilebrowser)
    engine.pageManager.add_page(pageEzinesList)
    engine.pageManager.add_page(pageEzinesIssues)
    engine.pageManager.add_page(pageEzinesArticles)
    engine.pageManager.add_page(pageEzinesArticleDetail)
    
    # Configure page rotation
    rotation_pages = ["Overview", "RSS_BBC", "RSS_ARS", "RSS_0DAY", "RSS_TALK", "Weather", "Meditations", "EzinesList"]
    engine.pageManager.set_rotation_pages(rotation_pages)
    engine.pageManager.enable_rotation()
    
    engine.pageManager.set_current_page("Overview")

    while True:
        engine.Tick()
        time.sleep(REFRESH_TIME)

# Run curses application
curses.wrapper(main)
