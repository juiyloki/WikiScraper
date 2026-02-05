# WikiScraper & Language Analyzer

A modular Python tool for scraping Terraria Wiki data and analyzing language statistics.
Final grade project for the Python Course at MIMUW, winter semester 2025/2026.

**Author:** Agata Kopeć  
*ak469385@students.mimuw.edu.pl*

## Project Structure

- wiki_scraper.py: Main entry point for the CLI tool.
- src/: Source code modules (scraper, manager, data_analysis, argument).
- language_analysis.ipynb: Jupyter Notebook for statistical analysis.
- unit_tests.py: Unit tests for isolated logic.
- wiki_scraper_integration_test.py: End-to-end integration test.

## Installation

1. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  (Linux/Mac)
   .\venv\Scripts\activate   (Windows)

2. Install dependencies:
   pip install -r requirements.txt

## Usage (CLI)

Run these commands from the project root:

1. Get a summary:
   python wiki_scraper.py --summary "Moon Lord"

2. Extract a table to CSV:
   python wiki_scraper.py --table "Eye of Cthulhu" --number 1 --first-row-is-header

3. Count words (updates word-counts.json):
   python wiki_scraper.py --count-words "Terraria"

4. Recursive Auto-Count (BFS crawler):
   python wiki_scraper.py --auto-count-words "Terraria" --depth 2 --wait 1.0

## Testing

- Run Unit Tests:
  python unit_tests.py

- Run Integration Test:
  python wiki_scraper_integration_test.py

Note: If you encounter "ModuleNotFoundError: No module named src", set your PYTHONPATH:
  export PYTHONPATH=$PYTHONPATH:.  (Linux/Mac)
  $env:PYTHONPATH="."              (Windows PowerShell)

## Data Analysis (Jupyter)

1. Run: jupyter notebook
2. Open 'Language_Analysis.ipynb'.
3. Run all cells. The notebook will automatically generate the required test datasets if they are missing.

## License

Scraped content is available under CC BY-NC-SA 3.0.