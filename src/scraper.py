import os
import time
import requests
from bs4 import BeautifulSoup

class WikiScraper:
    """
    Handles the retrieval and parsing of Wiki data.
    Supports both live web scraping and local file reading for testing.
    """

    def __init__(self, base_url, use_local_file=False, local_file_path=None):
        """
        Initialize the scraper.

        :param base_url: The root URL ("https://terraria.wiki.gg/wiki/").
        :param use_local_file: If True, reads from disk instead of the web.
        :param local_file_path: Path to the HTML file (required if use_local_file is True).
        """
        self.base_url = base_url
        self.use_local_file = use_local_file
        self.local_file_path = local_file_path

    def _get_soup(self, phrase):
        """
        Internal helper. Fetches HTML content and returns a BeautifulSoup object.
        Handles the logic switch between HTTP requests and local files.
        """
        html_content = ""

        if self.use_local_file:
            # Local Mode (For Testing/Safety)
            if not self.local_file_path or not os.path.exists(self.local_file_path):
                raise FileNotFoundError(f"Local file not found: {self.local_file_path}")
            
            with open(self.local_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
        else:
            # Web Mode
            # Convert spaces to underscores (e.g. "Moon Lord" -> "Moon_Lord")
            formatted_phrase = phrase.replace(" ", "_")
            url = f"{self.base_url}{formatted_phrase}"
            
            try:
                response = requests.get(url)
                
                # Handle cases where article is not available
                if response.status_code == 404:
                    print(f"[!] Article not found: {phrase} (URL: {url})")
                    return None
                
                response.raise_for_status() # Raise error for 500s or connection issues
                html_content = response.text

            except requests.RequestException as e:
                print(f"[!] Network error fetching {url}: {e}")
                return None

        # Parse HTML
        return BeautifulSoup(html_content, 'html.parser')

    def get_summary(self, phrase):
        """
        Finds the first paragraph of the article and returns clear text.
        Skips menus/fixed elements, returns text without HTML tags.
        """
        soup = self._get_soup(phrase)
        if not soup:
            return None

        # Logic for Terraria Wiki (wiki.gg)
        # Main content is inside <div class="mw-parser-output">
        content_div = soup.find('div', class_='mw-parser-output')
        
        if not content_div:
            # Fallback for some other wiki structures if needed
            content_div = soup.find('div', id='mw-content-text')

        if not content_div:
            print("[!] Could not locate article content div.")
            return None

        # Find the first paragraph
        # recursive=False ensures we don't grab a paragraph inside a table/box
        paragraphs = content_div.find_all('p', recursive=False)

        for p in paragraphs:
            # get_text() strips all tags (<b>, <a>, etc.)
            text = p.get_text().strip()
            
            # Skip empty paragraphs or those that are just newlines
            if len(text) > 1:
                return text
        
        print("[!] No valid summary paragraph found.")
        return None
    
    def get_table(self, phrase, table_number):
        """
        Finds the n-th table in the article HTML.
        Returns the raw HTML string of that table to be processed by pandas.
        
        :param phrase: Search phrase
        :param table_number: 1-based index of the table to find (e.g. 1, 2, 3)
        """
        soup = self._get_soup(phrase)
        if not soup:
            return None

        # Find all <table> elements
        # Note: We look for standard HTML tables.
        # Some wikis use 'wikitable' class, but finding 'table' tag is most robust.
        tables = soup.find_all('table')

        if not tables:
            print(f"[!] No tables found on the page for '{phrase}'.")
            return None

        # Handle 1-based indexing (User says 1, Python needs 0)
        index = table_number - 1

        if index < 0 or index >= len(tables):
            print(f"[!] Table number {table_number} not found. (Found {len(tables)} tables).")
            return None

        # Return the string representation of the specific table
        return str(tables[index])
    
    def get_text(self, phrase):
        """
        Retrieves the full text of the article, excluding site navigation/menus.
       
        """
        soup = self._get_soup(phrase)
        if not soup:
            return None

        # Locate the main content area
        # On wiki.gg and MediaWiki, this is usually 'mw-parser-output'
        content_div = soup.find('div', class_='mw-parser-output')
        
        if not content_div:
             # Fallback
            content_div = soup.find('div', id='mw-content-text')

        if not content_div:
            print("[!] Could not locate article content.")
            return None

        # Extract text using Beautiful Soup's get_text
        # separator=' ' ensures words don't merge when tags are removed (e.g. "end.Start")
        return content_div.get_text(separator=' ', strip=True)
    
    def get_internal_links(self, phrase):
        """
        Finds valid internal links in the article to allow for recursive scraping.
        Returns a list of phrase strings (e.g., ['Eye_of_Cthulhu', 'King_Slime']).
        """
        soup = self._get_soup(phrase)
        if not soup:
            return []

        links = []
        content_div = soup.find('div', class_='mw-parser-output')
        
        if not content_div:
            content_div = soup.find('div', id='mw-content-text')

        if not content_div:
            return []

        # Find all anchor tags with an href attribute
        for a_tag in content_div.find_all('a', href=True):
            href = a_tag['href']

            # [cite: 78] Check for the /wiki/ prefix to ensure we stay on the site
            # We also ignore special pages like 'File:', 'Special:', 'Talk:' to keep it relevant
            if href.startswith('/wiki/') and ':' not in href:
                # Extract the phrase part: "/wiki/Moon_Lord" -> "Moon_Lord"
                clean_phrase = href.replace('/wiki/', '')
                links.append(clean_phrase)
        
        return links