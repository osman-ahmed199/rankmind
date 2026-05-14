import requests
from bs4 import BeautifulSoup
import sqlite3
import os

BASE_URL = "http://127.0.0.1:5000"

def clear_db():
    db_path = os.path.join("instance", "aeo_analyzer.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses")
        cursor.execute("DELETE FROM sites")
        cursor.execute("DELETE FROM users")
        conn.commit()
        conn.close()

def final_test():
    clear_db()
    s = requests.Session()
    email = "final_test@aeo.com"
    password = "password123"

    print("1. Registering...")
    r = s.get(f"{BASE_URL}/auth/register")
    soup = BeautifulSoup(r.text, "html.parser")
    csrf = soup.find("input", {"name": "csrf_token"})["value"]
    s.post(f"{BASE_URL}/auth/register", data={
        "email": email, "password": password, "confirm_password": password,
        "full_name": "Final Tester", "csrf_token": csrf
    }, allow_redirects=True)

    print("2. Logging in...")
    r2 = s.get(f"{BASE_URL}/auth/login")
    csrf2 = BeautifulSoup(r2.text, "html.parser").find("input", {"name": "csrf_token"})["value"]
    s.post(f"{BASE_URL}/auth/login", data={"email": email, "password": password, "csrf_token": csrf2}, allow_redirects=True)

    print("3. Analyzing https://safeco-group.com ...")
    r3 = s.post(f"{BASE_URL}/analysis/start", data={"url": "https://safeco-group.com"}, allow_redirects=True)
    
    print(f"Final URL: {r3.url}")
    if "/analysis/result/" in r3.url:
        print("--- SUCCESS: Analysis completed! ---")
        soup_res = BeautifulSoup(r3.text, "html.parser")
        site_display = soup_res.find("p", class_="text-gray-500").text.strip()
        print(f"Site Display in Result: {site_display}")
    else:
        print("--- FAILED: Analysis did not complete ---")
        soup_err = BeautifulSoup(r3.text, "html.parser")
        flash = soup_err.find(class_="animate-pulse-once")
        if flash: print(f"Error Message: {flash.text.strip()}")
        
    print("\n4. Checking Dashboard for Site Name...")
    r_dash = s.get(f"{BASE_URL}/dashboard/")
    soup_dash = BeautifulSoup(r_dash.text, "html.parser")
    site_name = soup_dash.find("h3", class_="font-bold text-lg text-gray-800 mb-2 truncate pr-2")
    if site_name:
        print(f"Site Name in Dashboard: {site_name.text.strip()}")
    else:
        print("Site not found in Dashboard.")

if __name__ == "__main__":
    final_test()
