import os
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import re
import json
from bs4 import BeautifulSoup
from pathlib import Path

input_dir = Path("/app/input")
output_dir = Path("/app/output")

# Create output directory if it doesn't exist
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Looking for PDFs in: {input_dir.resolve()}")

# Get all PDF files
pdf_files = list(input_dir.glob("*.pdf"))

for pdf_file in pdf_files:
    print(f"Processing {pdf_file.name}...")
    output_string = StringIO()
    with open(pdf_file, 'rb') as fin:
        extract_text_to_fp(fin, output_string, laparams=LAParams(),
                           output_type='html', codec=None)

    html = output_string.getvalue()
    output_string.close()

    # Parse HTML for title and headings
    soup = BeautifulSoup(html, 'html.parser')
    title_tag = soup.find('title')
    title = title_tag.text if title_tag else ''

    outline = []

    # Find headings by tag (h1, h2, h3) — unlikely from PDFMiner, but keeping just in case
    for level in ['h1', 'h2', 'h3']:
        for tag in soup.find_all(level):
            page = None
            parent_text = tag.parent.get_text()
            match = re.search(r'Page\s*(\d+)', parent_text)
            if match:
                page = int(match.group(1))
            else:
                prev = tag.find_previous(string=re.compile(r'Page\s*\d+'))
                if prev:
                    page_match = re.search(r'Page\s*(\d+)', prev)
                    if page_match:
                        page = int(page_match.group(1))
            outline.append({
                'level': level.upper(),
                'text': tag.get_text(strip=True),
                'page': page if page else 1
            })

    # Find headings by font size (most reliable)
    for tag in soup.find_all(True):
        style = tag.get('style', '')
        font_size = None

        match = re.search(r'font-size\s*:\s*(\d+)px', style)
        if match:
            font_size = int(match.group(1))
        elif tag.name == 'font' and tag.get('size'):
            try:
                font_size = int(tag.get('size'))
            except:
                pass

        if font_size is not None:
            if font_size >= 24:
                level = 'H1'
            elif font_size >= 16:
                level = 'H2'
            elif font_size >= 12:
                level = 'H3'
            else:
                continue  # Skip non-heading text

            page = None
            parent_text = tag.parent.get_text()
            match_page = re.search(r'Page\s*(\d+)', parent_text)
            if match_page:
                page = int(match_page.group(1))
            else:
                prev = tag.find_previous(string=re.compile(r'Page\s*\d+'))
                if prev:
                    page_match = re.search(r'Page\s*(\d+)', prev)
                    if page_match:
                        page = int(page_match.group(1))

            outline.append({
                'level': level,
                'text': tag.get_text(strip=True),
                'page': page if page else 1
            })

    # Output JSON
    result = {
        'title': title,
        'outline': outline
    }

    output_file = output_dir / f"{pdf_file.stem}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Processed {pdf_file.name} -> {output_file.name}")
