"""
Konu Modelleme Modülü

Bu modül, haber metinlerini LDA (Latent Dirichlet Allocation) kullanarak
otomatik olarak konulara/kategorilere ayırır.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.decomposition import NMF
from typing import List, Dict, Tuple
import pandas as pd
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TopicModeler:
    """LDA ve NMF kullanarak konu modelleme yapan sınıf"""
    
    def __init__(self, n_topics: int = 5, method: str = 'lda'):
        """
        Konu modelleyiciyi başlat
        
        Args:
            n_topics (int): Oluşturulacak konu sayısı
            method (str): 'lda' veya 'nmf' kullanılacak yöntem
        """
        self.n_topics = n_topics
        self.method = method
        self.vectorizer = None
        self.model = None
        self.feature_names = None
        
    def prepare_data(self, texts: List[str], max_features: int = 1000):
        """
        Metinleri TF-IDF vektörlerine dönüştürür
        
        Args:
            texts (List[str]): Temizlenmiş metinlerin listesi
            max_features (int): Maksimum özellik sayısı
        """
        logger.info("Metinler TF-IDF vektörlerine dönüştürülüyor...")
        
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words=None,  # Zaten temizlenmiş metinler
            min_df=2,  # En az 2 dokümanda geçen kelimeler
            max_df=0.95  # %95'ten fazla dokümanda geçen kelimeleri çıkar
        )
        
        # TF-IDF matrisini oluştur
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        logger.info(f"TF-IDF matrisi oluşturuldu: {tfidf_matrix.shape}")
        return tfidf_matrix
    
    def fit_model(self, tfidf_matrix):
        """
        Konu modelini eğitir
        
        Args:
            tfidf_matrix: TF-IDF matrisi
        """
        logger.info(f"{self.method.upper()} konu modeli eğitiliyor...")
        
        if self.method == 'lda':
            self.model = LatentDirichletAllocation(
                n_components=self.n_topics,
                random_state=42,
                max_iter=20,
                learning_method='batch'
            )
        elif self.method == 'nmf':
            self.model = NMF(
                n_components=self.n_topics,
                random_state=42,
                max_iter=200
            )
        else:
            raise ValueError("Method must be 'lda' or 'nmf'")
        
        # Modeli eğit
        self.model.fit(tfidf_matrix)
        logger.info("Konu modeli eğitimi tamamlandı")
    
    def get_topics(self, n_words: int = 10) -> List[List[Tuple[str, float]]]:
        """
        Her konu için en önemli kelimeleri döndürür
        
        Args:
            n_words (int): Her konu için döndürülecek kelime sayısı
            
        Returns:
            List[List[Tuple[str, float]]]: Her konu için (kelime, ağırlık) listesi
        """
        if self.model is None:
            raise ValueError("Model henüz eğitilmemiş")
        
        topics = []
        feature_names = self.vectorizer.get_feature_names_out()
        
        for topic_idx, topic in enumerate(self.model.components_):
            # En yüksek ağırlıklı kelimeleri al
            top_words_idx = topic.argsort()[:-n_words-1:-1]
            top_words = [(feature_names[i], topic[i]) for i in top_words_idx]
            topics.append(top_words)
        
        return topics
    
    def assign_topics_to_documents(self, texts: List[str]) -> List[int]:
        """
        Her dokümana en uygun konuyu atar
        
        Args:
            texts (List[str]): Doküman metinleri
            
        Returns:
            List[int]: Her doküman için atanan konu indeksi
        """
        if self.model is None or self.vectorizer is None:
            raise ValueError("Model henüz eğitilmemiş")
        
        # Dokümanları vektörize et
        tfidf_matrix = self.vectorizer.transform(texts)
        
        # Konu dağılımlarını hesapla
        topic_distributions = self.model.transform(tfidf_matrix)
        
        # En yüksek olasılıklı konuyu seç
        assigned_topics = topic_distributions.argmax(axis=1)
        
        return assigned_topics.tolist()
    
    def model_topics(self, texts: List[str]) -> Dict:
        """
        Konu modelleme yapar
        
        Args:
            texts (List[str]): Temizlenmiş metinlerin listesi
            
        Returns:
            Dict: Konu modelleme sonuçları
        """
        logger.info("Konu modelleme başlatılıyor...")
        
        if len(texts) < 2:
            logger.warning("Yetersiz metin sayısı, konu modelleme yapılamıyor")
            return {
                'topics': [],
                'topic_counts': {},
                'assigned_topics': [],
                'method': self.method,
                'n_topics': 0
            }
        
        try:
            # Veriyi hazırla
            tfidf_matrix = self.prepare_data(texts)
            
            # Modeli eğit
            self.fit_model(tfidf_matrix)
            
            # Konuları al
            topics = self.get_topics()
            
            # Dokümanlara konu ata
            assigned_topics = self.assign_topics_to_documents(texts)
            
            # Konu dağılımını hesapla
            topic_counts = pd.Series(assigned_topics).value_counts().to_dict()
            
            results = {
                'topics': topics,
                'topic_counts': topic_counts,
                'assigned_topics': assigned_topics,
                'method': self.method,
                'n_topics': self.n_topics,
                'total_documents': len(texts)
            }
            
            logger.info("Konu modelleme tamamlandı")
            return results
            
        except Exception as e:
            logger.error(f"Konu modelleme hatası: {e}")
            return {
                'topics': [],
                'topic_counts': {},
                'assigned_topics': [],
                'method': self.method,
                'n_topics': 0,
                'error': str(e)
            }
    
    def analyze_topics(self, texts: List[str], news_items: List[Dict]) -> Dict:
        """
        Konu analizi yapar ve sonuçları döndürür
        
        Args:
            texts (List[str]): Temizlenmiş metinler
            news_items (List[Dict]): Orijinal haber verileri
            
        Returns:
            Dict: Analiz sonuçları
        """
        logger.info("Konu analizi başlatılıyor...")
        
        # Veriyi hazırla
        tfidf_matrix = self.prepare_data(texts)
        
        # Modeli eğit
        self.fit_model(tfidf_matrix)
        
        # Konuları al
        topics = self.get_topics()
        
        # Dokümanlara konu ata
        assigned_topics = self.assign_topics_to_documents(texts)
        
        # Konu dağılımını hesapla
        topic_counts = pd.Series(assigned_topics).value_counts().to_dict()
        
        # Her konu için örnek haberler
        topic_examples = {}
        for topic_idx in range(self.n_topics):
            topic_news = [news_items[i] for i, assigned in enumerate(assigned_topics) if assigned == topic_idx]
            topic_examples[topic_idx] = topic_news[:3]  # İlk 3 örnek
        
        results = {
            'topics': topics,
            'topic_counts': topic_counts,
            'assigned_topics': assigned_topics,
            'topic_examples': topic_examples,
            'method': self.method,
            'n_topics': self.n_topics
        }
        
        logger.info("Konu analizi tamamlandı")
        return results
    
    def print_topic_summary(self, results: Dict):
        """
        Konu analizi sonuçlarını yazdırır
        """
        print(f"\n=== {results['method'].upper()} Konu Analizi Sonuçları ===")
        print(f"Toplam Konu Sayısı: {results['n_topics']}")
        
        print("\n📊 Konu Dağılımı:")
        for topic_idx, count in results['topic_counts'].items():
            print(f"Konu {topic_idx}: {count} haber")
        
        print("\n🏷️ Konu İçerikleri:")
        for topic_idx, topic_words in enumerate(results['topics']):
            print(f"\nKonu {topic_idx}:")
            words_str = ", ".join([f"{word} ({weight:.3f})" for word, weight in topic_words[:5]])
            print(f"  Anahtar kelimeler: {words_str}")
            
            # Örnek haberler
            if topic_idx in results['topic_examples']:
                examples = results['topic_examples'][topic_idx]
                print(f"  Örnek haberler:")
                for i, example in enumerate(examples, 1):
                    title = example.get('title', '')[:60]
                    print(f"    {i}. {title}...")

# Test için örnek kullanım
if __name__ == "__main__":
    # Örnek metinler
    sample_texts = [
        "ekonomi büyüme hedef revize edildi bakan açıklama",
        "bakan ekonomi büyüme açıklama yaptı",
        "büyüme hedef ekonomi 2024",
        "siyaset cumhurbaşkanı toplantı karar",
        "cumhurbaşkanı siyaset karar aldı",
        "spor futbol maç sonuç galibiyet",
        "futbol spor maç sonuç",
        "hava durumu sıcaklık yağış",
        "sıcaklık hava durumu artış"
    ]
    
    # LDA konu modelleme
    lda_modeler = TopicModeler(n_topics=3, method='lda')
    lda_results = lda_modeler.model_topics(sample_texts)
    
    print("LDA Konu Modelleme Sonuçları:")
    print(lda_results)
    
    # NMF konu modelleme
    nmf_modeler = TopicModeler(n_topics=3, method='nmf')
    nmf_results = nmf_modeler.model_topics(sample_texts)
    
    print("\nNMF Konu Modelleme Sonuçları:")
    print(nmf_results) 