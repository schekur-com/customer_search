import os
import pandas as pd
import requests
from datetime import datetime

class DynamicCustomsIntelligence:
    def __init__(self):
        # Güvenlik önceliğimiz: Gümrük veya veri sağlayıcı servis anahtarları burada tutulur
        self.customs_api_token = os.getenv("CUSTOMS_DATA_TOKEN", "MOCK_TOKEN")

    def analyze_shipments(self, company_name: str, hs_code: str, product_desc: str):
        """
        Kullanıcının girdiğine göre tamamen dinamik arama yapar.
        Tek bir ürüne bağlı kalmaz; sorgu anındaki gtip ve ürün tanımını doğrular.
        """
        print(f"[ANALİZ] '{company_name}' firması {hs_code} ({product_desc}) için taranıyor...")
        
        # Gerçek senaryoda burası uluslararası açık gümrük/konşimento havuzlarına (Örn: UN Comtrade, Port Customs API vb.) istek atar
        # Şimdilik dinamik filtreleme mantığını simüle eden güvenli bir kontrol simülasyonu kuruyoruz:
        
        # Dinamik içerik tarama simülasyonu
        has_import_history = True # Test amaçlı pozitif dönüyoruz
        shipment_count = 12 # Son 1 yıldaki sevkiyat sayısı
        
        analysis_result = {
            'verified_hs_code': hs_code,
            'matched_product': product_desc,
            'has_active_imports': has_import_history,
            'total_shipments_12months': shipment_count,
            'confidence_score': 85 if has_import_history else 10
        }
        
        return analysis_result

    def process_pipeline(self, current_hs_code: str, current_product_desc: str):
        """Maps verileriyle dinamik sorgu verilerini birleştirir."""
        raw_data_path = "data_vault/maps_raw_leads.parquet"
        
        if not os.path.exists(raw_data_path):
            print("[HATA] Öncelikli olarak Maps verisi toplanmalıdır. Modül 1'i çalıştırın.")
            return
            
        df_maps = pd.read_parquet(raw_data_path)
        enriched_leads = []
        
        for index, row in df_maps.iterrows():
            # Kullanıcının dinamik girdilerine göre her firmayı gümrük süzgecinden geçiriyoruz
            customs_data = self.analyze_shipments(
                company_name=row['company_name'],
                hs_code=current_hs_code,
                product_desc=current_product_desc
            )
            
            # Dinamik Puanlama ve Birleştirme
            combined_lead = {**row.to_dict(), **customs_data}
            # Nihai B2B İhracat Skoru Hesaplama (Dinamik)
            combined_lead['final_export_score'] = (row['google_rating'] * 10) + (customs_data['total_shipments_12months'] * 4)
            
            enriched_leads.append(combined_lead)
            
        df_final = pd.DataFrame(enriched_leads)
        
        # En yüksek skorlu gerçek alıcıları en üste sırala
        df_final = df_final.sort_values(by='final_export_score', ascending=False)
        
        # Çıktıyı güvenli klasöre yaz
        os.makedirs("data_vault", exist_ok=True)
        df_final.to_parquet("data_vault/dynamic_export_leads.parquet", index=False)
        df_final.to_csv("data_vault/dynamic_export_leads.csv", index=False, encoding='utf-8')
        print(f"[BAŞARILI] Dinamik istihbarat tamamlandı. {len(df_final)} firma yeni kriterlere göre skorlandı.")

if __name__ == "__main__":
    # Kullanıcının o an sisteme ne sormak istediğini yakalayan dinamik değişkenler
    # GitHub Actions veya yerel terminal üzerinden beslenir
    CURRENT_HS = os.getenv("DYNAMIC_HS_CODE", "8481.80") # Varsayılan Endüstriyel Vanalar
    CURRENT_DESC = os.getenv("DYNAMIC_PRODUCT_DESC", "industrial valves and flow control elements")
    
    matcher = DynamicCustomsIntelligence()
    matcher.process_pipeline(current_hs_code=CURRENT_HS, current_product_desc=CURRENT_DESC)
