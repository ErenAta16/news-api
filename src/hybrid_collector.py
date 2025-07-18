"""
Hibrit Haber Toplayıcı Modülü (RSS + API)

Bu modül, hem RSS hem de API kaynaklarından haber toplar.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict

from rss_collector import FinalRSSCollector
from api_collector import APINewsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridNewsCollector:
    """RSS ve API kaynaklarından haber toplayan hibrit sınıf"""
    
    def __init__(self):
        """Hibrit toplayıcıyı başlat"""
        self.rss_collector = FinalRSSCollector()
        self.api_collector = APINewsCollector()
        
    async def collect_all_news(self) -> List[Dict]:
        """
        Tüm kaynaklardan haber toplar (RSS + API)
        
        Returns:
            List[Dict]: Tüm kaynaklardan toplanan haberler
        """
        logger.info("🚀 Hibrit haber toplama başlatılıyor...")
        
        all_news = []
        
        try:
            # 1. RSS'den haber toplama
            logger.info("📡 RSS kaynaklarından haber toplanıyor...")
            rss_news = await self.rss_collector.collect_all_feeds()
            logger.info(f"✅ RSS: {len(rss_news)} haber toplandı")
            all_news.extend(rss_news)
            
            # 2. API'den haber toplama
            logger.info("🌐 API kaynaklarından haber toplanıyor...")
            api_news = self.api_collector.get_news_from_api()
            logger.info(f"✅ API: {len(api_news)} haber toplandı")
            all_news.extend(api_news)
            
            # 3. Duplicate temizliği
            unique_news = self._remove_duplicates(all_news)
            
            logger.info(f"🎯 Toplam: {len(unique_news)} benzersiz haber toplandı")
            return unique_news
            
        except Exception as e:
            logger.error(f"❌ Hibrit toplama hatası: {e}")
            return all_news
    
    def _remove_duplicates(self, news_list: List[Dict]) -> List[Dict]:
        """Duplicate haberleri temizler"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title = news.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news
    
    def get_statistics(self, news_list: List[Dict]) -> Dict:
        """
        Hibrit haber istatistiklerini hesaplar
        
        Args:
            news_list (List[Dict]): Haber listesi
            
        Returns:
            Dict: İstatistikler
        """
        if not news_list:
            return {
                "total_news": 0,
                "rss_news": 0,
                "API Haberleri": 0,
                "source_distribution": {},
                "category_distribution": {}
            }
        
        sources = {}
        categories = {}
        rss_count = 0
        api_count = 0
        
        for news in news_list:
            source = news.get("source_name", "Bilinmeyen")
            category = news.get("category", "genel")
            
            sources[source] = sources.get(source, 0) + 1
            categories[category] = categories.get(category, 0) + 1
            
            # RSS vs API sayımı
            if news.get("category") == "API Haberleri":
                api_count += 1
            else:
                rss_count += 1
        
        return {
            "total_news": len(news_list),
            "rss_news": rss_count,
            "API Haberleri": api_count,
            "source_distribution": sources,
            "category_distribution": categories
        }

if __name__ == "__main__":
    # Test
    async def test_hybrid():
        collector = HybridNewsCollector()
        news = await collector.collect_all_news()
        stats = collector.get_statistics(news)
        print(f"Hibrit Test: {stats['total_news']} haber")
        print(f"RSS: {stats['rss_news']}, API: {stats['api_news']}")
    
    asyncio.run(test_hybrid()) 