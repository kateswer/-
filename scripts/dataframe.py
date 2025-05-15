import pandas as pd

def main():

    csv_filename = "poems_dataset.csv"
    df = pd.read_csv(csv_filename, encoding="utf-8")

    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')

    # Создание второй таблицы без колонки text, но с 'text_length'
    df_no_text = df.drop(columns=['text'], errors='ignore')

    df_no_text.to_csv("poems_dataset_no_text.csv", index=False, encoding='utf-8')

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 50)

    print(" Первые 10 строк с текстом ")
    print(df.head(10))

    print("\n Информация о таблице с текстом ")
    print(df.info())

    print("\n Количество пропусков в колонках таблицы с текстом ")
    print(df.isna().sum())

    print("\n Первые 10 строк с длиной текста ")
    print(df_no_text.head(10))

    print("\n Информация таблице с длиной текста ")
    print(df_no_text.info())

    print("\n Статистика по числовым колонкам таблицы с длиной текста ")
    print(df.describe())

    print("\n Количество пропусков в колонках таблицы с длиной текста ")
    print(df.isna().sum())

if __name__ == "__main__":
    main()

