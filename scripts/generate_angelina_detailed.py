import re

md_path = 'content/Family/Angelina-and-Taylor.md'
html_path = 'hu/angelina-and-taylor-detailed.html'

with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

html_content = '<div class="narrative-content narrative-content-wide">\n'

first_p = True
for line in lines:
    line = line.strip()
    if not line:
        continue
    
    if line.startswith('# '):
        continue # Skip main title
    
    if line.startswith('## '):
        title = line[3:].strip()
        html_content += f'    <h2 class="section-title narrative-section-title">{title}</h2>\n'
    else:
        # Paragraph
        html_content += f'    <p class="narrative-text">{line}</p>\n'

html_content += '</div>'

with open(html_path, 'r', encoding='utf-8') as f:
    original_html = f.read()

# Replace the placeholder content
new_html = re.sub(
    r'<div class="narrative-content">.*?</div>',
    html_content,
    original_html,
    flags=re.DOTALL
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Done generating HTML.")
