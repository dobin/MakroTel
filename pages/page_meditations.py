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
    def __init__(self, framebuffer: FrameBuffer):
        super().__init__(framebuffer)
        
        # Load a random quote
        quote_data: Dict[str, str] = self._load_random_quote()
        
        # Add components
        # Line 0: Status bar
        self.components.append(ComponentClock(framebuffer, 0, 0))  # in status bar

        # Line 1: Title
        self.components.append(ComponentLabel(framebuffer, 0, 1, 40, "Marcus Aurelius - Meditations", center=True))
        # Line 2: Subtitle with book and quote number
        subtitle = f"{quote_data.get('book', '')} - {quote_data.get('quote_num', '')}"
        self.components.append(ComponentLabel(framebuffer, 0, 2, 40, subtitle, center=True))

        # Line 2-25: Quote text area
        self.textarea = ComponentTextArea(framebuffer, 0, 3, self.framebuffer.width, HEIGHT-3, quote_data['text'])
        self.components.append(self.textarea)
        
        # Add instructions at the bottom
        #self.components.append(ComponentText(framebuffer, 1, 24, "Use UP/DOWN arrows to navigate pages"))
    

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
            
            # Format the quote for display
            #formatted_quote = f"{book} - Quote {quote_num}\n\n"
            #formatted_quote += text
            #return formatted_quote

            ret = {
                "book": book,
                "quote_num": quote_num,
                "text": text
            }
            return ret
            
        except Exception as e:
            myLogger.log(f"Error loading quote: {str(e)}")

        return {}
    

