import os
import json
from typing import List
from framebuffer import FrameBuffer
from pages.page import Page
from components.component_label import ComponentLabel
from components.component_pageable_textarea import ComponentTextAreaPageable
from components.sequence import Sequence
from config import HEIGHT
from mylogger import myLogger
from utils import get_selection_key, parse_selection_key


class ZineEntry:
    """Represents a zine"""
    def __init__(self, id: int, name: str, path: str, about: dict):
        self.id: int = id
        self.name: str = name
        self.path: str = path
        self.about: dict = about


class PageEzinesList(Page):
    """Display list of available e-zines"""
    
    def __init__(self, framebuffer: FrameBuffer, name: str):
        super().__init__(framebuffer, name)
        
        # Configuration
        self.base_directory = os.path.join("data", "ezines-augmented", "zines")
        self.zines_per_page = 3  # Show 3 zines per page for better readability
        
        # Data
        self.zines: List[ZineEntry] = []
        
        # Components
        self.c_title = ComponentLabel(
            framebuffer,
            0,
            0,
            self.framebuffer.width,
            "E-Zines",
            center=True
        )
        
        self.textarea_zines = ComponentTextAreaPageable(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2,
            "",
            entries_per_page=self.zines_per_page
        )
        
        self.components.append(self.c_title)
        self.components.append(self.textarea_zines)
    
    def Initial(self):
        """Initialize the ezine list"""
        self._load_zines()
        self._update_screen()
    
    def KeyPressed(self, keys: Sequence):
        """Handle key presses"""
        # Handle number/letter selection keys
        if keys.length() == 1:
            rel_id = parse_selection_key(keys.valeurs[0])
            if rel_id is not None:
                self._select_zine(rel_id)
                return
        
        # Handle 'r' for refresh
        if keys.egale(Sequence('r')):
            self._load_zines()
            self._update_screen()
            return
        
        # Let parent handle other keys (page navigation, back navigation)
        super().KeyPressed(keys)
    
    def _select_zine(self, rel_id: int):
        """Select a zine and navigate to issues page"""
        abs_id = self.textarea_zines.rel_page_offset_to_abs_id(rel_id, len(self.zines))
        if abs_id == -1:
            return
        
        zine = self.zines[abs_id]
        myLogger.log(f"Selected zine: {zine.name}")
        
        # Navigate to issues page with zine data
        pageInput = {
            "zine_id": zine.id,
            "zine_name": zine.name,
            "zine_path": zine.path,
            "zine_about": zine.about
        }
        if self.pageManager is not None:
            self.pageManager.set_current_page("EzinesIssues", pageInput)
    
    def _load_zines(self):
        """Load all available zines"""
        self.zines = []
        try:
            if not os.path.exists(self.base_directory):
                myLogger.log(f"Zines directory not found: {self.base_directory}")
                return
            
            zine_dirs = [d for d in os.listdir(self.base_directory)
                        if os.path.isdir(os.path.join(self.base_directory, d))]
            zine_dirs.sort()
            
            zine_id = 0
            for zine_dir in zine_dirs:
                zine_path = os.path.join(self.base_directory, zine_dir)
                about_path = os.path.join(zine_path, "about.json")
                
                if os.path.exists(about_path):
                    try:
                        with open(about_path, 'r', encoding='utf-8') as f:
                            about = json.load(f)
                        
                        zine = ZineEntry(zine_id, zine_dir, zine_path, about)
                        self.zines.append(zine)
                        zine_id += 1
                    except Exception as e:
                        myLogger.log(f"Error loading {about_path}: {str(e)}")
        
        except Exception as e:
            myLogger.log(f"Error loading zines: {str(e)}")
    
    def _update_screen(self):
        """Update screen with zines list"""
        self.c_title.set_text("E-Zines")
        
        # Generate all pages (3 zines per page for better readability)
        total_zines = len(self.zines)
        total_pages = max(1, (total_zines + self.zines_per_page - 1) // self.zines_per_page)
        all_pages = []
        
        for page_num in range(total_pages):
            start_idx = page_num * self.zines_per_page
            end_idx = min(start_idx + self.zines_per_page, total_zines)
            
            lines = []
            page_rel_id = 1
            for i in range(start_idx, end_idx):
                zine = self.zines[i]
                key = get_selection_key(page_rel_id)
                
                # Format: [key] Name - Topic
                name = zine.about.get('name', zine.name)
                date = zine.about.get('date', '')
                description = zine.about.get('description', '')
                
                lines.append(f"{key} {name} ({date})")
                lines.append(f"  {description}")
                lines.append("")  # Blank line
                
                page_rel_id += 1
            
            content = "\n".join(lines)
            all_pages.append(content)
        
        self.textarea_zines.set_page_contents(all_pages)
