# Page Editing and Build Guidelines

Whenever you build, edit, or create an HTML page in this project:

1. **Format document**:
   - Ensure the document is formatted with 4-space indentation using `js-beautify` or the helper script `node scripts/format_document.js <file>`.
2. **Remove empty lines in document**:
   - Strip all blank/empty lines from the document so no lines containing only whitespace (`^\s*$`) remain.

### Automation Scripts

- To format and strip empty lines from a single file:
  ```bash
  node scripts/format_document.js <path/to/file.html>
  ```
- To format and strip empty lines from all HTML files across the project:
  ```bash
  node scripts/format_document.js --all
  ```
- Running the build pipeline automatically applies formatting and empty-line removal:
  ```bash
  python3 scripts/build_pages.py
  ```
