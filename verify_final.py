import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def verify_final():
    s = requests.Session()
    email = "osman@safeco-group.com"
    password = "password123"

    print("1. Logging in as Admin...")
    r = s.get(f"{BASE_URL}/auth/login")
    soup = BeautifulSoup(r.text, "html.parser")
    csrf = soup.find("input", {"name": "csrf_token"})["value"]
    s.post(f"{BASE_URL}/auth/login", data={"email": email, "password": password, "csrf_token": csrf}, allow_redirects=True)

    print("\n2. Verifying Billing Page...")
    r_bill = s.get(f"{BASE_URL}/billing/")
    if r_bill.status_code == 200 and "الخطط" in r_bill.text:
        print("--- SUCCESS: Billing Page looks good! ---")
    else:
        print(f"--- FAILED: Billing Page status {r_bill.status_code} ---")

    print("\n3. Verifying Admin Dashboard...")
    r_admin = s.get(f"{BASE_URL}/admin/")
    if r_admin.status_code == 200 and "إجمالي المستخدمين" in r_admin.text:
        print("--- SUCCESS: Admin Dashboard looks good! ---")
    else:
        print(f"--- FAILED: Admin Dashboard status {r_admin.status_code} ---")

if __name__ == "__main__":
    verify_final()
