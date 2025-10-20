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


class IssueEntry:
    """Represents a zine issue"""
    def __init__(self, id: int, issue_num: int, release_date: str, editor: str, path: str):
        self.id: int = id
        self.issue_num: int = issue_num
        self.release_date: str = release_date
        self.editor: str = editor
        self.path: str = path


class PageEzinesIssues(Page):
    """Display list of issues for a selected e-zine"""
    
    def __init__(self, framebuffer: FrameBuffer, name: str):
        super().__init__(framebuffer, name)
        
        # Configuration
        self.issues_per_page = 20
        
        # Zine data (from pageInput)
        self.zine_id = None
        self.zine_name = ""
        self.zine_path = ""
        self.zine_about = {}
        
        # Data
        self.issues: List[IssueEntry] = []
        
        # Components
        self.c_title = ComponentLabel(
            framebuffer,
            0,
            0,
            self.framebuffer.width,
            "Issues",
            center=True
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
        
        self.components.append(self.c_title)
        self.components.append(self.textarea_issues)
    
    def Initial(self):
        """Initialize the issues list"""
        # Get zine data from pageInput
        pageInput = self.get_page_input_once()
        if pageInput:
            self.zine_id = pageInput.get("zine_id")
            self.zine_name = pageInput.get("zine_name", "")
            self.zine_path = pageInput.get("zine_path", "")
            self.zine_about = pageInput.get("zine_about", {})
        
        self._load_issues()
        self._update_screen()
    
    def KeyPressed(self, keys: Sequence):
        """Handle key presses"""
        # Handle number/letter selection keys
        if keys.length() == 1:
            rel_id = parse_selection_key(keys.valeurs[0])
            if rel_id is not None:
                self._select_issue(rel_id)
                return
        
        # Handle 'r' for refresh
        if keys.egale(Sequence('r')):
            self._load_issues()
            self._update_screen()
            return
        
        # Let parent handle other keys (page navigation, back navigation)
        super().KeyPressed(keys)
    
    def _select_issue(self, rel_id: int):
        """Select an issue and navigate to articles page"""
        abs_id = self.textarea_issues.rel_page_offset_to_abs_id(rel_id, len(self.issues))
        if abs_id == -1:
            return
        
        issue = self.issues[abs_id]
        myLogger.log(f"Selected issue: {issue.issue_num}")
        
        # Navigate to articles page with issue data
        pageInput = {
            "zine_id": self.zine_id,
            "zine_name": self.zine_name,
            "zine_about": self.zine_about,
            "issue_id": issue.id,
            "issue_num": issue.issue_num,
            "issue_path": issue.path,
            "release_date": issue.release_date,
            "editor": issue.editor
        }
        if self.pageManager is not None:
            self.pageManager.set_current_page("EzinesArticles", pageInput)
    
    def _load_issues(self):
        """Load issues for the current zine"""
        self.issues = []
        if not self.zine_path:
            return
        
        try:
            issues_path = os.path.join(self.zine_path, "issues.json")
            if not os.path.exists(issues_path):
                myLogger.log(f"Issues file not found: {issues_path}")
                return
            
            with open(issues_path, 'r', encoding='utf-8') as f:
                issues_data = json.load(f)
            
            issue_id = 0
            for issue_data in issues_data:
                issue_num = issue_data.get('Issue', 0)
                issue_path = os.path.join(self.zine_path, str(issue_num))
                
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
    
    def _update_screen(self):
        """Update screen with issues list"""
        zine_display_name = self.zine_about.get('name', self.zine_name)
        title = f"{zine_display_name} - Issues"
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
                key = get_selection_key(page_rel_id)
                lines.append(f"[{key}] Issue {issue.issue_num} - {issue.release_date}")
                page_rel_id += 1
            
            content = "\n".join(lines)
            all_pages.append(content)
        
        self.textarea_issues.set_page_contents(all_pages)
