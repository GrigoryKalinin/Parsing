from ai_content_generator import AIContentGenerator
import pandas as pd
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def main():
    """Заполняет пустые поля каталога с помощью ИИ"""
    
    # Проверяем наличие API ключа в .env
    env_api_key = os.getenv('API_KEY')
    
    if env_api_key:
        print(f"Найден API ключ в .env: {env_api_key[:20]}...")
        use_env = input("Использовать ключ из .env? (y/n): ").lower().strip()
        
        if use_env == 'y':
            api_key = env_api_key
            print("Используется API ключ из .env")
        else:
            api_key = input("Введите ваш API ключ: ").strip()
    else:
        print("Файл .env не найден или API_KEY не указан")
        api_key = input("Введите ваш API ключ: ").strip()
    
    if not api_key:
        print("API ключ не указан. Завершение работы.")
        return
    
    # Загружаем каталог
    try:
        catalog_df = pd.read_csv('catalog6_formatted.csv', sep=';', encoding='utf-8-sig')
        print(f"Загружен каталог с {len(catalog_df)} товарами")
    except FileNotFoundError:
        print("Файл catalog6_formatted.csv не найден. Сначала запустите final_update_catalog_format_description.py")
        return
    
    # Создаем генератор ИИ
    ai_generator = AIContentGenerator(api_key)
    
    # Подсчитываем пустые поля
    empty_fields = ['SEO Titile', 'SEO Meta Keywords', 'SEO Meta Description', 'Краткое описание']
    total_empty = 0
    
    print("\nСтатистика пустых полей:")
    for field in empty_fields:
        empty_count = catalog_df[field].isna().sum() + (catalog_df[field] == '').sum()
        total_empty += empty_count
        print(f"  {field}: {empty_count} пустых")
    
    print(f"\nВсего пустых полей: {total_empty}")
    
    if total_empty == 0:
        print("Все поля уже заполнены!")
        return
    
    # Подтверждение
    proceed = input(f"\nЗаполнить {total_empty} пустых полей? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Отменено.")
        return
    
    # Обработка товаров
    print("\nНачинаю обработку...")
    processed = 0
    
    for index, row in catalog_df.iterrows():
        print(f"Товар {index + 1}/{len(catalog_df)}: {row['Наименование'][:40]}...")
        
        # Генерируем контент
        generated_content = ai_generator.process_catalog_row(row)
        
        # Обновляем DataFrame
        updated_fields = []
        for field, content in generated_content.items():
            if content:
                catalog_df.at[index, field] = content
                updated_fields.append(field)
                processed += 1
        
        if updated_fields:
            print(f"  Обновлено: {', '.join(updated_fields)}")
        
        # Промежуточное сохранение каждые 10 товаров
        if (index + 1) % 10 == 0:
            catalog_df.to_csv('catalog6_ai_filled.csv', sep=';', index=False, encoding='utf-8-sig')
            print(f"  Промежуточное сохранение ({index + 1} товаров)")
    
    # Финальное сохранение
    catalog_df.to_csv('catalog6_ai_filled.csv', sep=';', index=False, encoding='utf-8-sig')
    print(f"\nГотово! Обработано {processed} полей. Результат сохранен в catalog6_ai_filled.csv")

if __name__ == "__main__":
    main()