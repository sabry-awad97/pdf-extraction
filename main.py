import argparse
import io
import requests
from bs4 import BeautifulSoup
import PyPDF2
import urllib


class PDFScraper:
    def __init__(self, url):
        self.url = url

    def scrape_pdf_links(self):
        try:
            # Make a request to the webpage
            response = requests.get(self.url)

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all the links to PDF files
            pdf_links = soup.find_all(
                'a', href=lambda x: x and x.lower().endswith('.pdf'))

            # Extract the PDF links
            pdf_links = [link['href'] for link in pdf_links]

            return pdf_links
        except Exception as e:
            print(f'Error: {e}')
            return []


class PDFSearcher:
    def __init__(self, base_url):
        self.base_url = base_url

    def search(self, pdf_links, word):
        results = []
        for link in pdf_links:
            try:
                # Check if the link is a relative or an absolute URL
                if not urllib.parse.urlparse(link).scheme:
                    # Combine the base URL with the relative URL
                    link = urllib.parse.urljoin(self.base_url, link)

                # Make a request to download the PDF file
                response = requests.get(link)

                # Open the response content as a binary stream
                stream = io.BytesIO(response.content)

                # Create a PDF object
                pdf = PyPDF2.PdfFileReader(stream)

                # Iterate over all the pages
                for page in range(pdf.getNumPages()):
                    # Extract the text from the page
                    text = pdf.getPage(page).extractText()

                    # Search for the word in the text
                    start = 0
                    while True:
                        start = text.find(word, start)
                        if start == -1:
                            break

                        # Calculate the end position
                        end = start + len(word)

                        # Extract the line of text containing the search word
                        line = text[:end].splitlines()[-1]

                        # Calculate the line number
                        line_number = len(text[:end].splitlines())

                        # Calculate the start and end positions within the line
                        line_start = start - text[:start].rfind('\n')
                        line_end = end - text[:end].rfind('\n')

                        # Add the search result to the list
                        result = {
                            'file': link,
                            'page': page,
                            'line_number': line_number,
                            'line_start': line_start,
                            'line_end': line_end,
                            'line': line,
                        }
                        print(result)
                        results.append(result)

                        # Continue searching from the end position
                        start = end
            except Exception as e:
                print(f'Error: {e}')

        return results


# Test the classes
url = ''

if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='The URL of the website to scrape')
    parser.add_argument('word', help='The word to search for in the PDF files')
    args = parser.parse_args()

    # Scrape the website for PDF links
    scraper = PDFScraper(args.url)
    pdf_links = scraper.scrape_pdf_links()

    # Search the PDF files for the specified word
    searcher = PDFSearcher("https://www.capitol.hawaii.gov/")
    searcher.search(pdf_links, args.word)
