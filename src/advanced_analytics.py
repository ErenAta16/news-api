"""
Gelişmiş Analiz Modülü

Bu modül, haber verilerinde anlamlı ve işlevsel analizler yapar:
- Zaman serisi ve trend analizi
- Otomatik kategori etiketleme
- Anomali ve olay tespiti
- Gündem haritası
- Otomatik alarm sistemi
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import re
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """Gelişmiş haber analizi sınıfı"""
    
    def __init__(self):
        # Kategori anahtar kelimeleri
        self.category_keywords = {
            'gündem': ['cumhurbaşkanı', 'bakan', 'meclis', 'hükümet', 'siyaset'],
            'ekonomi': ['ekonomi', 'borsa', 'dolar', 'enflasyon', 'faiz', 'bütçe'],
            'spor': ['futbol', 'basketbol', 'maç', 'lig', 'şampiyon', 'spor'],
            'dünya': ['abd', 'rusya', 'avrupa', 'bm', 'nato', 'dünya'],
            'teknoloji': ['teknoloji', 'yapay zeka', 'internet', 'dijital', 'yazılım'],
            'sağlık': ['sağlık', 'hastane', 'doktor', 'tedavi', 'ilaç', 'virüs'],
            'eğitim': ['eğitim', 'okul', 'üniversite', 'öğrenci', 'sınav'],
            'çevre': ['çevre', 'iklim', 'doğa', 'kirlilik', 'yeşil']
        }
        
    def extract_time_features(self, news_items: List[Dict]) -> pd.DataFrame:
        """
        Haber verilerinden zaman özelliklerini çıkarır
        """
        df = pd.DataFrame(news_items)
        df['published'] = pd.to_datetime(df['published'])
        df['date'] = df['published'].dt.date
        df['hour'] = df['published'].dt.hour
        df['day_of_week'] = df['published'].dt.day_name()
        df['is_weekend'] = df['published'].dt.weekday >= 5
        return df
    
    def analyze_trends(self, news_items: List[Dict], keyword: str = None) -> Dict:
        """
        Zaman serisi trend analizi yapar
        """
        logger.info("Trend analizi başlatılıyor...")
        
        df = self.extract_time_features(news_items)
        
        # Günlük haber yoğunluğu
        daily_counts = df.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        
        # Trend hesaplama (7 günlük hareketli ortalama)
        daily_counts['trend'] = daily_counts['count'].rolling(window=7, min_periods=1).mean()
        
        # Belirli kelime için trend
        if keyword:
            keyword_counts = df[df['title'].str.contains(keyword, case=False, na=False) | 
                               df['summary'].str.contains(keyword, case=False, na=False)]
            keyword_daily = keyword_counts.groupby('date').size().reset_index(name='keyword_count')
            keyword_daily['date'] = pd.to_datetime(keyword_daily['date'])
            keyword_daily['keyword_trend'] = keyword_daily['keyword_count'].rolling(window=3, min_periods=1).mean()
        else:
            keyword_daily = None
        
        # Anomali tespiti (haber yoğunluğunda ani artışlar)
        if len(daily_counts) > 0:
            anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            daily_counts['anomaly'] = anomaly_detector.fit_predict(daily_counts[['count']].values)
        else:
            daily_counts['anomaly'] = []
        
        # En yoğun günler
        peak_days = daily_counts.nlargest(5, 'count')[['date', 'count']]
        
        results = {
            'daily_counts': daily_counts,
            'keyword_trends': keyword_daily,
            'peak_days': peak_days,
            'total_news': len(df),
            'date_range': (df['published'].min(), df['published'].max())
        }
        
        logger.info("Trend analizi tamamlandı")
        return results
    
    def categorize_news(self, news_items: List[Dict]) -> Dict:
        """
        Haberleri otomatik olarak kategorilere ayırır
        """
        logger.info("Haber kategorizasyonu başlatılıyor...")
        
        categorized_news = defaultdict(list)
        category_scores = defaultdict(int)
        
        for item in news_items:
            text = f"{item['title']} {item['summary']}".lower()
            best_category = 'diğer'
            best_score = 0
            
            for category, keywords in self.category_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > best_score:
                    best_score = score
                    best_category = category
            
            categorized_news[best_category].append(item)
            category_scores[best_category] += 1
        
        # Kategori dağılımı
        category_distribution = dict(category_scores)
        
        # En popüler kategoriler
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = {
            'categorized_news': dict(categorized_news),
            'category_distribution': category_distribution,
            'top_categories': top_categories
        }
        
        logger.info("Haber kategorizasyonu tamamlandı")
        return results
    
    def detect_events(self, news_items: List[Dict]) -> Dict:
        """
        Önemli olayları ve anomalileri tespit eder
        """
        logger.info("Olay tespiti başlatılıyor...")
        
        df = self.extract_time_features(news_items)
        
        # Saatlik haber yoğunluğu
        hourly_counts = df.groupby('hour').size()
        
        # Anormal saatler (ortalama + 2 standart sapma)
        mean_hourly = hourly_counts.mean()
        std_hourly = hourly_counts.std()
        anomaly_hours = hourly_counts[hourly_counts > mean_hourly + 2*std_hourly]
        
        # Günlük yoğunluk anomalileri
        daily_counts = df.groupby('date').size()
        mean_daily = daily_counts.mean()
        std_daily = daily_counts.std()
        anomaly_days = daily_counts[daily_counts > mean_daily + 2*std_daily]
        
        # Acil durum kelimeleri
        emergency_keywords = ['deprem', 'yangın', 'kazası', 'ölüm', 'kriz', 'acil', 'patlama']
        emergency_news = []
        
        for item in news_items:
            text = f"{item['title']} {item['summary']}".lower()
            if any(keyword in text for keyword in emergency_keywords):
                emergency_news.append(item)
        
        results = {
            'anomaly_hours': anomaly_hours.to_dict(),
            'anomaly_days': anomaly_days.to_dict(),
            'emergency_news': emergency_news,
            'total_emergency': len(emergency_news)
        }
        
        logger.info("Olay tespiti tamamlandı")
        return results
    
    def analyze_source_comparison(self, news_items: List[Dict]) -> Dict:
        """
        Farklı haber kaynaklarını karşılaştırır
        """
        logger.info("Kaynak karşılaştırması başlatılıyor...")
        
        df = pd.DataFrame(news_items)
        
        # Kaynak bazında kategori dağılımı
        source_category_analysis = {}
        
        for source in df['source'].unique():
            source_news = df[df['source'] == source]
            categorized = self.categorize_news(source_news.to_dict('records'))
            source_category_analysis[source] = categorized['category_distribution']
        
        # Kaynak bazında haber yoğunluğu
        source_counts = df['source'].value_counts()
        
        # Kaynak bazında ortalama haber uzunluğu
        df['title_length'] = df['title'].str.len()
        df['summary_length'] = df['summary'].str.len()
        source_avg_lengths = df.groupby('source')[['title_length', 'summary_length']].mean()
        
        results = {
            'source_category_analysis': source_category_analysis,
            'source_counts': source_counts.to_dict(),
            'source_avg_lengths': source_avg_lengths.to_dict()
        }
        
        logger.info("Kaynak karşılaştırması tamamlandı")
        return results
    
    def generate_alerts(self, news_items: List[Dict], alert_thresholds: Dict = None) -> List[Dict]:
        """
        Otomatik alarm ve bildirimler üretir
        """
        logger.info("Alarm sistemi başlatılıyor...")
        
        if alert_thresholds is None:
            alert_thresholds = {
                'emergency_keywords': 5,  # Acil durum kelimesi geçen haber sayısı
                'daily_news_spike': 50,   # Günlük haber sayısı artışı
                'category_spike': 20      # Kategori bazında artış
            }
        
        alerts = []
        
        # Acil durum alarmları
        emergency_keywords = ['deprem', 'yangın', 'kazası', 'ölüm', 'kriz', 'acil']
        emergency_count = 0
        
        for item in news_items:
            text = f"{item['title']} {item['summary']}".lower()
            if any(keyword in text for keyword in emergency_keywords):
                emergency_count += 1
        
        if emergency_count >= alert_thresholds['emergency_keywords']:
            alerts.append({
                'type': 'emergency',
                'message': f'⚠️ Acil durum haberlerinde artış: {emergency_count} haber',
                'severity': 'high',
                'timestamp': datetime.now()
            })
        
        # Günlük yoğunluk alarmları
        df = self.extract_time_features(news_items)
        today_count = len(df[df['date'] == datetime.now().date()])
        
        if today_count >= alert_thresholds['daily_news_spike']:
            alerts.append({
                'type': 'volume',
                'message': f'📈 Günlük haber yoğunluğu yüksek: {today_count} haber',
                'severity': 'medium',
                'timestamp': datetime.now()
            })
        
        # Kategori alarmları
        categorized = self.categorize_news(news_items)
        for category, count in categorized['top_categories']:
            if count >= alert_thresholds['category_spike']:
                alerts.append({
                    'type': 'category',
                    'message': f'🏷️ {category} kategorisinde yoğunluk: {count} haber',
                    'severity': 'low',
                    'timestamp': datetime.now()
                })
        
        logger.info(f"{len(alerts)} alarm üretildi")
        return alerts
    
    def create_agenda_map(self, news_items: List[Dict]) -> Dict:
        """
        Gündem haritası oluşturur
        """
        logger.info("Gündem haritası oluşturuluyor...")
        
        df = self.extract_time_features(news_items)
        
        # Günlük konu dağılımı
        daily_topics = {}
        
        for date in df['date'].unique():
            daily_news = df[df['date'] == date]
            # Günlük en popüler kelimeler
            all_text = ' '.join(daily_news['title'].tolist() + daily_news['summary'].tolist())
            words = re.findall(r'\b\w+\b', all_text.lower())
            word_counts = Counter(words)
            daily_topics[date] = word_counts.most_common(5)
        
        # Haftalık trend analizi
        df['week'] = df['published'].dt.isocalendar().week
        weekly_trends = df.groupby('week').size()
        
        # Konu değişim hızı
        topic_velocity = {}
        dates = sorted(daily_topics.keys())
        
        for i in range(1, len(dates)):
            prev_topics = set(word for word, _ in daily_topics[dates[i-1]])
            curr_topics = set(word for word, _ in daily_topics[dates[i]])
            
            new_topics = curr_topics - prev_topics
            dropped_topics = prev_topics - curr_topics
            
            topic_velocity[dates[i]] = {
                'new': list(new_topics),
                'dropped': list(dropped_topics),
                'stable': list(prev_topics & curr_topics)
            }
        
        results = {
            'daily_topics': daily_topics,
            'weekly_trends': weekly_trends.to_dict(),
            'topic_velocity': topic_velocity
        }
        
        logger.info("Gündem haritası oluşturuldu")
        return results

# Test için örnek kullanım
if __name__ == "__main__":
    # Örnek haber verileri
    sample_news = [
        {
            'title': 'Deprem sonrası yardım çalışmaları',
            'summary': 'İstanbul\'da meydana gelen deprem sonrası yardım çalışmaları başladı.',
            'published': '2024-01-15T10:00:00',
            'source': 'https://example.com'
        },
        {
            'title': 'Ekonomi büyüme verileri açıklandı',
            'summary': 'Türkiye ekonomisi yüzde 3 büyüdü.',
            'published': '2024-01-15T11:00:00',
            'source': 'https://example.com'
        }
    ]
    
    analyzer = AdvancedAnalytics()
    
    # Trend analizi
    trends = analyzer.analyze_trends(sample_news, keyword='deprem')
    print("Trend analizi:", trends)
    
    # Kategorizasyon
    categories = analyzer.categorize_news(sample_news)
    print("Kategoriler:", categories)
    
    # Olay tespiti
    events = analyzer.detect_events(sample_news)
    print("Olaylar:", events)
    
    # Alarmlar
    alerts = analyzer.generate_alerts(sample_news)
    print("Alarmlar:", alerts) 