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

