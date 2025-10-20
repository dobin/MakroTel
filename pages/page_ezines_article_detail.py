import os
from typing import List
from framebuffer import FrameBuffer
from pages.page import Page
from components.component_label import ComponentLabel
from components.component_textarea import ComponentTextArea
from components.sequence import Sequence
from config import HEIGHT
from mylogger import myLogger


class PageEzinesArticleDetail(Page):
    """Display detailed metadata about a selected article"""
    
    def __init__(self, framebuffer: FrameBuffer, name: str):
        super().__init__(framebuffer, name)
        
        # Article data (from pageInput)
        self.zine_id = None
        self.zine_name = ""
        self.zine_about = {}
        self.issue_id = None
        self.issue_num = 0
        self.article_id = None
        self.article_num = 0
        self.metadata = {}
        self.txt_path = ""
        
        # Components
        self.c_title = ComponentLabel(
            framebuffer,
            0,
            0,
            self.framebuffer.width,
            "Article Detail",
            center=True
        )
        
        self.textarea_detail = ComponentTextArea(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2,
            ""
        )
        
        self.components.append(self.c_title)
        self.components.append(self.textarea_detail)
    
    def Initial(self):
        """Initialize the article detail view"""
        # Get article data from pageInput
        pageInput = self.get_page_input_once()
        if pageInput:
            self.zine_id = pageInput.get("zine_id")
            self.zine_name = pageInput.get("zine_name", "")
            self.zine_about = pageInput.get("zine_about", {})
            self.issue_id = pageInput.get("issue_id")
            self.issue_num = pageInput.get("issue_num", 0)
            self.article_id = pageInput.get("article_id")
            self.article_num = pageInput.get("article_num", 0)
            self.metadata = pageInput.get("metadata", {})
            self.txt_path = pageInput.get("txt_path", "")
        
        self._update_screen()
    
    def KeyPressed(self, keys: Sequence):
        """Handle key presses"""
        # Space key opens the article for reading
        if keys.egale(Sequence([ord(' ')])):
            self._read_article()
            return
        
        # Let parent handle other keys (back navigation)
        super().KeyPressed(keys)
    
    def _read_article(self):
        """Open the current article in Page80Read"""
        if not self.txt_path:
            return
        
        try:
            with open(self.txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pageReadInput = {
                "id": self.article_id,
                "title": self.metadata.get('title', 'Unknown'),
                "content": content,
            }
            if self.pageManager is not None:
                self.pageManager.set_current_page("80Read", pageReadInput)
        except Exception as e:
            myLogger.log(f"Error reading article {self.txt_path}: {str(e)}")
    
    def _update_screen(self):
        """Update screen with article details"""
        self.c_title.set_text(f"Article #{self.article_num}")
        
        lines = []
        
        title = self.metadata.get('title', 'Unknown')
        lines.append(f"TITLE: {title}")
        
        authors = self.metadata.get('authors', 'Unknown')
        lines.append(f"AUTHORS: {authors}")
        
        date = self.metadata.get('date', 'Unknown')
        lines.append(f"DATE: {date}")
        
        summary = self.metadata.get('summary', '')
        if summary:
            lines.append("")
            lines.extend(self._wrap_text(summary, self.framebuffer.width))
            lines.append("")
        
        lines.append("")
        lines.append("Press SPACE to read the article")
        
        content = "\n".join(lines)
        self.textarea_detail.set_text(content)
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to fit within width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
