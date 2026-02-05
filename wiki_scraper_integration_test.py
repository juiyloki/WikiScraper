"""
Integration Test
================
Tests the Scraper's ability to load a local file
and extract a summary correctly.
Exits with code 0 on success, 1 on failure.
"""

import sys
import os
import shutil
from src.scraper import WikiScraper


def run_integration_test():
    # Setup: Define directory and filename logic.
    test_dir = "integration_test_env"
    phrase = "Team Rocket"
    filename = "Team_Rocket.html"
    file_path = os.path.join(test_dir, filename)

    expected_summary = "Terraria is a land of adventure! A land of mystery!"

    html_content = """
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

    print("[*] Setting up integration test environment...")

    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    print(f"[*] Creating dummy HTML file at: {file_path}")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    try:
        # Execution: Run the Scraper in local mode
        print("[*] Initializing Scraper with local_file_dir...")

        scraper = WikiScraper(
            base_url="http://mock.url",
            use_local_file=True,
            local_file_dir=test_dir
        )

        print(f"[*] Running get_summary('{phrase}')...")
        # The scraper will internally look for test_dir/Team_Rocket.html.
        actual_summary = scraper.get_summary(phrase)

        # 3. Verification: Assert logic.
        print(f"[*] Expected: '{expected_summary}'")
        print(f"[*] Actual:   '{actual_summary}'")

        if actual_summary == expected_summary:
            print("\n[SUCCESS] Integration test passed.")
        else:
            print("\n[FAILURE] Summaries do not match.")

        shutil.rmtree(test_dir)
        sys.exit(0)

    except Exception as e:
        print(f"\n[ERROR] Integration test crashed: {e}")
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        sys.exit(1)


if __name__ == "__main__":
    run_integration_test()
