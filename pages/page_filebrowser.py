import os
from typing import List
from framebuffer import FrameBuffer
from pages.page import Page
from components.component_label import ComponentLabel
from components.component_pageable_textarea import ComponentTextAreaPageable
from components.sequence import Sequence
from config import HEIGHT
from mylogger import myLogger


class FileEntry():
    """Represents a file or directory entry"""
    def __init__(self, id: int, name: str, is_dir: bool, full_path: str):
        self.id: int = id
        self.name: str = name
        self.is_dir: bool = is_dir
        self.full_path: str = full_path


class PageFileBrowser(Page):
    def __init__(self, framebuffer: FrameBuffer, name: str, path: str = "data"):
        super().__init__(framebuffer, name)
        
        # Configuration
        self.base_directory = path
        self.current_directory = path
        self.entries_per_page = 9  # Support 1-9 entries per page
        
        # File/directory data
        self.entries: List[FileEntry] = []
        
        # Components
        # Line 1: Title showing current directory
        self.c_title = ComponentLabel(
            framebuffer, 
            0, 
            0, 
            self.framebuffer.width, 
            "File Browser", 
            center=True
        )
        
        # Line 3-25: Pageable file listing
        self.pageable_textarea = ComponentTextAreaPageable(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2,
            "",
            entries_per_page=self.entries_per_page
        )
        
        # Set callback to handle page changes
        self.pageable_textarea.set_on_page_change_callback(self._on_page_changed)
        
        self.components.append(self.c_title)
        self.components.append(self.pageable_textarea)

    
    def Initial(self):
        """Initialize the file browser page"""
        # Check if a specific path was provided in page input
        pageInput = self.get_page_input_once()
        if pageInput and "path" in pageInput:
            self.current_directory = pageInput["path"]
        
        self._load_directory()
        self._update_screen()

    
    def KeyPressed(self, keys: Sequence):
        """Handle key presses for file browser"""
        # Handle number keys 1-9 for selection
        if keys.length() == 1:
            key_val = keys.valeurs[0]
            
            # Check for numeric keys 1-9
            if ord('1') <= key_val <= ord('9'):
                rel_id = key_val - ord('0')  # Convert ASCII to int (1-based)
                self._handle_selection(rel_id)
                return
            
            # Check for letter keys 0, a-z for extended selection
            elif key_val == ord('0'):
                self._handle_selection(10)  # 0 maps to position 10
                return
            elif ord('a') <= key_val <= ord('z'):
                # a=11, b=12, etc.
                rel_id = 11 + (key_val - ord('a'))
                self._handle_selection(rel_id)
                return
        
        # Handle 'r' for refresh
        if keys.egale(Sequence('r')):
            self._load_directory()
            self._update_screen()
            return
        
        # Let parent handle other keys (like page switching and left/right navigation)
        super().KeyPressed(keys)

    
    def _handle_selection(self, rel_id: int):
        """Handle selection of a file or directory by relative ID"""
        abs_id = self._rel_page_offset_to_abs_id(rel_id)
        
        if abs_id == -1 or abs_id >= len(self.entries):
            myLogger.log(f"Invalid selection: {rel_id} (abs: {abs_id})")
            return
        
        entry = self.entries[abs_id]
        myLogger.log(f"Selected: {entry.name} (is_dir: {entry.is_dir})")
        
        if entry.is_dir:
            # Navigate into directory
            self.current_directory = entry.full_path
            self._load_directory()
            self._update_screen()
        else:
            # Open file in Page80Read
            try:
                with open(entry.full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                pageReadInput = {
                    "id": entry.id,
                    "title": entry.name,
                    "content": content,
                }
                self.pageManager.set_current_page("80Read", pageReadInput)
            except Exception as e:
                myLogger.log(f"Error reading file {entry.full_path}: {str(e)}")

    
    def _load_directory(self):
        """Load files and directories from the current directory"""
        try:
            myLogger.log(f"PageFileBrowser: Loading directory {self.current_directory}")
            self.entries = []
            
            # Add parent directory entry if not at base
            if self.current_directory != self.base_directory:
                parent_dir = os.path.dirname(self.current_directory)
                parent_entry = FileEntry(0, "..", True, parent_dir)
                self.entries.append(parent_entry)
            
            # List directory contents
            if os.path.exists(self.current_directory):
                items = os.listdir(self.current_directory)
                items.sort()  # Sort alphabetically
                
                # Separate directories and files
                dirs = []
                files = []
                
                for item in items:
                    full_path = os.path.join(self.current_directory, item)
                    if os.path.isdir(full_path):
                        dirs.append((item, full_path))
                    else:
                        files.append((item, full_path))
                
                # Add directories first, then files
                entry_id = 1 if self.entries else 0  # Start from 1 if we have ".."
                
                for name, full_path in dirs:
                    entry = FileEntry(entry_id, name, True, full_path)
                    self.entries.append(entry)
                    entry_id += 1
                
                for name, full_path in files:
                    entry = FileEntry(entry_id, name, False, full_path)
                    self.entries.append(entry)
                    entry_id += 1
            else:
                myLogger.log(f"Directory does not exist: {self.current_directory}")
                
        except Exception as e:
            error_msg = f"Error loading directory: {str(e)}"
            myLogger.log(error_msg)

    
    def _update_screen(self):
        """Update the screen with current directory contents"""
        # Update title with current directory
        display_path = self.current_directory
        if len(display_path) > self.framebuffer.width - 4:
            # Truncate path if too long
            display_path = "..." + display_path[-(self.framebuffer.width - 7):]
        self.c_title.set_text(f"[{display_path}]")
        
        # Calculate pagination
        total_entries = len(self.entries)
        current_page = self.pageable_textarea.get_current_page()
        
        # Calculate entry range for current page
        start_idx = current_page * self.entries_per_page
        end_idx = min(start_idx + self.entries_per_page, total_entries)
        
        # Format the entries for the current page
        formatted_lines = []
        
        page_rel_id = 1
        for i in range(start_idx, end_idx):
            entry = self.entries[i]
            
            # Format entry with selection key
            selection_key = self._get_selection_key(page_rel_id)
            
            # Add directory indicator
            if entry.is_dir:
                formatted_lines.append(f"{selection_key} [{entry.name}]/")
            else:
                formatted_lines.append(f"{selection_key} {entry.name}")
            
            page_rel_id += 1
        
        formatted_text = "\n".join(formatted_lines)
        
        # Calculate total pages based on total entries
        total_pages = (total_entries + self.entries_per_page - 1) // self.entries_per_page
        
        # Create page contents array (only need to set content for pages we can generate)
        page_contents = []
        for page_idx in range(total_pages):
            page_start = page_idx * self.entries_per_page
            page_end = min(page_start + self.entries_per_page, total_entries)
            
            page_lines = []
            page_rel_id = 1
            for i in range(page_start, page_end):
                entry = self.entries[i]
                selection_key = self._get_selection_key(page_rel_id)
                
                if entry.is_dir:
                    page_lines.append(f"{selection_key} [{entry.name}]/")
                else:
                    page_lines.append(f"{selection_key} {entry.name}")
                
                page_rel_id += 1
            
            page_contents.append("\n".join(page_lines))
        
        # Update the pageable textarea with all page contents
        self.pageable_textarea.set_page_contents(page_contents)

    
    def _on_page_changed(self, new_page: int):
        """Callback when the page changes in the pageable textarea component"""
        self._update_screen()

    
    def _rel_page_offset_to_abs_id(self, rel_id: int) -> int:
        """Convert relative page entry ID to absolute entry ID"""
        current_page = self.pageable_textarea.get_current_page()
        abs_id = current_page * self.entries_per_page + (rel_id - 1)
        if 0 <= abs_id < len(self.entries):
            return abs_id
        return -1

    
    def _get_selection_key(self, rel_id: int) -> str:
        """Get the selection key string for a relative ID (1-based)"""
        if 1 <= rel_id <= 9:
            return str(rel_id)
        elif rel_id == 10:
            return "0"
        elif 11 <= rel_id <= 36:
            # a-z
            return chr(ord('a') + (rel_id - 11))
        else:
            return "?"
