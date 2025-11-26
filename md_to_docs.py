#!/usr/bin/env python3
"""
Markdown to Documentation HTML Converter
Run like: python md_to_docs.py TUTORIAL.md -o docs.html --title "LIPID+ - Documentation"

Converts a markdown file to a documentation HTML page with:
- Left sidebar navigation (Level 1 headings as main items)
- Collapsible submenus (Level 2 headings as sub-items)
- Styled content sections
- Dark mode support
- Mobile responsive design
"""

import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import html


@dataclass
class Section:
    """Represents a documentation section"""
    id: str
    title: str
    level: int
    content: str = ""
    children: list = field(default_factory=list)
    parent_id: Optional[str] = None


class MarkdownToDocsConverter:
    def __init__(self, title: str = "Documentation", logo_path: str = "images/logo.svg",
                 css_path: str = "css/style.css", github_url: str = "#"):
        self.title = title
        self.logo_path = logo_path
        self.css_path = css_path
        self.github_url = github_url
        self.sections: list[Section] = []
        
    def slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text
    
    def parse_markdown(self, md_content: str) -> list[Section]:
        """Parse markdown content into sections"""
        lines = md_content.split('\n')
        sections = []
        current_h1: Optional[Section] = None
        current_section: Optional[Section] = None
        content_buffer = []
        in_code_block = False
        
        def save_content():
            nonlocal content_buffer, current_section
            if current_section and content_buffer:
                current_section.content = '\n'.join(content_buffer)
                content_buffer = []
        
        for line in lines:
            # Track code blocks to avoid matching # inside them
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if current_section:
                    content_buffer.append(line)
                continue
            
            # Skip heading detection inside code blocks
            if in_code_block:
                if current_section:
                    content_buffer.append(line)
                continue
            
            # Check for Level 1 heading (must be at start of line)
            h1_match = re.match(r'^#\s+(.+)$', line)
            if h1_match:
                save_content()
                title = h1_match.group(1).strip()
                section_id = f"page-{self.slugify(title)}"
                current_h1 = Section(id=section_id, title=title, level=1)
                current_section = current_h1
                sections.append(current_h1)
                continue
            
            # Check for Level 2 heading
            h2_match = re.match(r'^##\s+(.+)$', line)
            if h2_match and current_h1:
                save_content()
                title = h2_match.group(1).strip()
                section_id = f"page-{self.slugify(current_h1.title)}-{self.slugify(title)}"
                h2_section = Section(
                    id=section_id, 
                    title=title, 
                    level=2, 
                    parent_id=current_h1.id
                )
                current_h1.children.append(h2_section)
                current_section = h2_section
                continue
            
            # Accumulate content
            if current_section:
                content_buffer.append(line)
        
        # Save remaining content
        save_content()
        
        self.sections = sections
        return sections
    
    def convert_markdown_to_html(self, md_content: str) -> str:
        """Convert markdown content to HTML"""
        html_content = md_content
        
        # Escape HTML special characters in text (but not in code blocks)
        # We'll handle code blocks separately
        
        # Convert code blocks first (preserve them)
        code_blocks = []
        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"___CODE_BLOCK_{len(code_blocks)-1}___"
        
        # Triple backtick code blocks
        html_content = re.sub(
            r'```(\w*)\n(.*?)```',
            save_code_block,
            html_content,
            flags=re.DOTALL
        )
        
        # Inline code
        inline_codes = []
        def save_inline_code(match):
            inline_codes.append(match.group(1))
            return f"___INLINE_CODE_{len(inline_codes)-1}___"
        
        html_content = re.sub(r'`([^`]+)`', save_inline_code, html_content)
        
        # Convert headings (h3, h4 - h1 and h2 are handled as sections)
        html_content = re.sub(
            r'^####\s+(.+)$',
            r'<h4 class="text-lg font-semibold mt-6 mb-3 dark:text-white">\1</h4>',
            html_content,
            flags=re.MULTILINE
        )
        html_content = re.sub(
            r'^###\s+(.+)$',
            r'<h3 class="text-xl font-semibold mt-6 mb-3 dark:text-white">\1</h3>',
            html_content,
            flags=re.MULTILINE
        )
        
        # Convert horizontal rules
        html_content = re.sub(r'^---+$', '<hr />', html_content, flags=re.MULTILINE)
        
        # Convert bold
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        
        # Convert italic
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
        
        # Convert links
        html_content = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2" class="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300">\1</a>',
            html_content
        )
        
        # Convert tables
        html_content = self._convert_tables(html_content)
        
        # Convert unordered lists
        html_content = self._convert_lists(html_content)
        
        # Convert paragraphs (non-empty lines that aren't already HTML)
        lines = html_content.split('\n')
        result_lines = []
        in_list = False
        in_pre = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if in_list:
                    in_list = False
                result_lines.append('')
                continue
            
            # Skip lines that are already HTML tags or special markers
            if (stripped.startswith('<') or 
                stripped.startswith('___') or
                stripped.startswith('|') or
                stripped.startswith('-') and len(stripped) > 1 and stripped[1] == ' '):
                result_lines.append(line)
                continue
            
            # Wrap plain text in paragraph tags
            if not stripped.startswith('<'):
                result_lines.append(f'<p class="text-lg text-gray-700 leading-relaxed mb-4 dark:text-gray-300">{stripped}</p>')
            else:
                result_lines.append(line)
        
        html_content = '\n'.join(result_lines)
        
        # Restore code blocks with styling
        for i, code_block in enumerate(code_blocks):
            match = re.match(r'```(\w*)\n(.*?)```', code_block, re.DOTALL)
            if match:
                lang = match.group(1) or 'text'
                code = html.escape(match.group(2).strip())
                styled_block = f'''<pre data-language="{lang}">
<code class="language-{lang}">{code}</code>
</pre>'''
                html_content = html_content.replace(f"___CODE_BLOCK_{i}___", styled_block)
        
        # Restore inline code with styling
        for i, code in enumerate(inline_codes):
            escaped_code = html.escape(code)
            styled_code = f'<code>{escaped_code}</code>'
            html_content = html_content.replace(f"___INLINE_CODE_{i}___", styled_code)
        
        return html_content
    
    def _convert_tables(self, content: str) -> str:
        """Convert markdown tables to HTML tables"""
        lines = content.split('\n')
        result = []
        table_lines = []
        in_table = False
        
        for line in lines:
            if '|' in line and line.strip().startswith('|'):
                in_table = True
                table_lines.append(line)
            else:
                if in_table:
                    # Process the table
                    result.append(self._process_table(table_lines))
                    table_lines = []
                    in_table = False
                result.append(line)
        
        # Handle table at end of content
        if table_lines:
            result.append(self._process_table(table_lines))
        
        return '\n'.join(result)
    
    def _process_table(self, lines: list[str]) -> str:
        """Process markdown table lines into HTML table"""
        if len(lines) < 2:
            return '\n'.join(lines)
        
        html_table = ['<div class="overflow-x-auto mb-6">']
        html_table.append('<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">')
        
        for i, line in enumerate(lines):
            # Skip separator line (------|----)
            if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                continue
            
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            
            if i == 0:
                # Header row
                html_table.append('<thead class="bg-gray-50 dark:bg-gray-800">')
                html_table.append('<tr>')
                for cell in cells:
                    html_table.append(f'<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">{cell}</th>')
                html_table.append('</tr>')
                html_table.append('</thead>')
                html_table.append('<tbody class="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">')
            else:
                # Data row
                html_table.append('<tr>')
                for cell in cells:
                    html_table.append(f'<td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{cell}</td>')
                html_table.append('</tr>')
        
        html_table.append('</tbody>')
        html_table.append('</table>')
        html_table.append('</div>')
        
        return '\n'.join(html_table)
    
    def _convert_lists(self, content: str) -> str:
        """Convert markdown lists to HTML lists"""
        lines = content.split('\n')
        result = []
        list_items = []
        list_type = None  # 'ul' or 'ol'
        indent_level = 0
        
        for line in lines:
            # Check for unordered list item
            ul_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
            # Check for ordered list item
            ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
            
            if ul_match:
                if list_type != 'ul' and list_items:
                    result.append(self._create_list(list_items, list_type))
                    list_items = []
                list_type = 'ul'
                list_items.append(ul_match.group(2))
            elif ol_match:
                if list_type != 'ol' and list_items:
                    result.append(self._create_list(list_items, list_type))
                    list_items = []
                list_type = 'ol'
                list_items.append(ol_match.group(2))
            else:
                if list_items:
                    result.append(self._create_list(list_items, list_type))
                    list_items = []
                    list_type = None
                result.append(line)
        
        # Handle remaining list items
        if list_items:
            result.append(self._create_list(list_items, list_type))
        
        return '\n'.join(result)
    
    def _create_list(self, items: list[str], list_type: str) -> str:
        """Create HTML list from items"""
        tag = list_type or 'ul'
        list_class = "list-disc" if tag == 'ul' else "list-decimal"
        html_list = [f'<{tag} class="{list_class} list-inside space-y-2 mb-4 text-gray-700 dark:text-gray-300">']
        for item in items:
            html_list.append(f'<li>{item}</li>')
        html_list.append(f'</{tag}>')
        return '\n'.join(html_list)
    
    def generate_sidebar_nav(self) -> str:
        """Generate sidebar navigation HTML"""
        nav_items = []
        
        for section in self.sections:
            if section.children:
                # Section with subsections - create collapsible menu
                submenu_id = f"submenu-{self.slugify(section.title)}"
                nav_items.append(f'''
                            <!-- Collapsible {section.title} Menu -->
                            <div>
                                <button onclick="toggleSidebarMenu('{submenu_id}', this)" class="sidebar-link group w-full flex items-center justify-between px-3 py-2 text-base font-medium rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white" aria-expanded="false">
                                    <span>{section.title}</span>
                                    <svg class="submenu-chevron w-5 h-5 transform transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                                </button>
                                <div id="{submenu_id}" class="hidden mt-1 space-y-1 pl-4 border-l-2 border-gray-200 ml-3 dark:border-gray-600">''')
                
                for child in section.children:
                    nav_items.append(f'''
                                    <a href="#" class="sidebar-link group flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white" data-page-id="{child.id}" onclick="showPage('{child.id}', 'nav-docs', this)">
                                        {child.title}
                                    </a>''')
                
                nav_items.append('''
                                </div>
                            </div>''')
            else:
                # Simple section without subsections
                nav_items.append(f'''
                            <a href="#" class="sidebar-link group flex items-center px-3 py-2 text-base font-medium rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white" data-page-id="{section.id}" onclick="showPage('{section.id}', 'nav-docs', this)">
                                {section.title}
                            </a>''')
        
        return '\n'.join(nav_items)
    
    def generate_dropdown_items(self) -> str:
        """Generate dropdown menu items for top navigation"""
        items = []
        for section in self.sections:
            items.append(f'''                    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700" onclick="showPage('{section.id}', 'nav-docs', this)" data-page-id="{section.id}">{section.title}</a>''')
        return '\n'.join(items)
    
    def generate_content_sections(self) -> str:
        """Generate content sections HTML"""
        sections_html = []
        
        for section in self.sections:
            # Convert section content
            content_html = self.convert_markdown_to_html(section.content)
            
            section_html = f'''
                <!-- Page: {section.title} -->
                <section id="{section.id}" class="page-content hidden">
                    <h1 class="text-4xl font-bold mb-6 pb-2 border-b border-gray-200 text-gray-900 dark:text-white dark:border-gray-700">{section.title}</h1>
                    {content_html}'''
            
            # Add child sections
            for child in section.children:
                child_content_html = self.convert_markdown_to_html(child.content)
                section_html += f'''
                    
                    <section id="{child.id}-content" class="mt-10">
                        <h2 class="text-2xl font-semibold mt-8 mb-4 dark:text-white">{child.title}</h2>
                        {child_content_html}
                    </section>'''
            
            section_html += '''
                </section>'''
            
            sections_html.append(section_html)
            
            # Also create separate pages for child sections if they should be standalone
            for child in section.children:
                child_content_html = self.convert_markdown_to_html(child.content)
                child_section = f'''
                <!-- Page: {child.title} -->
                <section id="{child.id}" class="page-content hidden">
                    <h1 class="text-4xl font-bold mb-6 pb-2 border-b border-gray-200 text-gray-900 dark:text-white dark:border-gray-700">{child.title}</h1>
                    {child_content_html}
                </section>'''
                sections_html.append(child_section)
        
        return '\n'.join(sections_html)
    
    def get_first_page_id(self) -> str:
        """Get the ID of the first page for default display"""
        if self.sections:
            return self.sections[0].id
        return "page-home"
    
    def generate_html(self, md_content: str) -> str:
        """Generate complete HTML document from markdown"""
        self.parse_markdown(md_content)
        
        sidebar_nav = self.generate_sidebar_nav()
        dropdown_items = self.generate_dropdown_items()
        content_sections = self.generate_content_sections()
        first_page_id = self.get_first_page_id()
        
        return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Load Roboto font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet">
    <!-- Link to external stylesheet -->
    <link rel="stylesheet" href="{self.css_path}">
</head>
<body class="bg-white text-gray-800 dark:bg-gray-900 dark:text-gray-200 transition-colors duration-200">

    <!-- Overlay for mobile menu -->
    <div id="overlay" class="fixed inset-0 bg-black bg-opacity-50 z-30 hidden md:hidden" onclick="toggleMobileMenu()"></div>

    <!-- Top Navigation Bar -->
    <nav class="fixed top-0 left-0 w-full h-16 bg-white border-b border-gray-200 z-40 flex items-center justify-between pl-10 pr-4 md:pl-10 md:pr-6 dark:bg-gray-900 dark:border-gray-700">
        <!-- Logo and Mobile Menu Button -->
        <div class="flex items-center space-x-4">
            <!-- Mobile Menu Button (Hamburger) -->
            <button id="mobile-menu-btn" class="md:hidden text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white" onclick="toggleMobileMenu()" aria-label="Toggle menu">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </button>
            
            <!-- Logo/Title -->
            <a href="index.html" class="flex items-center space-x-2">
                <!-- Logo Image -->
                <img src="{self.logo_path}" alt="Logo" class="w-24 h-16">
            </a>
        </div>

        <!-- Desktop Navigation Links -->
        <div class="hidden md:flex items-center space-x-6">
            <a href="index.html" class="nav-link text-gray-600 hover:text-purple-600 dark:text-gray-300 dark:hover:text-purple-300">Home</a>
            
            <!-- Docs Dropdown -->
            <div class="relative">
                <button class="nav-link nav-active flex items-center text-gray-600 hover:text-purple-600 dark:text-gray-300 dark:hover:text-purple-300" data-nav-id="nav-docs" onclick="toggleDropdown('docs-dropdown')">
                    Docs
                    <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </button>
                <div id="docs-dropdown" class="dropdown-menu hidden absolute right-0 mt-2 w-48 bg-white rounded-md shadow-xl z-50 border border-gray-100 py-1 dark:bg-gray-800 dark:border-gray-700">
{dropdown_items}
                </div>
            </div>

            <!-- About Dropdown -->
            <div class="relative">
                <button class="nav-link flex items-center text-gray-600 hover:text-purple-600 dark:text-gray-300 dark:hover:text-purple-300" data-nav-id="nav-about" onclick="toggleDropdown('about-dropdown')">
                    About
                    <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </button>
                <div id="about-dropdown" class="dropdown-menu hidden absolute right-0 mt-2 w-48 bg-white rounded-md shadow-xl z-50 border border-gray-100 py-1 dark:bg-gray-800 dark:border-gray-700">
                    <a href="about.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">About Us</a>
                    <a href="about.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">Contact</a>
                    <a href="about.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">Citation</a>
                </div>
            </div>
            
            <!-- Search Bar -->
            <form class="relative" onsubmit="handleSearch(event)">
                <input id="search-input" type="text" placeholder="Search docs..." class="bg-gray-100 border border-gray-300 rounded-md py-1.5 px-4 text-sm w-48 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:placeholder-gray-500">
                <button type="submit" class="text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 hover:text-purple-600 dark:hover:text-purple-400" aria-label="Search">
                    <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </button>
            </form>

            <!-- Dark Mode Toggle -->
            <button id="dark-mode-toggle" class="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-white" onclick="toggleDarkMode()" aria-label="Toggle dark mode">
                <svg id="theme-icon-light" class="w-6 h-6 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                <svg id="theme-icon-dark" class="w-6 h-6 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
            </button>

            <!-- GitHub Link -->
            <a href="{self.github_url}" target="_blank" rel="noopener noreferrer" class="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-white" aria-label="GitHub repository">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.165 6.839 9.489.5.092.682-.217.682-.483 0-.237-.009-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.84c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.026 2.747-1.026.546 1.379.202 2.398.1 2.65.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.001 10.001 0 0022 12c0-5.523-4.477-10-10-10z"/>
                </svg>
            </a>
        </div>
    </nav>

    <!-- Main Container -->
    <div class="relative min-h-screen">
        <!-- Sidebar -->
        <aside id="sidebar" class="fixed top-0 left-0 w-64 lg:w-72 h-screen bg-gray-50 border-r border-gray-200 z-30 md:translate-x-0 transition-transform duration-300 ease-in-out dark:bg-gray-800 dark:border-gray-700 transform -translate-x-full">
            <!-- Sidebar content wrapper with padding for top nav -->
            <div id="sidebar-content" class="h-full pt-16 overflow-y-auto">
                <div class="px-4 py-6">

                    <!-- Docs Nav -->
                    <nav id="nav-docs" class="sidebar-nav">
                        <!-- Navigation items for Docs -->
                        <div class="space-y-1">
{sidebar_nav}
                        </div>
                    </nav>

                </div>
            </div>
        </aside>

        <!-- Main Content Area -->
        <main id="content-area" class="w-full pt-16 transition-all duration-300 ease-in-out md:pl-64 lg:pl-72">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
                {content_sections}
            </div>
        </main>
    </div>

    <!-- Search Modal -->
    <div id="search-modal" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden flex items-center justify-center">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <p id="search-modal-message" class="text-gray-700 dark:text-gray-300 mb-4"></p>
            <button onclick="closeSearchModal()" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">Close</button>
        </div>
    </div>

    <script>
        // --- Page Navigation ---
        function showPage(pageId, navId, clickedElement) {{
            // Hide all page content sections
            document.querySelectorAll('.page-content').forEach(page => {{
                page.classList.add('hidden');
            }});

            // Show the selected page
            const targetPage = document.getElementById(pageId);
            if (targetPage) {{
                targetPage.classList.remove('hidden');
            }}

            // Remove active class from all sidebar links
            document.querySelectorAll('.sidebar-link').forEach(link => {{
                link.classList.remove('sidebar-active');
            }});

            // Add active class to clicked element
            if (clickedElement) {{
                clickedElement.classList.add('sidebar-active');
            }}

            // Close mobile menu on page navigation
            if (window.innerWidth < 768) {{
                toggleMobileMenu(false);
            }}

            // Close dropdowns
            closeAllDropdowns();
        }}

        // --- Dropdown Menus ---
        function toggleDropdown(dropdownId) {{
            const dropdown = document.getElementById(dropdownId);
            const isOpen = !dropdown.classList.contains('hidden');
            
            // Close all dropdowns first
            closeAllDropdowns();

            // If it was closed, open it
            if (!isOpen) {{
                dropdown.classList.remove('hidden');
            }}
        }}

        function closeAllDropdowns() {{
            document.querySelectorAll('.dropdown-menu').forEach(menu => {{
                menu.classList.add('hidden');
            }});
        }}

        // Close dropdowns if clicking outside
        window.addEventListener('click', function(event) {{
            if (!event.target.closest('[onclick^="toggleDropdown"]')) {{
                closeAllDropdowns();
            }}
        }});

        // --- Sidebar Submenu ---
        function toggleSidebarMenu(submenuId, element) {{
            const submenu = document.getElementById(submenuId);
            const chevron = element.querySelector('.submenu-chevron');
            if (submenu) {{
                submenu.classList.toggle('hidden');
                chevron.classList.toggle('rotate-180');
                element.setAttribute('aria-expanded', !submenu.classList.contains('hidden'));
            }}
        }}

        // --- Mobile Menu Toggle ---
        function toggleMobileMenu(forceState) {{
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('overlay');
            const mobileMenuBtn = document.getElementById('mobile-menu-btn');
            
            let open;
            if (typeof forceState === 'boolean') {{
                open = forceState;
            }} else {{
                open = sidebar.classList.contains('-translate-x-full');
            }}

            if (open) {{
                sidebar.classList.remove('-translate-x-full');
                sidebar.classList.add('translate-x-0');
                overlay.classList.remove('hidden');
                mobileMenuBtn.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`;
            }} else {{
                sidebar.classList.add('-translate-x-full');
                sidebar.classList.remove('translate-x-0');
                overlay.classList.add('hidden');
                mobileMenuBtn.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>`;
            }}
        }}

        // --- Search Modal ---
        function showSearchModal(message) {{
            document.getElementById('search-modal-message').textContent = message;
            document.getElementById('search-modal').classList.remove('hidden');
        }}

        function closeSearchModal() {{
            document.getElementById('search-modal').classList.add('hidden');
        }}

        function handleSearch(event) {{
            event.preventDefault();
            const input = document.getElementById('search-input');
            const query = input.value.trim();
            if (query) {{
                showSearchModal(`Search functionality for "${{query}}" is not implemented yet.`);
            }} else {{
                showSearchModal('Please enter a search term.');
            }}
        }}
        
        // --- Dark Mode ---
        const themeIconLight = document.getElementById('theme-icon-light');
        const themeIconDark = document.getElementById('theme-icon-dark');

        function toggleDarkMode() {{
            if (document.documentElement.classList.contains('dark')) {{
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
                themeIconLight.classList.remove('hidden');
                themeIconDark.classList.add('hidden');
            }} else {{
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
                themeIconDark.classList.remove('hidden');
                themeIconLight.classList.add('hidden');
            }}
        }}

        // Check for saved theme preference
        function applyInitialTheme() {{
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
                document.documentElement.classList.add('dark');
                themeIconDark.classList.remove('hidden');
            }} else {{
                document.documentElement.classList.remove('dark');
                themeIconLight.classList.remove('hidden');
            }}
        }}

        applyInitialTheme();

        // --- Initialize Page ---
        // Show first page by default
        document.addEventListener('DOMContentLoaded', function() {{
            const firstLink = document.querySelector('.sidebar-link[data-page-id]');
            if (firstLink) {{
                showPage('{first_page_id}', 'nav-docs', firstLink);
            }}
        }});
    </script>

</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown to Documentation HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example usage:
  python md_to_docs.py TUTORIAL.md -o docs.html
  python md_to_docs.py TUTORIAL.md -o docs.html --title "LIPID+ Documentation"
  python md_to_docs.py TUTORIAL.md -o docs.html --logo images/logo.svg --github https://github.com/user/repo
        '''
    )
    
    parser.add_argument('input', help='Input Markdown file path')
    parser.add_argument('-o', '--output', default='docs.html', help='Output HTML file path (default: docs.html)')
    parser.add_argument('--title', default='LIPID+ - Documentation', help='Page title')
    parser.add_argument('--logo', default='images/logo.svg', help='Path to logo image')
    parser.add_argument('--css', default='css/style.css', help='Path to CSS file')
    parser.add_argument('--github', default='https://github.com/pluskal-lab/DreaMS', help='GitHub repository URL')
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert
    converter = MarkdownToDocsConverter(
        title=args.title,
        logo_path=args.logo,
        css_path=args.css,
        github_url=args.github
    )
    
    html_content = converter.generate_html(md_content)
    
    # Write output
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Successfully converted '{args.input}' to '{args.output}'")
    print(f"Found {len(converter.sections)} main sections")
    
    for section in converter.sections:
        print(f"  - {section.title}")
        for child in section.children:
            print(f"      - {child.title}")
    
    return 0


if __name__ == '__main__':
    exit(main())
