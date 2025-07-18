"""
Kelime Sıklığı Analizi ve Anahtar Kelime Bulutu Modülü

Bu modül, temizlenmiş haber başlıkları ve özetleri üzerinde
kelime sıklığı analizi yapar ve anahtar kelime bulutu oluşturur.
"""

from collections import Counter
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordAnalyzer:
    """Kelime sıklığı ve anahtar kelime bulutu analizleri için sınıf"""
    
    def __init__(self):
        """WordAnalyzer'ı başlat"""
        pass

    def get_word_frequencies(self, texts: List[str], top_n: int = 30) -> List[Tuple[str, int]]:
        """
        Kelime sıklıklarını hesaplar
        Args:
            texts (List[str]): Temizlenmiş metinlerin listesi
            top_n (int): En sık geçen ilk N kelime
        Returns:
            List[Tuple[str, int]]: (kelime, frekans) çiftleri
        """
        all_words = []
        for text in texts:
            all_words.extend(text.split())
        counter = Counter(all_words)
        return counter.most_common(top_n)
    
    def analyze_word_frequency(self, texts: List[str], top_n: int = 30) -> Dict:
        """
        Kelime sıklığı analizi yapar
        
        Args:
            texts (List[str]): Temizlenmiş metinlerin listesi
            top_n (int): En sık geçen ilk N kelime
            
        Returns:
            Dict: Kelime sıklığı analiz sonuçları
        """
        logger.info("Kelime sıklığı analizi başlatılıyor...")
        
        # Kelime sıklıklarını hesapla
        word_freqs = self.get_word_frequencies(texts, top_n)
        
        # Toplam kelime sayısı
        total_words = sum(freq for _, freq in word_freqs)
        
        # Kelime uzunluğu analizi
        word_lengths = []
        for text in texts:
            words = text.split()
            word_lengths.extend([len(word) for word in words])
        
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        
        # Benzersiz kelime sayısı
        unique_words = len(set(word for text in texts for word in text.split()))
        
        results = {
            'word_frequencies': word_freqs,
            'total_words': total_words,
            'unique_words': unique_words,
            'avg_word_length': round(avg_word_length, 2),
            'top_words': [word for word, _ in word_freqs[:10]],
            'top_frequencies': [freq for _, freq in word_freqs[:10]]
        }
        
        logger.info(f"Kelime sıklığı analizi tamamlandı: {len(word_freqs)} kelime analiz edildi")
        return results

    def generate_wordcloud_data(self, texts: List[str]) -> Dict:
        """
        Anahtar kelime bulutu için veri oluşturur
        
        Args:
            texts (List[str]): Temizlenmiş metinlerin listesi
            
        Returns:
            Dict: Wordcloud verileri
        """
        logger.info("Wordcloud verisi oluşturuluyor...")
        
        # Tüm metinleri birleştir
        combined_text = ' '.join(texts)
        
        # Kelime sıklıklarını hesapla
        word_freqs = self.get_word_frequencies(texts, top_n=50)
        
        # Wordcloud için frekans sözlüğü
        wordcloud_freqs = {word: freq for word, freq in word_freqs}
        
        # En sık geçen kelimeler (görselleştirme için)
        top_words = [word for word, _ in word_freqs[:20]]
        top_freqs = [freq for _, freq in word_freqs[:20]]
        
        results = {
            'combined_text': combined_text,
            'word_frequencies': wordcloud_freqs,
            'top_words': top_words,
            'top_frequencies': top_freqs,
            'total_unique_words': len(wordcloud_freqs)
        }
        
        logger.info("Wordcloud verisi oluşturuldu")
        return results

    def plot_word_frequencies(self, word_freqs: List[Tuple[str, int]], title: str = "Word Frequencies"):
        """
        Kelime sıklıklarını bar chart olarak görselleştirir
        """
        words, counts = zip(*word_freqs)
        plt.figure(figsize=(12, 6))
        # Seaborn uyarısını düzeltmek için hue parametresi ekledim
        sns.barplot(x=list(counts), y=list(words), orient='h', palette='viridis', hue=list(words), legend=False)
        plt.title(title)
        plt.xlabel('Frequency')
        plt.ylabel('Word')
        plt.tight_layout()
        plt.show()

    def generate_wordcloud(self, texts: List[str], title: str = "Word Cloud"):
        """
        Anahtar kelime bulutu oluşturur ve görselleştirir
        """
        text = ' '.join(texts)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title)
        plt.tight_layout()
        plt.show()

# Test için örnek kullanım
if __name__ == "__main__":
    sample_texts = [
        "ekonomi büyüme hedef revize edildi",
        "bakan ekonomi büyüme açıklama yaptı",
        "büyüme hedef ekonomi 2024"
    ]
    analyzer = WordAnalyzer()
    
    # Kelime sıklığı analizi
    freq_analysis = analyzer.analyze_word_frequency(sample_texts, top_n=5)
    print("Kelime sıklığı analizi:", freq_analysis)
    
    # Wordcloud verisi
    wordcloud_data = analyzer.generate_wordcloud_data(sample_texts)
    print("Wordcloud verisi:", wordcloud_data)
    
    # Görselleştirme
    freqs = analyzer.get_word_frequencies(sample_texts, top_n=5)
    print("En sık geçen kelimeler:", freqs)
    analyzer.plot_word_frequencies(freqs, title="En Sık Geçen Kelimeler")
    analyzer.generate_wordcloud(sample_texts, title="Anahtar Kelime Bulutu") 