import glob
from bs4 import BeautifulSoup
import re
import datetime
import json


def get_content(soup):
    text = soup.find(id="agendaContent").get_text(separator='\n')
    cleaned_text = '\n'.join(line for line in text.split('\n') if line.strip())
    return cleaned_text

def get_datetime(soup):
    month_map = {
        "januari": 1,
        "februari": 2,
        "maart": 3,
        "april": 4,
        "mei": 5,
        "juni": 6,
        "juli": 7,
        "augustus": 8,
        "september": 9,
        "oktober": 10,
        "november": 11,
        "december": 12
    }
    date_line = soup.find("div", {"class": "agendaDatum"}).get_text().strip()
    match = re.match(r"(.*) ([\d\:]+) tot .*", date_line)
    if match:
        day, mth, year = match[1].split()
        hr, min = match[2].split(':')
        return datetime.datetime(int(year), month_map[mth], int(day), int(hr), int(min))
    return date_line

def filter_content(content: str) -> str:
    """ Remove all lines up to and including the line containing 'liturgie' (case insensitive)
    And remove all lines from the line containing 'Rooster' or 'Vragen'"""
    content_lines = content.split('\n')
    filtered_with_header = []
    filtered_liturgy_only = []
    liturgy_section = False
    for ln in content_lines:
        if any([ln.strip().lower().startswith(keyword) for keyword in 
                  ["rooster", "vragen", "gespreksvragen", "bespreekvragen", "houd me op de hoogte"]]):
                break
        filtered_with_header.append(ln)
        if not liturgy_section:
            liturgy_section = "liturgie" in ln.lower()
        else:
            if "youtube" in ln.lower():
                break
            filtered_liturgy_only.append(ln)
    if not liturgy_section:
        return '\n'.join(filtered_with_header)
    return '\n'.join(filtered_liturgy_only)

def preprocess():
    base_path = "./data/"
    file_list = [f for f in glob.glob(f"{base_path}/raw/service_*.html")]
    print(f"Parsing {len(file_list)} files")
    parsed = []

    for file in file_list:
        with open(file, 'r', encoding="utf-8") as f:
            data = f.read()
        soup = BeautifulSoup(data, 'html.parser')
        date_time = get_datetime(soup)
        content = get_content(soup)
        liturgy = filter_content(content)
        
        parsed.append({
            "date": date_time.strftime("%Y-%m-%d %H:%M"), 
            "liturgy": liturgy, 
            "file": file, 
            "full_content": content,
            })

    with open(f"{base_path}/output/zangdiensten.json", "w") as o:
        json.dump(parsed, o)


if __name__ == "__main__":
    preprocess()