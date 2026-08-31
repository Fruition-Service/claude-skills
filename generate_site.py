import os
import re
import json
import shutil
import markdown

SCRAPED_DIR = 'scraped-pages'
DIST_DIR = 'dist'
TEMPLATES_DIR = 'templates'

def parse_markdown(md_text):
    lines = md_text.split('\n')
    title = "Skill"
    description = ""
    
    # Extract Title
    for i, line in enumerate(lines):
        if line.startswith('# '):
            title = line[2:].strip()
            lines.pop(i)
            break
            
    # Extract Description (first non-empty line after title that isn't a heading)
    desc_idx = -1
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('#'):
            description = line.strip()
            desc_idx = i
            break
            
    if desc_idx != -1:
        lines.pop(desc_idx)
        
    # The rest is content
    content_md = '\n'.join(lines)
    content_html = markdown.markdown(content_md)
    
    return title, description, content_html

def main():
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)
        
    shutil.copy(os.path.join(TEMPLATES_DIR, 'style.css'), os.path.join(DIST_DIR, 'style.css'))
    
    with open(os.path.join(TEMPLATES_DIR, 'index_template.html'), 'r') as f:
        index_template = f.read()
        
    with open(os.path.join(TEMPLATES_DIR, 'skill_template.html'), 'r') as f:
        skill_template = f.read()
        
    skills = []
    
    for item in sorted(os.listdir(SCRAPED_DIR)):
        item_path = os.path.join(SCRAPED_DIR, item)
        if os.path.isdir(item_path) and item not in ['_landing', 'manifest.json']:
            skill_md_path = os.path.join(item_path, 'SKILL.md')
            if os.path.exists(skill_md_path):
                with open(skill_md_path, 'r', encoding='utf-8') as f:
                    md_text = f.read()
                    
                title, description, content_html = parse_markdown(md_text)
                
                # Truncate description for grid if it's too long
                short_desc = description
                if len(short_desc) > 120:
                    short_desc = short_desc[:117] + "..."
                    
                skills.append({
                    'slug': item,
                    'title': title,
                    'description': short_desc
                })
                
                # Create skill page
                skill_dist_dir = os.path.join(DIST_DIR, 'skills', item)
                os.makedirs(skill_dist_dir, exist_ok=True)
                
                html_out = skill_template.replace('{{ TITLE }}', title)
                html_out = html_out.replace('{{ DESCRIPTION }}', description)
                html_out = html_out.replace('{{ CONTENT }}', content_html)
                
                with open(os.path.join(skill_dist_dir, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(html_out)
                    
    # Generate Index Grid
    cards_html = ""
    for skill in skills:
        cards_html += f"""
      <a href="skills/{skill['slug']}/index.html" class="skill-card">
        <h3>{skill['title']}</h3>
        <p>{skill['description']}</p>
      </a>"""
      
    final_index = index_template.replace('<!-- SKILL_CARDS_PLACEHOLDER -->', cards_html)
    with open(os.path.join(DIST_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(final_index)
        
    print(f"Successfully generated {len(skills)} skill pages.")

if __name__ == '__main__':
    main()
