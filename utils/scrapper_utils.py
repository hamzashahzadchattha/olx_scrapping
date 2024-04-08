import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os
from database.helper import create_ad
from utils.http import bad_request
from database.db import db


load_dotenv("../.env")  

class OlxScraper:
    def __init__(self, data_input):
        self.data = data_input
        self.bearer_token = os.getenv("BEARER_TOKEN")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.refresh_token_endpoints = os.getenv("REFRESH_TOKEN_ENDPOINT")

    @staticmethod
    def extract_iid_from_url(url):
        match = re.search(r'iid-(\d+)', url)
        return int(match.group(1)) if match else None


    @staticmethod
    def convert_relative_time_to_datetime(relative_time):
        TIME_UNITS = {
        'minute': 1,
        'hour': 60,
        'day': 24 * 60,
        'week': 7 * 24 * 60,
        'year': 365 * 24 * 60 
        }
        now = datetime.now()
        relative_time = relative_time.strip()

        time_pattern = r'^(\d+)\s*([a-z]+)\s*ago$'
        match = re.match(time_pattern, relative_time, re.IGNORECASE)

        if match:
            value = int(match.group(1))
            unit = match.group(2).rstrip('s').lower()

            if unit in TIME_UNITS:
                delta = timedelta(minutes=value * TIME_UNITS[unit])
                result_datetime = now - delta
                return result_datetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                print(f"Unsupported time unit: {unit}")
        else:
            print(f"Error parsing relative time string: {relative_time}")

        return now.strftime('%Y-%m-%d %H:%M:%S')
    
    def refresh_token_api(self):
        payload = {
            "grant_type": "refresh_token",
            "client_id": "frontend",
            "scope": "openid",
            "refresh_token": self.refresh_token
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(self.refresh_token_endpoints, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            print("data id Token", data["id_token"])
            return data["id_token"]
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Error refreshing token: {e}")
            return bad_request(e)


    def scrape_olx(self):
        url = self.data["website"]
        print("URL",url)
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            for article in soup.find_all("article", class_="_7e3920c1"):

                link = article.find("a")["href"]
                price_element = article.select_one("span._95eae7db")
                title_element = article.select_one("h2.a5112ca8")
                kilometer_element = article.find("span", class_="e021be12")
                ad_image_element = article.find("img", class_="_76b7f29a")
                location_element = article.select_one("span[aria-label='Location']")
                creation_date_element = article.select_one("span[aria-label='Creation date']")

                if None in (price_element, title_element, kilometer_element, ad_image_element, location_element, creation_date_element):
                    continue

                price = price_element.text.strip()
                title = title_element.text.strip()
                kilometer_driven = kilometer_element.text.strip()
                ad_image_url = ad_image_element["src"]
                location = location_element.text.strip('•')
                creation_date = creation_date_element.text.strip()

                IdInt = self.extract_iid_from_url(link)
                creation_date = self.convert_relative_time_to_datetime(creation_date)

                owner_info_url = f"https://www.olx.com.pk/api/listing/{IdInt}/contactInfo/"
                headers = {"Authorization": f"Bearer {self.bearer_token}"}
                owner_info_response = requests.get(owner_info_url, headers=headers)

                if owner_info_response.status_code == 401:
                    print("refreshingg...")
                    new_token = self.refresh_token_api()
                    if new_token:
                        self.bearer_token = new_token
                        headers = {"Authorization": f"Bearer {self.bearer_token}"}
                        owner_info_response = requests.get(owner_info_url, headers=headers)

                if owner_info_response.status_code == 200:
                    owner_info_data = owner_info_response.json()
                    name = owner_info_data.get("name")
                    mobile = owner_info_data.get("mobile")
                    whatsapp = owner_info_data.get("whatsapp")
                    print("if_Owner_info : ", title, price, location, creation_date, ad_image_url, kilometer_driven, name, mobile, whatsapp)

                    create_ad(db,{
                        "title": title,
                        "price": price,
                        "location": location,
                        "ad_posted_at": creation_date,
                        "ad_image": ad_image_url,
                        "kilometer_driven": kilometer_driven,
                        "owner_info": {
                            "name": name,
                            "mobile": mobile,
                            "whatsapp": whatsapp
                        }
                    })
            return True

        except (requests.RequestException, AttributeError, json.JSONDecodeError) as e:
            return bad_request(e)
# if __name__ == "__main__":
#     jsonpath = "./DataWrapped.json"
#     data = OlxScraper.load_json(jsonpath)
#     refresh_token_endpoints = "https://auth.olx.com.pk/auth/realms/olx-pk/protocol/openid-connect/token"
#     refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlNGU1MjI1MS05M2U0LTQwYTItYjQ3Yy01NTBkYWY5ODZhN2EifQ.eyJpYXQiOjE3MTI1MjgxMzMsImp0aSI6ImIwYzI5MTczLTFmNDctNDZlNi1iMGUwLTM5OWJhYWM2NTE2OSIsImlzcyI6Imh0dHBzOi8vYXV0aC5vbHguY29tLnBrL2F1dGgvcmVhbG1zL29seC1wayIsImF1ZCI6Imh0dHBzOi8vYXV0aC5vbHguY29tLnBrL2F1dGgvcmVhbG1zL29seC1wayIsInN1YiI6ImYxNDVkODRmLTgyYTEtNDdkMS04MWRiLTc0NWYxYWI2MGY3YiIsInR5cCI6Ik9mZmxpbmUiLCJhenAiOiJmcm9udGVuZCIsInNlc3Npb25fc3RhdGUiOiI1MzQ0ODRiMi01OTQzLTRiNTQtYWI5OS0xMjhlNjdhNTkzOWEiLCJzY29wZSI6Im9wZW5pZCBvZmZsaW5lX2FjY2VzcyByZWFsbV9yb2xlcyB1c2VyX3Byb2ZpbGUiLCJzaWQiOiI1MzQ0ODRiMi01OTQzLTRiNTQtYWI5OS0xMjhlNjdhNTkzOWEifQ.YjDYE2O8p-obulLbN6XVpbhqzql43KvEw3a3NQ--iik"
#     bearer_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTNG1Dd1NGbGR0SmEyMjFVampGM2NyeVg5bThhOFcyVlpBR2poS3B4WlNzIn0.eyJleHAiOjE3MTI1MzcxMTMsImlhdCI6MTcxMjUzNjIxMywiYXV0aF90aW1lIjoxNzEyNTIzOTI4LCJqdGkiOiI5NWFhYmQ0My03NmQ1LTQyYTctYTBhYS04NTYzNGE4ZmMyM2QiLCJpc3MiOiJodHRwczovL2F1dGgub2x4LmNvbS5way9hdXRoL3JlYWxtcy9vbHgtcGsiLCJhdWQiOiJmcm9udGVuZCIsInN1YiI6ImYxNDVkODRmLTgyYTEtNDdkMS04MWRiLTc0NWYxYWI2MGY3YiIsInR5cCI6IklEIiwiYXpwIjoiZnJvbnRlbmQiLCJzZXNzaW9uX3N0YXRlIjoiNTM0NDg0YjItNTk0My00YjU0LWFiOTktMTI4ZTY3YTU5MzlhIiwiYXRfaGFzaCI6IjBRblZmRVItSERmdVUzSlhkT3dWNUEiLCJhY3IiOiIxIiwic2lkIjoiNTM0NDg0YjItNTk0My00YjU0LWFiOTktMTI4ZTY3YTU5MzlhIiwicmVhbG1fcm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsInVzZXIiXSwiaWRlbnRpdHlfcHJvdmlkZXJzIjpbImdvb2dsZSJdLCJuYW1lIjoiXHVEODNEXHVEQzREIiwicGhvbmVfbnVtYmVyIjoiKzkyMzA2NzkyMjY3MSIsImV4dGVybmFsX2lkIjoiZjE0NWQ4NGYtODJhMS00N2QxLTgxZGItNzQ1ZjFhYjYwZjdiIiwiZW1haWwiOiJncmVhdGNoYXR0aGFAZ21haWwuY29tIiwiaXNfcGFzc3dvcmRsZXNzX2xvZ2luIjp0cnVlfQ.GKIVsfziy9M-Uf4mYnbhyd8bdzdidP9SoovcUAnwP3Plty7heb-2xrQ9lhrR7GciqvkyZhHJgoeW5VrjqoW-v8YJwQNIxyfN8MGlkK9OP5IodDulYU0GSJjMBSQ7NBpM5yJIuETYp_Ur5GvXwY1BiLb9WD-BZNIWvbZgfhrT_0ifYXbRsTwXJaC7BbHBFQZFUUmGt4ervYrNxeSqk7LYI-hbOHgZh3rkuwYDatrIhk1dalwv-7McZj_qp2bDpoPh0SsZea_A8RUXAXSWo4CrnNciy9ThL0r6dhoG7OYFRjbMgCgzw_-2-5iEfx0Xxrai4Rls9OEH2ZTSwrLC3szJ-g"
#     olx_scraper = OlxScraper(data, bearer_token)
#     olx_scraper.scrape_olx()
