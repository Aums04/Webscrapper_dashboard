# AI News Web Scraper - Enhanced Version

An advanced web scraper for collecting AI news articles from ainews.com with comprehensive data analysis and visualization capabilities.

## 🚀 Features

### Enhanced Scraping Engine
- ✅ **Robust Error Handling** - Retry logic and comprehensive error logging
- ✅ **Rate Limiting** - Configurable delays to respect server resources
- ✅ **Full Article Content** - Extracts both summaries and complete article text
- ✅ **Duplicate Detection** - Automatically removes duplicate articles
- ✅ **Multiple Output Formats** - Saves data in both CSV and JSON formats
- ✅ **Comprehensive Logging** - Detailed logs for monitoring and debugging

### Data Analysis & Insights
- ✅ **Keyword Analysis** - Identifies trending topics and common keywords
- ✅ **Timeline Analysis** - Shows article publication patterns over time
- ✅ **Content Statistics** - Word count analysis and content quality metrics
- ✅ **Export Reports** - Generates comprehensive analysis reports

### Web Dashboard
- ✅ **Real-time Dashboard** - Live view of scraped articles
- ✅ **Statistics Overview** - Key metrics and data insights
- ✅ **Responsive Design** - Works perfectly on desktop and mobile
- ✅ **API Endpoints** - JSON API for external integrations
- ✅ **Modern UI** - Beautiful Bootstrap-based interface

## 📁 Project Structure

```
single_site_scraper/
├── single_site_scraper.py   # Main scraper with advanced features
├── analyze_data.py       # Data analysis and reporting tools
├── dashboard.py          # Web dashboard for viewing data
├── config.json          # Configuration settings
├── requirements.txt     # Python dependencies
├── run_scraper.bat      # Windows batch script for easy execution
├── README.md            # This documentation
├── scraper.log          # Logging output (created after first run)
└── assets/
    ├── csv/
    │   └── ainews.csv    # Scraped data in CSV format
    └── json/
        └── ainews.json   # Scraped data in JSON format with metadata
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Virtual environment (recommended)

### Quick Setup
1. **Navigate to the single_site_scraper directory**:
   ```cmd
   cd single_site_scraper
   ```

2. **Run the automated setup** (Windows):
   ```cmd
   run_scraper.bat
   ```
   This will automatically:
   - Set up virtual environment
   - Install dependencies
   - Run the scraper
   - Generate analysis reports

### Manual Setup
1. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

2. **Run the enhanced scraper**:
   ```cmd
   python single_site_scraper.py
   ```

3. **Analyze the data**:
   ```cmd
   python analyze_data.py
   ```

4. **Start the web dashboard**:
   ```cmd
   python dashboard.py
   ```
   Then open http://localhost:5000 in your browser

## ⚙️ Configuration

Edit `config.json` to customize scraper behavior:

```json
{
    "base_url": "https://www.ainews.com/",
    "csv_path": "assets/csv/ainews.csv",
    "json_path": "assets/json/ainews.json",
    "delay_between_requests": 1,
    "max_retries": 3,
    "timeout": 10,
    "fetch_full_content": true
}
```

### Configuration Options:
- **`delay_between_requests`**: Seconds to wait between requests (respect rate limits)
- **`max_retries`**: Number of retry attempts for failed requests
- **`timeout`**: Request timeout in seconds
- **`fetch_full_content`**: Whether to fetch complete article content (slower but more data)

## 🎯 Usage Examples

### Basic Scraping
```cmd
python single_site_scraper.py
```

### Fast Scraping (Skip Full Content)
```cmd
python single_site_scraper.py --no-content
```

### Custom Configuration
```cmd
python single_site_scraper.py --config my_config.json
```

### Data Analysis
```cmd
python analyze_data.py
```

### Web Dashboard
```cmd
python dashboard.py
```

## 📊 Output Data

### CSV Format (`assets/csv/ainews.csv`)
| Column | Description |
|--------|-------------|
| title | Article title |
| short_desc | Brief description/summary |
| image_url | Featured image URL |
| timestamp | Publication timestamp |
| source | Source website URL |
| published | Publication status |
| anchor_link | Direct link to full article |
| long_desc | Complete article content |
| word_count | Word count of full content |
| scraped_at | When the article was scraped |
| domain | Source domain |

### JSON Format (`assets/json/ainews.json`)
Structured format with metadata and all article data:
```json
{
    "metadata": {
        "total_articles": 150,
        "new_articles": 25,
        "duplicates_removed": 5,
        "last_updated": "2025-06-25T10:30:00",
        "source": "https://www.ainews.com/"
    },
    "articles": [...]
}
```

## 🌐 Dashboard Features

### Statistics Overview
- Total articles scraped
- Articles with full content
- Date range of articles
- Real-time updates

### Article Browser
- Latest articles display
- Direct links to source articles
- Word count indicators
- Publication timestamps

### API Endpoints
- `GET /api/articles` - All articles in JSON format
- `GET /api/stats` - Statistics summary
- `GET /` - Main dashboard interface

## 📝 Analysis Reports

The analyzer generates comprehensive reports including:
- **Basic Statistics**: Article counts, content metrics
- **Keyword Analysis**: Most common terms and trending topics
- **Timeline Patterns**: Publication frequency over time
- **Sample Data**: Preview of scraped articles

Reports are saved as `analysis_report.txt` for easy sharing.

## 🔍 Monitoring & Debugging

### Logging
- All activities logged to `scraper.log`
- Includes request status, errors, and processing times
- Configurable log levels

### Error Handling
- Automatic retry for failed requests
- Graceful handling of network issues
- Detailed error reporting

## 🛡️ Best Practices

### Respectful Scraping
- Built-in rate limiting (1-second delays by default)
- Proper User-Agent headers
- Retry logic to handle temporary failures
- Respects server resources

### Data Quality
- Automatic duplicate removal
- Data validation and cleaning
- Comprehensive metadata tracking
- Multiple output formats for flexibility

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Connection Errors**
   - Check internet connection
   - Increase timeout in config.json
   - Website might be temporarily unavailable

3. **No Data Found**
   - Website structure might have changed
   - Check scraper.log for detailed errors
   - Update CSS selectors if needed

4. **Dashboard Issues**
   - Ensure Flask is installed
   - Check if port 5000 is available
   - Try running on different port

### Getting Help
- Check `scraper.log` for detailed error information
- Verify configuration settings in `config.json`
- Ensure all dependencies are installed

## 🔮 Future Enhancements

- [ ] Support for multiple news sources
- [ ] Sentiment analysis of articles
- [ ] Email notifications for new content
- [ ] Database storage options
- [ ] Docker containerization
- [ ] Automated scheduling
- [ ] Content classification with ML

## 📄 License

This project is for educational purposes. Please respect website terms of service and use responsibly.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
