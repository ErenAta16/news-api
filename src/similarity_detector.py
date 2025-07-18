"""
Benzerlik Tespiti ve Copy-Paste Habercilik Analizi Modülü

Bu modül, farklı haber kaynaklarında benzer içerikleri tespit eder
ve copy-paste habercilik analizi yapar.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Set
import pandas as pd
from datetime import datetime
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimilarityDetector:
    """Haber benzerliklerini tespit eden sınıf"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Benzerlik tespit ediciyi başlat
        
        Args:
            similarity_threshold (float): Benzerlik eşiği (0-1 arası)
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = None
        
    def prepare_texts(self, news_items: List[Dict]) -> List[str]:
        """
        Haber metinlerini analiz için hazırlar
        
        Args:
            news_items (List[Dict]): Haber verilerinin listesi
            
        Returns:
            List[str]: Hazırlanmış metinler
        """
        texts = []
        for item in news_items:
            # Başlık ve özeti birleştir
            title = item.get('title', '')
            summary = item.get('summary', '')
            combined_text = f"{title} {summary}".strip()
            texts.append(combined_text)
        return texts
    
    def calculate_cosine_similarity(self, texts: List[str]) -> np.ndarray:
        """
        Cosine similarity matrisini hesaplar
        
        Args:
            texts (List[str]): Metinlerin listesi
            
        Returns:
            np.ndarray: Similarity matrisi
        """
        logger.info("Cosine similarity hesaplanıyor...")
        
        # TF-IDF vektörlerini oluştur
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,
            min_df=1,
            max_df=0.95
        )
        
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Cosine similarity hesapla
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        logger.info(f"Similarity matrisi oluşturuldu: {similarity_matrix.shape}")
        return similarity_matrix
    
    def find_similar_pairs(self, similarity_matrix: np.ndarray, news_items: List[Dict]) -> List[Dict]:
        """
        Benzer haber çiftlerini bulur
        
        Args:
            similarity_matrix (np.ndarray): Similarity matrisi
            news_items (List[Dict]): Haber verileri
            
        Returns:
            List[Dict]: Benzer haber çiftleri
        """
        similar_pairs = []
        n_items = len(news_items)
        
        # Üst üçgen matrisi kontrol et (tekrarı önlemek için)
        for i in range(n_items):
            for j in range(i + 1, n_items):
                similarity = similarity_matrix[i][j]
                
                if similarity >= self.similarity_threshold:
                    pair = {
                        'news1': news_items[i],
                        'news2': news_items[j],
                        'similarity_score': similarity,
                        'news1_index': i,
                        'news2_index': j
                    }
                    similar_pairs.append(pair)
        
        # Benzerlik skoruna göre sırala
        similar_pairs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        logger.info(f"{len(similar_pairs)} benzer haber çifti bulundu")
        return similar_pairs
    
    def detect_similarities(self, news_items: List[Dict]) -> Dict:
        """
        Haber benzerliklerini tespit eder
        
        Args:
            news_items (List[Dict]): Haber verilerinin listesi
            
        Returns:
            Dict: Benzerlik analizi sonuçları
        """
        logger.info("Benzerlik tespiti başlatılıyor...")
        
        if len(news_items) < 2:
            logger.warning("Yetersiz haber sayısı, benzerlik analizi yapılamıyor")
            return {
                'similar_pairs': [],
                'source_analysis': {},
                'copy_paste_patterns': {},
                'total_news': len(news_items),
                'similarity_threshold': self.similarity_threshold
            }
        
        try:
            # Metinleri hazırla
            texts = self.prepare_texts(news_items)
            
            # Similarity matrisini hesapla
            similarity_matrix = self.calculate_cosine_similarity(texts)
            
            # Benzer çiftleri bul
            similar_pairs = self.find_similar_pairs(similarity_matrix, news_items)
            
            # Kaynak analizi
            source_analysis = self.analyze_source_similarity(similar_pairs)
            
            # Copy-paste kalıpları
            copy_paste_patterns = self.detect_copy_paste_patterns(similar_pairs)
            
            results = {
                'similar_pairs': similar_pairs,
                'source_analysis': source_analysis,
                'copy_paste_patterns': copy_paste_patterns,
                'similarity_matrix': similarity_matrix.tolist(),
                'total_news': len(news_items),
                'similarity_threshold': self.similarity_threshold,
                'total_similar_pairs': len(similar_pairs)
            }
            
            logger.info("Benzerlik tespiti tamamlandı")
            return results
            
        except Exception as e:
            logger.error(f"Benzerlik tespiti hatası: {e}")
            return {
                'similar_pairs': [],
                'source_analysis': {},
                'copy_paste_patterns': {},
                'total_news': len(news_items),
                'similarity_threshold': self.similarity_threshold,
                'error': str(e)
            }
    
    def analyze_source_similarity(self, similar_pairs: List[Dict]) -> Dict:
        """
        Kaynak bazında benzerlik analizi yapar
        
        Args:
            similar_pairs (List[Dict]): Benzer haber çiftleri
            
        Returns:
            Dict: Kaynak analizi sonuçları
        """
        source_pairs = {}
        source_counts = {}
        
        for pair in similar_pairs:
            source1 = pair['news1'].get('source', 'Bilinmeyen')
            source2 = pair['news2'].get('source', 'Bilinmeyen')
            
            # Kaynak çiftini oluştur (sıralı)
            source_pair = tuple(sorted([source1, source2]))
            
            if source_pair not in source_pairs:
                source_pairs[source_pair] = []
            source_pairs[source_pair].append(pair)
            
            # Tekil kaynak sayılarını güncelle
            for source in [source1, source2]:
                if source not in source_counts:
                    source_counts[source] = 0
                source_counts[source] += 1
        
        # Kaynak çiftlerini analiz et
        source_analysis = {}
        for source_pair, pairs in source_pairs.items():
            avg_similarity = np.mean([p['similarity_score'] for p in pairs])
            source_analysis[source_pair] = {
                'count': len(pairs),
                'avg_similarity': avg_similarity,
                'pairs': pairs
            }
        
        return {
            'source_pairs': source_analysis,
            'source_counts': source_counts,
            'total_similar_pairs': len(similar_pairs)
        }
    
    def detect_copy_paste_patterns(self, similar_pairs: List[Dict]) -> Dict:
        """
        Copy-paste habercilik kalıplarını tespit eder
        
        Args:
            similar_pairs (List[Dict]): Benzer haber çiftleri
            
        Returns:
            Dict: Copy-paste analizi sonuçları
        """
        patterns = {
            'exact_matches': [],      # Tam eşleşmeler
            'high_similarity': [],    # Yüksek benzerlik
            'moderate_similarity': [], # Orta benzerlik
            'source_patterns': {},    # Kaynak kalıpları
            'time_patterns': {}       # Zaman kalıpları
        }
        
        for pair in similar_pairs:
            similarity = pair['similarity_score']
            
            # Benzerlik seviyesine göre kategorize et
            if similarity >= 0.95:
                patterns['exact_matches'].append(pair)
            elif similarity >= 0.8:
                patterns['high_similarity'].append(pair)
            elif similarity >= 0.7:
                patterns['moderate_similarity'].append(pair)
            
            # Kaynak kalıplarını analiz et
            source1 = pair['news1'].get('source', '')
            source2 = pair['news2'].get('source', '')
            
            if source1 != source2:  # Farklı kaynaklar arası
                source_key = f"{source1} ↔ {source2}"
                if source_key not in patterns['source_patterns']:
                    patterns['source_patterns'][source_key] = []
                patterns['source_patterns'][source_key].append(pair)
        
        return patterns
    
    def generate_similarity_report(self, similar_pairs: List[Dict], analysis_results: Dict) -> str:
        """
        Benzerlik analizi raporu oluşturur
        
        Args:
            similar_pairs (List[Dict]): Benzer haber çiftleri
            analysis_results (Dict): Analiz sonuçları
            
        Returns:
            str: Rapor metni
        """
        report = []
        report.append("=== BENZERLİK VE COPY-PASTE ANALİZİ RAPORU ===")
        report.append(f"Toplam Haber Sayısı: {analysis_results.get('total_news', 0)}")
        report.append(f"Benzerlik Eşiği: {analysis_results.get('similarity_threshold', 0.7)}")
        report.append(f"Tespit Edilen Benzer Çift: {len(similar_pairs)}")
        
        # Benzerlik seviyeleri
        if 'copy_paste_patterns' in analysis_results:
            patterns = analysis_results['copy_paste_patterns']
            report.append(f"\n📊 Benzerlik Seviyeleri:")
            report.append(f"  - Tam Eşleşme (≥0.95): {len(patterns.get('exact_matches', []))}")
            report.append(f"  - Yüksek Benzerlik (≥0.8): {len(patterns.get('high_similarity', []))}")
            report.append(f"  - Orta Benzerlik (≥0.7): {len(patterns.get('moderate_similarity', []))}")
        
        # Kaynak analizi
        if 'source_analysis' in analysis_results:
            source_analysis = analysis_results['source_analysis']
            source_pairs = source_analysis.get('source_pairs', {})
            
            if source_pairs:
                report.append(f"\n📰 Kaynak Bazında Benzerlik:")
                for source_pair, data in list(source_pairs.items())[:5]:  # İlk 5
                    sources = " ↔ ".join(source_pair)
                    report.append(f"  - {sources}: {data['count']} çift (ort. {data['avg_similarity']:.3f})")
        
        # En benzer haberler
        if similar_pairs:
            report.append(f"\n🔍 En Benzer Haberler:")
            for i, pair in enumerate(similar_pairs[:3], 1):
                title1 = pair['news1'].get('title', '')[:50]
                title2 = pair['news2'].get('title', '')[:50]
                similarity = pair['similarity_score']
                report.append(f"  {i}. Benzerlik: {similarity:.3f}")
                report.append(f"     Haber 1: {title1}...")
                report.append(f"     Haber 2: {title2}...")
        
        return "\n".join(report)
    
    def analyze_similarity(self, news_items: List[Dict]) -> Dict:
        """
        Kapsamlı benzerlik analizi yapar
        
        Args:
            news_items (List[Dict]): Haber verilerinin listesi
            
        Returns:
            Dict: Analiz sonuçları
        """
        logger.info("Kapsamlı benzerlik analizi başlatılıyor...")
        
        # Benzerlik tespiti
        similarity_results = self.detect_similarities(news_items)
        
        # Rapor oluştur
        report = self.generate_similarity_report(
            similarity_results.get('similar_pairs', []),
            similarity_results
        )
        
        results = {
            **similarity_results,
            'report': report
        }
        
        logger.info("Kapsamlı benzerlik analizi tamamlandı")
        return results

# Test için örnek kullanım
if __name__ == "__main__":
    # Örnek haber verileri
    sample_news = [
        {
            'title': 'Ekonomi büyüme hedefi revize edildi',
            'summary': 'Bakan açıklama yaptı',
            'source': 'https://example1.com'
        },
        {
            'title': 'Ekonomi büyüme hedefi güncellendi',
            'summary': 'Bakan açıklama yaptı',
            'source': 'https://example2.com'
        },
        {
            'title': 'Spor haberleri',
            'summary': 'Futbol maç sonuçları',
            'source': 'https://example3.com'
        }
    ]
    
    detector = SimilarityDetector(similarity_threshold=0.6)
    results = detector.detect_similarities(sample_news)
    
    print("Benzerlik analizi sonuçları:")
    print(f"Toplam haber: {results['total_news']}")
    print(f"Benzer çift sayısı: {results['total_similar_pairs']}")
    
    if results['similar_pairs']:
        print("\nEn benzer haberler:")
        for pair in results['similar_pairs'][:2]:
            print(f"Benzerlik: {pair['similarity_score']:.3f}")
            print(f"  - {pair['news1']['title']}")
            print(f"  - {pair['news2']['title']}") 