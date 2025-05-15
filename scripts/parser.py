import requests
from bs4 import BeautifulSoup
import time
import json
import re
import csv

BASE_URL = "https://knihi.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )
}


KEYWORDS = [
    "кроў", "жыццё", "вецер", "зямля", "любоў", "смутак", "вясна", "зімa", "сонца",
    "душа", "сэрца", "боль", "шчасце", "святло", "цені", "надзея", "памяць", "воля"
]

MAX_POEM_LENGTH = 2000  # Ограничение максимальной длины текста

AUTHORS = {
    "Jakub_Kolas": "Якуб Колас",
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None

def is_poem_page(url):
    """
    Проверяет, является ли страница стихотворением
    """
    soup = get_soup(url)
    if soup is None:
        return False
    poem_div = soup.find("div", class_="POETRY")
    if poem_div:
        text = poem_div.get_text(strip=True)
        return len(text) <= MAX_POEM_LENGTH
    return False

def parse_poem_page(url):
    """
    Извлекает данные из страницы стихотворений и возвращает словарь с ключами
    """
    soup = get_soup(url)
    if soup is None:
        return None

    h2_tags = soup.find_all("h2")
    if len(h2_tags) >= 2:
        title = h2_tags[1].text.strip().strip('"')
        author = h2_tags[0].text.strip()
    else:
        title = "Без названия"
        author = "Неизвестен"

    year = None
    i_tag = soup.find("i")
    if i_tag:
        date_text = i_tag.get_text(strip=True)
        year_match = re.search(r'(\d{4})', date_text)
        if year_match:
            year = year_match.group(1)

    poem_div = soup.find("div", class_="POETRY")
    text = ""
    if poem_div:
        text = poem_div.get_text(separator="\n").strip()

    result = {
        "title": title,
        "author": author,
        "year": year,
        "url": url,
        "text": text
    }
    return result



def collect_poems(author_key, author_name, limit=101):
    """
    Собирает стихи с фильтрацией по ключевым словам
    """
    author_url = f"{BASE_URL}/{author_key}/"
    soup = get_soup(author_url)
    if soup is None:
        print(f"Не удалось загрузить страницу автора {author_name}")
        return []

    poem_links = set()
    for a in soup.find_all("a", href=True):
        href = a['href'].strip()
        if href.startswith("javascript:") or href.startswith("#") or href.startswith("mailto:") or href == "":
            continue
        if href.startswith(f"/{author_key}/") and href.endswith(".html") and "_book" not in href:
            full_url = BASE_URL + href
            poem_links.add(full_url)

    print(f"{author_name}: найдено уникальных ссылок: {len(poem_links)}")

    poems = []
    count = 0
    for link in poem_links:
        if count >= limit:
            break
        try:
            if not is_poem_page(link):
                continue
            poem = parse_poem_page(link)
            if poem is None:
                continue


            soup_poem = get_soup(link)
            if soup_poem is None:
                continue
            poem_div = soup_poem.find("div", class_="POETRY")
            if poem_div is None:
                continue
            text_lower = poem_div.get_text(separator="\n").lower()
            if any(word in text_lower for word in KEYWORDS):
                poems.append(poem)  # Добавляем без текста
                count += 1
                print(f"{author_name}: собран стих '{poem['title']}'")
            time.sleep(0.3)
        except Exception as e:
            print(f"Ошибка при парсинге {link}: {e}")

    print(f"{author_name}: собрано стихотворений с ключевыми словами: {len(poems)}\n")
    return poems

def save_poems_to_csv(poems, filename="poems_dataset.csv"):
    """Сохраняет полный датасет с текстом стихотворений"""
    with open(filename, "w", encoding="utf-8", newline='') as csvfile:
        fieldnames = ["title", "author", "year", "url", "text"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for poem in poems:
            writer.writerow(poem)
    print(f"Данные сохранены в {filename}")

def main():
    all_poems = []
    for author_key, author_name in AUTHORS.items():
        poems = collect_poems(author_key, author_name, limit=101)
        all_poems.extend(poems)

    save_poems_to_csv(all_poems, filename="poems_dataset.csv")

    with open("poems_dataset.json", "w", encoding="utf-8") as f:
        json.dump(all_poems, f, ensure_ascii=False, indent=4)

    print(f"Всего собрано стихотворений: {len(all_poems)}")


if __name__ == "__main__":
    main()


