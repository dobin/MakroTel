import os
import json
from typing import List, Dict, Optional
from framebuffer import FrameBuffer
from pages.page import Page
from components.component_label import ComponentLabel
from components.component_pageable_textarea import ComponentTextAreaPageable
from components.component_tabs import ComponentTabs
from components.sequence import Sequence
from config import HEIGHT
from mylogger import myLogger


class ZineEntry:
    """Represents a zine"""
    def __init__(self, id: int, name: str, path: str, about: Dict):
        self.id: int = id
        self.name: str = name
        self.path: str = path
        self.about: Dict = about


class IssueEntry:
    """Represents a zine issue"""
    def __init__(self, id: int, issue_num: int, release_date: str, editor: str, path: str):
        self.id: int = id
        self.issue_num: int = issue_num
        self.release_date: str = release_date
        self.editor: str = editor
        self.path: str = path


class ArticleEntry:
    """Represents an article within an issue"""
    def __init__(self, id: int, article_num: int, metadata: Dict, txt_path: str):
        self.id: int = id
        self.article_num: int = article_num
        self.metadata: Dict = metadata
        self.txt_path: str = txt_path


class PageEzines(Page):
    """Multi-level ezine browser: Zines -> Issues -> Articles -> Article Detail -> Read"""
    
    # Navigation levels (tab names)
    TAB_ZINES = "zines"
    TAB_ISSUES = "issues"
    TAB_ARTICLES = "articles"
    TAB_ARTICLE_DETAIL = "article_detail"
    
    def __init__(self, framebuffer: FrameBuffer, name: str):
        super().__init__(framebuffer, name)
        
        # Configuration
        self.base_directory = os.path.join("data", "ezines-augmented", "zines")

        self.zines_per_page = 3 # Show 3 zines per page for better readability
        self.issues_per_page = 20
        self.articles_per_page = 1
        self.article_details_per_page = 1
        
        # Navigation state
        self.current_zine: Optional[ZineEntry] = None
        self.current_issue: Optional[IssueEntry] = None
        self.current_article: Optional[ArticleEntry] = None
        
        # Data collections
        self.zines: List[ZineEntry] = []
        self.issues: List[IssueEntry] = []
        self.articles: List[ArticleEntry] = []
        
        # Components
        self.c_title = ComponentLabel(
            framebuffer,
            0,
            0,
            self.framebuffer.width,
            "E-Zines",
            center=True
        )
        
        # Create tabs component
        self.tabs = ComponentTabs(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2
        )
        
        # Create a ComponentTextAreaPageable for each tab
        self.textarea_zines = ComponentTextAreaPageable(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2,
            "",
            entries_per_page=self.zines_per_page
        )
        
        self.textarea_issues = ComponentTextAreaPageable(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2,
            "",
            entries_per_page=self.issues_per_page
        )
        
        self.textarea_articles = ComponentTextAreaPageable(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2,
            "",
            entries_per_page=1  # Show 1 article per page
        )
        
        self.textarea_detail = ComponentTextAreaPageable(
            framebuffer,
            0,
            2,
            self.framebuffer.width,
            HEIGHT - 2,
            "",
            entries_per_page=1  # Show 1 detail page
        )
        
        # Add textareas as tabs
        self.tabs.add_tab(self.TAB_ZINES, self.textarea_zines)
        self.tabs.add_tab(self.TAB_ISSUES, self.textarea_issues)
        self.tabs.add_tab(self.TAB_ARTICLES, self.textarea_articles)
        self.tabs.add_tab(self.TAB_ARTICLE_DETAIL, self.textarea_detail)
        
        self.components.append(self.c_title)
        self.components.append(self.tabs)
    
    def Initial(self):
        """Initialize the ezine browser"""
        self.tabs.set_active_tab(self.TAB_ZINES)
        self._load_zines()
        self._update_screen()
    
    def KeyPressed(self, keys: Sequence):
        """Handle key presses"""
        # Handle number/letter selection keys
        if keys.length() == 1:
            key_val = keys.valeurs[0]
            
            # Check for numeric keys 1-9
            if ord('1') <= key_val <= ord('9'):
                rel_id = key_val - ord('0')
                self._handle_selection(rel_id)
                return
            
            # Check for '0' and letters a-z
            elif key_val == ord('0'):
                self._handle_selection(10)
                return
            elif ord('a') <= key_val <= ord('z'):
                rel_id = 11 + (key_val - ord('a'))
                self._handle_selection(rel_id)
                return
        
        # Handle 'r' for refresh
        if keys.egale(Sequence('r')):
            self._refresh_current_level()
            return
        
        # Handle backspace/escape to go back
        if keys.egale(Sequence('\x7f')) or keys.egale(Sequence('\x1b')):
            self._go_back()
            return
        
        # Let parent handle other keys (page navigation)
        super().KeyPressed(keys)
    
    def _handle_selection(self, rel_id: int):
        """Handle selection based on current level"""
        current_tab = self.tabs.get_active_tab()
        
        if current_tab == self.TAB_ZINES:
            self._select_zine(rel_id)
        elif current_tab == self.TAB_ISSUES:
            self._select_issue(rel_id)
        elif current_tab == self.TAB_ARTICLES:
            self._select_article(rel_id)
        elif current_tab == self.TAB_ARTICLE_DETAIL:
            # In detail view, any key goes to reading
            self._read_article()
    
    def _select_zine(self, rel_id: int):
        """Select a zine and navigate to issues"""
        abs_id = self._rel_to_abs_id(rel_id, len(self.zines))
        if abs_id == -1:
            return
        
        self.current_zine = self.zines[abs_id]
        myLogger.log(f"Selected zine: {self.current_zine.name}")
        
        # Reset page number when selecting a new zine
        self.textarea_issues.page_current_page = 0
        
        self.tabs.set_active_tab(self.TAB_ISSUES)
        self._load_issues()
        self._update_screen()
    
    def _select_issue(self, rel_id: int):
        """Select an issue and navigate to articles"""
        abs_id = self._rel_to_abs_id(rel_id, len(self.issues))
        if abs_id == -1:
            return
        
        self.current_issue = self.issues[abs_id]
        myLogger.log(f"Selected issue: {self.current_issue.issue_num}")
        
        # Reset page number when selecting a new issue
        self.textarea_articles.page_current_page = 0
        
        self.tabs.set_active_tab(self.TAB_ARTICLES)
        self._load_articles()
        self._update_screen()
    
    def _select_article(self, rel_id: int):
        """Select an article and show detail view"""
        abs_id = self._rel_to_abs_id(rel_id, len(self.articles))
        if abs_id == -1:
            return
        
        self.current_article = self.articles[abs_id]
        myLogger.log(f"Selected article: {self.current_article.metadata.get('title', 'Unknown')}")
        
        # Reset page number when selecting a new article
        self.textarea_detail.page_current_page = 0
        
        self.tabs.set_active_tab(self.TAB_ARTICLE_DETAIL)
        self._update_screen()
    
    def _read_article(self):
        """Open the current article in Page80Read"""
        if not self.current_article:
            return
        
        try:
            with open(self.current_article.txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pageReadInput = {
                "id": self.current_article.id,
                "title": self.current_article.metadata.get('title', 'Unknown'),
                "content": content,
            }
            self.pageManager.set_current_page("80Read", pageReadInput)
        except Exception as e:
            myLogger.log(f"Error reading article {self.current_article.txt_path}: {str(e)}")
    
    def _go_back(self):
        """Navigate back one level"""
        current_tab = self.tabs.get_active_tab()
        
        if current_tab == self.TAB_ARTICLE_DETAIL:
            self.tabs.set_active_tab(self.TAB_ARTICLES)
            self.current_article = None
        elif current_tab == self.TAB_ARTICLES:
            self.tabs.set_active_tab(self.TAB_ISSUES)
            self.current_issue = None
        elif current_tab == self.TAB_ISSUES:
            self.tabs.set_active_tab(self.TAB_ZINES)
            self.current_zine = None
        else:
            # Already at top level, go back to previous page
            super().KeyPressed(Sequence('\x7f'))
            return
        
        self._update_screen()
    
    def _refresh_current_level(self):
        """Reload data for current level"""
        current_tab = self.tabs.get_active_tab()
        
        if current_tab == self.TAB_ZINES:
            self._load_zines()
        elif current_tab == self.TAB_ISSUES:
            self._load_issues()
        elif current_tab == self.TAB_ARTICLES:
            self._load_articles()
        
        self._update_screen()
    
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
    
    def _load_issues(self):
        """Load issues for the current zine"""
        self.issues = []
        if not self.current_zine:
            return
        
        try:
            issues_path = os.path.join(self.current_zine.path, "issues.json")
            if not os.path.exists(issues_path):
                myLogger.log(f"Issues file not found: {issues_path}")
                return
            
            with open(issues_path, 'r', encoding='utf-8') as f:
                issues_data = json.load(f)
            
            issue_id = 0
            for issue_data in issues_data:
                issue_num = issue_data.get('Issue', 0)
                issue_path = os.path.join(self.current_zine.path, str(issue_num))
                
                if os.path.exists(issue_path):
                    issue = IssueEntry(
                        issue_id,
                        issue_num,
                        issue_data.get('ReleaseDate', 'Unknown'),
                        issue_data.get('Editor', 'Unknown'),
                        issue_path
                    )
                    self.issues.append(issue)
                    issue_id += 1
        
        except Exception as e:
            myLogger.log(f"Error loading issues: {str(e)}")
    
    def _load_articles(self):
        """Load articles for the current issue"""
        self.articles = []
        if not self.current_issue:
            return
        
        try:
            issue_path = self.current_issue.path
            if not os.path.exists(issue_path):
                myLogger.log(f"Issue directory not found: {issue_path}")
                return
            
            # Find all .json files in the issue directory
            json_files = [f for f in os.listdir(issue_path) if f.endswith('.json')]
            
            # Sort by numeric prefix
            json_files.sort(key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else 999)
            
            article_id = 0
            for json_file in json_files:
                json_path = os.path.join(issue_path, json_file)
                # Derive .txt filename
                txt_file = json_file.replace('.json', '.txt')
                txt_path = os.path.join(issue_path, txt_file)
                
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
        """Update screen based on current level"""
        current_tab = self.tabs.get_active_tab()
        
        if current_tab == self.TAB_ZINES:
            self._display_zines()
        elif current_tab == self.TAB_ISSUES:
            self._display_issues()
        elif current_tab == self.TAB_ARTICLES:
            self._display_articles()
        elif current_tab == self.TAB_ARTICLE_DETAIL:
            self._display_article_detail()
    
    def _display_zines(self):
        """Display zines overview"""
        self.c_title.set_text("E-Zines")
        
        # Generate all pages (3 zines per page for better readability)
        zines_per_page = 3
        total_zines = len(self.zines)
        total_pages = max(1, (total_zines + zines_per_page - 1) // zines_per_page)
        all_pages = []
        
        for page_num in range(total_pages):
            start_idx = page_num * zines_per_page
            end_idx = min(start_idx + zines_per_page, total_zines)
            
            lines = []
            page_rel_id = 1
            for i in range(start_idx, end_idx):
                zine = self.zines[i]
                key = self._get_selection_key(page_rel_id)
                
                # Format: [key] Name - Topic
                name = zine.about.get('name', zine.name)
                topic = zine.about.get('topic', '')
                date = zine.about.get('date', '')
                description = zine.about.get('description', '')
                
                lines.append(f"{key} {name} ({date})")
                lines.append(f"  {description}")
                #lines.append(f"  {topic}")
                lines.append("")  # Blank line
                
                page_rel_id += 1
            
            content = "\n".join(lines)
            all_pages.append(content)
        
        self.textarea_zines.set_page_contents(all_pages)
    
    def _display_issues(self):
        """Display issues for current zine"""
        if not self.current_zine:
            return
        
        title = f"{self.current_zine.about.get('name', self.current_zine.name)} - Issues"
        self.c_title.set_text(title)
        
        # Generate all pages
        total_issues = len(self.issues)
        total_pages = max(1, (total_issues + self.issues_per_page - 1) // self.issues_per_page)
        all_pages = []
        
        for page_num in range(total_pages):
            start_idx = page_num * self.issues_per_page
            end_idx = min(start_idx + self.issues_per_page, total_issues)
            
            lines = []
            page_rel_id = 1
            for i in range(start_idx, end_idx):
                issue = self.issues[i]
                key = self._get_selection_key(page_rel_id)
                lines.append(f"[{key}] Issue {issue.issue_num} - {issue.release_date}")
                page_rel_id += 1
            
            content = "\n".join(lines)
            all_pages.append(content)
        
        self.textarea_issues.set_page_contents(all_pages)
    
    def _display_articles(self):
        """Display articles for current issue"""
        if not self.current_issue:
            return
        
        zine_name = self.current_zine.about.get('name', self.current_zine.name) if self.current_zine else "Unknown"
        title = f"{zine_name} #{self.current_issue.issue_num}"
        self.c_title.set_text(title)
        
        # Generate all pages (1 article per page)
        total_articles = len(self.articles)
        all_pages = []
        
        for i in range(total_articles):
            article = self.articles[i]
            key = self._get_selection_key(1)  # Always use key "1" since only 1 article per page
            
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
    
    def _display_article_detail(self):
        """Display detailed information about selected article"""
        if not self.current_article:
            return
        
        metadata = self.current_article.metadata
        lines = []
        self.c_title.set_text(f"Article #{self.current_article.article_num}")

        title = metadata.get('title', 'Unknown')
        lines.append(f"TITLE: {title}")
        
        authors = metadata.get('authors', 'Unknown')
        lines.append(f"AUTHORS: {authors}")
        
        date = metadata.get('date', 'Unknown')
        lines.append(f"DATE: {date}")
        
        summary = metadata.get('summary', '')
        if summary:
            lines.append("")
            lines.extend(self._wrap_text(summary, self.framebuffer.width))
            lines.append("")
        
        content = "\n".join(lines)
        # For detail view, show all content as a single page
        self.textarea_detail.set_page_contents([content])
    
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
    
    def _rel_to_abs_id(self, rel_id: int, total_items: int) -> int:
        """Convert relative page ID to absolute ID"""
        current_tab = self.tabs.get_active_tab()
        
        # Get the current page from the appropriate textarea
        if current_tab == self.TAB_ZINES:
            current_page = self.textarea_zines.get_current_page()
            items_per_page = self.zines_per_page
        elif current_tab == self.TAB_ISSUES:
            current_page = self.textarea_issues.get_current_page()
            items_per_page = self.issues_per_page
        elif current_tab == self.TAB_ARTICLES:
            current_page = self.textarea_articles.get_current_page()
            items_per_page = self.articles_per_page
        elif current_tab == self.TAB_ARTICLE_DETAIL:
            items_per_page = self.article_details_per_page
        else:
            # For detail view, no pagination
            return 0
        
        abs_id = current_page * items_per_page + (rel_id - 1)
        if 0 <= abs_id < total_items:
            return abs_id
        return -1
    
    def _get_selection_key(self, rel_id: int) -> str:
        """Get selection key string for relative ID"""
        if 1 <= rel_id <= 9:
            return str(rel_id)
        elif rel_id == 10:
            return "0"
        elif 11 <= rel_id <= 36:
            return chr(ord('a') + (rel_id - 11))
        else:
            return "?"
