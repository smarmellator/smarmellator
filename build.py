#!/usr/bin/env python3
import os
import re
import markdown
from datetime import datetime

POSTS_MD_DIR = 'posts_md'
POSTS_DIR = 'posts'
TEMPLATE_FILE = 'posts/template.html'

def get_template():
    with open(TEMPLATE_FILE, 'r') as f:
        return f.read()

def extract_frontmatter(content):
    """Extract title and date from markdown header."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        body = match.group(2)
        title_match = re.search(r'title:\s*(.+?)$', frontmatter, re.MULTILINE)
        date_match = re.search(r'date:\s*(.+?)$', frontmatter, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else 'Untitled'
        date = date_match.group(1).strip() if date_match else datetime.now().strftime('%B %d, %Y')
        return title, date, body
    return 'Untitled', datetime.now().strftime('%B %d, %Y'), content

def convert_md_to_html(md_content):
    """Convert markdown to HTML with some custom extensions."""
    md = markdown.Markdown(extensions=['extra', 'codehilite'])
    return md.convert(md_content)

def build_post(md_file):
    """Build a single post from markdown to HTML."""
    md_path = os.path.join(POSTS_MD_DIR, md_file)
    with open(md_path, 'r') as f:
        md_content = f.read()
    
    title, date, body = extract_frontmatter(md_content)
    html_content = convert_md_to_html(body)
    
    template = get_template()
    
    # Generate a post_id from filename
    post_id = os.path.splitext(md_file)[0]
    html_filename = f"{post_id}.html"
    
    # Replace title
    template = re.sub(r'<title>[^<]*</title>', f'<title>{title} - Matteo Di Mario</title>', template)
    
    # Replace post title
    template = re.sub(r'<h1 class="post-title">[^<]*</h1>', f'<h1 class="post-title">{title}</h1>', template)
    
    # Replace meta (date and author)
    template = re.sub(r'<div class="post-meta">\s*<a href="/">[^<]*</a> · [^<]*</div>', 
                     f'<div class="post-meta"><a href="/">&lt;matteodimario&gt;</a> · {date}</div>', template)
    
    # Replace post content - find the exact pattern
    # Find post-content div and replace everything inside it until back-link
    pattern = r'(<div class="post-content">).*?(</article>)'
    replacement = r'\1\n' + html_content + r'\n\2'
    template = re.sub(pattern, replacement, template, flags=re.DOTALL)
    
    # Replace POST_ID in JavaScript
    template = re.sub(r"const POST_ID = '[^']*';", f"const POST_ID = '{post_id}';", template)
    
    output_path = os.path.join(POSTS_DIR, html_filename)
    with open(output_path, 'w') as f:
        f.write(template)
    
    print(f"Built: {html_filename}")

def main():
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)
    
    md_files = [f for f in os.listdir(POSTS_MD_DIR) if f.endswith('.md')]
    
    if not md_files:
        print(f"No .md files found in {POSTS_MD_DIR}")
        return
    
    for md_file in sorted(md_files):
        build_post(md_file)
    
    print(f"\nDone! Built {len(md_files)} post(s)")

if __name__ == '__main__':
    main()
