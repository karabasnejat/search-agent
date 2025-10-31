"""OpenAIBulletinWriter - Infrastructure implementation of IBulletinWriter."""

from typing import List

import openai

from application.use_cases.generate_bulletin_use_case import IBulletinWriter
from domain.entities.news_article import NewsArticle
from domain.value_objects.date_range import DateRange


class OpenAIBulletinWriter(IBulletinWriter):
    """
    OpenAI GPT-4O implementation of bulletin writer.
    
    Follows Dependency Inversion Principle by implementing application interface.
    Belongs to infrastructure layer - handles external AI service.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize bulletin writer with OpenAI API key.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o)
        """
        openai.api_key = api_key
        self._model = model
    
    def write_bulletin(
        self,
        articles: List[NewsArticle],
        date_range: DateRange
    ) -> str:
        """
        Write a Turkish bulletin from news articles using GPT-4O.
        
        Args:
            articles: List of news articles
            date_range: Date range for the bulletin
            
        Returns:
            Formatted bulletin content in Turkish
        """
        if not articles:
            return f"Haftal?k Yapay Zeka B?lteni ({date_range.format_for_display()})\n\nBu tarih aral???nda haber bulunamad?."
        
        # Prepare content for GPT
        articles_content = self._format_articles_for_prompt(articles, date_range)
        
        # Create prompt
        prompt = self._create_prompt(articles_content, date_range)
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "Sen yapay zeka sekt?r?nde 15 y?ll?k deneyime sahip k?demli bir teknoloji analisti ve end?stri uzman?s?n. Karma??k teknolojik geli?meleri derinlemesine analiz edip, C-level y?neticiler, ara?t?rmac?lar ve yat?r?mc?lar i?in sofistike, ?ok katmanl? analizler ?retiyorsun. Yaz?lar?n stratejik ?ng?r?ler, pazar dinamikleri ve sekt?rel etki analizleri i?eriyor."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"B?lten olu?turulamad?: {str(e)}"
    
    def _format_articles_for_prompt(
        self,
        articles: List[NewsArticle],
        date_range: DateRange
    ) -> str:
        """
        Format articles for GPT prompt.
        
        Args:
            articles: List of news articles
            date_range: Date range
            
        Returns:
            Formatted string
        """
        start_date_str = date_range.start_date.strftime("%d %B %Y")
        end_date_str = date_range.end_date.strftime("%d %B %Y")
        
        content = f"TARGET DATE RANGE: {start_date_str} to {end_date_str}\n\n"
        
        for article in articles:
            content += f"HABER BA?LIK: {article.title}\n"
            content += f"URL: {article.url}\n"
            if article.published_date:
                content += f"YAYIN TAR?H?: {article.published_date.strftime('%d %B %Y')}\n"
            content += f"??ER?K: {article.summary}\n"
            content += f"KATEGOR?: {article.category.value}\n"
            content += f"UYARI: Bu haberin tarihini kontrol et - sadece {start_date_str} ile {end_date_str} aras?ndaki haberleri dahil et\n"
            content += "-" * 80 + "\n\n"
        
        return content
    
    def _create_prompt(self, articles_content: str, date_range: DateRange) -> str:
        """
        Create GPT prompt for bulletin generation.
        
        Args:
            articles_content: Formatted articles content
            date_range: Date range
            
        Returns:
            Prompt string
        """
        start_date_str = date_range.start_date.strftime("%d %B %Y")
        end_date_str = date_range.end_date.strftime("%d %B %Y")
        
        return f"""
You are a senior technology analyst and expert AI industry journalist writing an in-depth weekly AI bulletin. Your audience consists of C-level executives, AI researchers, venture capitalists, and technology strategists who require sophisticated analysis and comprehensive insights.

**STRICT DATE FILTERING:**
- START DATE: {start_date_str}
- END DATE: {end_date_str}
- ONLY include news published between these dates
- REJECT any news outside this date range

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
- Use **bold** for company names (e.g., **OpenAI**, **Anthropic**, **Google DeepMind**)
- Write in professional Turkish
- Each article: short engaging headline + 6-8 sentence summary

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
{articles_content}

Please only include news from {start_date_str} to {end_date_str}. Add the URLs provided in the content as "Kaynak:" at the end of each news item.
If there are no news in the specified date range, please indicate this clearly.
"""
