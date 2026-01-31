import argparse

class WikiArgumentParser:
    """
    Handles the parsing and validation of command-line arguments.
    """

    def __init__(self):
        # Allowing help descriptions to be formatted prettier
        self.parser = argparse.ArgumentParser(
            description="Terraria Wiki Scraper",
            formatter_class=argparse.RawTextHelpFormatter
        )
        self._setup_arguments()

    def _setup_arguments(self):
        """
        Defines all possible CLI arguments.
        Use a mutually exclusive group for the main commands to ensure
        the user runs only one primary operation at a time.
        add.argument() flags:
            metavar='PHRASE': makes the instructions cleaner: usage: --summary PHRASE instead of usage: --summary SUMMARY
            type=int: converts command-line args into specific types
            action: turns the argument into an on/off flag
            choices: limits user input to selected choices
        """
        # Primary Argument Group (User must select exactly one)
        
        action_group = self.parser.add_mutually_exclusive_group(required=True)

        action_group.add_argument(
            '--summary',
            metavar='PHRASE',
            type=str,
            help='Get the first paragraph of the article for the given phrase.'
        )

        action_group.add_argument(
            '--table',
            metavar='PHRASE',
            type=str,
            help='Get a specific table from the article. Requires --number.'
        )

        action_group.add_argument(
            '--count-words',
            metavar='PHRASE',
            type=str,
            help='Count word frequencies in the specified article.'
        )

        action_group.add_argument(
            '--analyze-relative-word-frequency',
            action='store_true',  # Flag, not a value input
            help='Compare scraped word counts against language statistics.\n'
                 'Requires --mode and --count.'
        )

        action_group.add_argument(
            '--auto-count-words',
            metavar='PHRASE',
            type=str,
            help='recursively count words following links.\n'
                 'Requires --depth and --wait.'
        )

        # Secondary Arguments (Dependencies)
        
        # Table arguments 
        self.parser.add_argument(
            '--number',
            type=int,
            help='The index of the table to extract (starting from 1).'
        )
        self.parser.add_argument(
            '--first-row-is-header',
            action='store_true',
            help='If set, the first row of the table is treated as headers.'
        )

        # Analysis arguments 
        self.parser.add_argument(
            '--mode',
            choices=['article', 'language'], # argparse handles validation automatically
            help='Sorting mode for analysis: "article" or "language".'
        )
        self.parser.add_argument(
            '--count',
            type=int,
            help='Number of rows to display in the analysis table.'
        )
        self.parser.add_argument(
            '--chart',
            metavar='PATH',
            type=str,
            help='Path to save the generated bar chart (e.g., ./chart.png).'
        )

        # Auto-count arguments 
        self.parser.add_argument(
            '--depth',
            type=int,
            help='Recursion depth for auto-count words.'
        )
        self.parser.add_argument(
            '--wait',
            type=float,
            help='Wait time (seconds) between requests to avoid bans.'
        )

    def parse_args(self):
        """
        Parses system arguments and validates dependencies.
        Returns the Namespace object if successful.
        """
        args = self.parser.parse_args()
        self._validate_dependencies(args)
        return args

    def _validate_dependencies(self, args):
        """
        Manually checks conditional requirements that argparse cannot enforce natively.
        Exits with error if a dependency is missing.
        """
        # 1. Validation for --table 
        if args.table and args.number is None:
            self.parser.error("The argument --table requires --number.")

        # 2. Validation for --analyze-relative-word-frequency 
        if args.analyze_relative_word_frequency:
            if not args.mode:
                self.parser.error("--analyze-relative-word-frequency requires --mode.")
            if not args.count:
                self.parser.error("--analyze-relative-word-frequency requires --count.")

        # 3. Validation for --auto-count-words 
        if args.auto_count_words:
            if args.depth is None:
                self.parser.error("--auto-count-words requires --depth.")
            if args.wait is None:
                self.parser.error("--auto-count-words requires --wait.")