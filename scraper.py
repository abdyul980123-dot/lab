import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin
from datetime import datetime


class LogicMonitorSupportScraper:
    """
    Fixed scraper for LogicMonitor Support Center
    Extracts documentation links from the sidebar navigation
    """
    
    def __init__(self, delay=1.5):
        self.base_url = "https://www.logicmonitor.com/support"
        self.delay = delay
        self.session = requests.Session()
        
        # Headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0',
        })
        
        self.data = {
            'main_categories': [],
            'documentation_links': [],
            'scraped_at': datetime.now().isoformat()
        }
    
    def fetch_page(self, url):
        """Fetch page with error handling and rate limiting"""
        try:
            time.sleep(self.delay + random.uniform(0, 0.5))
            print(f"Fetching: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
            
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def scrape(self):
        """Main scraping method"""
        html = self.fetch_page(self.base_url)
        if not html:
            print("Failed to fetch page")
            return self.data
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract from docs navigation
        self._extract_from_docs_nav(soup)
        
        print(f"\nScraping completed!")
        print(f"Found {len(self.data['main_categories'])} main categories")
        print(f"Found {len(self.data['documentation_links'])} documentation links")
        
        return self.data
    
    def _extract_from_docs_nav(self, soup):
        """Extract all documentation links from the docs-nav sidebar"""
        docs_nav = soup.find('ul', class_='docs-nav')
        
        if not docs_nav:
            print("docs-nav not found")
            return
        
        # Get all links in the docs nav
        all_links = docs_nav.find_all('a', href=True)
        print(f"Found {len(all_links)} total links in docs-nav")
        
        # Extract top-level categories (items with has_children class)
        top_level_items = docs_nav.find_all('li', class_='has_children', recursive=False)
        
        for item in top_level_items:
            cat_link = item.find('a')
            if cat_link:
                title = cat_link.get_text(strip=True)
                self.data['main_categories'].append({
                    'category': title,
                    'type': 'top_level'
                })
        
        # Extract all actual documentation links (those with /support/ hrefs)
        extracted_urls = set()
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Filter for documentation links
            if href and href != '#' and '/support/' in href and len(text) > 2:
                full_url = urljoin("https://www.logicmonitor.com", href)
                
                # Avoid duplicates
                if full_url not in extracted_urls:
                    extracted_urls.add(full_url)
                    self.data['documentation_links'].append({
                        'title': text[:150],
                        'url': full_url,
                        'source': 'docs_nav'
                    })
    
    def save_results(self, format='json'):
        """Save scraped data to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"logicmonitor_support_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print(f"Saved to {filename}")
    
    def print_summary(self):
        """Print a readable summary of scraped data"""
        print("\n" + "="*60)
        print("LOGICMONITOR SUPPORT CENTER - SCRAPED DATA")
        print("="*60)
        
        print("\nMAIN CATEGORIES:")
        for cat in self.data['main_categories'][:20]:
            print(f"  - {cat['category']}")
        if len(self.data['main_categories']) > 20:
            print(f"  ... and {len(self.data['main_categories']) - 20} more")
        
        print(f"\nDOCUMENTATION LINKS (Total: {len(self.data['documentation_links'])}):")
        for link in self.data['documentation_links'][:15]:
            print(f"  - {link['title']}")
            print(f"    {link['url'][:80]}")
        if len(self.data['documentation_links']) > 15:
            print(f"  ... and {len(self.data['documentation_links']) - 15} more")


# Example usage
if __name__ == "__main__":
    scraper = LogicMonitorSupportScraper(delay=2)
    data = scraper.scrape()
    scraper.print_summary()
    scraper.save_results(format='json')
