import unittest
import os
import shutil
from src.scraper import WikiScraper


class TestWikiScraper(unittest.TestCase):

    def setUp(self):
        """
        Runs before each test.
        Creates a temporary DIRECTORY and a dummy HTML file inside it.
        """
        self.test_dir = "test_data_unit"
        self.base_url = "https://fake.url/"
        self.phrase = "Test Page"

        # Create the directory if it doesn't exist.
        if not os.path.exists(self.test_dir):
            os.mkdir(self.test_dir)

        # Create a dummy HTML structure mimicking MediaWiki/Wiki.gg.
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

        # Save as "Test_Page.html" (matching the phrase we will query).
        filename = f"{self.phrase.replace(' ', '_')}.html"
        self.file_path = os.path.join(self.test_dir, filename)

        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Initialize scraper in LOCAL mode pointing to the DIRECTORY.
        self.scraper = WikiScraper(
            base_url=self.base_url,
            use_local_file=True,
            local_file_dir=self.test_dir
        )

    def tearDown(self):
        """
        Runs after each test.
        Cleans up the temporary directory and all files inside.
        """
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # --- SUMMARY TEST---
    def test_get_summary_cleans_tags(self):
        """
        Test if get_summary finds the first <p> and strips HTML tags (<b>).
        """
        # Note: Using self.phrase so it finds the file created in setUp.
        result = self.scraper.get_summary(self.phrase)
        expected = "This is the summary paragraph."
        self.assertEqual(result, expected)

    # --- TABLE INDEXING TEST ---
    def test_get_table_indexing(self):
        """
        Test if get_table correctly handles 1-based indexing.
        Requesting table #2 should return the second table in HTML.
        """
        # Ask for table #2.
        result_html = self.scraper.get_table(self.phrase, table_number=2)

        # We expect the HTML of the second table.
        self.assertIn("Table 2 Data", result_html)
        self.assertNotIn("Table 1 Data", result_html)

    # --- LINK FILTERING TEST ---
    def test_get_internal_links_filtering(self):
        """
        Test if get_internal_links ignores external URLs
        and special namespaces.
        """
        links = self.scraper.get_internal_links(self.phrase)

        # Should contain: 'Valid_Link'.
        # Should NOT contain: 'google.com', 'File:...', 'Talk:...'.
        self.assertIn("Valid_Link", links)
        self.assertEqual(len(links), 1,
                         "Should have filtered out 3 invalid links")

    # --- MISSING CONTENT TEST ---
    def test_missing_content_returns_none(self):
        """
        Test behavior when the specific content div is missing.
        """
        # Overwrite the file with broken HTML (no mw-parser-output).
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("<html><body><div>"
                    "No parser output here</div></body></html>")
        result = self.scraper.get_summary(self.phrase)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
