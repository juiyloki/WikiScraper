import os
import json
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
from wordfreq import top_n_list, word_frequency


class DataAnalyzer:
    """
    Handles data processing, analysis, and file I/O operations.
    Responsibility: Converts raw data from Scraper into structured formats
    (CSV, JSON) and performs statistical analysis.
    """

    def process_table(self, table_html, phrase, first_row_is_header=False):
        """
        Converts a raw HTML table into a Pandas DataFrame, saves it to CSV,
        and prints column value counts.

        :param table_html: String containing the raw <table> HTML.
        :param phrase: The search phrase (used for naming the CSV file).
        :param first_row_is_header: if True, treats the first row as columns.
        """
        try:
            # If flag --first-row-is-header was added,
            # take first row as a header (header = 0).
            # Otherwise ignore headers and treat everything
            # like data (header = None).
            header_arg = 0 if first_row_is_header else None

            # Pandas read_html returns a list of DataFrames,
            # here our table is the 1st (and only) elem.
            # Wrap the HTML string in StringIO,
            # to avoid warnings in newer Pandas versions.
            # Include identified header param.
            dfs = pd.read_html(StringIO(str(table_html)), header=header_arg)

            if not dfs:
                print("[!] Pandas could not parse the table.")
                return

            df = dfs[0]

            # Save to CSV.
            filename = f"{phrase}.csv"
            df.to_csv(filename, index=False)
            print(f"[+] Table saved successfully to: {filename}")

            # Print Value Counts.
            print("\n--- COLUMN VALUE COUNTS ---")
            for col in df.columns:
                print(f"\nColumn: {col}")
                # dropna=True ensures we don't count empty cells.
                print(df[col].value_counts())
            print("---------------------------")

        except ValueError as e:
            print(f"[!] Error processing table: {e}")
        except Exception as e:
            print(f"[!] Unexpected error in analyzer: {e}")

    def update_word_counts(self, text):
        """
        Counts words in the provided text
        and updates the persistent JSON storage.
        """
        json_file = "word-counts.json"

        # Load existing data or start fresh.
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    word_counts = json.load(f)
            except json.JSONDecodeError:
                print("[!] Error decoding JSON. Starting with empty counts.")
                word_counts = {}
        else:
            word_counts = {}

        # Tokenize and Clean Text.
        # Perform simple normalization: lowercase and strip common punctuation.
        words = text.split()

        for raw_word in words:
            # Remove basic punctuation from edges (e.g., "word," -> "word").
            # We keep internal punctuation like "don't" or "mid-air".
            word = raw_word.strip(".,!?;:()[]\"'")

            # Normalize to lowercase for consistency.
            word = word.lower()

            if not word:
                continue

            # Update Counts.
            # Increment the total count across all program runs.
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

        # Save data back to the JSON file.
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(word_counts, f, indent=4, ensure_ascii=False)
            print(f"[+] Word counts updated in '{json_file}'.")
        except IOError as e:
            print(f"[!] Error saving word counts: {e}")

    def generate_frequency_chart(self, mode, count, chart_path=None):
        """
        Analyzes relative word frequency and optionally generates a chart.
        """
        json_file = "word-counts.json"

        # Load Wiki Data.
        if not os.path.exists(json_file):
            print("[!] No word counts found. Run --count-words first.")
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            wiki_data = json.load(f)

        if not wiki_data:
            print("[!] Word count file is empty.")
            return

        # Convert to pandas Series for simplicity.
        wiki_series = pd.Series(wiki_data, name="wiki_raw")

        # Load Language Data (Standard English).
        # Fetch top 5000 English words to ensure good overlap.
        lang_words = top_n_list('en', 5000)

        # Create a dictionary of {word: frequency_score}.
        # word_frequency returns a float (e.g. 0.05 for 'the').
        lang_data = {w: word_frequency(w, 'en') for w in lang_words}
        lang_series = pd.Series(lang_data, name="lang_raw")

        # Create Comparison DataFrame.
        # Align them on the 'word' index.
        df = pd.DataFrame({
            'wiki_raw': wiki_series,
            'lang_raw': lang_series
        })

        # Normalization.
        # Divide by the maximum value in that column,
        # so both scales are 0.0 to 1.0.
        df['wiki_norm'] = df['wiki_raw'] / df['wiki_raw'].max()
        df['lang_norm'] = df['lang_raw'] / df['lang_raw'].max()

        # Fill NaNs (words missing in one source) with 0 for plotting.
        df = df.fillna(0)

        # Sorting Logic.
        if mode == 'article':
            # Sort by Wiki frequency, showing gaps in Language.
            df = df.sort_values(by='wiki_norm', ascending=False)
        elif mode == 'language':
            # Sort by Language frequency, showing gaps in Wiki.
            df = df.sort_values(by='lang_norm', ascending=False)

        # Slice the top N items requested by user.
        top_df = df.head(count)

        # Print Table.
        print(f"\n--- ANALYSIS (Mode: {mode}, Top {count}) ---")
        print(top_df[['wiki_raw', 'wiki_norm', 'lang_norm']])
        print("---------------------------------------------")

        # Generate Chart.
        if chart_path:
            self._plot_chart(top_df, chart_path)

    def _plot_chart(self, df, path):
        """
        Helper method to draw the matplotlib chart.

        """
        import numpy as np

        words = df.index.tolist()
        x = np.arange(len(words))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))

        # Create two bars per word.
        ax.bar(
            x - width/2,
            df['wiki_norm'],
            width,
            label='Wiki Article',
            color='blue')
        ax.bar(
            x + width/2,
            df['lang_norm'],
            width,
            label='English Language',
            color='red')

        # Formatting.
        ax.set_ylabel('Normalized Frequency')
        ax.set_title('Relative Word Frequency: Wiki vs English')
        ax.set_xticks(x)
        ax.set_xticklabels(words, rotation=45, ha='right')
        ax.legend()

        fig.tight_layout()
        plt.savefig(path)
        print(f"[+] Chart saved to: {path}")
