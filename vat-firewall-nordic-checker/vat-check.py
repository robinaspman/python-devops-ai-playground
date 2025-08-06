import zeep
import requests
import json
import datetime
from bs4 import BeautifulSoup
import os

# -------------------------------
# 💾 Utility: File Logger
# -------------------------------

def log_verification(data, filename="vat_verification_log.json"):
    log = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            log = json.load(f)
    data["verified_at"] = datetime.datetime.now().isoformat()
    log.append(data)
    with open(filename, "w") as f:
        json.dump(log, f, indent=2)

# -------------------------------
# 🇪🇺 EU VAT Check (VIES)
# -------------------------------

def validate_eu_vat(country_code, vat_number):
    wsdl_url = 'https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl'
    client = zeep.Client(wsdl=wsdl_url)
    try:
        response = client.service.checkVat(countryCode=country_code, vatNumber=vat_number)
        data = {
            "type": "EU_VAT",
            "country_code": country_code,
            "vat_number": vat_number,
            "valid": response.valid,
            "name": response.name,
            "address": response.address
        }
        log_verification(data)
        return data
    except Exception as e:
        return {"error": str(e), "country_code": country_code, "vat_number": vat_number}

# -------------------------------
# 🇳🇴 Norway Company Checker
# -------------------------------

def validate_norwegian_org(org_nr):
    url = f"https://w2.brreg.no/enhet/sok/detalj.jsp?orgnr={org_nr}"
    response = requests.get(url)
    result = {
        "type": "NO_ORG",
        "org_nr": org_nr,
        "country": "NO",
        "valid": False,
        "company_name": "N/A",
        "source": url
    }
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        if title and "Enhet" in title.text:
            result["valid"] = True
            result["company_name"] = title.text.strip()
    log_verification(result)
    return result

# -------------------------------
# 🇸🇪 Sweden VAT & Org.nr Checker
# -------------------------------

def validate_swedish_company(org_nr):
    url = f"https://www.allabolag.se/{org_nr}"
    response = requests.get(url)
    result = {
        "type": "SE_ORG",
        "org_nr": org_nr,
        "country": "SE",
        "source": url,
        "momsregistrerad": False,
        "found": False
    }
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        result["found"] = 'företagsinformation' in soup.text.lower()
        result["momsregistrerad"] = 'momsregistrerad' in soup.text.lower()
    log_verification(result)
    return result

# -------------------------------
# 🇮🇸 Iceland Manual Lookup URL
# -------------------------------

def check_iceland_manual_url(company_number):
    result = {
        "type": "IS_MANUAL",
        "country": "IS",
        "company_number": company_number,
        "manual_url": f"https://www.rsk.is/fyrirtaekjaskra/leit/{company_number}"
    }
    log_verification(result)
    return result

# -------------------------------
# 🔘 Menu System
# -------------------------------

def menu():
    print("\n🌍 Nordic VAT Firewall – Interactive Checker")
    print("Choose a country:")
    print("1. 🇪🇺 EU VIES VAT Check")
    print("2. 🇳🇴 Norway (Brreg) Company Check")
    print("3. 🇸🇪 Sweden Allabolag Check")
    print("4. 🇮🇸 Iceland Manual Check Link")
    print("5. ❌ Exit")

    choice = input("Enter option number: ").strip()

    if choice == "1":
        cc = input("Enter EU country code (e.g., DK, FI, DE): ").strip().upper()
        vat = input("Enter VAT number: ").strip()
        print(validate_eu_vat(cc, vat))

    elif choice == "2":
        org = input("Enter Norwegian Org.nr: ").strip()
        print(validate_norwegian_org(org))

    elif choice == "3":
        org = input("Enter Swedish Org.nr: ").strip()
        print(validate_swedish_company(org))

    elif choice == "4":
        comp = input("Enter Icelandic company number: ").strip()
        print(check_iceland_manual_url(comp))

    elif choice == "5":
        print("Goodbye!")
        exit()

    else:
        print("❌ Invalid input. Try again.")

    print("\n----------------------------")
    menu()

# -------------------------------
# 🔁 Start Menu
# -------------------------------

if __name__ == "__main__":
    menu()

