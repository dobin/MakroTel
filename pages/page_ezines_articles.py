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


class ArticleEntry:
    """Represents an article within an issue"""
    def __init__(self, id: int, article_num: int, metadata: dict, txt_path: str):
        self.id: int = id
        self.article_num: int = article_num
        self.metadata: dict = metadata
        self.txt_path: str = txt_path


class PageEzinesArticles(Page):
    """Display list of articles in a selected issue"""
    
    def __init__(self, framebuffer: FrameBuffer, name: str):
        super().__init__(framebuffer, name)
        
        # Configuration
        self.articles_per_page = 1  # Show 1 article per page for better readability
        
        # Issue data (from pageInput)
        self.zine_id = None
        self.zine_name = ""
        self.zine_about = {}
        self.issue_id = None
        self.issue_num = 0
        self.issue_path = ""
        self.release_date = ""
        self.editor = ""
        
        # Data
        self.articles: List[ArticleEntry] = []
        
        # Components
        self.c_title = ComponentLabel(
            framebuffer,
            0,
            0,
            self.framebuffer.width,
            "Articles",
            center=True
        )
        
        self.textarea_articles = ComponentTextAreaPageable(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2,
            "",
            entries_per_page=self.articles_per_page
        )
        
        self.components.append(self.c_title)
        self.components.append(self.textarea_articles)
    
    def Initial(self):
        """Initialize the articles list"""
        # Get issue data from pageInput
        pageInput = self.get_page_input_once()
        if pageInput:
            self.zine_id = pageInput.get("zine_id")
            self.zine_name = pageInput.get("zine_name", "")
            self.zine_about = pageInput.get("zine_about", {})
            self.issue_id = pageInput.get("issue_id")
            self.issue_num = pageInput.get("issue_num", 0)
            self.issue_path = pageInput.get("issue_path", "")
            self.release_date = pageInput.get("release_date", "")
            self.editor = pageInput.get("editor", "")
        
        self._load_articles()
        self._update_screen()
    
    def KeyPressed(self, keys: Sequence):
        """Handle key presses"""
        # Handle number/letter selection keys
        if keys.length() == 1:
            rel_id = parse_selection_key(keys.valeurs[0])
            if rel_id is not None:
                self._select_article(rel_id)
                return
        
        # Handle 'r' for refresh
        if keys.egale(Sequence('r')):
            self._load_articles()
            self._update_screen()
            return
        
        # Let parent handle other keys (page navigation, back navigation)
        super().KeyPressed(keys)
    
    def _select_article(self, rel_id: int):
        """Select an article and navigate to detail page"""
        abs_id = self.textarea_articles.rel_page_offset_to_abs_id(rel_id, len(self.articles))
        if abs_id == -1:
            return
        
        article = self.articles[abs_id]
        myLogger.log(f"Selected article: {article.metadata.get('title', 'Unknown')}")
        
        # Navigate to article detail page
        pageInput = {
            "zine_id": self.zine_id,
            "zine_name": self.zine_name,
            "zine_about": self.zine_about,
            "issue_id": self.issue_id,
            "issue_num": self.issue_num,
            "article_id": article.id,
            "article_num": article.article_num,
            "metadata": article.metadata,
            "txt_path": article.txt_path
        }
        if self.pageManager is not None:
            self.pageManager.set_current_page("EzinesArticleDetail", pageInput)
    
    def _load_articles(self):
        """Load articles for the current issue"""
        self.articles = []
        if not self.issue_path:
            return
        
        try:
            if not os.path.exists(self.issue_path):
                myLogger.log(f"Issue directory not found: {self.issue_path}")
                return
            
            # Find all .json files in the issue directory
            json_files = [f for f in os.listdir(self.issue_path) if f.endswith('.json')]
            
            # Sort by numeric prefix
            json_files.sort(key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else 999)
            
            article_id = 0
            for json_file in json_files:
                json_path = os.path.join(self.issue_path, json_file)
                # Derive .txt filename
                txt_file = json_file.replace('.json', '.txt')
                txt_path = os.path.join(self.issue_path, txt_file)
                
                if os.path.exists(txt_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        article_num = int(json_file.split('.')[0]) if json_file.split('.')[0].isdigit() else article_id
                        article = ArticleEntry(article_id, article_num, metadata, txt_path)
                        self.articles.append(article)
                        article_id += 1
                    except Exception as e:
                        myLogger.log(f"Error loading article {json_path}: {str(e)}")
        
        except Exception as e:
            myLogger.log(f"Error loading articles: {str(e)}")
    
    def _update_screen(self):
        """Update screen with articles list"""
        zine_display_name = self.zine_about.get('name', self.zine_name)
        title = f"{zine_display_name} #{self.issue_num}"
        self.c_title.set_text(title)
        
        # Generate all pages (1 article per page)
        total_articles = len(self.articles)
        all_pages = []
        
        for i in range(total_articles):
            article = self.articles[i]
            key = get_selection_key(1)  # Always use key "1" since only 1 article per page
            
            lines = []
            
            # Display: [key] Article#: Title
            #          Authors - Date
            #          Short summary
            title_text = article.metadata.get('title', 'Unknown')
            authors = article.metadata.get('authors', 'Unknown')
            date = article.metadata.get('date', 'Unknown')
            short_summary = article.metadata.get('short_summary', '')
            historical_context = article.metadata.get('historical_context', '')

            title_wrapped = self._wrap_text(f"[{key}] {title_text}", self.framebuffer.width - 10)
            lines.extend(title_wrapped)
            if date:
                lines.append(f"   #{article.article_num} - {date}")
            else: 
                lines.append(f"   #{article.article_num}")

            if authors:
                lines.append(f"   {authors}")

            lines.append(f"")
            if short_summary:
                summary_lines = self._wrap_text(short_summary, self.framebuffer.width, "")
                lines.extend(summary_lines)
            if historical_context:
                hist_lines = self._wrap_text(historical_context, self.framebuffer.width, "")
                lines.append(f"")
                lines.append("Historical Context:")
                lines.extend(hist_lines)
            
            lines.append("")
            
            content = "\n".join(lines)
            all_pages.append(content)
        
        self.textarea_articles.set_page_contents(all_pages)
    
    def _wrap_text(self, text: str, width: int, prefix: str = "") -> List[str]:
        """Wrap text to fit within width"""
        words = text.split()
        lines = []
        current_line = prefix
        
        for word in words:
            test_line = current_line + (" " if current_line != prefix else "") + word
            if len(test_line) <= width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = prefix + word
        
        if current_line:
            lines.append(current_line)
        
        return lines
