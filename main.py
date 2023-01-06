import io
import requests
from bs4 import BeautifulSoup
import PyPDF2


class PDFScraper:
    def __init__(self, url):
        self.url = url

    def scrape_pdf_links(self):
        # Make a request to the webpage
        response = requests.get(self.url)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the links to PDF files
        pdf_links = soup.find_all('a', href=lambda x: x and x.endswith('.pdf'))

        # Extract the PDF links
        pdf_links = [link['href'] for link in pdf_links]

        return pdf_links


class PDFSearcher:
    def search(self, pdf_links, word):
        for link in pdf_links:
            # Make a request to download the PDF file
            response = requests.get(link)

            # Open the response content as a binary stream
            stream = io.BytesIO(response.content)

            # Open the PDF file
            with open(stream, 'rb') as f:
                # Create a PDF object
                pdf = PyPDF2.PdfFileReader(f)

                # Iterate over all the pages
                for page in range(pdf.getNumPages()):
                    # Extract the text from the page
                    text = pdf.getPage(page).extractText()

                    # Search for the word in the text
                    if word in text:
                        print(f'Found "{word}" in page {page} of {link}')


# Test the classes
url = 'https://www.capitol.hawaii.gov/sessions/session2022/testimony/'
scraper = PDFScraper(url)
pdf_links = scraper.scrape_pdf_links()

searcher = PDFSearcher()
searcher.search(pdf_links, 'the')
