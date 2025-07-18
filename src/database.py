"""
Veri Tabanı Modülü - SQLite Tabanlı Haber ve Analiz Veri Tabanı

Bu modül, haber verilerini ve analiz sonuçlarını SQLite veri tabanında saklar:
- Haber verileri (RSS'ten çekilen)
- Analiz sonuçları (kelime analizi, konu modelleme, vb.)
- Gelişmiş analiz sonuçları (trend, kategori, co-occurrence)
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsDatabase:
    """Haber veri tabanı sınıfı"""
    
    def __init__(self, db_path: str = "news_database.db"):
        """
        Veri tabanını başlat
        
        Args:
            db_path (str): Veri tabanı dosya yolu
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Veri tabanı tablolarını oluştur"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Haber kaynakları tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news_sources (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        url TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Haberler tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        summary TEXT,
                        link TEXT,
                        published TIMESTAMP,
                        source TEXT,
                        title_clean TEXT,
                        summary_clean TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Analiz sonuçları tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_type TEXT NOT NULL,
                        results TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Gelişmiş analiz sonuçları tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS advanced_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_data TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # İndeksler oluştur
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_published ON news(published)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_source ON news(source)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_advanced_analysis_date ON advanced_analysis(created_at)')
                
                conn.commit()
                logger.info("Veri tabanı tabloları oluşturuldu")
                
        except Exception as e:
            logger.error(f"Veri tabanı başlatma hatası: {e}")
            raise
    
    def add_source(self, name: str, url: str) -> bool:
        """
        Haber kaynağı ekle
        
        Args:
            name (str): Kaynak adı
            url (str): RSS URL'si
            
        Returns:
            bool: Başarı durumu
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR REPLACE INTO news_sources (name, url) VALUES (?, ?)',
                    (name, url)
                )
                conn.commit()
                logger.info(f"Kaynak eklendi: {name}")
                return True
                
        except Exception as e:
            logger.error(f"Kaynak ekleme hatası: {e}")
            return False
    
    def get_sources(self) -> List[Dict]:
        """
        Tüm haber kaynaklarını getir
        
        Returns:
            List[Dict]: Kaynak listesi
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, url FROM news_sources')
                sources = []
                for row in cursor.fetchall():
                    sources.append({
                        'name': row[0],
                        'url': row[1]
                    })
                return sources
                
        except Exception as e:
            logger.error(f"Kaynak getirme hatası: {e}")
            return []
    
    def save_news(self, news_item: Dict) -> bool:
        """
        Haber kaydet
        
        Args:
            news_item (Dict): Haber verisi
            
        Returns:
            bool: Başarı durumu
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Aynı link varsa güncelle, yoksa ekle
                cursor.execute('''
                    INSERT OR REPLACE INTO news 
                    (title, summary, link, published, source, title_clean, summary_clean)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    news_item.get('title', ''),
                    news_item.get('summary', ''),
                    news_item.get('link', ''),
                    news_item.get('published', ''),
                    news_item.get('source', ''),
                    news_item.get('title_clean', ''),
                    news_item.get('summary_clean', '')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Haber kaydetme hatası: {e}")
            return False
    
    def insert_news(self, news_items: List[Dict]) -> int:
        """
        Birden fazla haber kaydet
        
        Args:
            news_items (List[Dict]): Haber listesi
            
        Returns:
            int: Kaydedilen haber sayısı
        """
        count = 0
        for item in news_items:
            if self.save_news(item):
                count += 1
        
        logger.info(f"{count} haber kaydedildi")
        return count
    
    def get_all_news(self, limit: int = 1000) -> List[Dict]:
        """
        Tüm haberleri getir
        
        Args:
            limit (int): Maksimum haber sayısı
            
        Returns:
            List[Dict]: Haber listesi
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT title, summary, link, published, source, title_clean, summary_clean
                    FROM news 
                    ORDER BY published DESC 
                    LIMIT ?
                ''', (limit,))
                
                news_items = []
                for row in cursor.fetchall():
                    news_items.append({
                        'title': row[0],
                        'summary': row[1],
                        'link': row[2],
                        'published': row[3],
                        'source': row[4],
                        'title_clean': row[5],
                        'summary_clean': row[6]
                    })
                
                return news_items
                
        except Exception as e:
            logger.error(f"Haber getirme hatası: {e}")
            return []
    
    def get_news_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Tarih aralığına göre haberleri getir
        
        Args:
            start_date (str): Başlangıç tarihi (YYYY-MM-DD)
            end_date (str): Bitiş tarihi (YYYY-MM-DD)
            
        Returns:
            List[Dict]: Haber listesi
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT title, summary, link, published, source, title_clean, summary_clean
                    FROM news 
                    WHERE DATE(published) BETWEEN ? AND ?
                    ORDER BY published DESC
                ''', (start_date, end_date))
                
                news_items = []
                for row in cursor.fetchall():
                    news_items.append({
                        'title': row[0],
                        'summary': row[1],
                        'link': row[2],
                        'published': row[3],
                        'source': row[4],
                        'title_clean': row[5],
                        'summary_clean': row[6]
                    })
                
                return news_items
                
        except Exception as e:
            logger.error(f"Tarih aralığı haber getirme hatası: {e}")
            return []
    
    def save_analysis_result(self, analysis_type: str, results: Dict) -> bool:
        """
        Analiz sonucunu kaydet
        
        Args:
            analysis_type (str): Analiz türü
            results (Dict): Analiz sonuçları
            
        Returns:
            bool: Başarı durumu
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO analysis_results (analysis_type, results) VALUES (?, ?)',
                    (analysis_type, json.dumps(results, ensure_ascii=False))
                )
                conn.commit()
                logger.info(f"Analiz sonucu kaydedildi: {analysis_type}")
                return True
                
        except Exception as e:
            logger.error(f"Analiz sonucu kaydetme hatası: {e}")
            return False
    
    def get_analysis_result(self, analysis_type: str) -> Optional[Dict]:
        """
        Analiz sonucunu getir
        
        Args:
            analysis_type (str): Analiz türü
            
        Returns:
            Optional[Dict]: Analiz sonucu
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT results FROM analysis_results WHERE analysis_type = ? ORDER BY created_at DESC LIMIT 1',
                    (analysis_type,)
                )
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
                
        except Exception as e:
            logger.error(f"Analiz sonucu getirme hatası: {e}")
            return None
    
    def save_analysis_results(self, results: Dict) -> bool:
        """
        Gelişmiş analiz sonuçlarını kaydet
        
        Args:
            results (Dict): Tüm analiz sonuçları
            
        Returns:
            bool: Başarı durumu
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # JSON serileştirme için veriyi temizle
                def clean_for_json(obj):
                    if isinstance(obj, dict):
                        return {str(k): clean_for_json(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [clean_for_json(item) for item in obj]
                    elif isinstance(obj, tuple):
                        return str(obj)  # Tuple'ları string'e çevir
                    elif isinstance(obj, (datetime, pd.Timestamp)):
                        return obj.isoformat()
                    elif isinstance(obj, (np.integer, np.floating)):
                        return float(obj)
                    elif isinstance(obj, np.ndarray):
                        return obj.tolist()
                    elif hasattr(obj, '__class__') and 'Graph' in obj.__class__.__name__:
                        # NetworkX Graph objelerini kaldır
                        return "Graph object (removed for JSON serialization)"
                    elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict', None)):
                        # DataFrame ve benzeri objeleri dict'e çevir
                        try:
                            return obj.to_dict('records')
                        except:
                            return str(obj)
                    else:
                        return obj
                
                cleaned_results = clean_for_json(results)
                
                # Metadata'yı ayrı kaydet
                metadata = cleaned_results.get('metadata', {})
                
                cursor.execute(
                    'INSERT INTO advanced_analysis (analysis_data, metadata) VALUES (?, ?)',
                    (json.dumps(cleaned_results, ensure_ascii=False), json.dumps(metadata, ensure_ascii=False))
                )
                conn.commit()
                logger.info("Gelişmiş analiz sonuçları kaydedildi")
                return True
                
        except Exception as e:
            logger.error(f"Gelişmiş analiz kaydetme hatası: {e}")
            return False
    
    def get_latest_analysis(self) -> Optional[Dict]:
        """
        En son analiz sonuçlarını getir
        
        Returns:
            Optional[Dict]: En son analiz sonuçları
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT analysis_data FROM advanced_analysis ORDER BY created_at DESC LIMIT 1'
                )
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
                
        except Exception as e:
            logger.error(f"En son analiz getirme hatası: {e}")
            return None
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """
        Analiz geçmişini getir
        
        Args:
            limit (int): Maksimum kayıt sayısı
            
        Returns:
            List[Dict]: Analiz geçmişi
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT analysis_data, created_at FROM advanced_analysis ORDER BY created_at DESC LIMIT ?',
                    (limit,)
                )
                
                history = []
                for row in cursor.fetchall():
                    analysis_data = json.loads(row[0])
                    history.append({
                        'data': analysis_data,
                        'created_at': row[1]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Analiz geçmişi getirme hatası: {e}")
            return []
    
    def get_news_count(self) -> int:
        """
        Toplam haber sayısını getir
        
        Returns:
            int: Haber sayısı
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM news')
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Haber sayısı getirme hatası: {e}")
            return 0
    
    def get_all_news(self, limit: int = 1000) -> List[Dict]:
        """
        Tüm haberleri getir (son limit kadar)
        
        Args:
            limit (int): Maksimum haber sayısı
            
        Returns:
            List[Dict]: Haber listesi
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT title, summary, link, published, source, title_clean, summary_clean
                    FROM news 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                news_list = []
                for row in cursor.fetchall():
                    news_list.append({
                        'title': row[0],
                        'summary': row[1],
                        'link': row[2],
                        'published': row[3],
                        'source': row[4],
                        'title_clean': row[5],
                        'summary_clean': row[6]
                    })
                
                logger.info(f"{len(news_list)} haber getirildi")
                return news_list
                
        except Exception as e:
            logger.error(f"Haber getirme hatası: {e}")
            return []
    
    def get_source_stats(self) -> Dict:
        """
        Kaynak bazında istatistikleri getir
        
        Returns:
            Dict: Kaynak istatistikleri
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT source, COUNT(*) as count 
                    FROM news 
                    GROUP BY source 
                    ORDER BY count DESC
                ''')
                
                stats = {}
                for row in cursor.fetchall():
                    stats[row[0]] = row[1]
                
                return stats
                
        except Exception as e:
            logger.error(f"Kaynak istatistikleri getirme hatası: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """
        Eski verileri temizle
        
        Args:
            days (int): Kaç günden eski veriler silinecek
            
        Returns:
            int: Silinen kayıt sayısı
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Eski haberleri sil
                cursor.execute('''
                    DELETE FROM news 
                    WHERE DATE(published) < DATE('now', '-{} days')
                '''.format(days))
                
                deleted_news = cursor.rowcount
                
                # Eski analiz sonuçlarını sil
                cursor.execute('''
                    DELETE FROM analysis_results 
                    WHERE DATE(created_at) < DATE('now', '-{} days')
                '''.format(days))
                
                deleted_analysis = cursor.rowcount
                
                conn.commit()
                logger.info(f"{deleted_news} eski haber, {deleted_analysis} eski analiz silindi")
                return deleted_news + deleted_analysis
                
        except Exception as e:
            logger.error(f"Veri temizleme hatası: {e}")
            return 0

# Test için örnek kullanım
if __name__ == "__main__":
    db = NewsDatabase()
    
    # Test verisi
    test_news = {
        'title': 'Test Haber',
        'summary': 'Test özet',
        'link': 'https://test.com',
        'published': '2024-01-15T10:00:00',
        'source': 'Test Kaynak'
    }
    
    # Haber kaydet
    db.save_news(test_news)
    
    # Haberleri getir
    news_list = db.get_all_news()
    print(f"Toplam {len(news_list)} haber var")
    
    # Kaynak istatistikleri
    stats = db.get_source_stats()
    print("Kaynak istatistikleri:", stats) 