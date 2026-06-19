import os
import json
import requests
import pandas as pd
from datetime import datetime

class MapsIntelligenceEngine:
    def __init__(self):
        # Güvenli ortam değişkeninden API anahtarını alıyoruz
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("[HATA] GOOGLE_MAPS_API_KEY bulunamadı! Güvenlik protokolü gereği işlem durduruldu.")
        
        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def search_target_companies(self, query: str, region: str):
        """Belirlenen bölgede ve sektörde kurumsal firmaları tarar."""
        print(f"[BİLGİ] {region} bölgesinde '{query}' için tarama başlatılıyor...")
        
        params = {
            'query': f"{query} in {region}",
            'key': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            print(f"[HATA] API isteği başarısız oldu: {response.status_code}")
            return []

        results = response.json().get('results', [])
        cleaned_leads = []

        for place in results:
            # Filtreleme: Ciddi B2B firmaların analizi için detay taraması yapılıyor
            place_id = place.get('place_id')
            detail_data = self.get_company_details(place_id)
            
            # Basit perakende noktalarını elemek için filtre (Örn: Tesisatçı dükkanları vb.)
            types = place.get('types', [])
            if 'home_goods_store' in types or 'plumber' in types:
                continue  # Perakendecileri atla, doğrudan endüstriyel odak
                
            lead = {
                'company_name': place.get('name'),
                'address': place.get('formatted_address'),
                'google_rating': place.get('rating', 0),
                'total_reviews': place.get('user_ratings_total', 0),
                'website': detail_data.get('website', 'YOK'),
                'phone': detail_data.get('international_phone_number', 'YOK'),
                'place_id': place_id,
                'extracted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'customs_verified': "PENDING" # 2. Modülde gümrükle eşleşecek
            }
            cleaned_leads.append(lead)
            
        return cleaned_leads

    def get_company_details(self, place_id: str):
        """Firmanın web sitesi ve uluslararası telefonunu güvenli ve detaylı çeker."""
        params = {
            'place_id': place_id,
            'fields': 'website,international_phone_number',
            'key': self.api_key
        }
        try:
            res = requests.get(self.details_url, params=params)
            if res.status_code == 200:
                return res.json().get('result', {})
        except Exception as e:
            print(f"[UYARI] Detay çekilemedi (Place ID: {place_id}): {str(e)}")
        return {}

if __name__ == "__main__":
    # Test ve Actions entegrasyonu için giriş noktası
    try:
        engine = MapsIntelligenceEngine()
        
        # GitHub Secrets'tan gelen dinamik hedef kelimeler
        keywords = os.getenv("TARGET_KEYWORDS", "industrial flow control distributor").split(",")
        regions = os.getenv("TARGET_REGIONS", "Germany").split(",")
        
        all_data = []
        for reg in regions:
            for kw in keywords:
                data = engine.search_target_companies(kw.strip(), reg.strip())
                all_data.extend(data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            # Veriyi güvenli ve sıkıştırılmış Parquet formatında saklıyoruz (Excel'e dönüştürülebilir)
            os.makedirs("data_vault", exist_ok=True)
            df.to_parquet("data_vault/maps_raw_leads.parquet", index=False)
            print(f"[BAŞARILI] {len(all_data)} potansiyel ihracat müşterisi 'data_vault' içine güvenlikle kaydedildi.")
        else:
            print("[UYARI] Kriterlere uygun veri bulunamadı veya filtreye takıldı.")
            
    except Exception as error:
        print(f"[KRİTİK HATA] Sistem durduruldu: {str(error)}")
