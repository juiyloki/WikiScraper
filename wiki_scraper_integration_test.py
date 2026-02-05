"""
Integration Test
================
Tests the Scraper's ability to load a local file and extract a summary correctly.
Exits with code 0 on success, 1 on failure.
"""

import sys
import os
from src.scraper import WikiScraper

def run_integration_test():
    # 1. Setup: Define the expected output and create a dummy file
    filename = "integration_test_doc.html"
    expected_summary = "Terraria is a land of adventure! A land of mystery!"
    
    html_content = f"""
    <html>
        <body>
            <div class="mw-parser-output">
                <p>   
                    <b>Terraria</b> is a land of adventure! <a href="#">A land of mystery!</a>
                </p>
            </div>
        </body>
    </html>
    """

    print("[*] Creating dummy HTML file...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    try:
        # 2. Execution: Run the Scraper in local mode
        print("[*] Initializing Scraper in local mode...")
        scraper = WikiScraper(
            base_url="http://mock.url",
            use_local_file=True,
            local_file_path=filename
        )

        print("[*] Running get_summary()...")
        actual_summary = scraper.get_summary("Test_Phrase")

        # 3. Verification: Assert logic
        print(f"[*] Expected: '{expected_summary}'")
        print(f"[*] Actual:   '{actual_summary}'")

        if actual_summary == expected_summary:
            print("\n[SUCCESS] Integration test passed.")
            sys.exit(0)
        else:
            print("\n[FAILURE] Summaries do not match.")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Integration test crashed: {e}")
        sys.exit(1)
        
    finally:
        # 4. Cleanup: Remove the file
        if os.path.exists(filename):
            os.remove(filename)
            print("[*] Cleanup complete.")

if __name__ == "__main__":
    run_integration_test()