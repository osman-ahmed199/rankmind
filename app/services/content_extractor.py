from bs4 import BeautifulSoup
import json
import re

class ContentExtractor:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')
        # Remove script and style elements
        for script_or_style in self.soup(["script", "style"]):
            script_or_style.decompose()

    def extract_all(self):
        data = {
            "title": self.get_title(),
            "meta_description": self.get_meta_description(),
            "headings": self.get_headings(),
            "paragraphs": self.get_paragraphs(),
            "internal_links": self.get_internal_links(),
            "og_tags": self.get_og_tags(),
            "word_count": self.get_word_count()
        }
        return data

    def get_title(self):
        return self.soup.title.string.strip() if self.soup.title else ""

    def get_meta_description(self):
        meta = self.soup.find("meta", attrs={"name": "description"})
        if not meta:
            meta = self.soup.find("meta", attrs={"property": "og:description"})
        return meta.get("content", "").strip() if meta else ""

    def get_headings(self):
        headings = {
            "h1": [h.get_text().strip() for h in self.soup.find_all("h1")],
            "h2": [h.get_text().strip() for h in self.soup.find_all("h2")],
            "h3": [h.get_text().strip() for h in self.soup.find_all("h3")]
        }
        return headings

    def get_paragraphs(self):
        # Limit to first 10 paragraphs to avoid huge results
        return [p.get_text().strip() for p in self.soup.find_all("p") if p.get_text().strip()][:10]

    def get_internal_links(self):
        links = []
        for a in self.soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/') or href.startswith('#'):
                links.append(href)
        return list(set(links))[:20] # Limit and unique

    def get_og_tags(self):
        og = {}
        for meta in self.soup.find_all("meta", property=re.compile(r'^og:')):
            og[meta["property"]] = meta.get("content", "")
        return og

    def get_word_count(self):
        text = self.soup.get_text()
        words = re.findall(r'\w+', text)
        return len(words)
