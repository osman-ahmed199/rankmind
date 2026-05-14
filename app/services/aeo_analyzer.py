import json
import os
import httpx
from groq import Groq
from flask import current_app

class AEOAnalyzer:
    def __init__(self):
        # Explicitly disable proxy environment variables for this client
        self.client = Groq(
            api_key=current_app.config['GROQ_API_KEY'],
            http_client=httpx.Client(trust_env=False)
        )
        self.model = "llama-3.1-8b-instant"

    def analyze_content(self, scraped_data):
        prompt = f"""
        Analyze the following website content for Answer Engine Optimization (AEO).
        AEO is how well a website is optimized for AI search engines like Perplexity, ChatGPT, and Gemini.

        Website Data:
        Title: {scraped_data.get('title')}
        Meta Description: {scraped_data.get('meta_description')}
        Headings: {json.dumps(scraped_data.get('headings'))}
        Word Count: {scraped_data.get('word_count')}
        Paragraph Samples: {json.dumps(scraped_data.get('paragraphs'))}

        Evaluate based on these 5 criteria (Score each 0-100):
        1. E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)
        2. Semantic Structure (Use of headings and logical flow)
        3. Answer Optimization (Directness and clarity of answers)
        4. Content Depth (How well the topic is covered)
        5. Technical Readability (How easily AI can parse the content)

        Output MUST be in valid JSON format with this structure:
        {{
            "overall_score": number,
            "breakdown": {{
                "eeat": {{"score": number, "label": "E-E-A-T"}},
                "semantic": {{"score": number, "label": "Semantic Structure"}},
                "answer": {{"score": number, "label": "Answer Optimization"}},
                "depth": {{"score": number, "label": "Content Depth"}},
                "technical": {{"score": number, "label": "Technical Readability"}}
            }},
            "issues": [
                {{"severity": "high|medium|low", "message": "Issue in Arabic"}}
            ],
            "action_plan": [
                {{"priority": "high|medium|low", "step": "Action step in Arabic"}}
            ],
            "ai_summary": "Short explanation in Arabic why the site might not appear in AI search results"
        }}
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional AEO (Answer Engine Optimization) expert. Always respond in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                result = json.loads(completion.choices[0].message.content)
                # Ensure essential fields exist
                if 'overall_score' not in result:
                    result['overall_score'] = 0
                if 'action_plan' not in result:
                    result['action_plan'] = []
                return result, None
            except json.JSONDecodeError:
                print("DEBUG: Malformed JSON from AI. Using fallback.")
                fallback = {
                    "overall_score": 0,
                    "breakdown": {},
                    "issues": [{"severity": "high", "message": "فشل تحليل المحتوى بشكل صحيح. يرجى المحاولة لاحقاً."}],
                    "action_plan": [],
                    "ai_summary": "تعذر توليد ملخص بسبب خطأ في معالجة البيانات."
                }
                return fallback, None

        except Exception as e:
            with open('groq_error.log', 'w', encoding='utf-8') as f:
                f.write(str(e))
            print(f"DEBUG GROQ ERROR: {str(e)}")
            
            error_str = str(e).lower()
            if "rate_limit" in error_str:
                return None, "تم تجاوز حد الاستخدام المسموح به لـ AI. يرجى المحاولة لاحقاً."
            elif "api_key" in error_str or "401" in error_str:
                return None, "مفتاح API غير صالح. يرجى التأكد من صحة GROQ_API_KEY في الإعدادات أو تواصل مع الدعم."
            elif "connection" in error_str:
                return None, "فشل الاتصال بخادم الذكاء الاصطناعي. تأكد من اتصال الإنترنت وحاول مرة أخرى."
            
            return None, f"حدث خطأ أثناء تحليل البيانات بالذكاء الاصطناعي. يرجى المحاولة لاحقاً."
