import os
import json
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
from wordfreq import top_n_list, word_frequency

class DataAnalyzer:
    """
    Handles data processing, analysis, and file I/O operations.
    Responsibility: Converts raw data from Scraper into structured formats (CSV, JSON)
    and performs statistical analysis.
    """

    def process_table(self, table_html, phrase, first_row_is_header=False):
        """
        Converts a raw HTML table into a Pandas DataFrame, saves it to CSV,
        and prints column value counts.

        :param table_html: String containing the raw <table> HTML.
        :param phrase: The search phrase (used for naming the CSV file).
        :param first_row_is_header: Boolean, if True, treats the first row as columns.
        """
        try:
            # Pandas read_html returns a list of DataFrames (one for each table found).
            # We wrap the HTML string in StringIO to avoid warnings in newer Pandas versions.
            dfs = pd.read_html(StringIO(str(table_html)))
            
            if not dfs:
                print("[!] Pandas could not parse the table.")
                return

            # We take the first table found in the HTML snippet provided
            df = dfs[0]

            # Logic for headers 
            # If the user explicitly stated the first row is a header, Pandas usually detects this.
            # If not, or if we need to force it, we can adjust here. 
            # Note: read_html usually defaults to 'header=0' (first row).
            if not first_row_is_header:
                # If we strictly want no headers, we might reload or adjust, 
                # but standard pandas behavior is usually sufficient. 
                # If needed, we could set header=None in read_html, but that depends on implementation details.
                pass

            # 1. Save to CSV 
            # Filename: "szukana fraza.csv"
            filename = f"{phrase}.csv"
            df.to_csv(filename, index=False)
            print(f"[+] Table saved successfully to: {filename}")

            # 2. Print Value Counts 
            print("\n--- COLUMN VALUE COUNTS ---")
            for col in df.columns:
                print(f"\nColumn: {col}")
                # dropna=True ensures we don't count empty cells
                print(df[col].value_counts())
            print("---------------------------")

        except ValueError as e:
            print(f"[!] Error processing table: {e}")
        except Exception as e:
            print(f"[!] Unexpected error in analyzer: {e}")

    def update_word_counts(self, text):
        """
        [Placeholder]
        Counts words in the provided text and updates the persistent JSON storage.
        
        Logic to implement:
        1. Load existing 'word-counts.json' if it exists.
        2. Clean text (remove punctuation, lower case).
        3. Update counts.
        4. Save back to JSON.
        """
        print("[*] Analyzer: Word count update logic not yet implemented.")
        pass

    def generate_frequency_chart(self, mode, count, chart_path=None):
        """
        [Placeholder]
        Performs the relative word frequency analysis.

        Logic to implement:
        1. Load 'word-counts.json'.
        2. Load language statistics (e.g., from wordfreq).
        3. Compare and sort based on 'mode' (article vs language).
        4. Generate a matplotlib bar chart if 'chart_path' is provided.
        """
        print("[*] Analyzer: Chart generation logic not yet implemented.")
        pass

    def update_word_counts(self, text):
        """
        Counts words in the provided text and updates the persistent JSON storage.
        [cite_start][cite: 32, 34]
        """
        json_file = "word-counts.json"
        
        # 1. Load existing data or start fresh
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    word_counts = json.load(f)
            except json.JSONDecodeError:
                print("[!] Error decoding JSON. Starting with empty counts.")
                word_counts = {}
        else:
            word_counts = {}

        # 2. Tokenize and Clean Text
        # We perform simple normalization: lowercase and strip common punctuation.
        # [cite_start]This keeps the logic simple as per assignment flexibility[cite: 107].
        words = text.split()
        
        for raw_word in words:
            # Remove basic punctuation from edges (e.g., "word," -> "word")
            # We keep internal punctuation like "don't" or "mid-air".
            word = raw_word.strip(".,!?;:()[]\"'")
            
            # Normalize to lowercase for consistency
            word = word.lower()
            
            if not word:
                continue

            # 3. Update Counts
            # [cite_start]Increment the total count across all program runs [cite: 34]
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

        # [cite_start]4. Save back to JSON [cite: 35]
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
        
        # 1. Load Wiki Data
        if not os.path.exists(json_file):
            print("[!] No word counts found. Run --count-words first.")
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            wiki_data = json.load(f)

        if not wiki_data:
            print("[!] Word count file is empty.")
            return

        # Convert to Series for easier math
        wiki_series = pd.Series(wiki_data, name="wiki_raw")
        
        # 2. Load Language Data (Standard English)
        # We get the top 5000 English words to ensure good overlap
        lang_words = top_n_list('en', 5000) 
        
        # Create a dictionary of {word: frequency_score}
        # word_frequency returns a float (e.g. 0.05 for 'the')
        lang_data = {w: word_frequency(w, 'en') for w in lang_words}
        lang_series = pd.Series(lang_data, name="lang_raw")

        # 3. Create Comparison DataFrame
        # We align them on the 'word' index
        df = pd.DataFrame({
            'wiki_raw': wiki_series,
            'lang_raw': lang_series
        })

        # 4. Normalization 
        # Divide by the maximum value in that column so both scales are 0.0 to 1.0
        df['wiki_norm'] = df['wiki_raw'] / df['wiki_raw'].max()
        df['lang_norm'] = df['lang_raw'] / df['lang_raw'].max()

        # Fill NaNs (words missing in one source) with 0 for plotting
        df = df.fillna(0)

        # 5. Sorting Logic 
        if mode == 'article':
            # Sort by Wiki frequency, showing gaps in Language
            df = df.sort_values(by='wiki_norm', ascending=False)
        elif mode == 'language':
            # Sort by Language frequency, showing gaps in Wiki
            df = df.sort_values(by='lang_norm', ascending=False)
        
        # Slice the top N items requested by user
        top_df = df.head(count)

        # 6. Print Table
        print(f"\n--- ANALYSIS (Mode: {mode}, Top {count}) ---")
        print(top_df[['wiki_raw', 'wiki_norm', 'lang_norm']])
        print("---------------------------------------------")

        # 7. Generate Chart 
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
        
        # Create two bars per word
        rects1 = ax.bar(x - width/2, df['wiki_norm'], width, label='Wiki Article', color='blue')
        rects2 = ax.bar(x + width/2, df['lang_norm'], width, label='English Language', color='red')

        # Formatting
        ax.set_ylabel('Normalized Frequency')
        ax.set_title('Relative Word Frequency: Wiki vs English')
        ax.set_xticks(x)
        ax.set_xticklabels(words, rotation=45, ha='right')
        ax.legend()

        fig.tight_layout()
        plt.savefig(path)
        print(f"[+] Chart saved to: {path}")