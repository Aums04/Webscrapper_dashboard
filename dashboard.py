from flask import Flask, render_template_string, jsonify, request
import pandas as pd
import json
import os
from datetime import datetime

app = Flask(__name__)

class DataViewer:
    def __init__(self, csv_path="assets/csv/ainews.csv", json_path="assets/json/ainews.json"):
        self.csv_path = csv_path
        self.json_path = json_path
    
    @staticmethod
    def get_latest_multisite_csv():
        csv_dir = os.path.join('assets', 'csv')
        files = [f for f in os.listdir(csv_dir) if f.startswith('ai_ml_multisite_') and f.endswith('.csv')]
        if not files:
            return None
        files.sort(reverse=True)
        return os.path.join(csv_dir, files[0])

    def get_data(self):
        """Load and return data"""
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path)
            # Convert timestamp to readable format
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['formatted_date'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            return df
        return pd.DataFrame()
    
    def get_stats(self):
        """Get basic statistics"""
        df = self.get_data()
        if df.empty:
            return {}
        
        stats = {
            'total_articles': len(df),
            'articles_with_content': len(df[df['long_desc'].notna()]) if 'long_desc' in df.columns else 0,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_range': {
                'earliest': df['timestamp'].min().strftime('%Y-%m-%d') if 'timestamp' in df.columns else 'N/A',
                'latest': df['timestamp'].max().strftime('%Y-%m-%d') if 'timestamp' in df.columns else 'N/A'
            }
        }
        return stats

viewer = DataViewer()

@app.route('/')
def index():
    """Main dashboard page"""
    use_multi = request.args.get('multi', '0') == '1'
    if use_multi:
        multi_csv = DataViewer.get_latest_multisite_csv()
        viewer = DataViewer(csv_path=multi_csv) if multi_csv else DataViewer()
    else:
        viewer = DataViewer()
    df = viewer.get_data()
    stats = viewer.get_stats()
    
    # Get recent articles (top 10)
    recent_articles = []
    if not df.empty:
        if 'timestamp' in df.columns:
            df_sorted = df.sort_values('timestamp', ascending=False)
        else:
            df_sorted = df
        
        for _, row in df_sorted.head(10).iterrows():
            # Safely handle short_desc that might be NaN/float
            short_desc = row.get('short_desc', 'No description')
            if pd.isna(short_desc) or not isinstance(short_desc, str):
                short_desc = 'No description'
            else:
                # Truncate for display
                short_desc = short_desc[:200] + "..." if len(short_desc) > 200 else short_desc
            
            # Safely handle title that might be NaN/float
            title = row.get('title', 'No title')
            if pd.isna(title) or not isinstance(title, str):
                title = 'No title'
            
            article = {
                'title': title,
                'short_desc': short_desc,
                'timestamp': row.get('formatted_date', 'No date'),
                'anchor_link': row.get('anchor_link', '#'),
                'word_count': row.get('word_count', 0)
            }
            recent_articles.append(article)
    
    return render_template_string(HTML_TEMPLATE, 
                                articles=recent_articles, 
                                stats=stats,
                                use_multi=use_multi)

@app.route('/api/articles')
def api_articles():
    """API endpoint for articles data"""
    df = viewer.get_data()
    if df.empty:
        return jsonify([])
    
    # Convert to JSON format
    articles = []
    for _, row in df.iterrows():
        # Safely handle potential NaN/float values
        title = row.get('title', '')
        if pd.isna(title) or not isinstance(title, str):
            title = ''
        
        short_desc = row.get('short_desc', '')
        if pd.isna(short_desc) or not isinstance(short_desc, str):
            short_desc = ''
        
        anchor_link = row.get('anchor_link', '')
        if pd.isna(anchor_link) or not isinstance(anchor_link, str):
            anchor_link = ''
        
        image_url = row.get('image_url', '')
        if pd.isna(image_url) or not isinstance(image_url, str):
            image_url = ''
        
        article = {
            'title': title,
            'short_desc': short_desc,
            'timestamp': row.get('timestamp', '').isoformat() if pd.notna(row.get('timestamp', '')) else '',
            'anchor_link': anchor_link,
            'word_count': row.get('word_count', 0),
            'image_url': image_url
        }
        articles.append(article)
    
    return jsonify(articles)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify(viewer.get_stats())

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI News Scraper Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .article-card {
            transition: transform 0.2s;
            border-left: 4px solid #007bff;
        }
        .article-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .word-count-badge {
            background-color: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
    </style>
</head>
<body class="bg-light">
    <div class="container-fluid py-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">
                    🤖 AI News Scraper Dashboard
                </h1>
            </div>
        </div>
        
        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <h3>{{ stats.total_articles }}</h3>
                        <p class="mb-0">Total Articles</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <h3>{{ stats.articles_with_content }}</h3>
                        <p class="mb-0">With Full Content</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body text-center">
                        <h6>{{ stats.date_range.earliest }}</h6>
                        <p class="mb-0">Earliest Article</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body text-center">
                        <h6>{{ stats.date_range.latest }}</h6>
                        <p class="mb-0">Latest Article</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recent Articles -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Recent Articles</h5>
                        <small class="text-muted">Last updated: {{ stats.last_updated }}</small>
                    </div>
                    <div class="card-body">
                        {% if articles %}
                            {% for article in articles %}
                            <div class="card article-card mb-3">
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-8">
                                            <h6 class="card-title">
                                                {% if article.anchor_link %}
                                                    <a href="{{ article.anchor_link }}" target="_blank" class="text-decoration-none">
                                                        {{ article.title }}
                                                    </a>
                                                {% else %}
                                                    {{ article.title }}
                                                {% endif %}
                                            </h6>
                                            <p class="card-text text-muted">{{ article.short_desc }}</p>
                                        </div>
                                        <div class="col-md-4 text-end">
                                            <small class="text-muted d-block">{{ article.timestamp }}</small>
                                            {% if article.word_count > 0 %}
                                                <span class="word-count-badge">{{ article.word_count }} words</span>
                                            {% endif %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <div class="alert alert-warning" role="alert">
                                <h6>No articles found!</h6>
                                <p class="mb-0">Run the scraper first to see articles here.</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Refresh Button and Data Toggle -->
        <div class="row mt-4">
            <div class="col-12 text-center">
                <button class="btn btn-primary" onclick="location.reload()">
                    🔄 Refresh Data
                </button>
                <a href="/api/articles" class="btn btn-outline-secondary ms-2">
                    📥 Download JSON
                </a>
                <a href="/?multi={% if not use_multi %}1{% else %}0{% endif %}" class="btn btn-warning ms-2">
                    {% if not use_multi %}Switch to Multi-site Data{% else %}Switch to Single-site Data{% endif %}
                </a>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

if __name__ == '__main__':
    print("Starting AI News Dashboard...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
