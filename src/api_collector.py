"""
API Tabanlı Haber Toplayıcı Modülü

Bu modül, NewsAPI kullanarak haber verilerini çeker.
API Key environment variable'dan alınır.
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict
import logging

# .env dosyasını yükle
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv yoksa devam et

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APINewsCollector:
    """NewsAPI kullanarak haber toplayan sınıf"""
    
    def __init__(self):
        """API toplayıcıyı başlat"""
        # API key'i environment variable'dan al
        self.api_key = os.getenv('NEWS_API_KEY', '')
        if not self.api_key:
            logger.warning("NEWS_API_KEY environment variable bulunamadı!")
            self.api_key = "demo_key"  # Demo key kullan
        self.base_url = "https://newsapi.org/v2"
        self.session = requests.Session()
        
    def get_news_from_api(self, query: str = "turkey", language: str = "tr", page_size: int = 20) -> List[Dict]:
        """
        API'den haber çeker
        
        Args:
            query (str): Arama terimi
            language (str): Dil kodu
            page_size (int): Sayfa başına haber sayısı
            
        Returns:
            List[Dict]: Haber verilerinin listesi
        """
        try:
            url = f"{self.base_url}/everything"
            params = {
                "apiKey": self.api_key,
                "q": query,
                "language": language,
                "pageSize": page_size,
                "sortBy": "publishedAt"
            }
            
            logger.info(f"API'den haber çekiliyor: {query}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                logger.error(f"API hatası: {data.get('message', 'Bilinmeyen hata')}")
                return []
            
            articles = data.get("articles", [])
            news_list = []
            
            for article in articles:
                news_item = {
                    "title": article.get("title", ""),
                    "summary": article.get("description", ""),
                    "link": article.get("url", ""),
                    "published": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "API"),
                    "category": "API Haberleri",
                    "collected_at": datetime.now().isoformat(),
                    "source_name": article.get("source", {}).get("name", "API")
                }
                news_list.append(news_item)
            
            logger.info(f"{len(news_list)} API haber çekildi")
            return news_list
            
        except Exception as e:
            logger.error(f"API'den veri çekilirken hata: {e}")
            return []
    
    def get_statistics(self, news_list: List[Dict]) -> Dict:
        """
        Haber istatistiklerini hesaplar
        
        Args:
            news_list (List[Dict]): Haber listesi
            
        Returns:
            Dict: İstatistikler
        """
        if not news_list:
            return {
                "total_news": 0,
                "source_distribution": {},
                "category_distribution": {}
            }
        
        sources = {}
        categories = {}
        
        for news in news_list:
            source = news.get("source_name", "Bilinmeyen")
            category = news.get("category", "genel")
            
            sources[source] = sources.get(source, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_news": len(news_list),
            "source_distribution": sources,
            "category_distribution": categories
        }

if __name__ == "__main__":
    # Test
    collector = APINewsCollector()
    news = collector.get_news_from_api()
    stats = collector.get_statistics(news)
    print(f"API Test: {stats['total_news']} haber çekildi") 