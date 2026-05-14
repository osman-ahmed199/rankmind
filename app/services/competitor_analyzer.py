import os
import json
from groq import Groq
import httpx

class CompetitorAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(
            api_key=self.api_key,
            http_client=httpx.Client(trust_env=False)
        )

    def analyze_competition(self, user_url, competitor_urls):
        """
        Compares the user's site with up to 3 competitors for AEO.
        """
        all_urls = [user_url] + competitor_urls
        
        prompt = f"""
        Analyze these {len(all_urls)} websites for AI Engine Optimization (AEO):
        {chr(10).join([f"{i+1}. {url}" for i, url in enumerate(all_urls)])}

        Rank them 1-{len(all_urls)} based on:
        - E-E-A-T score
        - Semantic structure
        - Answer optimization
        - Content depth

        Output the result in strict JSON format:
        {{
            "rankings": [
                {{
                    "url": "website.com",
                    "rank": 1,
                    "score": 85,
                    "gap": 0,
                    "is_user": true/false
                }}
            ],
            "comparison_table": {{
                "criteria": ["EEAT", "Structure", "Answers", "Depth"],
                "data": [
                    {{"url": "site.com", "scores": [80, 70, 90, 85]}}
                ]
            }},
            "ai_insight": "Detailed explanation of why user's site is ranked X and what to improve to beat the leader."
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "أنت محلل SEO متخصص في مقارنة المنافسين لـ AI Engine Optimization (AEO). اكتب تحليل الفجوة التنافسية بالعربي الفصحى فقط. لا تستخدم الإنجليزية إطلاقاً في التحليل. Output only JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            
            result = json.loads(chat_completion.choices[0].message.content)
            return result, None
        except Exception as e:
            return None, str(e)
