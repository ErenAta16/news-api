# 📰 News Analysis System

Advanced RSS-based news analysis and visualization platform with hybrid data collection (RSS + API).

## 🚀 Quick Start

### Main Menu
```bash
quick_start.bat
```

### Direct Launch
```bash
# Run full analysis
start_analysis.bat

# Launch dashboard
start_dashboard.bat

# Automatic scheduler
start_scheduler.bat

# Quick start
quick_start.bat
```

## 📁 Project Structure

```
EntegreOtomasyon/
├── src/
│   ├── main.py                 # Main analysis system
│   ├── dashboard.py            # Streamlit dashboard
│   ├── rss_collector.py        # RSS data collector
│   ├── api_collector.py        # API data collector
│   ├── hybrid_collector.py     # Hybrid collector (RSS + API)
│   ├── database.py             # Database management
│   ├── text_processor.py       # Text processing
│   ├── advanced_analytics.py   # Advanced analytics
│   ├── cooccurrence_analyzer.py # Co-occurrence analysis
│   ├── topic_modeling.py       # Topic modeling
│   ├── similarity_detector.py  # Similarity detection
│   ├── network_analyzer.py     # Network analysis
│   ├── word_analysis.py        # Word analysis
│   └── scheduler.py            # Automatic scheduler
├── quick_start.bat             # Main menu
├── start_analysis.bat          # Analysis launcher
├── start_dashboard.bat         # Dashboard launcher
├── start_scheduler.bat         # Automatic scheduler
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables example
└── README.md                  # Documentation
```

## 🎯 Features

### 📡 Hybrid Data Collection
- **RSS Sources**: Hürriyet, Milliyet, Habertürk, Anadolu Ajansı
- **API Sources**: NewsAPI integration
- **200+ news** automatic collection
- **4 categories**: gündem, ekonomi, spor, dünya
- **Asynchronous data fetching**
- **⏰ Automatic scheduler**: Hourly collection
- **💾 Data storage**: Raw data + analysis results

### 🔤 Text Analysis
- **6000+ total words** processing
- **3000+ unique words** detection
- **Stopword cleaning**
- **Word frequency analysis**
- **Topic modeling with LDA**
- **Co-occurrence analysis**

### 📊 Visualization
- **Word frequency charts**
- **Category distribution**
- **Source comparison**
- **Co-occurrence networks**
- **Trend analysis**
- **Interactive Streamlit dashboard**

### 🛡️ Security Features
- **Environment variables** for API keys
- **Secure configuration** management
- **Gitignore** for sensitive files

## 🛠️ Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Create .env file
cp .env.example .env

# Add your API key to .env file
NEWS_API_KEY=your_api_key_here
```

3. **Launch main menu:**
```bash
quick_start.bat
```

## 📈 Usage

### 1. Full Analysis
- Collects news from RSS and API sources
- Performs text processing and analysis
- Saves results to database
- Generates comprehensive reports

### 2. Dashboard
- **Streamlit web interface**
- **Real-time data visualization**
- **Interactive charts and tables**
- **Modern UI with professional design**
- **Responsive layout**

### 3. Automatic Scheduler
- **Hourly automatic news collection**
- **Continuous data updates**
- **Background processing**
- **Error handling and logging**

### 4. Raw Data Viewing
- **View collected raw news data**
- **Track analysis history**
- **Export data in CSV format**
- **Database management**

### 5. System Status
- **Project status monitoring**
- **File structure viewing**
- **Usage instructions**
- **Performance metrics**

## 🔧 Technical Details

### **Core Technologies:**
- **Python 3.9+**
- **Streamlit** - Web dashboard
- **SQLite** - Database
- **Feedparser** - RSS processing
- **Requests** - HTTP requests
- **Plotly** - Chart creation
- **NLTK** - Natural language processing
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing

### **Advanced Features:**
- **Asynchronous processing**
- **Error handling and recovery**
- **Fallback systems**
- **Performance optimization**
- **Memory management**

## 📊 Analysis Results

### Most Frequent Words
1. bir (72) - one
2. türkiye (28) - turkey
3. başkanı (24) - president
4. yeni (22) - new
5. milli (18) - national

### Category Distribution
- **Gündem**: 130 news (current events)
- **Ekonomi**: 30 news (economy)
- **Spor**: 30 news (sports)
- **Dünya**: 58 news (world)

### Source Distribution
- **RSS Sources**: 248 news
- **API Sources**: 52 news
- **Total**: 300+ news

## 🌐 Dashboard Access

After launching the dashboard:
- **Local URL**: http://localhost:8501
- **Network URL**: http://192.168.1.37:8501

### Dashboard Features:
- **Modern UI Design**: Professional blue theme
- **Real-time Data**: Live updates from database
- **Interactive Charts**: Plotly-based visualizations
- **Responsive Layout**: Mobile-friendly design
- **Error Handling**: Graceful degradation

## 🔐 Security Configuration

### Environment Variables:
```bash
# .env file structure
NEWS_API_KEY=your_api_key_here
DATABASE_PATH=news_database.db
LOG_LEVEL=INFO
```

### API Key Setup:
1. Get API key from [NewsAPI](https://newsapi.org/)
2. Add to `.env` file
3. Never commit `.env` file to git

## 📝 Development

### Project Structure:
```
src/
├── dashboard.py          # Main dashboard application
├── main.py              # Analysis pipeline
├── hybrid_collector.py  # Data collection
├── database.py          # Database operations
├── text_processor.py    # Text processing
└── analytics/           # Analysis modules
```

### Code Quality:
- **Type hints** throughout
- **Error handling** in all modules
- **Logging** for debugging
- **Documentation** for all functions
- **Modular design** for maintainability

## 🚀 Performance

### Optimization Features:
- **Lazy loading** for heavy computations
- **Caching** for repeated calculations
- **Memory management** for large datasets
- **Asynchronous processing** for I/O operations
- **Database indexing** for fast queries

### Monitoring:
- **Processing time** tracking
- **Memory usage** monitoring
- **Error rate** tracking
- **Data collection** statistics

## 📄 License

This project is developed for educational and research purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions and support:
- Check the documentation
- Review the code comments
- Open an issue on GitHub

---

**Built with ❤️ for news analysis and data science** 