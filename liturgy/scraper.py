import argparse
import os
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm 
import requests
import json

def read_cookie(filepath = "./auth_cookie.txt"):
    # get the cookie from web browser and paste it in a text file. Should look something like this: 
    # kerkspot=<some characters>; ident=<some characters>; s=1
    with open(filepath, 'r') as f:
        auth_cookie = f.readline().strip()
    return auth_cookie


def get_agenda(headers, year: int, month: int):
    url = f"https://www.immanuelkerkdelft.nl/go/gemeente/agenda/?d={month}|{year}&g="
    return requests.request("GET", url, headers=headers)


def get_event_ids_month(soup):
        event_ids = []
        all_services = soup.find_all("div", class_="show-info soortID1393")
        for service_event in all_services:
            event_id_text = service_event.get('id')
            event_id_match = re.match(r"eventID(\d+)", event_id_text)
            if event_id_match:
                event_ids.append(event_id_match[1])
        return event_ids


def get_page(headers, id):
    url = f"https://www.immanuelkerkdelft.nl/agenda/{id}/"
    headers = {'Cookie': auth_cookie}
    return requests.request("GET", url, headers=headers)


def scrape_message_ids(headers):
    print("Scraping calendar for events...")
    base_path = "./data/raw/"
    month_from = 1
    year_from = 2023
    month_to = 1
    year_to = 2025

    year_month = []
    for year in range(year_from, year_to+1):
        for month in range(month_from if year == year_from else 1, (month_to if year==year_to else 12)+1):
            year_month.append((year, month))

    for year, month in tqdm(year_month):
        req = get_agenda(headers, year, month)
        if req.status_code == 200:            
            with open(f"{base_path}/agenda_{year}_{month}.html", "w") as outp_file:
                outp_file.write(req.text)
        elif req.status_code == 401:
            raise ValueError("Received HTTP 401. Your auth cookie might be expired.")
        else: 
            raise ValueError(f"Unkown error: received {req.status_code}")
    
    ids_to_search = []
    file_list = sorted(Path(base_path).glob("agenda_*"))
    for file in tqdm(file_list):
        with open(file, 'r') as f:
            data = f.read()   
            soup = BeautifulSoup(data, 'html.parser')
            event_ids = get_event_ids_month(soup)
            ids_to_search.extend(event_ids)

    with open(f'{base_path}/event_ids.json', 'w') as f:
        json.dump(ids_to_search, f) 
    print("Done.")


def scrape_liturgies(headers):
    base_path = "./data/raw/"
    with open(f'{base_path}/event_ids.json', 'r') as f:
        ids_to_search = json.load(f)

    found_ids = []
    for i in tqdm(ids_to_search):
        r = get_page(headers, i)
        if r.status_code == 200:
            found_ids.append(i)
            with open(f"{base_path}/service_{i}.html", 'w', encoding="utf-8") as o:
                o.write(r.text)
    
    print(f"Found ids: {found_ids}")
    print(f"Max: {max(found_ids)}, min: {min(found_ids)}")

if __name__ == "__main__":
     
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-message-ids', action="store_true", help="Don't scrape the agenda for events")
    parser.add_argument('--no-liturgy', action="store_true", help="Don't scrape the liturgies")
    args = parser.parse_args()

    base_path = "./data/raw/"
    os.makedirs(base_path, exist_ok=True)
    auth_cookie = read_cookie()
    headers = {'Cookie': auth_cookie}

    if args.no_message_ids:
        print("skipping message id scraping")
    else:
        scrape_message_ids(headers)

    if args.no_liturgy:
        print("skipping liturgy scraping")
    else:
        print("Scraping liturgies...")
        scrape_liturgies(headers)