import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3
import json

from hybrid_collector import HybridNewsCollector
from text_processor import TextProcessor
from advanced_analytics import AdvancedAnalytics
from cooccurrence_analyzer import CooccurrenceAnalyzer
from database import NewsDatabase

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsScheduler:
    """Otomatik haber toplama ve analiz zamanlayıcısı"""
    
    def __init__(self):
        """Zamanlayıcı sistemini başlat"""
        self.hybrid_collector = HybridNewsCollector()
        self.text_processor = TextProcessor()
        self.advanced_analytics = AdvancedAnalytics()
        self.cooccurrence_analyzer = CooccurrenceAnalyzer()
        self.database = NewsDatabase()
        
        # Zamanlayıcı ayarları
        self.is_running = False
        self.collection_interval = 60  # dakika
        self.max_retries = 3
        
    async def collect_and_analyze(self) -> Dict:
        """
        Haber toplama ve analiz işlemini gerçekleştirir
        
        Returns:
            Dict: Analiz sonuçları
        """
        start_time = datetime.now()
        logger.info(f"🕐 {start_time.strftime('%H:%M:%S')} - Haber toplama başlatılıyor...")
        
        try:
            # 1. Hibrit haber toplama (RSS + API)
            news_data = await self.hybrid_collector.collect_all_news()
            
            if not news_data:
                logger.warning("⚠️ Hiç haber toplanamadı!")
                return {}
            
            logger.info(f"✅ {len(news_data)} haber toplandı")
            
            # 2. İstatistikleri hesapla
            stats = self.hybrid_collector.get_statistics(news_data)
            
            # 3. Metin işleme
            processed_texts = []
            for news in news_data:
                full_text = f"{news['title']} {news['summary']}"
                processed_text = self.text_processor.process_text(full_text)
                processed_texts.append(processed_text)
            
            # 4. Analizler
            basic_analysis = self._perform_basic_analysis(processed_texts, news_data)
            advanced_analysis = self._perform_advanced_analysis(news_data, processed_texts)
            cooccurrence_analysis = self._perform_cooccurrence_analysis(processed_texts)
            
            # 5. Metadata
            metadata = {
                'collection_time': start_time.isoformat(),
                'total_news': len(news_data),
                'rss_news': stats['rss_news'],
                'API Haberleri': stats['API Haberleri'],
                'sources': list(stats['source_distribution'].keys()),
                'categories': list(stats['category_distribution'].keys()),
                'analysis_version': '3.0',
                'collection_type': 'hybrid',
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            
            # 6. Sonuçları birleştir
            analysis_results = {
                'basic_analysis': basic_analysis,
                'advanced_analysis': advanced_analysis,
                'cooccurrence_analysis': cooccurrence_analysis,
                'metadata': metadata
            }
            
            # 7. Veritabanına kaydet
            self.database.save_analysis_results(analysis_results)
            
            # 8. Ham haber verilerini de kaydet
            self._save_raw_news_data(news_data, start_time)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"✅ Analiz tamamlandı! Süre: {duration:.2f} saniye")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Haber toplama sırasında hata: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _perform_basic_analysis(self, processed_texts: List[str], news_data: List[Dict]) -> Dict:
        """Temel analiz gerçekleştirir"""
        try:
            combined_text = " ".join(processed_texts)
            word_frequencies = self.text_processor.get_word_frequencies(combined_text)
            
            top_words = list(word_frequencies.keys())[:20]
            top_frequencies = list(word_frequencies.values())[:20]
            
            wordcloud_data = {
                'combined_text': combined_text,
                'word_frequencies': word_frequencies,
                'top_words': top_words,
                'top_frequencies': top_frequencies,
                'total_unique_words': len(word_frequencies)
            }
            
            topics = self.text_processor.extract_topics(combined_text)
            
            return {
                'word_frequency': {
                    'word_frequencies': [f"('{word}', {freq})" for word, freq in word_frequencies.items()],
                    'total_words': len(combined_text.split()),
                    'unique_words': len(word_frequencies),
                    'avg_word_length': sum(len(word) for word in word_frequencies.keys()) / len(word_frequencies) if word_frequencies else 0,
                    'top_words': top_words,
                    'top_frequencies': top_frequencies
                },
                'wordcloud_data': wordcloud_data,
                'topics': topics
            }
            
        except Exception as e:
            logger.error(f"Temel analiz hatası: {e}")
            return {}
    
    def _perform_advanced_analysis(self, news_data: List[Dict], processed_texts: List[str]) -> Dict:
        """Gelişmiş analiz gerçekleştirir"""
        try:
            categories = self.advanced_analytics.analyze_categories(news_data)
            sources = self.advanced_analytics.analyze_sources(news_data)
            events = self.advanced_analytics.detect_events(news_data)
            similarities = self.advanced_analytics.find_similar_news(news_data)
            
            return {
                'categories': categories,
                'sources': sources,
                'events': events,
                'similarities': similarities
            }
            
        except Exception as e:
            logger.error(f"Gelişmiş analiz hatası: {e}")
            return {}
    
    def _perform_cooccurrence_analysis(self, processed_texts: List[str]) -> Dict:
        """Co-occurrence analizi gerçekleştirir"""
        try:
            cooccurrences = self.cooccurrence_analyzer.analyze_cooccurrences(processed_texts)
            network_data = self.cooccurrence_analyzer.create_network_data(cooccurrences)
            
            return {
                'cooccurrences': cooccurrences,
                'network_data': network_data
            }
            
        except Exception as e:
            logger.error(f"Co-occurrence analiz hatası: {e}")
            return {}
    
    def _save_raw_news_data(self, news_data: List[Dict], collection_time: datetime):
        """Ham haber verilerini veritabanına kaydeder"""
        try:
            conn = sqlite3.connect('src/news_database.db')
            cursor = conn.cursor()
            
            # Ham haber tablosu oluştur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS raw_news_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_time TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    link TEXT,
                    source TEXT,
                    category TEXT,
                    published_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Verileri ekle
            for news in news_data:
                cursor.execute('''
                    INSERT INTO raw_news_data 
                    (collection_time, title, summary, link, source, category, published_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    collection_time.isoformat(),
                    news.get('title', ''),
                    news.get('summary', ''),
                    news.get('link', ''),
                    news.get('source', ''),
                    news.get('category', ''),
                    news.get('published_date', '')
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ {len(news_data)} ham haber verisi kaydedildi")
            
        except Exception as e:
            logger.error(f"❌ Ham haber verisi kaydetme hatası: {e}")
    
    def schedule_collection(self):
        """Her saat başı haber toplama zamanla"""
        logger.info("⏰ Zamanlayıcı ayarlanıyor...")
        
        # Her saat başı çalıştır
        schedule.every().hour.at(":00").do(self._run_collection)
        
        # İlk çalıştırma (eğer saat başı değilse, bir sonraki saat başını bekle)
        current_minute = datetime.now().minute
        if current_minute != 0:
            next_hour = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            wait_minutes = (next_hour - datetime.now()).total_seconds() / 60
            logger.info(f"⏳ İlk toplama {wait_minutes:.1f} dakika sonra başlayacak")
        
        logger.info("✅ Zamanlayıcı aktif! Her saat başı haber toplanacak.")
    
    def _run_collection(self):
        """Zamanlanmış toplama işlemini çalıştırır"""
        asyncio.run(self.collect_and_analyze())
    
    def start(self):
        """Zamanlayıcıyı başlat"""
        if self.is_running:
            logger.warning("⚠️ Zamanlayıcı zaten çalışıyor!")
            return
        
        self.is_running = True
        self.schedule_collection()
        
        logger.info("🚀 Otomatik haber toplama sistemi başlatıldı!")
        logger.info("📊 Her saat başı haber toplanacak")
        logger.info("💾 Veriler veritabanına kaydedilecek")
        logger.info("⏹️ Durdurmak için Ctrl+C tuşlarına basın")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Her dakika kontrol et
                
        except KeyboardInterrupt:
            logger.info("⏹️ Zamanlayıcı durduruluyor...")
            self.stop()
    
    def stop(self):
        """Zamanlayıcıyı durdur"""
        self.is_running = False
        schedule.clear()
        logger.info("✅ Zamanlayıcı durduruldu!")

# Ana çalıştırma fonksiyonu
def main():
    """Zamanlayıcı sistemini başlat"""
    print("🚀 Otomatik Haber Toplama Sistemi")
    print("=" * 60)
    print("📅 Her saat başı haber toplanacak")
    print("💾 Veriler veritabanına kaydedilecek")
    print("⏹️ Durdurmak için Ctrl+C")
    print("=" * 60)
    
    scheduler = NewsScheduler()
    scheduler.start()

if __name__ == "__main__":
    main() 