import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud

KEYWORDS = [
    "кроў", "жыццё", "вецер", "зямля", "любоў", "смутак", "вясна", "зімa", "сонца",
    "душа", "сэрца", "боль", "шчасце", "святло", "цені", "надзея", "памяць", "воля"
]
# Переводы ключевых слов
BEL_RU = {
    "кроў": "кровь", "жыццё": "жизнь", "вецер": "ветер", "зямля": "земля", "любоў": "любовь",
    "смутак": "грусть", "вясна": "весна", "зімa": "зима", "сонца": "солнце", "душа": "душа",
    "сэрца": "сердце", "боль": "боль", "шчасце": "счастье", "святло": "свет", "цені": "тени",
    "надзея": "надежда", "памяць": "память", "воля": "воля"
}

# Тематические группы ключевых слов
THEME_GROUPS = {
    "Природа": ["вецер", "зямля", "вясна", "зімa", "сонца"],
    "Чувства": ["любоў", "смутак", "шчасце", "боль", "надзея", "воля", "кроў", "святло"],
    "Душевные состояния": ["жыццё", "душа", "сэрца", "цені", "памяць"],
}

def load_poems_texts(json_filename):
    with open(json_filename, 'r', encoding='utf-8') as f:
        poems = json.load(f)
    return poems

def count_keywords_frequency(texts, keywords):
    counter = Counter()
    for text in texts:
        text_lower = text.lower()
        for word in keywords:
            count = text_lower.count(word.lower())
            if count > 0:
                counter[word] += count
    return counter

def count_frequency_by_groups(texts, theme_groups):
    group_freq = {group: 0 for group in theme_groups}
    for text in texts:
        text_lower = text.lower()
        for group, words in theme_groups.items():
            for word in words:
                group_freq[group] += text_lower.count(word)
    return group_freq

def plot_bar(freq_counter, title='Частота ключевых слов'):
    words = list(freq_counter.keys())
    counts = list(freq_counter.values())

    plt.figure(figsize=(12,6))
    bars = plt.bar(words, counts, color='skyblue')
    plt.title(title)
    plt.xlabel('Категории')
    plt.ylabel('Количество вхождений')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, str(height), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

def plot_wordcloud(freq_dict, title='Облако слов'):
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        collocations=False
    ).generate_from_frequencies(freq_dict)

    plt.figure(figsize=(12,6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.show()

def plot_length_distribution(df):
    df_filtered = df.dropna(subset=['year', 'text']).copy()
    df_filtered['text_length'] = df_filtered['text'].apply(len)

    plt.figure(figsize=(12,6))
    grouped = df_filtered.groupby('year')['text_length'].mean()
    grouped.plot(kind='bar', color='coral')
    plt.title('Средняя длина стихотворений по годам')
    plt.xlabel('Год')
    plt.ylabel('Средняя длина (символы)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_year_distribution(df):
    plt.figure(figsize=(12,6))
    year_counts = df['year'].dropna().value_counts().sort_index()
    plt.bar(year_counts.index.astype(str), year_counts.values, color='skyblue')
    plt.title('Распределение количества стихотворений по годам')
    plt.xlabel('Год публикации')
    plt.ylabel('Количество стихотворений')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def main():
    poems = load_poems_texts('poems_dataset.json')
    texts = [poem.get('text', '') for poem in poems]

    # Частоты по всем ключевым словам
    freq_counter = count_keywords_frequency(texts, KEYWORDS)
    if not freq_counter:
        print("Ключевые слова не найдены в текстах.")
        return

    freq_counter_ru = {BEL_RU[word]: count for word, count in freq_counter.items()}
    freq_counter_ru = dict(sorted(freq_counter_ru.items(), key=lambda x: x[1], reverse=True))
    plot_bar(freq_counter_ru, title='Частота ключевых слов в стихах')

    # Частоты по тематическим группам
    freq_by_theme = count_frequency_by_groups(texts, THEME_GROUPS)
    plot_bar(freq_by_theme, title='Частота ключевых слов по тематическим группам')

    # Облако слов топ 15 частотных вне ключевых
    all_words = []
    for text in texts:
        words = text.lower().split()
        all_words.extend(words)

    filtered_words = [w for w in all_words if len(w) > 4 and w not in KEYWORDS]
    counter_all = Counter(filtered_words)
    top15_non_keywords = dict(counter_all.most_common(15))
    plot_wordcloud(top15_non_keywords, title='Облако слов: топ 15 частотных слов вне ключевых')

    # Облако слов топ 15 самых редких слов
    rare_words = [item for item in counter_all.items() if item[1] > 0]
    rare_words_sorted = sorted(rare_words, key=lambda x: x[1])
    top15_rare_words = dict(rare_words_sorted[:15])
    plot_wordcloud(top15_rare_words, title='Облако слов: топ 15 самых редких слов')

    # Анализ по длине и годам 
    df = pd.DataFrame(poems)
    if 'year' in df.columns and 'text' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
        plot_length_distribution(df)
        plot_year_distribution(df)

if __name__ == "__main__":
    main()
