# Debugging Status: Tauri Markdown Generation Issue

## Current State (2026-01-05)

### ✅ Completed Features
1. **Scraping Core**: 
   - Python script (`main.py`) successfully scrapes FM Korea posts using Playwright.
   - Saves individual JSON files to `data/raw`.
   - Cleans up `data/raw` before each new run.
2. **NotebookLM Conversion (CLI)**:
   - When run vertically via CLI (`python main.py member [ID] [PAGES]`), Markdown generation WORKS.
   - Files are created in `data/notebooklm`.
   - Posts are sorted by recency (document_srl descending).
3. **Tauri Integration**:
   - `page.tsx` now correctly manages event listeners (no duplicates on re-run).
   - UI displays progress logs and results card.
   - `open_explorer` command added to Rust backend to open files/folders.
   - `current_dir` explicitly set in `commands.rs` to project root (hardcoded for dev).

### ❌ Outstanding Issue
**Markdown File Generation Fails in Tauri Environment**
- **Symptom**: 
  - User reports "Markdown is not generated" when running via Tauri app.
  - CLI execution works perfectly, but triggering the same logic via Tauri seems to fail at the generation step or file saving step.
  - UI might show results, but files are missing from `data/notebooklm` (or user cannot find them).
- **Potential Causes**:
  1. **Path/Permission Issue**: Even with `current_dir` set, the python process spawned by Tauri might behave differently regarding file creation permissions or path resolution for `data/notebooklm`.
  2. **Python Environment**: Tauri might be picking up a different Python environment or missing dependencies if not strictly using the `.venv` (though `python_path` is hardcoded).
  3. **Silent Failure**: The `export_to_notebooklm` function might be failing silently in the Tauri context due to encoding or library issues that don't manifest in the CLI.
  4. **Process Termination**: The Python process might be terminated by Tauri/Rust before it flushes the file write implementation.

### Next Steps for Debugging
1. **Log File Paths**: Modify `export_to_notebooklm` to print the **absolute path** where it tries to write files, to confirm where they are going.
2. **Check Rust Logs**: Run `npm run tauri dev` and watch the terminal output closely for any stderr from the Python process during the conversion phase.
3. **Hardcode Absolute Paths**: Temporarily hardcode an absolute path like `C:\fmkorea_debug\` for output to rule out relative path issues.

## Technical Details
- **Frontend**: Next.js 15
- **Backend**: Rust (Tauri 2.0)
- **Scraper**: Python 3 (Playwright, BeautifulSoup4)
- **Data Flow**: Tauri(Rust) -> spawns Python -> emits 'scraping-log' -> Frontend(React) receives events.
