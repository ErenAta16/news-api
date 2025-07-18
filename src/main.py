"""
Gelişmiş Haber Analizi Ana Sistemi

Bu modül, gelişmiş RSS toplayıcı ile entegre edilmiş
tam haber analizi pipeline'ını çalıştırır.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List

# Modül importları
from hybrid_collector import HybridNewsCollector
from text_processor import TextProcessor
from advanced_analytics import AdvancedAnalytics
from cooccurrence_analyzer import CooccurrenceAnalyzer
from database import NewsDatabase

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedNewsAnalysis:
    """Gelişmiş haber analizi sınıfı"""
    
    def __init__(self):
        """Analiz sistemini başlat"""
        self.hybrid_collector = HybridNewsCollector()
        self.text_processor = TextProcessor()
        self.advanced_analytics = AdvancedAnalytics()
        self.cooccurrence_analyzer = CooccurrenceAnalyzer()
        self.database = NewsDatabase()
        
    async def run_full_analysis(self) -> Dict:
        """
        Tam haber analizi pipeline'ını çalıştırır
        
        Returns:
            Dict: Analiz sonuçları
        """
        logger.info("🚀 Gelişmiş Haber Analizi Başlatılıyor...")
        logger.info("=" * 60)
        
        try:
            # 1. Hibrit haber toplama (RSS + API)
            logger.info("🚀 Hibrit haber toplama başlatılıyor...")
            news_data = await self.hybrid_collector.collect_all_news()
            
            if not news_data:
                logger.error("❌ Hiç haber toplanamadı!")
                return {}
            
            logger.info(f"✅ {len(news_data)} haber toplandı")
            
            # 2. İstatistikleri hesapla
            stats = self.hybrid_collector.get_statistics(news_data)
            logger.info(f"📊 İstatistikler: {stats['total_news']} haber (RSS: {stats['rss_news']}, API: {stats['API Haberleri']})")
            
            # 3. Metin işleme
            logger.info("🔤 Metin işleme başlatılıyor...")
            processed_texts = []
            
            for news in news_data:
                # Başlık ve özeti birleştir
                full_text = f"{news['title']} {news['summary']}"
                processed_text = self.text_processor.process_text(full_text)
                processed_texts.append(processed_text)
            
            logger.info(f"✅ {len(processed_texts)} metin işlendi")
            
            # 4. Temel analiz
            logger.info("📊 Temel analiz başlatılıyor...")
            basic_analysis = self._perform_basic_analysis(processed_texts, news_data)
            
            # 5. Gelişmiş analiz
            logger.info("🔍 Gelişmiş analiz başlatılıyor...")
            advanced_analysis = self._perform_advanced_analysis(news_data, processed_texts)
            
            # 6. Co-occurrence analizi
            logger.info("🔗 Co-occurrence analizi başlatılıyor...")
            cooccurrence_analysis = self._perform_cooccurrence_analysis(processed_texts)
            
            # 7. Metadata oluştur
            metadata = {
                'total_news': len(news_data),
                'rss_news': stats['rss_news'],
                'API Haberleri': stats['API Haberleri'],
                'sources': list(stats['source_distribution'].keys()),
                'categories': list(stats['category_distribution'].keys()),
                'collection_time': datetime.now().isoformat(),
                'analysis_version': '3.0',
                'collection_type': 'hybrid'
            }
            
            # 8. Sonuçları birleştir
            analysis_results = {
                'basic_analysis': basic_analysis,
                'advanced_analysis': advanced_analysis,
                'cooccurrence_analysis': cooccurrence_analysis,
                'metadata': metadata
            }
            
            # 9. Veritabanına kaydet
            logger.info("💾 Sonuçlar veritabanına kaydediliyor...")
            self.database.save_analysis_results(analysis_results)
            
            logger.info("✅ Analiz tamamlandı!")
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Analiz sırasında hata: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _perform_basic_analysis(self, processed_texts: List[str], news_data: List[Dict]) -> Dict:
        """Temel analiz gerçekleştirir"""
        try:
            # Tüm metinleri birleştir
            combined_text = " ".join(processed_texts)
            
            # Kelime frekansı analizi
            word_frequencies = self.text_processor.get_word_frequencies(combined_text)
            
            # En sık kullanılan kelimeler
            top_words = list(word_frequencies.keys())[:20]
            top_frequencies = list(word_frequencies.values())[:20]
            
            # Word cloud verisi
            wordcloud_data = {
                'combined_text': combined_text,
                'word_frequencies': word_frequencies,
                'top_words': top_words,
                'top_frequencies': top_frequencies,
                'total_unique_words': len(word_frequencies)
            }
            
            # Konu modelleme
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
            # Kategori analizi
            categories = self.advanced_analytics.analyze_categories(news_data)
            
            # Kaynak analizi
            sources = self.advanced_analytics.analyze_sources(news_data)
            
            # Olay tespiti
            events = self.advanced_analytics.detect_events(news_data)
            
            # Benzerlik analizi
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
            # Co-occurrence analizi
            cooccurrences = self.cooccurrence_analyzer.analyze_cooccurrences(processed_texts)
            
            # Ağ analizi
            network_data = self.cooccurrence_analyzer.create_network_data(cooccurrences)
            
            return {
                'cooccurrences': cooccurrences,
                'network_data': network_data
            }
            
        except Exception as e:
            logger.error(f"Co-occurrence analiz hatası: {e}")
            return {}

# Ana çalıştırma fonksiyonu
async def main():
    """Ana analiz sistemini çalıştır"""
    analyzer = EnhancedNewsAnalysis()
    
    print("🚀 Gelişmiş Haber Analizi Sistemi")
    print("=" * 60)
    
    # Tam analizi çalıştır
    results = await analyzer.run_full_analysis()
    
    if results:
        print("\n✅ ANALİZ TAMAMLANDI!")
        print(f"📊 Toplam haber: {results['metadata']['total_news']}")
        print(f"📡 Kaynaklar: {', '.join(results['metadata']['sources'])}")
        print(f"🏷️ Kategoriler: {', '.join(results['metadata']['categories'])}")
        print(f"⏰ Analiz zamanı: {results['metadata']['collection_time']}")
        
        # Temel analiz sonuçları
        if 'basic_analysis' in results and 'word_frequency' in results['basic_analysis']:
            word_freq = results['basic_analysis']['word_frequency']
            print(f"\n📈 TEMEL ANALİZ SONUÇLARI:")
            print(f"  Toplam kelime: {word_freq['total_words']}")
            print(f"  Benzersiz kelime: {word_freq['unique_words']}")
            print(f"  Ortalama kelime uzunluğu: {word_freq['avg_word_length']:.2f}")
            
            print(f"\n🔤 EN SIK KULLANILAN KELİMELER:")
            for i, (word, freq) in enumerate(zip(word_freq['top_words'][:10], word_freq['top_frequencies'][:10]), 1):
                print(f"  {i}. {word}: {freq}")
        
        # Gelişmiş analiz sonuçları
        if 'advanced_analysis' in results and 'categories' in results['advanced_analysis']:
            categories = results['advanced_analysis']['categories']
            if 'category_distribution' in categories:
                print(f"\n🏷️ KATEGORİ DAĞILIMI:")
                for category, count in categories['category_distribution'].items():
                    print(f"  {category}: {count} haber")
        
        print(f"\n💾 Sonuçlar veritabanına kaydedildi!")
        print(f"🌐 Dashboard'u görüntülemek için: streamlit run dashboard_fixed.py")
        
    else:
        print("\n❌ Analiz başarısız oldu!")

if __name__ == "__main__":
    asyncio.run(main()) 