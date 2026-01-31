from src.scraper import WikiScraper

"""
Scraper Manager
============================
Acts as the central controller for the application, orchestrating the interaction
between the CLI input, data fetching, and the processing.
"""

class ScraperManager:
    """
    Responsibility:
    ---------------
    Interprets the arguments provided by the user and dispatches the task
    to the appropriate worker modules. Separates logic regarding *what* from *how*.
    """

    BASE_URL = "https://terraria.wiki.gg/wiki/"

    def __init__(self, args):
        """
        :param args: Namespace object from argparse containing valid user inputs.
        """
        self.args = args

    def scrape(self):
        """
        Main execution switch.
        Checks which command-line flag was active and executes the corresponding
        workflow.
        """
        # 1. Initialize the WikiScraper object
        # We currently hardcode the URL, but the class is designed to accept
        # a local file path later for the integration tests.
        scraper = WikiScraper(self.BASE_URL)

        # 2. Dispatch Logic

        # --- BRANCH 1: SUMMARY ---
        if self.args.summary:
            print(f"[*] Fetching summary for: {self.args.summary}...")
            
            # Call the scraper 
            result = scraper.get_summary(self.args.summary)
            
            if result:
                # Output the text content
                print("\n--- SUMMARY ---")
                print(result)
                print("---------------")
            else:
                print("[!] Failed to retrieve summary or article not found.")

        # --- BRANCH 2: TABLE ---
        elif self.args.table:
            print("[*] Table extraction is not implemented yet.")
            # To be implemented: scraper.get_table(...) -> analyzer.save_csv(...)

        # --- BRANCH 3: WORD COUNT ---
        elif self.args.count_words:
             print("[*] Word counting is not implemented yet.")
             # To be implemented: scraper.get_text(...) -> analyzer.update_counts(...)

        # --- BRANCH 4: AUTO COUNT (RECURSIVE) ---
        elif self.args.auto_count_words:
            print("[*] Recursive scraping is not implemented yet.")

        # --- BRANCH 5: ANALYSIS ---
        elif self.args.analyze_relative_word_frequency:
             print("[*] Analysis is not implemented yet.")