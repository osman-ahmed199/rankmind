import requests
from urllib.parse import urlparse

class ScraperService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def validate_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def get_html(self, url):
        if not self.validate_url(url):
            return None, "رابط غير صحيح. يرجى التأكد من كتابة الرابط بشكل كامل (مثل https://example.com)"

        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=15, 
                verify=True,
                allow_redirects=True
            )
            
            # Handle encoding
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding

            if response.status_code == 200:
                return response.text, None
            elif response.status_code == 404:
                return None, "لم يتم العثور على الصفحة (404). تأكد من صحة الرابط."
            else:
                return None, f"فشل الوصول للموقع. رمز الخطأ: {response.status_code}"

        except requests.exceptions.Timeout:
            return None, "انتهت مهلة الاتصال. الموقع بطيء جداً أو غير متاح حالياً."
        except requests.exceptions.SSLError:
            return None, "خطأ في شهادة الأمان (SSL). لا يمكن الوصول للموقع بشكل آمن."
        except requests.exceptions.ConnectionError:
            return None, "تعذر الاتصال بالموقع. تأكد من أن الرابط يعمل بشكل صحيح."
        except Exception as e:
            return None, f"حدث خطأ غير متوقع: {str(e)}"
