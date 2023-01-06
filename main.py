from urllib.parse import unquote, urlparse
import PyPDF2
import re
import requests
from bs4 import BeautifulSoup
from os.path import basename

url = "https://www.capitol.hawaii.gov/sessions/session2022/testimony/"
word = "doctor"
# Make a request to the webpage
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the links to PDF files
pdf_links = soup.find_all('a', href=re.compile(r".+[PDF|pdf]$"))

# Print the PDF links
for link in pdf_links:
    print(link['href'])

