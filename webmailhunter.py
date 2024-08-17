from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re

# Function to extract emails using regex
def extract_emails(text):
    return set(re.findall(r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+", text, re.I))

# Normalize relative and partial URLs to full URLs
def normalize_url(base_url, link):
    if link.startswith('/'):
        return urllib.parse.urljoin(base_url, link)
    elif not link.startswith(('http', 'https')):
        return urllib.parse.urljoin(base_url, link)
    return link

# Get user input for the target URL and max pages to scan
user_url = input('[+] Enter Target URL To Scan: ')
max_pages = int(input('[+] Enter Maximum Number of Pages to Scan: '))

# Initialize data structures
urls = deque([user_url])
scraped_urls = set()
emails = set()

count = 0

try:
    while len(urls):
        count += 1
        if count > max_pages:
            print(f"[!] Reached max pages limit of {max_pages}. Stopping...")
            break

        # Get the next URL to process
        url = urls.popleft()
        scraped_urls.add(url)

        # Extract base URL and path for relative links
        parts = urllib.parse.urlsplit(url)
        base_url = '{0.scheme}://{0.netloc}'.format(parts)

        print(f'[{count}] Processing {url}')

        # Attempt to make a request to the URL
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx responses
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"[!] Failed to process {url}: {e}")
            continue

        # Extract and collect emails
        new_emails = extract_emails(response.text)
        emails.update(new_emails)

        # Parse HTML and collect new links to visit
        soup = BeautifulSoup(response.text, features="lxml")
        for anchor in soup.find_all("a"):
            link = anchor.get('href', '')
            normalized_link = normalize_url(base_url, link)
            if normalized_link not in urls and normalized_link not in scraped_urls:
                urls.append(normalized_link)

except KeyboardInterrupt:
    print('[-] Operation interrupted by user.')

# Display the results
print('\n[+] Email addresses found:')
if emails:
    for mail in emails:
        print(mail)
else:
    print("No emails found.")

print(f'\n[+] Processed {count} pages.')
