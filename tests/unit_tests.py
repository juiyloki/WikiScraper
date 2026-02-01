import unittest
import os
from src.scraper import WikiScraper

class TestWikiScraper(unittest.TestCase):
    
    def setUp(self):
        """
        Runs before EACH test.
        Creates a temporary HTML file to simulate a Wiki page without internet.
        """
        self.test_file_path = "test_dummy_page.html"
        self.base_url = "https://fake.url/"
        
        # Create a dummy HTML structure mimicking MediaWiki/Wiki.gg
        html_content = """
        <html>
            <body>
                <div class="mw-parser-output">
                    <p>This is the <b>summary</b> paragraph.</p>
                    <p>This is the second paragraph.</p>
                    
                    <table>
                        <tr><td>Table 1 Data</td></tr>
                    </table>
                    
                    <table>
                        <tr><td>Table 2 Data</td></tr>
                    </table>

                    <a href="/wiki/Valid_Link">Valid</a>
                    <a href="https://google.com">External</a>
                    <a href="/wiki/File:Image.png">File</a>
                    <a href="/wiki/Talk:Discussion">Talk</a>
                </div>
            </body>
        </html>
        """
        
        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Initialize scraper in LOCAL mode
        self.scraper = WikiScraper(
            base_url=self.base_url, 
            use_local_file=True, 
            local_file_path=self.test_file_path
        )

    def tearDown(self):
        """
        Runs after EACH test.
        Cleans up the temporary file.
        """
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    # --- TEST 1: SUMMARY EXTRACTION ---
    def test_get_summary_cleans_tags(self):
        """
        Test if get_summary finds the first <p> and strips HTML tags (<b>).
        """
        result = self.scraper.get_summary("IgnoredPhraseInLocalMode")
        expected = "This is the summary paragraph."
        self.assertEqual(result, expected)

    # --- TEST 2: TABLE INDEXING ---
    def test_get_table_indexing(self):
        """
        Test if get_table correctly handles 1-based indexing.
        Requesting table #2 should return the second table in HTML.
        """
        # We ask for table #2
        result_html = self.scraper.get_table("Ignored", table_number=2)
        
        # We expect the HTML of the second table
        self.assertIn("Table 2 Data", result_html)
        self.assertNotIn("Table 1 Data", result_html)

    # --- TEST 3: LINK FILTERING ---
    def test_get_internal_links_filtering(self):
        """
        Test if get_internal_links ignores external URLs and special namespaces (File:, Talk:).
        """
        links = self.scraper.get_internal_links("Ignored")
        
        # Should contain: 'Valid_Link'
        # Should NOT contain: 'google.com', 'File:Image.png', 'Talk:Discussion'
        self.assertIn("Valid_Link", links)
        self.assertEqual(len(links), 1, "Should have filtered out 3 invalid links")

    # --- TEST 4: MISSING CONTENT ---
    def test_missing_content_returns_none(self):
        """
        Test behavior when the specific content div is missing.
        """
        # Overwrite the file with empty HTML
        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write("<html><body><div>No parser output here</div></body></html>")
            
        result = self.scraper.get_summary("Ignored")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()