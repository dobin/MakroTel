from constants.keys import MINITEL_COLOR
from pages.page import Page
from components.sequence import Sequence
from typing import Dict

from framebuffer import FrameBuffer, CharacterAttributes
from terminals.terminal_minitel import *

from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover
from components.component_menu import ComponentMenu
from components.component_textfield import ComponentTextField
from components.component_label import ComponentLabel
from components.component_textarea import ComponentTextArea
from config import HEIGHT

import os
import random


class PageMeditations(Page):
    def __init__(self, framebuffer: FrameBuffer, name: str):
        super().__init__(framebuffer, name)

        # Add components
        # Line 0: Status bar
        #self.components.append(ComponentClock(framebuffer, 0, 0))

        self.c_title = ComponentLabel(framebuffer, 0, 1, 40, "Marcus Aurelius - Meditations", center=True)
        self.c_subtitle = ComponentLabel(framebuffer, 0, 2, 40, "", center=True)
        self.c_content = ComponentTextArea(framebuffer, 0, 4, self.framebuffer.width, HEIGHT-4, "")

        self.components.append(self.c_title)
        self.components.append(self.c_subtitle)
        self.components.append(self.c_content)


    def Initial(self):
        self._update()


    def KeyPressed(self, keys: Sequence):
        if keys.egale(Sequence('r')):
            self._update()

        return super().KeyPressed(keys)


    def _update(self):
        # Load a random quote
        quote_data: Dict[str, str] = self._load_random_quote()
        
        # Line 2: Subtitle with book and quote number
        subtitle = f"{quote_data.get('book', '')} - {quote_data.get('quote_num', '')}"
        self.c_subtitle.set_text(subtitle)

        # Line 2-25: Quote text area
        self.c_content.set_text(quote_data.get('text', ''))
        

    def _load_random_quote(self) -> Dict[str, str]:
        """Load a random quote from the meditations quotes directory"""
        try:
            quotes_dir = os.path.join("data", "meditations", "quotes")
            
            # Get all quote files
            quote_files = [f for f in os.listdir(quotes_dir) if f.startswith("quote_") and f.endswith(".txt")]
            
            if not quote_files:
                myLogger.log("No quotes found in the meditations directory.")
                return {}
            
            # Select a random quote file
            random_file = random.choice(quote_files)
            quote_path = os.path.join(quotes_dir, random_file)
            
            # Read and parse the quote file
            with open(quote_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse the three lines: Book, Quote, Text
            book = ""
            quote_num = ""
            text = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("Book:"):
                    book = line[5:].strip()
                elif line.startswith("Quote:"):
                    quote_num = line[6:].strip()
                elif line.startswith("Text:"):
                    text = line[5:].strip()
            
            ret = {
                "book": book,
                "quote_num": quote_num,
                "text": text
            }
            return ret
            
        except Exception as e:
            myLogger.log(f"Error loading quote: {str(e)}")

        return {}
    

