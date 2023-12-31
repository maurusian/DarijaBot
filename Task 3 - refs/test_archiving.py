import requests
import re
from datetime import datetime

def extract_last_archive_url(html_text):
    # The regular expression pattern to find archive URLs in the HTML content
    pattern = re.compile(r"https://web\.archive\.org/web/\d+/http[s]?://[^\s\"'<]+")
    
    # Find all archive URLs
    archive_urls = re.findall(pattern, html_text)
    
    # Get the last archive URL
    last_archive_url = None
    for archive_url in archive_urls:
        if url in archive_url:
            last_archive_url = archive_url
            break
        
    
    return last_archive_url

def get_date_from_archive_url(archive_url):
    pattern = re.compile(r"/web/(\d{14})/")
    match = re.search(pattern, archive_url)
    if match:
        timestamp_str = match.group(1)
        timestamp_str = timestamp_str[:8]  # Take only the YYYYMMDD part
        return datetime.strptime(timestamp_str, "%Y%m%d").strftime("%d %B %Y")
    else:
        return None

def fetch_from_archive(url):
    archive_url = f"https://web.archive.org/web/{url}"
    response = requests.get(archive_url)
    
    if response.status_code == 200:
        archiving_date = response.headers.get('X-Archive-Orig-date', 'Unknown date')
        archive_url = extract_last_archive_url(response.text)
        archiving_date = get_date_from_archive_url(archive_url)
        return archive_url, archiving_date
    else:
        return None

url = "https://www.hespress.com/%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9%D9%8C-%D9%88%D8%A3%D9%85%D8%A7%D8%B2%D9%8A%D8%BA%D9%8A%D8%A9-%D9%88%D8%AF%D8%A7%D8%B1%D8%AC%D8%A9-%D9%85%D8%B3%D8%A7%D8%A8%D9%82%D8%A9-%D8%AA%D8%B7%D9%88%D8%B1-%D9%85-1159415.html"

print(fetch_from_archive(url))
