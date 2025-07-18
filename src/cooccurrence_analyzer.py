"""
Co-Occurrence ve Ağ Analizi Modülü

Bu modül, haber metinlerindeki kelimeler arası ilişkileri analiz eder:
- Co-occurrence (birlikte geçme) analizi
- Ağ grafiği ve kritik düğüm tespiti
- Kelime çiftleri ve üçlüleri
- Ağ metrikleri ve topluluk tespiti
"""

import networkx as nx
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from itertools import combinations
from typing import List, Dict, Tuple, Set
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CooccurrenceAnalyzer:
    """Co-occurrence ve ağ analizi sınıfı"""
    
    def __init__(self, window_size: int = 3, min_cooccurrence: int = 2):
        """
        Co-occurrence analiz ediciyi başlat
        
        Args:
            window_size (int): Birlikte geçme penceresi (kaç kelime aralığında)
            min_cooccurrence (int): Minimum birlikte geçme sayısı
        """
        self.window_size = window_size
        self.min_cooccurrence = min_cooccurrence
        self.graph = None
        
    def extract_cooccurrences(self, texts: List[str]) -> Dict[Tuple[str, str], int]:
        """
        Metinlerden co-occurrence çiftlerini çıkarır
        
        Args:
            texts (List[str]): Temizlenmiş metinlerin listesi
            
        Returns:
            Dict[Tuple[str, str], int]: Kelime çiftleri ve birlikte geçme sayıları
        """
        logger.info("Co-occurrence çiftleri çıkarılıyor...")
        
        cooccurrences = defaultdict(int)
        
        for text in texts:
            words = text.split()
            if len(words) < 2:
                continue
            
            # Belirtilen pencere boyutunda kelime çiftlerini oluştur
            for i in range(len(words)):
                for j in range(i + 1, min(i + self.window_size + 1, len(words))):
                    word1, word2 = sorted([words[i], words[j]])
                    if word1 != word2 and len(word1) > 2 and len(word2) > 2:  # Kısa kelimeleri filtrele
                        cooccurrences[(word1, word2)] += 1
        
        # Minimum eşiği geçen çiftleri filtrele
        filtered_cooccurrences = {
            pair: count for pair, count in cooccurrences.items() 
            if count >= self.min_cooccurrence
        }
        
        logger.info(f"{len(filtered_cooccurrences)} co-occurrence çifti bulundu")
        return filtered_cooccurrences
    
    def extract_trigrams(self, texts: List[str]) -> Dict[Tuple[str, str, str], int]:
        """
        Metinlerden trigram (üçlü kelime grupları) çıkarır
        
        Args:
            texts (List[str]): Temizlenmiş metinlerin listesi
            
        Returns:
            Dict[Tuple[str, str, str], int]: Trigramlar ve sayıları
        """
        logger.info("Trigram analizi başlatılıyor...")
        
        trigrams = defaultdict(int)
        
        for text in texts:
            words = text.split()
            if len(words) < 3:
                continue
            
            # Ardışık üçlü kelime grupları
            for i in range(len(words) - 2):
                trigram = tuple(words[i:i+3])
                if all(len(word) > 2 for word in trigram):  # Kısa kelimeleri filtrele
                    trigrams[trigram] += 1
        
        # En sık geçen trigramları döndür
        top_trigrams = dict(sorted(trigrams.items(), key=lambda x: x[1], reverse=True)[:20])
        
        logger.info(f"{len(top_trigrams)} trigram bulundu")
        return top_trigrams
    
    def build_network(self, cooccurrences: Dict[Tuple[str, str], int], 
                     min_weight: int = 3, max_nodes: int = 50) -> nx.Graph:
        """
        Co-occurrence verilerinden ağ grafiği oluşturur
        
        Args:
            cooccurrences (Dict[Tuple[str, str], int]): Co-occurrence çiftleri
            min_weight (int): Minimum ağırlık eşiği
            max_nodes (int): Maksimum node sayısı
            
        Returns:
            nx.Graph: Ağ grafiği
        """
        logger.info("Ağ grafiği oluşturuluyor...")
        
        # Grafiği oluştur
        G = nx.Graph()
        
        # En sık geçen kelimeleri bul
        word_counts = defaultdict(int)
        for (word1, word2), count in cooccurrences.items():
            word_counts[word1] += count
            word_counts[word2] += count
        
        # En popüler kelimeleri seç
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
        top_word_set = set(word for word, _ in top_words)
        
        # Node'ları ekle
        for word, count in top_words:
            G.add_node(word, weight=count, size=min(count * 2, 50))
        
        # Edge'leri ekle (minimum ağırlık eşiği ile)
        for (word1, word2), count in cooccurrences.items():
            if (word1 in top_word_set and word2 in top_word_set and 
                count >= min_weight):
                G.add_edge(word1, word2, weight=count, width=min(count, 10))
        
        self.graph = G
        logger.info(f"Ağ oluşturuldu: {G.number_of_nodes()} node, {G.number_of_edges()} edge")
        return G
    
    def analyze_network_metrics(self, G: nx.Graph) -> Dict:
        """
        Ağ metriklerini hesaplar
        
        Args:
            G (nx.Graph): Ağ grafiği
            
        Returns:
            Dict: Ağ metrikleri
        """
        metrics = {}
        
        # Temel metrikler
        metrics['num_nodes'] = G.number_of_nodes()
        metrics['num_edges'] = G.number_of_edges()
        metrics['density'] = nx.density(G)
        
        if G.number_of_nodes() > 1:
            # Merkezilik metrikleri
            metrics['degree_centrality'] = nx.degree_centrality(G)
            metrics['betweenness_centrality'] = nx.betweenness_centrality(G)
            metrics['closeness_centrality'] = nx.closeness_centrality(G)
            metrics['eigenvector_centrality'] = nx.eigenvector_centrality(G, max_iter=1000)
            
            # En merkezi kelimeler
            top_degree = sorted(metrics['degree_centrality'].items(), key=lambda x: x[1], reverse=True)[:10]
            top_betweenness = sorted(metrics['betweenness_centrality'].items(), key=lambda x: x[1], reverse=True)[:10]
            top_closeness = sorted(metrics['closeness_centrality'].items(), key=lambda x: x[1], reverse=True)[:10]
            top_eigenvector = sorted(metrics['eigenvector_centrality'].items(), key=lambda x: x[1], reverse=True)[:10]
            
            metrics['top_degree_words'] = top_degree
            metrics['top_betweenness_words'] = top_betweenness
            metrics['top_closeness_words'] = top_closeness
            metrics['top_eigenvector_words'] = top_eigenvector
            
            # Kritik düğümler (yüksek merkezilik skorları)
            critical_nodes = set()
            for word, _ in top_degree[:5]:
                critical_nodes.add(word)
            for word, _ in top_betweenness[:5]:
                critical_nodes.add(word)
            
            metrics['critical_nodes'] = list(critical_nodes)
        
        # Topluluk tespiti
        if G.number_of_nodes() > 2:
            try:
                communities = list(nx.community.greedy_modularity_communities(G))
                metrics['num_communities'] = len(communities)
                metrics['modularity'] = nx.community.modularity(G, communities)
                metrics['communities'] = [list(comm) for comm in communities]
                
                # Topluluk analizi
                community_analysis = {}
                for i, community in enumerate(communities):
                    community_nodes = list(community)
                    community_analysis[f'community_{i}'] = {
                        'nodes': community_nodes,
                        'size': len(community_nodes),
                        'avg_degree': np.mean([G.degree(node) for node in community_nodes])
                    }
                metrics['community_analysis'] = community_analysis
                
            except Exception as e:
                logger.warning(f"Topluluk tespiti başarısız: {e}")
                metrics['num_communities'] = 1
                metrics['modularity'] = 0
                metrics['communities'] = [list(G.nodes())]
        
        return metrics
    
    def find_keyword_associations(self, texts: List[str], target_keywords: List[str]) -> Dict:
        """
        Belirli anahtar kelimelerle birlikte geçen kelimeleri bulur
        
        Args:
            texts (List[str]): Metinler
            target_keywords (List[str]): Hedef anahtar kelimeler
            
        Returns:
            Dict: Anahtar kelime ilişkileri
        """
        logger.info("Anahtar kelime ilişkileri analiz ediliyor...")
        
        associations = {}
        
        for keyword in target_keywords:
            keyword_associations = defaultdict(int)
            
            for text in texts:
                if keyword.lower() in text.lower():
                    words = text.split()
                    # Hedef kelime ile aynı cümlede geçen diğer kelimeler
                    for word in words:
                        if word.lower() != keyword.lower() and len(word) > 2:
                            keyword_associations[word.lower()] += 1
            
            # En sık birlikte geçen kelimeler
            top_associations = sorted(keyword_associations.items(), 
                                    key=lambda x: x[1], reverse=True)[:10]
            associations[keyword] = top_associations
        
        return associations
    
    def analyze_temporal_cooccurrences(self, news_items: List[Dict]) -> Dict:
        """
        Zaman içinde co-occurrence değişimlerini analiz eder
        
        Args:
            news_items (List[Dict]): Haber verileri
            
        Returns:
            Dict: Zaman bazlı co-occurrence analizi
        """
        logger.info("Zaman bazlı co-occurrence analizi başlatılıyor...")
        
        # Tarihe göre haberleri grupla
        df = pd.DataFrame(news_items)
        df['published'] = pd.to_datetime(df['published'])
        df['date'] = df['published'].dt.date
        
        temporal_cooccurrences = {}
        
        for date in df['date'].unique():
            daily_news = df[df['date'] == date]
            daily_texts = [f"{row['title']} {row['summary']}" for _, row in daily_news.iterrows()]
            
            # Günlük co-occurrence analizi
            daily_cooccurrences = self.extract_cooccurrences(daily_texts)
            temporal_cooccurrences[date] = daily_cooccurrences
        
        # En sık değişen co-occurrence çiftleri
        all_pairs = set()
        for date_cooccurrences in temporal_cooccurrences.values():
            all_pairs.update(date_cooccurrences.keys())
        
        pair_trends = {}
        for pair in all_pairs:
            pair_trend = []
            for date in sorted(temporal_cooccurrences.keys()):
                count = temporal_cooccurrences[date].get(pair, 0)
                pair_trend.append(count)
            pair_trends[pair] = pair_trend
        
        results = {
            'temporal_cooccurrences': temporal_cooccurrences,
            'pair_trends': pair_trends,
            'total_pairs': len(all_pairs)
        }
        
        logger.info("Zaman bazlı co-occurrence analizi tamamlandı")
        return results
    
    def generate_cooccurrence_report(self, cooccurrences: Dict[Tuple[str, str], int], 
                                   metrics: Dict) -> str:
        """
        Co-occurrence analizi raporu oluşturur
        
        Args:
            cooccurrences (Dict[Tuple[str, str], int]): Co-occurrence çiftleri
            metrics (Dict): Ağ metrikleri
            
        Returns:
            str: Rapor metni
        """
        report = []
        report.append("=== CO-OCCURRENCE VE AĞ ANALİZİ RAPORU ===")
        report.append(f"Toplam Co-occurrence Çifti: {len(cooccurrences)}")
        report.append(f"Node Sayısı: {metrics['num_nodes']}")
        report.append(f"Edge Sayısı: {metrics['num_edges']}")
        report.append(f"Ağ Yoğunluğu: {metrics['density']:.3f}")
        
        if 'num_communities' in metrics:
            report.append(f"Topluluk Sayısı: {metrics['num_communities']}")
            report.append(f"Modülerlik: {metrics['modularity']:.3f}")
        
        # En güçlü co-occurrence çiftleri
        top_pairs = sorted(cooccurrences.items(), key=lambda x: x[1], reverse=True)[:10]
        report.append(f"\n🔗 En Güçlü Co-occurrence Çiftleri:")
        for i, ((word1, word2), count) in enumerate(top_pairs, 1):
            report.append(f"{i}. {word1} ↔ {word2}: {count} kez")
        
        # Kritik düğümler
        if 'critical_nodes' in metrics:
            report.append(f"\n⭐ Kritik Düğümler:")
            for node in metrics['critical_nodes']:
                report.append(f"  - {node}")
        
        # Topluluklar
        if 'communities' in metrics:
            report.append(f"\n👥 Kelime Toplulukları:")
            for i, community in enumerate(metrics['communities'][:3], 1):
                words = community[:5]  # İlk 5 kelime
                report.append(f"  Topluluk {i}: {', '.join(words)}...")
        
        return "\n".join(report)
    
    def analyze_cooccurrences(self, texts: List[str], target_keywords: List[str] = None) -> Dict:
        """
        Kapsamlı co-occurrence analizi yapar
        
        Args:
            texts (List[str]): Temizlenmiş metinler
            target_keywords (List[str]): Analiz edilecek hedef kelimeler
            
        Returns:
            Dict: Analiz sonuçları
        """
        logger.info("Co-occurrence analizi başlatılıyor...")
        
        # Co-occurrence çiftlerini çıkar
        cooccurrences = self.extract_cooccurrences(texts)
        
        # Trigram analizi
        trigrams = self.extract_trigrams(texts)
        
        # Ağ grafiği oluştur
        G = self.build_network(cooccurrences)
        
        # Ağ metriklerini hesapla
        metrics = self.analyze_network_metrics(G)
        
        # Anahtar kelime ilişkileri
        if target_keywords:
            associations = self.find_keyword_associations(texts, target_keywords)
        else:
            associations = {}
        
        # Rapor oluştur
        report = self.generate_cooccurrence_report(cooccurrences, metrics)
        
        results = {
            'cooccurrences': cooccurrences,
            'trigrams': trigrams,
            'graph': G,
            'metrics': metrics,
            'associations': associations,
            'report': report,
            'num_texts': len(texts)
        }
        
        logger.info("Co-occurrence analizi tamamlandı")
        return results

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
    
    # Co-occurrence analizi
    analyzer = CooccurrenceAnalyzer(window_size=3, min_cooccurrence=1)
    results = analyzer.analyze_cooccurrences(sample_texts, target_keywords=['ekonomi', 'siyaset'])
    
    print(results['report']) 