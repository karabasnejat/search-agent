from tavily import TavilyClient
import openai
from datetime import datetime, timedelta
import json
import re

class NewsBulletinGenerator:
    def __init__(self, tavily_api_key, openai_api_key):
        """
        Haber bülteni oluşturucu sınıfı
        
        Args:
            tavily_api_key (str): Tavily API anahtarı
            openai_api_key (str): OpenAI API anahtarı
        """
        self.tavily_client = TavilyClient(api_key="")
        openai.api_key = ""

    def search_ai_news(self, query="yapay zeka haberleri", days=7, include_domains=None):
        """
        Yapay zeka haberleri arar
        
        Args:
            query (str): Arama sorgusu
            days (int): Kaç günlük haber aranacağı
            include_domains (list): Aranacak domainlerin listesi
            
        Returns:
            dict: Arama sonuçları
        """
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                topic="news",
                days=days,
                max_results=25,
                include_raw_content=True,
                include_domains=include_domains
            )
            return response
        except Exception as e:
            print(f"Haber arama hatası: {e}")
            return None
    
    def parse_date_range(self, end_date_str):
        """
        Bitiş tarihinden 7 günlük tarih aralığı oluşturur
        
        Args:
            end_date_str (str): Bitiş tarihi (örn: "31 Ağustos 2025")
            
        Returns:
            tuple: (başlangıç_tarihi, bitiş_tarihi)
        """
        # Türkçe ay isimlerini İngilizce'ye çevir
        turkish_months = {
            'Ocak': 'January', 'Şubat': 'February', 'Mart': 'March',
            'Nisan': 'April', 'Mayıs': 'May', 'Haziran': 'June',
            'Temmuz': 'July', 'Ağustos': 'August', 'Eylül': 'September',
            'Ekim': 'October', 'Kasım': 'November', 'Aralık': 'December'
        }
        
        for tr_month, en_month in turkish_months.items():
            end_date_str = end_date_str.replace(tr_month, en_month)
        
        try:
            end_date = datetime.strptime(end_date_str, "%d %B %Y")
            start_date = end_date - timedelta(days=7)
            return start_date, end_date
        except ValueError as e:
            print(f"Tarih formatı hatası: {e}")
            return None, None
    
    def filter_news_by_date(self, search_results, start_date, end_date):
        """
        Arama sonuçlarındaki haberleri tarih aralığına göre filtreler
        
        Args:
            search_results (dict): Tavily arama sonuçları
            start_date (datetime): Başlangıç tarihi
            end_date (datetime): Bitiş tarihi
            
        Returns:
            str: Filtrelenmiş haber içeriği
        """
        if not search_results or 'results' not in search_results:
            return "Haber bulunamadı veya hatalı format."
        
        # İçeriği metin olarak birleştir
        full_content = ""
        date_range_note = f"TARGET DATE RANGE: {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}\n\n"
        full_content += date_range_note
        
        for result in search_results['results']:
            # Her haber için başlık, içerik ve URL'yi ekle
            title = result.get('title', 'Başlık bulunamadı')
            content = result.get('content', '')
            url = result.get('url', '')
            published_date = result.get('published_date', '')
            
            news_item = f"HABER BAŞLIK: {title}\n"
            news_item += f"URL: {url}\n"
            if published_date:
                news_item += f"YAYIN TARİHİ: {published_date}\n"
            news_item += f"İÇERİK: {content}\n"
            news_item += f"UYARI: Bu haberin tarihini kontrol et - sadece {start_date.strftime('%d %B %Y')} ile {end_date.strftime('%d %B %Y')} arasındaki haberleri dahil et\n"
            news_item += "-" * 80 + "\n\n"
            
            full_content += news_item
        
        return full_content
    
    def create_bulletin_with_gpt4o(self, filtered_content, start_date, end_date, date_instruction):
        """
        GPT-4O kullanarak filtrelenmiş içerikten bülten oluşturur
        
        Args:
            filtered_content (str): Filtrelenmiş haber içeriği
            start_date (datetime): Başlangıç tarihi
            end_date (datetime): Bitiş tarihi
            date_instruction (str): Tarih filtresi talimatı
            
        Returns:
            str: Oluşturulan haber bülteni
        """
        start_date_str = start_date.strftime("%d %B %Y")
        end_date_str = end_date.strftime("%d %B %Y")
        
        prompt = f"""
You are a senior technology analyst and expert AI industry journalist writing an in-depth weekly AI bulletin. Your audience consists of C-level executives, AI researchers, venture capitalists, and technology strategists who require sophisticated analysis and comprehensive insights.

{date_instruction}

**STRICT DATE FILTERING:**
- START DATE: {start_date_str}
- END DATE: {end_date_str}
- ONLY include news published between these dates
- REJECT any news from 11 August or earlier dates
- REJECT any news from September or later dates

**ADVANCED WRITING REQUIREMENTS:**

**STRUCTURE FOR EACH NEWS ITEM (4-6 paragraphs minimum):**

1. **Opening Paragraph**: Context-setting introduction with strategic implications
2. **Technical Deep Dive**: Detailed technical specifications, architecture, parameters, benchmarks
3. **Market Analysis**: Competitive landscape, market positioning, financial implications
4. **Industry Impact**: Sectoral disruption analysis, use case exploration, adoption barriers
5. **Critical Assessment**: Advantages, limitations, risks, skeptical viewpoints
6. **Future Outlook**: Long-term implications, regulatory considerations, strategic recommendations

**SOPHISTICATED WRITING STYLE:**
- Use complex sentence structures and sophisticated vocabulary
- Include specific technical details (model sizes, parameters, benchmarks, percentages)
- Reference industry context and historical comparisons
- Analyze competitive dynamics and market implications
- Discuss regulatory and ethical considerations
- Include expert opinions and industry reactions
- Analyze financial and business model implications
- Connect developments to broader AI ecosystem trends

**EXAMPLE OF DESIRED DEPTH AND STYLE:**

```
Haftalık Yapay Zeka Bülteni – 27. Sayı ({start_date_str} - {end_date_str})

1- Google, Gemini'ye 'kişisel bağlam' hafızası getiriyor: Yapay zeka asistanlarında kişiselleştirme devri

Google, Gemini yapay zekâ asistanına geçmiş sohbetleri hatırlama özelliği eklemeye başladı ve bu adım, sektörde kişiselleştirme odaklı yapay zeka deneyimlerinin yaygınlaşmasına işaret ediyor. Personal context (kişisel bağlam) adı verilen bu özellik, kullanıcıların daha önce paylaştığı tercih ve bilgileri öğrenerek yanıtlarını kişiye özel hâle getirme kabiliyeti sunuyor. Bu gelişme, OpenAI'nin ChatGPT'sinde henüz tam anlamıyla bulunmayan bir özellik olarak Google'a rekabette önemli bir avantaj sağlayabilir.

Teknik açıdan, kişisel bağlam özelliği Gemini 2.5 Pro modeliyle entegre şekilde çalışıyor ve kullanıcı etkileşim verilerini modelin long-term memory mekanizmasında saklayarak gelecekteki yanıtlarda bu bilgileri contextualize edebiliyor. Sistem, kullanıcının geçmiş tercihlerini, ilgi alanlarını ve davranış kalıplarını analiz ederek daha relevans yüksek öneriler sunabiliyor. Örneğin, daha önce sevdiğiniz bir çizgi roman karakterinden bahsettiyseniz, Gemini ondan ilham alarak doğum günü teması önerebiliyor ya da okuduğunuz kitap özetlerine dayanarak benzer tarzda kitaplar tavsiye edebiliyor.

Bu özelliğin piyasaya sürülmesi, yapay zeka asistanları arasındaki rekabeti kişiselleştirme cephesinde yoğunlaştırıyor. Google'ın bu hamlesi, özellikle Microsoft'un Copilot ve OpenAI'nin ChatGPT'sine karşı savunma stratejisinin bir parçası olarak değerlendiriliyor. Kişisel veri işleme kapasitesi, kullanıcı bağlılığını artıran kritik bir faktör haline gelirken, Google'ın arama motoru geçmişi ve Android ekosistemindeki veri avantajı bu alanda önemli bir rekabet üstünlüğü sağlayabilir.

Ancak bu gelişme, veri gizliliği ve güvenliği konularında ciddi soru işaretleri de beraberinde getiriyor. Kullanıcıların kişisel tercihlerinin ve davranış kalıplarının AI sistemleri tarafından depolanması, potansiyel veri sızıntıları ve kötüye kullanım risklerini artırıyor. Google'ın geçici sohbet modu sunması (Temporary Chat) ve kullanıcılara kişisel bağlam özelliğini kapatma seçeneği vermesi, bu endişelere yanıt verme çabası olarak görünse de, uzmanlar daha sıkı düzenlemelerin gerekli olabileceğini belirtiyor.

Uzun vadede, kişiselleştirilen AI asistanlarının yaygınlaşması, iş süreçlerinden eğitime, sağlıktan eğlenceye kadar pek çok sektörde köklü değişimlere yol açabilir. Bu trend, yapay zeka şirketlerini kullanıcı verisi toplamada daha agresif stratejiler izlemeye itebilir ve düzenleyici otoritelerin bu alanda daha net kurallar koymasını gerektirebilir. Google'ın bu adımı, sektörde "AI personalization arms race" olarak adlandırılabilecek yeni bir rekabet döneminin başlangıcı olabilir.

Kaynak: https://example-news-url.com
```

**CRITICAL CONTENT RULES:**
- NEVER fabricate, invent, or create fictional news content
- ONLY use factual information from the provided news sources
- STRICT DATE FILTERING: Only {start_date_str} to {end_date_str}
- Each article must be substantially longer and more analytical than basic news summaries
- Include specific technical details, market analysis, and industry implications
- Target sophisticated, expert-level audience with deep insights
- Minimum 4-6 paragraphs per news item
- Maximum 7 news items total 

Content:
{filtered_content}

Please only include news from {start_date_str} to {end_date_str}. Add the URLs provided in the content as "Kaynak:" at the end of each news item.
If there are no news in the specified date range, please indicate this clearly.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # veya "gpt-4o-mini"
                messages=[
                    {"role": "system", "content": "Sen yapay zeka sektöründe 15 yıllık deneyime sahip kıdemli bir teknoloji analisti ve endüstri uzmanısın. Karmaşık teknolojik gelişmeleri derinlemesine analiz edip, C-level yöneticiler, araştırmacılar ve yatırımcılar için sofistike, çok katmanlı analizler üretiyorsun. Yazıların stratejik öngörüler, pazar dinamikleri ve sektörel etki analizleri içeriyor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,  # Daha uzun metinler için token sayısını artırdık
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"GPT-4O ile bülten oluşturma hatası: {e}")
            return f"Bülten oluşturulamadı: {e}"
    
    def generate_bulletin(self, end_date_str, domains=None):
        """
        Ana fonksiyon: Yapay zeka haberlerini arar ve bülten oluşturur
        
        Args:
            end_date_str (str): Bitiş tarihi (örn: "31 Ağustos 2025")
            domains (list, optional): Aranacak domainlerin listesi. Defaults to None.
            
        Returns:
            str: Oluşturulan haber bülteni
        """
        print("Tarih aralığı hesaplanıyor...")
        start_date, end_date = self.parse_date_range(end_date_str)
        
        if not start_date or not end_date:
            return "Tarih formatı hatalı."
        
        print(f"Tarih aralığı: {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}")
        
        # Hesaplanan gün sayısını kullanarak arama yap (biraz daha geniş aralık)
        days_diff = (end_date - start_date).days

        print("Yapay zeka haberleri aranıyor...")
        # Önce belirli domainlerde ara
        search_results = self.search_ai_news(
            query="artificial intelligence AI machine learning deep learning GPT ChatGPT OpenAI Google Microsoft Meta yapay zeka",
            days=days_diff,
            include_domains=domains
        )
        
        # Eğer yeterli haber bulunamazsa, genel arama yap
        if not search_results or len(search_results.get('results', [])) < 5:
            print("Belirli domainlerde yeterli haber bulunamadı, genel arama yapılıyor...")
            search_results = self.search_ai_news(
                query="artificial intelligence AI machine learning deep learning GPT ChatGPT OpenAI Google Microsoft Meta yapay zeka",
                days=days_diff,
                include_domains=None  # Tüm domainlerde ara
            )
        
        if not search_results:
            return "Haberler aranamadı."
        
        # Bulunan haber sayısını göster
        news_count = len(search_results.get('results', []))
        print(f"Toplam {news_count} haber bulundu.")
        
        print("Haberler filtreleniyor...")
        filtered_content = self.filter_news_by_date(search_results, start_date, end_date)
        
        # Tarih aralığını açıkça belirt
        date_instruction = f"CRITICAL: Only include news from {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}. Reject any news outside this date range."
        
        print("GPT-4O ile bülten oluşturuluyor...")
        bulletin = self.create_bulletin_with_gpt4o(filtered_content, start_date, end_date, date_instruction)
        
        return bulletin


# Kullanım örneği
def main():
    # API anahtarlarınızı buraya girin
    TAVILY_API_KEY = ""
    OPENAI_API_KEY = ""  # OpenAI API anahtarınızı buraya girin
    
    # Haber bülteni oluşturucuyu başlat
    generator = NewsBulletinGenerator(TAVILY_API_KEY, OPENAI_API_KEY)
    
    # Kullanıcıdan tarih al
    print("Haber bülteni oluşturucu")
    print("=" * 40)
    end_date = input("Bitiş tarihini girin (örn: 31 Ağustos 2025): ").strip()
    
    if not end_date:
        end_date = datetime.now().strftime("%d %B %Y")  # Bugünün tarihini kullan
        print(f"Varsayılan tarih kullanılıyor: {end_date}")
    
    # Aranacak domainler - daha fazla kaynak eklendi
    target_domains = [
        "donanimhaber.com/yapay-zeka", 
        "artificialintelligence-news.com",
        "techcrunch.com",
        "venturebeat.com",
        "theverge.com",
        "wired.com",
        "arstechnica.com"
    ]
    
    print(f"\nBülten oluşturuluyor: {end_date}")
    print(f"Kaynaklar: {', '.join(target_domains)}")
    print("-" * 40)
    
    # Bülten oluştur
    bulletin = generator.generate_bulletin(end_date, domains=target_domains)
    
    print("\n" + "="*50)
    print("OLUŞTURULAN HABER BÜLTENİ")
    print("="*50)
    print(bulletin)
    
    # Bülteni dosyaya kaydet
    with open(f"haber_bulteni_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
        f.write(bulletin)
    print("\nBülten dosyaya kaydedildi.")

if __name__ == "__main__":
    main()