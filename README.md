# 📰 Haber Analizi Sistemi

Gelişmiş RSS tabanlı haber analizi ve görselleştirme platformu.

## 🚀 Hızlı Başlangıç

### Ana Menü
```bash
quick_start.bat
```

### Direkt Başlatma
```bash
# Tam analiz çalıştır
start_analysis.bat

# Dashboard başlat
start_dashboard.bat

# Otomatik zamanlayıcı
start_scheduler.bat

# Hızlı başlat
quick_start.bat
```

## 📁 Proje Yapısı

```
EntegreOtomasyon/
├── src/
│   ├── main.py                 # Ana analiz sistemi
│   ├── dashboard.py            # Streamlit dashboard
│   ├── rss_collector.py        # RSS veri toplayıcı
│   ├── database.py             # Veritabanı yönetimi
│   ├── text_processor.py       # Metin işleme
│   ├── advanced_analytics.py   # Gelişmiş analizler
│   ├── cooccurrence_analyzer.py # Co-occurrence analizi
│   └── news_database.db        # SQLite veritabanı
├── quick_start.bat             # Ana menü
├── start_analysis.bat          # Analiz başlatıcı
├── start_dashboard.bat         # Dashboard başlatıcı
├── start_scheduler.bat         # Otomatik zamanlayıcı
└── requirements.txt            # Python bağımlılıkları
```

## 🎯 Özellikler

### 📡 RSS Veri Toplama
- **207+ haber** otomatik toplama
- **4 kategori**: gündem, ekonomi, spor, dünya
- **3 kaynak**: Hürriyet, Anadolu Ajansı, BBC Türkçe
- Asenkron veri çekme
- **⏰ Otomatik zamanlayıcı**: Her saat başı toplama
- **💾 Veri kaydetme**: Ham veriler + analiz sonuçları

### 🔤 Metin Analizi
- **6073 toplam kelime** işleme
- **3393 benzersiz kelime** tespiti
- Stopword temizliği
- Kelime frekansı analizi

### 📊 Görselleştirme
- Kelime sıklığı grafikleri
- Kategori dağılımı
- Kaynak karşılaştırması
- Co-occurrence ağları
- Trend analizleri

## 🛠️ Kurulum

1. **Python bağımlılıklarını yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Environment variables ayarlayın:**
```bash
# .env dosyası oluşturun
cp .env.example .env

# API key'inizi .env dosyasına ekleyin
NEWS_API_KEY=your_api_key_here
```

3. **Ana menüyü başlatın:**
```bash
quick_start.bat
```

## 📈 Kullanım

### 1. Tam Analiz
- RSS kaynaklarından haber toplar
- Metin işleme ve analiz yapar
- Sonuçları veritabanına kaydeder

### 2. Dashboard
- Streamlit web arayüzü
- Gerçek zamanlı veri görselleştirme
- İnteraktif grafikler ve tablolar

### 3. Otomatik Zamanlayıcı
- Her saat başı otomatik haber toplama
- Sürekli veri güncelleme
- Arka plan çalışma

### 4. Ham Veri Görüntüleme
- Toplanan ham haber verilerini görüntüleme
- Analiz geçmişi takibi
- CSV formatında veri aktarma

### 5. Sistem Durumu
- Proje durumu kontrolü
- Dosya yapısı görüntüleme
- Kullanım talimatları

## 🔧 Teknik Detaylar

- **Python 3.9+**
- **Streamlit** - Web dashboard
- **SQLite** - Veritabanı
- **Feedparser** - RSS işleme
- **Plotly** - Grafik oluşturma
- **NLTK** - Doğal dil işleme

## 📊 Analiz Sonuçları

### En Sık Kullanılan Kelimeler
1. bir (72)
2. türkiye (28)
3. başkanı (24)
4. yeni (22)
5. milli (18)

### Kategori Dağılımı
- Gündem: 130 haber
- Ekonomi: 30 haber
- Spor: 30 haber
- Dünya: 58 haber

## 🌐 Dashboard Erişimi

Dashboard başlatıldıktan sonra:
- **Local URL**: http://localhost:8501
- **Network URL**: http://192.168.1.37:8501

## 📝 Lisans

Bu proje eğitim ve araştırma amaçlı geliştirilmiştir. 