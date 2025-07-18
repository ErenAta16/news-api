import sqlite3
import pandas as pd
from datetime import datetime
import json

def view_raw_news_data():
    """Ham haber verilerini görüntüler"""
    
    try:
        # Veritabanına bağlan
        conn = sqlite3.connect('news_database.db')
        
        # Ham haber verilerini çek
        query = '''
            SELECT 
                id,
                collection_time,
                title,
                summary,
                source,
                category,
                published_date,
                created_at
            FROM raw_news_data 
            ORDER BY collection_time DESC, created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("❌ Henüz ham haber verisi bulunmuyor!")
            print("💡 Zamanlayıcıyı çalıştırarak veri toplayabilirsiniz.")
            return
        
        print("📊 HAM HABER VERİLERİ")
        print("=" * 80)
        print(f"📈 Toplam Kayıt: {len(df)}")
        print(f"📅 İlk Toplama: {df['collection_time'].min()}")
        print(f"📅 Son Toplama: {df['collection_time'].max()}")
        print()
        
        # Kaynak dağılımı
        print("📡 KAYNAK DAĞILIMI:")
        source_counts = df['source'].value_counts()
        for source, count in source_counts.items():
            print(f"   {source}: {count} haber")
        print()
        
        # Kategori dağılımı
        print("🏷️ KATEGORİ DAĞILIMI:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"   {category}: {count} haber")
        print()
        
        # Toplama zamanları
        print("⏰ TOPLAMA ZAMANLARI:")
        collection_times = df['collection_time'].value_counts().head(10)
        for time, count in collection_times.items():
            print(f"   {time}: {count} haber")
        print()
        
        # Son 5 haber
        print("📰 SON 5 HABER:")
        recent_news = df.head(5)
        for idx, row in recent_news.iterrows():
            print(f"   {idx+1}. {row['title'][:60]}...")
            print(f"      Kaynak: {row['source']} | Kategori: {row['category']}")
            print(f"      Tarih: {row['collection_time']}")
            print()
        
        # İstatistikler
        print("📊 İSTATİSTİKLER:")
        print(f"   Ortalama başlık uzunluğu: {df['title'].str.len().mean():.1f} karakter")
        print(f"   Ortalama özet uzunluğu: {df['summary'].str.len().mean():.1f} karakter")
        print(f"   Benzersiz kaynak sayısı: {df['source'].nunique()}")
        print(f"   Benzersiz kategori sayısı: {df['category'].nunique()}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def export_raw_data_to_csv():
    """Ham verileri CSV dosyasına aktarır"""
    try:
        conn = sqlite3.connect('news_database.db')
        df = pd.read_sql_query('SELECT * FROM raw_news_data', conn)
        
        if df.empty:
            print("❌ Aktarılacak veri bulunmuyor!")
            return
        
        filename = f"raw_news_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"✅ Veriler {filename} dosyasına aktarıldı!")
        print(f"📊 Toplam {len(df)} kayıt aktarıldı")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Aktarma hatası: {e}")

def view_analysis_history():
    """Analiz geçmişini görüntüler"""
    try:
        conn = sqlite3.connect('news_database.db')
        
        # Analiz geçmişini çek
        query = '''
            SELECT 
                id,
                analysis_data,
                created_at
            FROM analysis_results 
            ORDER BY created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("❌ Henüz analiz sonucu bulunmuyor!")
            return
        
        print("📊 ANALİZ GEÇMİŞİ")
        print("=" * 80)
        print(f"📈 Toplam Analiz: {len(df)}")
        print(f"📅 İlk Analiz: {df['created_at'].min()}")
        print(f"📅 Son Analiz: {df['created_at'].max()}")
        print()
        
        # Son 5 analiz
        print("🔍 SON 5 ANALİZ:")
        for idx, row in df.head(5).iterrows():
            try:
                analysis_data = json.loads(row['analysis_data'])
                metadata = analysis_data.get('metadata', {})
                
                print(f"   {idx+1}. Analiz #{row['id']}")
                print(f"      Tarih: {row['created_at']}")
                print(f"      Haber Sayısı: {metadata.get('total_news', 'N/A')}")
                print(f"      Kaynaklar: {len(metadata.get('sources', []))}")
                print(f"      İşlem Süresi: {metadata.get('processing_time', 'N/A')} saniye")
                print()
                
            except json.JSONDecodeError:
                print(f"   {idx+1}. Analiz #{row['id']} - JSON hatası")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def main():
    """Ana menü"""
    while True:
        print("\n" + "="*60)
        print("📊 HAM VERİ GÖRÜNTÜLEME SİSTEMİ")
        print("="*60)
        print("[1] 📰 Ham Haber Verilerini Görüntüle")
        print("[2] 📊 Analiz Geçmişini Görüntüle")
        print("[3] 💾 Verileri CSV'ye Aktar")
        print("[4] ❌ Çıkış")
        print("="*60)
        
        choice = input("Seçiminizi yapın (1-4): ").strip()
        
        if choice == "1":
            print("\n" + "="*60)
            view_raw_news_data()
        elif choice == "2":
            print("\n" + "="*60)
            view_analysis_history()
        elif choice == "3":
            print("\n" + "="*60)
            export_raw_data_to_csv()
        elif choice == "4":
            print("👋 Görüntüleme sistemi kapatılıyor...")
            break
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main() 