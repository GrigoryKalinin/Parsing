import pandas as pd
import re

def clean_ai_generated_content(csv_file: str, output_file: str = None):
    """
    Очищает AI сгенерированный контент от нежелательных символов
    
    Args:
        csv_file: Путь к CSV файлу для очистки
        output_file: Путь для сохранения (по умолчанию перезаписывает исходный)
    """
    if output_file is None:
        output_file = csv_file
    
    # Загружаем каталог
    df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
    
    # Поля для очистки
    fields_to_clean = ['SEO Titile', 'SEO Meta Keywords', 'SEO Meta Description', 'SEO H1', 'Краткое описание']
    
    print(f"Очищаю {len(df)} товаров...")
    
    cleaned_count = 0
    
    for field in fields_to_clean:
        if field in df.columns:
            for index, value in df[field].items():
                if pd.notna(value) and value != '':
                    original_value = str(value)
                    
                    # Убираем звездочки и кавычки
                    cleaned_value = original_value.replace('*', '').replace('"', '').replace("'", '')
                    
                    # Убираем лишние пробелы
                    cleaned_value = re.sub(r'\s+', ' ', cleaned_value).strip()
                    
                    if cleaned_value != original_value:
                        df.at[index, field] = cleaned_value
                        cleaned_count += 1
                        print(f"Очищено {field} для товара {index + 1}: {original_value[:30]}... -> {cleaned_value[:30]}...")
    
    # Сохраняем результат
    df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
    print(f"\nОчистка завершена! Очищено {cleaned_count} полей. Результат сохранен в {output_file}")

if __name__ == "__main__":
    clean_ai_generated_content('catalog6_ai_filled.csv', 'catalog6_ai_cleaned.csv')