import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import json
import time
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class AINewsScraper:
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "base_url": "https://www.ainews.com/",
            "csv_path": "assets/csv/ainews.csv",
            "json_path": "assets/json/ainews.json",
            "delay_between_requests": 1,
            "max_retries": 3,
            "timeout": 10,
            "fetch_full_content": True
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logging.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logging.warning(f"Error loading config file: {e}. Using default configuration.")
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            logging.info(f"Created default configuration file: {config_file}")
        
        return default_config
    
    def make_request(self, url, retries=0):
        """Make HTTP request with retry logic"""
        try:
            response = self.session.get(url, timeout=self.config['timeout'])
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if retries < self.config['max_retries']:
                logging.warning(f"Request failed for {url}. Retrying in 2 seconds... (Attempt {retries + 1})")
                time.sleep(2)
                return self.make_request(url, retries + 1)
            else:
                logging.error(f"Failed to fetch {url} after {self.config['max_retries']} retries: {e}")
                return None
    
    def extract_article_content(self, url):
        """Extract full article content from article URL"""
        if not self.config['fetch_full_content']:
            return None
            
        response = self.make_request(url)
        if not response:
            return None
            
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            content_div = soup.find("div", id="content-blocks")
            if content_div:
                # Remove script and style elements
                for script in content_div(["script", "style"]):
                    script.decompose()
                return content_div.get_text(separator=" ", strip=True)
        except Exception as e:
            logging.error(f"Error extracting content from {url}: {e}")
        
        return None
    
    def scrape_news(self):
        """Main scraping function"""
        logging.info(f"Starting scrape of {self.config['base_url']}")
        
        response = self.make_request(self.config['base_url'])
        if not response:
            logging.error("Failed to fetch main page")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        logging.info(f"Status Code: {response.status_code}")
        
        results = []
        grid_div = soup.find("div", class_="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3")
        
        if not grid_div:
            logging.warning("Could not find main content grid")
            return results
        
        articles = grid_div.find_all("div", class_="transparent h-full cursor-pointer overflow-hidden rounded-lg flex flex-col border")
        logging.info(f"Found {len(articles)} articles")
        
        for i, div in enumerate(articles, 1):
            logging.info(f"Processing article {i}/{len(articles)}")
            
            # Extract article data
            article_data = self.extract_article_data(div)
            if article_data:
                results.append(article_data)
                
            # Add delay between requests
            if i < len(articles):
                time.sleep(self.config['delay_between_requests'])
        
        logging.info(f"Successfully scraped {len(results)} articles")
        return results
    
    def extract_article_data(self, div):
        """Extract data from a single article div"""
        try:
            # Title
            title_tag = div.find("h2")
            title = title_tag.get_text(strip=True) if title_tag else None
            
            # Short description
            desc_tag = div.find("p")
            short_desc = desc_tag.get_text(strip=True) if desc_tag else None
            
            # Image URL
            img_tag = div.find("img", class_="absolute inset-0 h-full w-full object-cover")
            image_url = img_tag.get("src") if img_tag else None
            if image_url and not image_url.startswith("http"):
                image_url = urljoin(self.config['base_url'], image_url)
            
            # Timestamp
            time_tag = div.find("time")
            timestamp = time_tag.get("datetime") if time_tag else None
            
            # Anchor Link
            anchor_link = None
            spacey_div = div.find("div", class_="space-y-3")
            if spacey_div:
                anchor_tag = spacey_div.find("a", href=True)
                if anchor_tag:
                    anchor_link = anchor_tag["href"]
                    if anchor_link and not anchor_link.startswith("http"):
                        anchor_link = urljoin(self.config['base_url'], anchor_link)
            
            # Long description (full article content)
            long_desc = None
            if anchor_link:
                long_desc = self.extract_article_content(anchor_link)
            
            # Additional metadata
            word_count = len(long_desc.split()) if long_desc else 0
            scraped_at = datetime.now().isoformat()
            
            return {
                "title": title,
                "short_desc": short_desc,
                "image_url": image_url,
                "timestamp": timestamp,
                "source": self.config['base_url'],
                "published": False,
                "anchor_link": anchor_link,
                "long_desc": long_desc,
                "word_count": word_count,
                "scraped_at": scraped_at,
                "domain": urlparse(self.config['base_url']).netloc
            }
            
        except Exception as e:
            logging.error(f"Error extracting article data: {e}")
            return None
    
    def save_data(self, results):
        """Save scraped data to CSV and JSON formats"""
        if not results:
            logging.warning("No data to save")
            return
        
        # Create directories
        csv_dir = os.path.dirname(self.config['csv_path'])
        json_dir = os.path.dirname(self.config['json_path'])
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)
        
        # Load existing data
        existing_df = self.load_existing_data()
        
        # Convert results to DataFrame
        new_df = pd.DataFrame(results)
        
        # Combine and remove duplicates
        if not existing_df.empty:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df
        
        # Remove duplicates based on title and timestamp
        original_count = len(combined_df)
        combined_df.drop_duplicates(subset=["title", "timestamp"], inplace=True)
        final_count = len(combined_df)
        
        # Sort by timestamp (newest first)
        if 'timestamp' in combined_df.columns:
            combined_df.sort_values('timestamp', ascending=False, inplace=True)
        
        # Save to CSV
        combined_df.to_csv(self.config['csv_path'], index=False)
        logging.info(f"Saved {final_count} unique articles to {self.config['csv_path']}")
        
        # Save to JSON
        json_data = {
            "metadata": {
                "total_articles": final_count,
                "new_articles": len(results),
                "duplicates_removed": original_count - final_count,
                "last_updated": datetime.now().isoformat(),
                "source": self.config['base_url']
            },
            "articles": combined_df.to_dict('records')
        }
        
        with open(self.config['json_path'], 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved data to {self.config['json_path']}")
        
        return combined_df
    
    def load_existing_data(self):
        """Load existing CSV data"""
        if os.path.exists(self.config['csv_path']):
            try:
                df = pd.read_csv(self.config['csv_path'])
                # Ensure all required columns exist
                required_columns = ["title", "short_desc", "image_url", "timestamp", "source", "published", "anchor_link", "long_desc"]
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = None
                return df
            except Exception as e:
                logging.error(f"Error loading existing data: {e}")
        
        return pd.DataFrame()
    
    def generate_summary(self, df):
        """Generate a summary of scraped data"""
        if df.empty:
            return
        
        summary = {
            "total_articles": len(df),
            "articles_with_content": len(df[df['long_desc'].notna()]),
            "date_range": {
                "earliest": df['timestamp'].min() if 'timestamp' in df.columns else None,
                "latest": df['timestamp'].max() if 'timestamp' in df.columns else None
            },
            "avg_word_count": df['word_count'].mean() if 'word_count' in df.columns else 0
        }
        
        logging.info("=== SCRAPING SUMMARY ===")
        logging.info(f"Total articles: {summary['total_articles']}")
        logging.info(f"Articles with full content: {summary['articles_with_content']}")
        logging.info(f"Average word count: {summary['avg_word_count']:.1f}")
        logging.info("========================")
        
        return summary

def main():
    parser = argparse.ArgumentParser(description='Enhanced AI News Scraper')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--no-content', action='store_true', help='Skip fetching full article content')
    args = parser.parse_args()
    
    # Create scraper instance
    scraper = AINewsScraper(args.config)
    
    # Override config if needed
    if args.no_content:
        scraper.config['fetch_full_content'] = False
    
    try:
        # Scrape news
        results = scraper.scrape_news()
        
        # Save data
        df = scraper.save_data(results)
        
        # Generate summary
        if df is not None:
            scraper.generate_summary(df)
        
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()

# This script is for single-site scraping only. For multi-site scraping, use the multisite_version project.
