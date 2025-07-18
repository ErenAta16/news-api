"""
Network Analizi Modülü

Bu modül, haber metinlerindeki kelimeler arasındaki ilişkileri
network grafikleri olarak görselleştirir ve analiz eder.
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
import pandas as pd
from itertools import combinations
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    """Haber metinlerindeki kelime ilişkilerini analiz eden sınıf"""
    
    def __init__(self, min_cooccurrence: int = 2, max_nodes: int = 50):
        """
        Network analiz ediciyi başlat
        
        Args:
            min_cooccurrence (int): Minimum birlikte geçme sayısı
            max_nodes (int): Maksimum node sayısı
        """
        self.min_cooccurrence = min_cooccurrence
        self.max_nodes = max_nodes
        self.graph = None
        
    def extract_cooccurrences(self, texts: List[str]) -> Dict[Tuple[str, str], int]:
        """
        Metinlerden birlikte geçen kelime çiftlerini çıkarır
        
        Args:
            texts (List[str]): Temizlenmiş metinlerin listesi
            
        Returns:
            Dict[Tuple[str, str], int]: Kelime çiftleri ve birlikte geçme sayıları
        """
        logger.info("Birlikte geçen kelimeler çıkarılıyor...")
        
        cooccurrences = defaultdict(int)
        
        for text in texts:
            words = text.split()
            if len(words) < 2:
                continue
                
            # Kelime çiftlerini oluştur
            for i in range(len(words)):
                for j in range(i + 1, min(i + 3, len(words))):  # 2-3 kelime aralığında
                    word1, word2 = sorted([words[i], words[j]])
                    if word1 != word2:
                        cooccurrences[(word1, word2)] += 1
        
        # Minimum eşiği geçen çiftleri filtrele
        filtered_cooccurrences = {
            pair: count for pair, count in cooccurrences.items() 
            if count >= self.min_cooccurrence
        }
        
        logger.info(f"{len(filtered_cooccurrences)} kelime çifti bulundu")
        return filtered_cooccurrences
    
    def build_network(self, cooccurrences: Dict[Tuple[str, str], int]) -> nx.Graph:
        """
        Network grafiğini oluşturur
        
        Args:
            cooccurrences (Dict[Tuple[str, str], int]): Kelime çiftleri
            
        Returns:
            nx.Graph: Network grafiği
        """
        logger.info("Network grafiği oluşturuluyor...")
        
        # Grafiği oluştur
        G = nx.Graph()
        
        # En sık geçen kelimeleri bul
        word_counts = defaultdict(int)
        for (word1, word2), count in cooccurrences.items():
            word_counts[word1] += count
            word_counts[word2] += count
        
        # En popüler kelimeleri seç
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:self.max_nodes]
        top_word_set = set(word for word, _ in top_words)
        
        # Node'ları ekle
        for word, count in top_words:
            G.add_node(word, weight=count, size=min(count * 2, 50))
        
        # Edge'leri ekle
        for (word1, word2), count in cooccurrences.items():
            if word1 in top_word_set and word2 in top_word_set:
                G.add_edge(word1, word2, weight=count, width=min(count, 10))
        
        self.graph = G
        logger.info(f"Network oluşturuldu: {G.number_of_nodes()} node, {G.number_of_edges()} edge")
        return G
    
    def calculate_network_metrics(self, G: nx.Graph) -> Dict:
        """
        Network metriklerini hesaplar
        
        Args:
            G (nx.Graph): Network grafiği
            
        Returns:
            Dict: Network metrikleri
        """
        metrics = {}
        
        # Temel metrikler
        metrics['num_nodes'] = G.number_of_nodes()
        metrics['num_edges'] = G.number_of_edges()
        metrics['density'] = nx.density(G)
        
        # Merkezilik metrikleri
        if G.number_of_nodes() > 1:
            metrics['degree_centrality'] = nx.degree_centrality(G)
            metrics['betweenness_centrality'] = nx.betweenness_centrality(G)
            metrics['closeness_centrality'] = nx.closeness_centrality(G)
            
            # En merkezi kelimeler
            top_degree = sorted(metrics['degree_centrality'].items(), key=lambda x: x[1], reverse=True)[:10]
            top_betweenness = sorted(metrics['betweenness_centrality'].items(), key=lambda x: x[1], reverse=True)[:10]
            
            metrics['top_degree_words'] = top_degree
            metrics['top_betweenness_words'] = top_betweenness
        
        # Topluluk tespiti
        if G.number_of_nodes() > 2:
            try:
                communities = list(nx.community.greedy_modularity_communities(G))
                metrics['num_communities'] = len(communities)
                metrics['modularity'] = nx.community.modularity(G, communities)
                metrics['communities'] = [list(comm) for comm in communities]
            except:
                metrics['num_communities'] = 1
                metrics['modularity'] = 0
                metrics['communities'] = [list(G.nodes())]
        
        return metrics
    
    def visualize_network(self, G: nx.Graph, metrics: Dict, title: str = "Kelime İlişkileri Network'ü"):
        """
        Network grafiğini görselleştirir
        
        Args:
            G (nx.Graph): Network grafiği
            metrics (Dict): Network metrikleri
            title (str): Grafik başlığı
        """
        plt.figure(figsize=(15, 12))
        
        # Layout hesapla
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
        # Node'ları çiz
        node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
        node_colors = [G.nodes[node]['weight'] for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, 
                              node_size=node_sizes,
                              node_color=node_colors,
                              cmap=plt.cm.viridis,
                              alpha=0.8)
        
        # Edge'leri çiz
        edge_weights = [G[u][v]['width'] for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, 
                              width=edge_weights,
                              alpha=0.6,
                              edge_color='gray')
        
        # Etiketleri çiz
        nx.draw_networkx_labels(G, pos, 
                               font_size=8,
                               font_weight='bold')
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Metrikleri göster
        info_text = f"Node: {metrics['num_nodes']}, Edge: {metrics['num_edges']}, Yoğunluk: {metrics['density']:.3f}"
        if 'num_communities' in metrics:
            info_text += f", Topluluk: {metrics['num_communities']}"
        plt.figtext(0.5, 0.02, info_text, ha='center', fontsize=12)
        
        plt.tight_layout()
        plt.show()
    
    def print_network_summary(self, metrics: Dict):
        """
        Network analizi özetini yazdırır
        
        Args:
            metrics (Dict): Network metrikleri
        """
        print("\n=== NETWORK ANALİZİ ÖZETİ ===")
        print(f"📊 Temel Metrikler:")
        print(f"   Node Sayısı: {metrics['num_nodes']}")
        print(f"   Edge Sayısı: {metrics['num_edges']}")
        print(f"   Yoğunluk: {metrics['density']:.3f}")
        
        if 'num_communities' in metrics:
            print(f"   Topluluk Sayısı: {metrics['num_communities']}")
            print(f"   Modülerlik: {metrics['modularity']:.3f}")
        
        if 'top_degree_words' in metrics:
            print(f"\n🏆 En Merkezi Kelimeler (Derece):")
            for i, (word, centrality) in enumerate(metrics['top_degree_words'][:5], 1):
                print(f"   {i}. {word}: {centrality:.3f}")
        
        if 'top_betweenness_words' in metrics:
            print(f"\n🌐 En Köprü Kelimeler (Betweenness):")
            for i, (word, centrality) in enumerate(metrics['top_betweenness_words'][:5], 1):
                print(f"   {i}. {word}: {centrality:.3f}")
        
        if 'communities' in metrics:
            print(f"\n👥 Kelime Toplulukları:")
            for i, community in enumerate(metrics['communities'][:3], 1):
                words = community[:5]  # İlk 5 kelime
                print(f"   Topluluk {i}: {', '.join(words)}...")
    
    def analyze_networks(self, texts: List[str]) -> Dict:
        """
        Alias: analyze_network fonksiyonunu ana akış ile uyumlu şekilde çağırır
        """
        return self.analyze_network(texts)

    def analyze_network(self, texts: List[str]) -> Dict:
        """
        Metinler üzerinden network analizi yapar
        Args:
            texts (List[str]): Temizlenmiş metinler
        Returns:
            Dict: Network analiz sonuçları
        """
        logger.info("Network analizi başlatılıyor...")
        cooccurrences = self.extract_cooccurrences(texts)
        G = self.build_network(cooccurrences)
        metrics = self.calculate_network_metrics(G)
        results = {
            'cooccurrences': cooccurrences,
            'graph': G,
            'metrics': metrics
        }
        logger.info("Network analizi tamamlandı")
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
    
    # Network analizi
    analyzer = NetworkAnalyzer(min_cooccurrence=1, max_nodes=20)
    results = analyzer.analyze_network(sample_texts) 