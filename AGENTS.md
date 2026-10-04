# Agent Workflow & Rules for Sovereign Nation of Waikiki Site

## HTML Page Builds and Edits

After building or editing any HTML page:
1. **Format document**: Format the HTML document with 4-space indentation.
2. **Remove empty lines in document**: Ensure there are no empty/blank lines in the document.

### Automation Utilities

- Format and clean a specific file:
  `node scripts/format_document.js <file.html>`
- Format and clean all pages:
  `node scripts/format_document.js --all`
- Build pages (automatically formats and strips empty lines):
  `python3 scripts/build_pages.py`
