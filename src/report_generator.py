import os
import pandas as pd
from weasyprint import HTML

class SCHEKURReportEngine:
    def __init__(self):
        self.data_path = "data_vault/dynamic_export_leads.csv"
        self.output_html = "data_vault/index.html" # GitHub Pages için kök yayın dosyası
        self.output_pdf = "data_vault/istihbarat_cikti_raporu.pdf"

    def generate_html_template(self, df_leads, metadata):
        """Web arayüzü ve kurumsal çıktı belgesi için dinamik şablon üretir."""
        table_rows = ""
        for idx, row in df_leads.iterrows():
            score_class = "score-high" if row['final_export_score'] >= 80 else "score-med"
            table_rows += f"""
            <tr>
                <td>{idx + 1}</td>
                <td><b>{row['Company Name']}</b></td>
                <td>{row['Target Country']} / {row['City']}</td>
                <td>{row['Industry Keywords']}</td>
                <td style="text-align: center; font-weight: bold;">{row['HS Code Verified']}</td>
                <td style="text-align: center; font-weight: bold; color: #2563eb;">{row['12M Shipment Count']}</td>
                <td>{row['Primary Source Country']}</td>
                <td><a href="{row['Website']}" target="_blank" class="link-text">{row['Website'].replace('https://','').replace('www.','')}</a><br><small>{row['International Phone']}</small></td>
                <td><span class="{score_class}">{int(row['Platform Export Score'])} / 100</span></td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <title>SCHEKUR B2B İhracat İstihbarat Raporu</title>
            <style>
                * {{ box-sizing: border-box; }}
                @page {{ size: A4 landscape; margin: 12mm 10mm; background-color: #f8fafc; }}
                body {{ font-family: Arial, sans-serif; color: #1e293b; margin: 0; padding: 0; background-color: #f8fafc; font-size: 10pt; line-height: 1.3; }}
                .header-container {{ background-color: #0f172a; color: #ffffff; padding: 20px 15mm; border-bottom: 4px solid #2563eb; }}
                .header-grid {{ display: table; width: 100%; }}
                .header-cell {{ display: table-cell; vertical-align: middle; }}
                .title-main {{ font-size: 20pt; font-weight: bold; margin: 0; color: #ffffff; }}
                .title-sub {{ font-size: 10pt; color: #94a3b8; margin-top: 4px; }}
                .meta-box {{ text-align: right; font-size: 9pt; color: #cbd5e1; display: table-cell; vertical-align: middle; }}
                .badge {{ background-color: #2563eb; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
                .summary-cards {{ display: table; width: 100%; margin: 15px 0; border-spacing: 10px 0; }}
                .card {{ display: table-cell; background: white; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0; width: 25%; }}
                .card-label {{ font-size: 8pt; text-transform: uppercase; color: #64748b; font-weight: 600; }}
                .card-value {{ font-size: 13pt; font-weight: bold; color: #0f172a; margin-top: 2px; }}
                table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 6px; border: 1px solid #e2e8f0; margin-top: 10px; }}
                th {{ background-color: #1e293b; color: white; font-weight: 600; text-align: left; padding: 10px; font-size: 8.5pt; }}
                td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; font-size: 8.5pt; vertical-align: middle; }}
                tr:nth-child(even) td {{ background-color: #f1f5f9; }}
                .score-high {{ font-weight: bold; color: #16a34a; background-color: #f0fdf4; padding: 4px 8px; border-radius: 4px; border: 1px solid #bbf7d0; }}
                .score-med {{ font-weight: bold; color: #ca8a04; background-color: #fefce8; padding: 4px 8px; border-radius: 4px; border: 1px solid #fef08a; }}
                .link-text {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
                .action-bar {{ margin: 15px 0; padding: 10px; background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; text-align: right; }}
                .btn {{ background-color: #16a34a; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 9pt; margin-left: 5px; }}
                .footer {{ margin-top: 25px; text-align: center; font-size: 8pt; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
            </style>
        </head>
        <body>
            <div class="header-container">
                <div class="header-grid">
                    <div class="header-cell">
                        <div class="title-main">SCHEKUR Intelligence Engine</div>
                        <div class="title-sub">Dinamik İhracat Müşteri Hedefleme Paneli</div>
                    </div>
                    <div class="header-cell meta-box">
                        Sistem Durumu: <span class="badge">AKTİF / GÜVENLİ</span>
                    </div>
                </div>
            </div>

            <div class="summary-cards">
                <div class="card"><div class="card-label">Sorgulanan Canlı GTİP</div><div class="card-value">{metadata['hs_code']}</div></div>
                <div class="card"><div class="card-label">Dinamik Ürün Tanımı</div><div class="card-value">{metadata['product_desc']}</div></div>
                <div class="card"><div class="card-label">Taranan Sektör Anahtarı</div><div class="card-value">{metadata['keywords']}</div></div>
                <div class="card"><div class="card-label">Nitelikli Alıcı Sayısı</div><div class="card-value">{len(df_leads)} Şirket</div></div>
            </div>

            <div class="action-bar" id="web-only-actions">
                <span style="float: left; padding-top: 4px; font-weight: 600; color:#64748b;">Müşteri İstihbarat Çıktıları</span>
                <a href="./istihbarat_cikti_raporu.pdf" class="btn" download>📥 Kurumsal PDF Raporu İndir</a>
                <a href="./dynamic_export_leads.csv" class="btn" style="background-color:#2563eb;" download>📊 Excel/CSV Verisini İndir</a>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 4%;">Sıra</th>
                        <th style="width: 18%;">Firma Adı</th>
                        <th style="width: 14%;">Ülke / Şehir</th>
                        <th style="width: 18%;">Sektör Kelimeleri</th>
                        <th style="th-width: 8%;">GTİP Kodu</th>
                        <th style="width: 8%;">12A Konşimento</th>
                        <th style="width: 12%;">Ana Tedarikçi Ülke</th>
                        <th style="width: 14%;">İletişim & Web</th>
                        <th style="width: 8%;">İhracat Skoru</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            <div class="footer">SCHEKUR Altyapısı ve Güvenli Veri İşleme Protokolü ile şifreli olarak üretilmiştir.</div>
        </body>
        </html>
        """

    def build_reports(self, current_hs, current_desc, current_kw):
        if not os.path.exists(self.data_path):
            print("[HATA] Raporlanacak veri seti bulunamadı!")
            return

        df = pd.read_csv(self.data_path)
        metadata = {'hs_code': current_hs, 'product_desc': current_desc, 'keywords': current_kw}

        html_data = self.generate_html_template(df, metadata)
        with open(self.output_html, "w", encoding="utf-8") as f:
            f.write(html_data)

        # PDF çıktısında indirme butonlarını gizle
        pdf_ready_html = html_data.replace('id="web-only-actions"', 'id="web-only-actions" style="display:none;"')
        HTML(string=pdf_ready_html).write_pdf(self.output_pdf)
        print("[BAŞARILI] Ofis çıktıları ve Canlı Web Sayfası başarıyla üretildi.")

if __name__ == "__main__":
    HS = os.getenv("DYNAMIC_HS_CODE", "8481.80")
    DESC = os.getenv("DYNAMIC_PRODUCT_DESC", "Industrial Valves / Vana")
    KW = os.getenv("TARGET_KEYWORDS", "industrial valves distributor")
    
    engine = SCHEKURReportEngine()
    engine.build_reports(current_hs=HS, current_desc=DESC, current_kw=KW)
