# PDF Outline Extractor

This project extracts structured outlines (like H1, H2, H3 headings) from PDF files based on font size and outputs them as JSON. It uses `pdfminer.six` to convert PDFs into HTML and then parses the HTML with `BeautifulSoup`.

---

## 🧠 Approach

1. **Convert PDF to HTML** using `pdfminer.six` with `extract_text_to_fp` and `output_type='html'`.
2. **Parse the HTML** using `BeautifulSoup` to identify potential headings.
3. **Detect headings** based on font size:
   - `>= 24px` → `H1`
   - `>= 16px` → `H2`
   - `>= 12px` → `H3`
4. **(Optional)**: Also looks for traditional `<h1>`, `<h2>`, `<h3>` tags if present (though rarely produced by PDFMiner).
5. **Outputs a JSON file** per PDF, with this structure:

```json
{
  "title": "Extracted Title",
  "outline": [
    {
      "level": "H1",
      "text": "Section Title",
      "page": 1
    },
    ...
  ]
}
