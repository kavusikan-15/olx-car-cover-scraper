"""
OLX Car Cover Scraper
Author: [Your Name]
Date: [Current Date]

This script searches for car covers on OLX India and saves the results to a CSV file.
"""

import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import time

def get_page_content(url):
    """Fetch the HTML content of a given URL with proper headers and error handling."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def parse_listing(listing):
    """Extract relevant information from a single listing card."""
    result = {
        'title': None,
        'price': None,
        'location': None,
        'time_posted': None,
        'link': None
    }
    
    try:
        # Extract title
        title_element = listing.find('span', {'data-aut-id': 'itemTitle'})
        if title_element:
            result['title'] = title_element.text.strip()
        
        # Extract price
        price_element = listing.find('span', {'data-aut-id': 'itemPrice'})
        if price_element:
            result['price'] = price_element.text.strip().replace('₹', '₹ ')
        
        # Extract location and time (usually combined in one element)
        location_element = listing.find('span', {'data-aut-id': 'item-location'})
        if location_element:
            location_text = location_element.text.strip()
            # Simple attempt to separate location and time
            parts = location_text.split('\n')
            if len(parts) >= 2:
                result['location'] = parts[0].strip()
                result['time_posted'] = parts[-1].strip()
            else:
                result['location'] = location_text
        
        # Extract link
        link_element = listing.find('a', href=True)
        if link_element:
            result['link'] = urljoin("https://www.olx.in/", link_element['href'])
            
    except Exception as e:
        print(f"Error parsing listing: {e}")
    
    return result

def save_to_csv(data, filename):
    """Save the scraped data to a CSV file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'price', 'location', 'time_posted', 'link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
        print(f"Successfully saved {len(data)} listings to {filename}")
    except IOError as e:
        print(f"Error writing to file: {e}")

def scrape_olx_car_covers():
    """Main function to scrape car covers from OLX."""
    print("Starting OLX car cover search...")
    start_time = time.time()
    
    # OLX search URL for car covers
    search_url = "https://www.olx.in/items/q-car-cover"
    
    # Get the page content
    html_content = get_page_content(search_url)
    if not html_content:
        print("Failed to retrieve page content. Exiting.")
        return
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    listings = soup.find_all('div', {'data-aut-id': 'itemBox'})
    
    if not listings:
        print("No listings found. The page structure may have changed.")
        return
    
    # Process all listings
    scraped_data = []
    for listing in listings:
        listing_data = parse_listing(listing)
        if listing_data['title']:  # Only include valid listings
            scraped_data.append(listing_data)
    
    # Save results
    if scraped_data:
        output_filename = 'olx_car_covers.csv'
        save_to_csv(scraped_data, output_filename)
    else:
        print("No valid listings found to save.")
    
    # Print summary
    elapsed_time = time.time() - start_time
    print(f"Scraping completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    scrape_olx_car_covers()