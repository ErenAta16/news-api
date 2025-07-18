"""
Final RSS Veri Toplayıcı Modülü

Bu modül, düzeltilmiş ve çalışan RSS kaynaklarından
haber verilerini çeker.
"""

import feedparser
import requests
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalRSSCollector:
    """Final RSS akışlarından haber verilerini toplayan sınıf"""
    
    def __init__(self):
        """RSS toplayıcıyı başlat"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Test edilmiş ve çalışan RSS kaynakları
        self.working_rss_sources = {
            'Gündem': [
                "https://www.hurriyet.com.tr/rss/anasayfa",
                "https://www.aa.com.tr/tr/rss/default?cat=guncel",
                "https://www.bbc.com/turkce/index.xml"
            ],
            'Ekonomi': [
                "https://www.aa.com.tr/tr/rss/default?cat=ekonomi"
            ],
            'Spor': [
                "https://www.aa.com.tr/tr/rss/default?cat=spor"
            ],
            'Dünya': [
                "https://www.aa.com.tr/tr/rss/default?cat=dunya",
                "https://www.bbc.com/turkce/index.xml"
            ]
        }
        
        # Alternatif kaynaklar
        self.alternative_sources = [
            "https://feeds.bbci.co.uk/turkce/rss.xml",
            "https://www.hurriyet.com.tr/rss/anasayfa",
            "https://www.aa.com.tr/tr/rss/default?cat=guncel"
        ]
    
    def get_news_from_rss(self, rss_url: str, category: str = 'Gündem') -> List[Dict]:
        """
        Belirtilen RSS URL'sinden haberleri çeker
        
        Args:
            rss_url (str): RSS akışının URL'si
            category (str): Haber kategorisi
            
        Returns:
            List[Dict]: Haber verilerinin listesi
        """
        try:
            logger.info(f"RSS akışından veri çekiliyor: {rss_url}")
            
            # Timeout olmadan RSS akışını parse et
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                logger.warning(f"RSS akışında hata var: {rss_url}")
            
            news_list = []
            
            for entry in feed.entries:
                # Tarih kontrolü yapmadan tüm haberleri al
                published_date = self._parse_date(entry.get('published', ''))
                
                news_item = {
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': published_date or datetime.now().isoformat(),
                    'source': rss_url,
                    'category': category,
                    'collected_at': datetime.now().isoformat(),
                    'source_name': self._extract_source_name(rss_url)
                }
                news_list.append(news_item)
            
            logger.info(f"{len(news_list)} haber çekildi: {rss_url}")
            return news_list
            
        except Exception as e:
            logger.error(f"RSS akışından veri çekilirken hata: {rss_url}, Hata: {str(e)}")
            return []
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Tarih string'ini ISO formatına çevirir
        
        Args:
            date_str (str): Tarih string'i
            
        Returns:
            Optional[str]: ISO formatında tarih veya None
        """
        if not date_str:
            return None
        
        try:
            # feedparser'ın tarih parse etme özelliğini kullan
            parsed_date = feedparser._parse_date(date_str)
            if parsed_date:
                return parsed_date.isoformat()
        except:
            pass
        
        return None
    
    def _extract_source_name(self, url: str) -> str:
        """
        URL'den kaynak adını çıkarır
        
        Args:
            url (str): RSS URL'si
            
        Returns:
            str: Kaynak adı
        """
        if 'hurriyet' in url:
            return 'Hürriyet'
        elif 'aa.com.tr' in url:
            return 'Anadolu Ajansı'
        elif 'bbc.com' in url or 'bbci.co.uk' in url:
            return 'BBC Türkçe'
        elif 'cnnturk' in url:
            return 'CNN Türk'
        elif 'ntv.com.tr' in url:
            return 'NTV'
        elif 'trthaber' in url:
            return 'TRT Haber'
        elif 'anadolu.com.tr' in url:
            return 'Anadolu'
        elif 'milliyet' in url:
            return 'Milliyet'
        else:
            return 'Diğer'
    
    async def collect_from_category(self, category: str) -> List[Dict]:
        """
        Belirli bir kategoriden haber toplar
        
        Args:
            category (str): Haber kategorisi
            
        Returns:
            List[Dict]: Kategoriden toplanan haberler
        """
        if category not in self.working_rss_sources:
            logger.warning(f"Bilinmeyen kategori: {category}")
            return []
        
        urls = self.working_rss_sources[category]
        all_news = []
        
        for url in urls:
            try:
                news = self.get_news_from_rss(url, category)
                all_news.extend(news)
                # Rate limiting
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"{url} kaynağından veri çekilemedi: {e}")
        
        logger.info(f"{category} kategorisinden {len(all_news)} haber toplandı")
        return all_news
    
    async def collect_all_feeds(self) -> List[Dict]:
        """
        Tüm RSS kaynaklarından haberleri toplar
        
        Returns:
            List[Dict]: Tüm kaynaklardan toplanan haberler
        """
        logger.info("Tüm RSS kaynaklarından veri toplanıyor...")
        
        all_news = []
        
        # Kategorilere göre toplama
        for category in self.working_rss_sources.keys():
            try:
                news = await self.collect_from_category(category)
                all_news.extend(news)
            except Exception as e:
                logger.error(f"{category} kategorisi toplanamadı: {e}")
        
        # Eğer hiç haber toplanamadıysa alternatif kaynakları dene
        if not all_news:
            logger.info("Ana kaynaklardan veri toplanamadı, alternatif kaynaklar deneniyor...")
            for url in self.alternative_sources:
                try:
                    news = self.get_news_from_rss(url, 'Gündem')
                    all_news.extend(news)
                    if news:
                        logger.info(f"Alternatif kaynaktan {len(news)} haber toplandı: {url}")
                except Exception as e:
                    logger.error(f"Alternatif kaynak hatası: {url}, {e}")
        
        # Duplicate haberleri temizle
        unique_news = self._remove_duplicates(all_news)
        
        logger.info(f"Toplam {len(unique_news)} benzersiz haber toplandı")
        return unique_news
    
    def _remove_duplicates(self, news_list: List[Dict]) -> List[Dict]:
        """
        Duplicate haberleri temizler
        
        Args:
            news_list (List[Dict]): Haber listesi
            
        Returns:
            List[Dict]: Benzersiz haberler
        """
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            # Başlığı normalize et
            title = news['title'].lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news
    
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
                'total_news': 0,
                'category_distribution': {},
                'source_distribution': {},
                'collection_time': datetime.now().isoformat()
            }
        
        # Kategori dağılımı
        category_counts = {}
        source_counts = {}
        
        for news in news_list:
            category = news.get('category', 'bilinmeyen')
            source = news.get('source_name', 'bilinmeyen')
            
            category_counts[category] = category_counts.get(category, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'total_news': len(news_list),
            'category_distribution': category_counts,
            'source_distribution': source_counts,
            'collection_time': datetime.now().isoformat()
        }

# Test için örnek kullanım
async def test_final_collector():
    """Final toplayıcıyı test et"""
    collector = FinalRSSCollector()
    
    print("🔍 Final RSS Toplayıcı Test Ediliyor...")
    print("=" * 60)
    
    # Tüm kategorilerden veri topla
    all_news = await collector.collect_all_feeds()
    
    # İstatistikleri göster
    stats = collector.get_statistics(all_news)
    
    print(f"\n📊 TOPLAMA İSTATİSTİKLERİ:")
    print(f"  Toplam haber: {stats['total_news']}")
    print(f"  Toplama zamanı: {stats['collection_time']}")
    
    print(f"\n🏷️ KATEGORİ DAĞILIMI:")
    for category, count in stats['category_distribution'].items():
        print(f"  {category}: {count} haber")
    
    print(f"\n📡 KAYNAK DAĞILIMI:")
    for source, count in stats['source_distribution'].items():
        print(f"  {source}: {count} haber")
    
    # Örnek haberler göster
    if all_news:
        print(f"\n📰 ÖRNEK HABERLER:")
        for i, news in enumerate(all_news[:5], 1):
            print(f"  {i}. {news['title']}")
            print(f"     Kategori: {news['category']}")
            print(f"     Kaynak: {news['source_name']}")
            print(f"     Tarih: {news['published']}")
            print()
    else:
        print("\n❌ Hiç haber toplanamadı!")

if __name__ == "__main__":
    asyncio.run(test_final_collector()) 