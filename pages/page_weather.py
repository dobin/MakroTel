import feedparser
import datetime
import time
import re
import urllib.request
import urllib.error
from typing import List

from components.component_textarea import ComponentTextArea
from pages.page import Page
from components.component_clock import ComponentClock
from components.component_label import ComponentLabel
from components.component_pageable_textarea import ComponentTextAreaPageable
from components.sequence import Sequence
from constants.keys import KEY_LEFT, KEY_RIGHT
from framebuffer import FrameBuffer
from config import HEIGHT
from mylogger import myLogger
from terminals.minitel_model import MinitelVideoMode
from utils import parse_selection_key


class PageWeather(Page):
    def __init__(self, framebuffer: FrameBuffer, name: str, feed_url):
        super().__init__(framebuffer, name, mode=MinitelVideoMode.TELEMATIC)

        self.weather: str = ""
        self.entries_per_page = 1  # Not really used for weather, but required by component

        # Line 1-25: Pageable RSS content text area (includes info label on last line)
        self.pageable_textarea = ComponentTextArea(
            framebuffer, 
            0, 
            1, 
            80, 
            HEIGHT - 1,
            "",
        )
        
        self.components.append(self.pageable_textarea)
        # Note: info_label is now part of pageable_textarea, no need to add separately


    def Initial(self):
        self._load_weather()
        self._update_screen()
        

    def KeyPressed(self, keys: Sequence):
        """Handle key presses for RSS page"""
        # Left-right navigation is now handled by the pageable_textarea component
        
        if keys.egale(Sequence('r')):
            myLogger.log("PageRss: Reloading RSS feed")
            self._load_weather()
            self._update_screen()

    def _load_weather(self):
        """Load weather data from wttr.in"""
        try:
            # Request weather data in text format
            url = "https://wttr.in/Uster?dFnQT"
            myLogger.log(f"PageWeather: Loading weather from {url}")
            
            # Create request with curl-like user agent to get plain text
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'curl/7.68.0')
            req.add_header('Accept', 'text/plain')
            
            # Make the request
            with urllib.request.urlopen(req, timeout=10) as response:
                weather_data = response.read().decode('utf-8')
                
            # Clean up the weather data for display
            self.weather = self._clean_weather_data(weather_data)
            myLogger.log("PageWeather: Weather data loaded successfully")
            
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP Error {e.code}: {e.reason}"
            myLogger.log(f"PageWeather: {error_msg}")
            self.weather = f"Weather service error:\n{error_msg}\n\nPlease try again later."
            
        except urllib.error.URLError as e:
            error_msg = f"Network error: {str(e.reason)}"
            myLogger.log(f"PageWeather: {error_msg}")
            self.weather = f"Network error:\n{error_msg}\n\nCheck your internet connection."
            
        except Exception as e:
            error_msg = f"Error loading weather: {str(e)}"
            myLogger.log(f"PageWeather: {error_msg}")
            self.weather = f"Weather loading error:\n{error_msg}"

    def _clean_weather_data(self, weather_data: str) -> str:
        """Clean and format weather data for terminal display"""
        lines = weather_data.split('\n')
        cleaned_lines = []

        if len(lines) >= 18:
            del lines[18]
        if len(lines) >= 8:
            del lines[8]

        for line in lines:
            # Remove ANSI escape sequences (color codes)
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            # Remove other terminal control sequences
            clean_line = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', clean_line)
            # Trim trailing whitespace but preserve leading spaces for formatting
            clean_line = clean_line.rstrip()
            cleaned_lines.append(clean_line)
        
        # Join lines and remove excessive empty lines
        result = '\n'.join(cleaned_lines)
        #result = re.sub(r'\n\n\n+', '\n\n', result)

        return result #.strip()

    def _update_screen(self):
        self.pageable_textarea.set_text(self.weather)