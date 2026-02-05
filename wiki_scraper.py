"""
WikiScraper
=======================
Terraria Wiki

Usage:
------
python wiki_scraper.py [ARGUMENTS]
Example: python wiki_scraper.py --summary "Moon Lord"
"""

import sys
from src.argument import WikiArgumentParser
from src.manager import ScraperManager


def main():
    """
    Initializes the argument parser and the scraper manager,
    delegates execution to the manager.

    """
    try:
        # Initialize the Argument Parser.
        parser = WikiArgumentParser()
        args = parser.parse_args()

        # Initialize the Scraper Manager.
        # The Manager receives the parsed arguments and decides
        # which tools to use based on the user's input.
        manager = ScraperManager(args)

        # Execute the Scraper Logic.
        # We call a single entry method on the manager, which internally
        # handles the branching logic (e.g., if args.summary -> do summary).
        manager.scrape()

        print("\n[Info] Data scraped from Terraria Wiki (wiki.gg).\n"
              "Content available under CC BY-NC-SA 3.0.")

    except KeyboardInterrupt:
        # Handles the user pressing Ctrl+C.
        print("\n[!] Operation cancelled by user. Exiting safely.")
        sys.exit(0)
    except Exception as e:
        # Catches any other unforeseen errors.
        print(f"\n[!] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
