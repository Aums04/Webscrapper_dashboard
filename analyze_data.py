import pandas as pd
import json
import os
from collections import Counter
import re
from datetime import datetime
import argparse

class NewsAnalyzer:
    def __init__(self, csv_path="assets/csv/ainews.csv", json_path="assets/json/ainews.json"):
        self.csv_path = csv_path
        self.json_path = json_path
        self.df = None
        
    def load_data(self):
        """Load data from CSV file"""
        if os.path.exists(self.csv_path):
            self.df = pd.read_csv(self.csv_path)
            print(f"Loaded {len(self.df)} articles from {self.csv_path}")
            return True
        else:
            print(f"CSV file not found: {self.csv_path}")
            return False
    
    def basic_stats(self):
        """Display basic statistics about the data"""
        if self.df is None:
            print("No data loaded. Please run load_data() first.")
            return
        
        print("\n=== BASIC STATISTICS ===")
        print(f"Total articles: {len(self.df)}")
        print(f"Articles with titles: {self.df['title'].notna().sum()}")
        print(f"Articles with descriptions: {self.df['short_desc'].notna().sum()}")
        print(f"Articles with full content: {self.df['long_desc'].notna().sum()}")
        print(f"Articles with images: {self.df['image_url'].notna().sum()}")
        
        if 'word_count' in self.df.columns:
            print(f"Average word count: {self.df['word_count'].mean():.1f}")
            print(f"Max word count: {self.df['word_count'].max()}")
            print(f"Min word count: {self.df['word_count'].min()}")
    
    def analyze_keywords(self, top_n=20):
        """Analyze most common keywords in titles and descriptions"""
        if self.df is None:
            return
        
        # Combine titles and descriptions
        text_data = []
        for _, row in self.df.iterrows():
            if pd.notna(row['title']):
                text_data.append(row['title'])
            if pd.notna(row['short_desc']):
                text_data.append(row['short_desc'])
        
        # Extract words (simple approach)
        all_words = []
        for text in text_data:
            # Simple word extraction (remove common stop words)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            # Filter out common stop words
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
            words = [word for word in words if word not in stop_words and len(word) > 3]
            all_words.extend(words)
        
        # Count words
        word_counts = Counter(all_words)
        most_common = word_counts.most_common(top_n)
        
        print(f"\n=== TOP {top_n} KEYWORDS ===")
        for word, count in most_common:
            print(f"{word}: {count}")
        
        return most_common
    
    def timeline_analysis(self):
        """Analyze articles over time"""
        if self.df is None or 'timestamp' not in self.df.columns:
            return
        
        # Convert timestamp to datetime
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['date'] = self.df['timestamp'].dt.date
        
        # Count articles per day
        daily_counts = self.df['date'].value_counts().sort_index()
        
        print(f"\n=== TIMELINE ANALYSIS ===")
        print(f"Date range: {daily_counts.index.min()} to {daily_counts.index.max()}")
        print(f"Average articles per day: {daily_counts.mean():.1f}")
        print(f"Most active day: {daily_counts.idxmax()} ({daily_counts.max()} articles)")
        
        return daily_counts
    
    def export_report(self, output_file="analysis_report.txt"):
        """Export analysis report to file"""
        if self.df is None:
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("AI NEWS SCRAPER - ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Basic stats
            f.write("BASIC STATISTICS:\n")
            f.write(f"Total articles: {len(self.df)}\n")
            f.write(f"Articles with titles: {self.df['title'].notna().sum()}\n")
            f.write(f"Articles with descriptions: {self.df['short_desc'].notna().sum()}\n")
            f.write(f"Articles with full content: {self.df['long_desc'].notna().sum()}\n")
            
            if 'word_count' in self.df.columns:
                f.write(f"Average word count: {self.df['word_count'].mean():.1f}\n")
            
            f.write("\nTOP 10 KEYWORDS:\n")
            keywords = self.analyze_keywords(10)
            for word, count in keywords:
                f.write(f"- {word}: {count}\n")
            
            f.write("\nSAMPLE TITLES:\n")
            for i, title in enumerate(self.df['title'].dropna().head(5), 1):
                f.write(f"{i}. {title}\n")
        
        print(f"Analysis report exported to: {output_file}")
    
    def display_sample_data(self, n=5):
        """Display sample articles"""
        if self.df is None:
            return
        
        print(f"\n=== SAMPLE ARTICLES (First {n}) ===")
        for i, row in self.df.head(n).iterrows():
            # Safely handle short_desc that might be NaN/float
            short_desc = row.get('short_desc', 'No description')
            if pd.isna(short_desc) or not isinstance(short_desc, str):
                short_desc = 'No description'
            else:
                short_desc = short_desc[:100] + "..." if len(short_desc) > 100 else short_desc
            
            print(f"\n{i+1}. {row.get('title', 'No title')}")
            print(f"   Description: {short_desc}")
            print(f"   Timestamp: {row.get('timestamp', 'No timestamp')}")
            print(f"   Link: {row.get('anchor_link', 'No link')}")

def get_latest_multisite_csv():
    csv_dir = os.path.join('assets', 'csv')
    files = [f for f in os.listdir(csv_dir) if f.startswith('ai_ml_multisite_') and f.endswith('.csv')]
    if not files:
        return None
    files.sort(reverse=True)
    return os.path.join(csv_dir, files[0])

def main():
    parser = argparse.ArgumentParser(description='Analyze AI/ML news data')
    parser.add_argument('--multi', action='store_true', help='Analyze multi-site data')
    args = parser.parse_args()

    if args.multi:
        csv_path = get_latest_multisite_csv()
        if not csv_path:
            print('No multi-site CSV file found.')
            return
        analyzer = NewsAnalyzer(csv_path=csv_path)
    else:
        analyzer = NewsAnalyzer()

    if analyzer.load_data():
        analyzer.basic_stats()
        analyzer.analyze_keywords()
        analyzer.timeline_analysis()
        analyzer.display_sample_data()
        analyzer.export_report()
    else:
        print('Please run the scraper first to generate data.')

if __name__ == "__main__":
    main()
