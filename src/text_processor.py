"""
Metin Ön İşleme Modülü

Bu modül, haber başlıkları ve özetleri üzerinde temel metin temizleme ve ön işleme işlemlerini gerçekleştirir.
"""

import re
import string
from typing import List, Dict
import nltk
from nltk.corpus import stopwords

# nltk stopwords ilk kullanımda indirilmeli
try:
    _ = stopwords.words('turkish')
except LookupError:
    nltk.download('stopwords')

class TextProcessor:
    """Temel metin ön işleme işlemlerini yapan sınıf"""
    def __init__(self, language: str = 'turkish'):
        self.language = language
        self.stopwords = set(stopwords.words(language))
        self.punctuation_table = str.maketrans('', '', string.punctuation)

    def clean_text(self, text: str) -> str:
        """
        Temel metin temizliği uygular
        - Küçük harfe çevirme
        - Noktalama işaretlerini kaldırma
        - Gereksiz boşlukları temizleme
        - Stopword (gereksiz kelime) temizliği
        """
        if not text:
            return ''
        # Küçük harfe çevir
        text = text.lower()
        # Noktalama işaretlerini kaldır
        text = text.translate(self.punctuation_table)
        # Rakamları kaldır
        text = re.sub(r'\d+', '', text)
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()
        # Stopword temizliği
        tokens = text.split()
        tokens = [word for word in tokens if word not in self.stopwords]
        return ' '.join(tokens)

    def process_text(self, text: str) -> str:
        """
        Tek bir metni işler (clean_text ile aynı)
        
        Args:
            text (str): İşlenecek metin
            
        Returns:
            str: İşlenmiş metin
        """
        return self.clean_text(text)

    def get_word_frequencies(self, text: str) -> Dict[str, int]:
        """
        Metindeki kelime frekanslarını hesaplar
        
        Args:
            text (str): Analiz edilecek metin
            
        Returns:
            Dict[str, int]: Kelime-frekans çiftleri
        """
        processed_text = self.process_text(text)
        words = processed_text.split()
        
        word_freq = {}
        for word in words:
            if len(word) > 2:  # 2 karakterden uzun kelimeler
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Frekansa göre sırala
        return dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True))

    def extract_topics(self, text: str) -> Dict:
        """
        Basit konu çıkarımı yapar
        
        Args:
            text (str): Analiz edilecek metin
            
        Returns:
            Dict: Konu analizi sonuçları
        """
        word_freq = self.get_word_frequencies(text)
        
        # En sık kullanılan kelimeleri konu olarak al
        top_words = list(word_freq.keys())[:30]
        
        # Basit konu grupları oluştur
        topics = []
        for i in range(0, len(top_words), 10):
            topic_words = top_words[i:i+10]
            topic_data = []
            for word in topic_words:
                freq = word_freq.get(word, 0)
                topic_data.append(f"('{word}', {freq})")
            topics.append(topic_data)
        
        return {
            'topics': topics,
            'total_topics': len(topics),
            'words_per_topic': 10
        }

    def process_news_item(self, news_item: Dict) -> Dict:
        """
        Bir haber kaydının başlık ve özetini temizler
        """
        news_item = news_item.copy()
        news_item['title_clean'] = self.clean_text(news_item.get('title', ''))
        news_item['summary_clean'] = self.clean_text(news_item.get('summary', ''))
        return news_item

    def process_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """
        Birden fazla haber kaydını topluca işler
        """
        return [self.process_news_item(item) for item in news_list]

# Test için örnek kullanım
if __name__ == "__main__":
    processor = TextProcessor()
    sample_news = {
        'title': 'SON DAKİKA: Ekonomi Bakanı yeni açıklama yaptı! 2024 yılında büyüme hedefi...'
        , 'summary': 'Ekonomi Bakanı, 2024 yılı için büyüme hedeflerinin revize edildiğini duyurdu. Detaylar haberimizde.'
    }
    cleaned = processor.process_news_item(sample_news)
    print("Temizlenmiş Başlık:", cleaned['title_clean'])
    print("Temizlenmiş Özet:", cleaned['summary_clean']) 