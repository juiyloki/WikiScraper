import time
from src.scraper import WikiScraper
from src.data_analysis import DataAnalyzer
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
        self.analyzer = DataAnalyzer()

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
        elif self.args.table: # [cite: 20]
            print(f"[*] Fetching table #{self.args.number} for: {self.args.table}...")
            
            # 1. Get raw HTML of the table from Scraper
            table_html = scraper.get_table(self.args.table, self.args.number)
            
            if table_html:
                # 2. Pass HTML to Analyzer to create CSV and stats
                # [cite: 21, 30]
                self.analyzer.process_table(
                    table_html, 
                    self.args.table, 
                    self.args.first_row_is_header
                )
            else:
                print("[!] Could not retrieve table data.")

        # --- BRANCH 3: WORD COUNT ---
        elif self.args.count_words:
            print(f"[*] Counting words for: {self.args.count_words}...")
            
            # 1. Get full text
            text = scraper.get_text(self.args.count_words)
            
            if text:
                # 2. Update the JSON database
                self.analyzer.update_word_counts(text)
            else:
                print("[!] Could not retrieve text.")

        # --- BRANCH 4: AUTO COUNT (RECURSIVE) ---
        elif self.args.auto_count_words:
            print(f"[*] Starting recursive scrape from: {self.args.auto_count_words}")
            print(f"[*] Depth: {self.args.depth}, Wait: {self.args.wait}s")

            # Queue structure: (current_phrase, current_depth)
            queue = [(self.args.auto_count_words, 0)]
            visited = set()

            while queue:
                current_phrase, current_depth = queue.pop(0)

                # Skip if already processed to prevent loops
                if current_phrase in visited:
                    continue
                
                visited.add(current_phrase)

                print(f"\n[{len(visited)}] Processing: {current_phrase} (Depth: {current_depth})")

                # 1. Scrape and Count Words for current page [cite: 68, 70]
                text = scraper.get_text(current_phrase)
                if text:
                    self.analyzer.update_word_counts(text)
                
                # 2. If we haven't hit max depth, find more links [cite: 71]
                if current_depth < self.args.depth:
                    new_links = scraper.get_internal_links(current_phrase)
                    
                    for link in new_links:
                        if link not in visited:
                            queue.append((link, current_depth + 1))
                
                # 3. Wait before the next request 
                # We check 'if queue' to avoid waiting after the very last item is done
                if queue:
                    time.sleep(self.args.wait)

        # --- BRANCH 5: ANALYSIS ---
        elif self.args.analyze_relative_word_frequency:
             print("[*] Analyzing word frequencies...")
             
             self.analyzer.generate_frequency_chart(
                 mode=self.args.mode,
                 count=self.args.count,
                 chart_path=self.args.chart
             )