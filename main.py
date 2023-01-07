import argparse
import io
import openpyxl
import requests
from bs4 import BeautifulSoup
import PyPDF2
import urllib


class Word:
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


class Line:
    def __init__(self, text, start, end, number):
        self.text = text
        self.start = start
        self.end = end
        self.number = number


class PDFPage:
    def __init__(self, page):
        self.page = page
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)


class PDFScraper:
    def __init__(self, url: str):
        self.url = url
        self.base_url: str = urllib.parse.urlparse(
            url).scheme + '://' + urllib.parse.urlparse(url).netloc

    def scrape_pdf_links(self, pages=1):
        try:
            for page in range(1, pages + 1):
                # Make a request to the webpage
                response = requests.get(self.url, params={'page': page})

                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all the links to PDF files
                pdf_links = soup.find_all(
                    'a', href=lambda x: x and x.lower().endswith('.pdf'))

                # Extract the PDF links
                pdf_links = [link['href'] for link in pdf_links]

                # Combine the base URL with the relative URLs
                pdf_links = [urllib.parse.urljoin(self.base_url, link)
                             if not urllib.parse.urlparse(link).scheme else link
                             for link in pdf_links]
            return pdf_links
        except Exception as e:
            print(f'Error: {e}')
            return []


class PDFSearcher:
    def __init__(self):
        self.cache = {}

    def search(self, pdf_links: list[str], words: list[str], limit=None):
        results = []
        for i, link in enumerate(pdf_links):
            if limit is not None and i >= limit:
                break
            try:
                # Check if the PDF file is in the cache
                if link in self.cache:
                    pdf = self.cache[link]
                else:
                    # Make a request to download the PDF file
                    response = requests.get(link)

                    # Open the response content as a binary stream
                    stream = io.BytesIO(response.content)

                    # Create a PDF object
                    pdf = PyPDF2.PdfFileReader(stream)

                    # Add the PDF to the cache
                    self.cache[link] = pdf

                # Iterate over all the pages
                for page_number in range(pdf.getNumPages()):
                    # Extract the text from the page
                    text = pdf.getPage(page_number).extractText()

                    # Create a PDFPage object
                    pdf_page = PDFPage(page_number)

                    # Split the text into lines
                    lines = text.splitlines()

                    # Iterate over the lines
                    line_number = 1
                    for line in lines:
                        # Iterate over the words
                        for word in words:
                            # Search for the word in the line
                            start = 0
                            while True:
                                start = line.find(word, start)
                                if start == -1:
                                    break

                                # Calculate the end position
                                end = start + len(word)

                                # Create a Word object
                                word_obj = Word(word, start, end)

                                # Create a Line object
                                line_obj = Line(line, start, end, line_number)

                                # Add the Line object to the PDFPage object
                                pdf_page.add_line(line_obj)

                                # Add the search result to the list
                                result = {
                                    'file': link,
                                    'page': pdf_page,
                                    'line': line_obj,
                                    'word': word_obj,
                                }
                                results.append(result)

                                # Continue searching from the end position
                                start = end
                        line_number += 1
            except Exception as e:
                print(f'Error: {e}')

        return results

    def save_to_excel(self, results, filename):
        # Create a new workbook
        workbook = openpyxl.Workbook()

        # Add a sheet to the workbook
        sheet = workbook.active
        sheet.title = 'Results'

        # Add the column headers
        sheet.append(['File',
                      'Page',
                      'Line',
                      'Line Start',
                      'Line End',
                      'Word',
                      ])

        # Add the search results to the sheet
        for result in results:
            sheet.append([
                result['file'],
                result['page'].page,
                result['line'].number,
                result['line'].start,
                result['line'].end,
                result['word'].text,
            ])

        # Save the workbook
        workbook.save(filename)


if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='The URL of the website to scrape')
    parser.add_argument('words', nargs='+',
                        help='Words to search for in the PDF files')
    parser.add_argument('-p', '--pages', type=int, default=1,
                        help='Number of pages to scrape')
    parser.add_argument('-l', '--limit', type=int,
                        help='Limit the number of PDF files to process')
    parser.add_argument('-o', '--output',
                        help='The name of the Excel file to save the results to')

    args = parser.parse_args()

    # Scrape the website for PDF links
    scraper = PDFScraper(args.url)
    pdf_links = scraper.scrape_pdf_links(args.pages)

    # Search the PDF files for the specified word
    searcher = PDFSearcher()
    results = searcher.search(pdf_links, args.words, args.limit)

    for result in results:
        print(f'File: {result["file"]}')
        print(f'Page: {result["page"].page}')
        print(f'Line: {result["line"].number}')
        print(f'Line Start: {result["line"].start}')
        print(f'Line End: {result["line"].end}')
        print(f'Word: {result["word"].text}')

    # Save the results to an Excel file
    searcher.save_to_excel(results, args.output)


# py main.py https://www.capitol.hawaii.gov/sessions/session2022/testimony/ the a -p 1 -l 2 -o results.xlsx
