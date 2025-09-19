from ai_content_generator import AIContentGenerator
import pandas as pd
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_ai_generator():
    """Тестирует генератор ИИ контента"""
    
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
        print("API ключ не указан. Тест отменен.")
        return
    
    # Создаем генератор
    ai_gen = AIContentGenerator(api_key)
    
    # Тестовые данные
    test_product = {
        'Наименование': 'Proma DSO-1000 деревообрабатывающий токарный станок',
        'Категория: 1': 'Каталог >> Деревообрабатывающее оборудование >> Токарные станки по дереву',
        'Цена': '18404,00',
        'Артикул': '25406130',
        'Описание': 'Токарный станок для обработки древесины'
    }
    
    print("Тестирую генерацию контента для товара:")
    print(f"Название: {test_product['Наименование']}")
    print(f"Категория: {test_product['Категория: 1']}")
    print(f"Цена: {test_product['Цена']} руб.")
    print("-" * 80)
    
    # Тестируем каждую функцию
    print("\n1. Генерирую SEO заголовок...")
    seo_title = ai_gen.generate_seo_title(
        test_product['Наименование'], 
        test_product['Категория: 1'], 
        test_product['Цена']
    )
    print(f"SEO Title: {seo_title}")
    
    print("\n2. Генерирую META описание...")
    meta_desc = ai_gen.generate_meta_description(
        test_product['Наименование'], 
        test_product['Категория: 1'], 
        test_product['Цена'],
        test_product['Описание']
    )
    print(f"META Description: {meta_desc}")
    
    print("\n3. Генерирую META ключевые слова...")
    meta_keywords = ai_gen.generate_meta_keywords(
        test_product['Наименование'], 
        test_product['Категория: 1']
    )
    print(f"META Keywords: {meta_keywords}")
    
    print("\n4. Генерирую краткое описание...")
    short_desc = ai_gen.generate_short_description(
        test_product['Наименование'], 
        test_product['Категория: 1'], 
        test_product['Цена']
    )
    print(f"Краткое описание: {short_desc}")
    
    print("\n5. Тестирую генерацию описания из tech данных...")
    test_tech_data = {
        'tech': '<table><tr><td>Мощность двигателя</td><td>370 Вт</td></tr><tr><td>Диаметр обработки</td><td>305 мм</td></tr><tr><td>Длина обработки</td><td>1000 мм</td></tr></table>',
        'equipment': '<table><tr><td>Станок</td><td>1 шт</td></tr><tr><td>Подручник</td><td>1 шт</td></tr><tr><td>Планшайба</td><td>1 шт</td></tr></table>'
    }
    
    test_row = pd.Series(test_product)
    tech_description = ai_gen.generate_description_from_tech(test_row, test_tech_data)
    print(f"Описание из tech данных: {tech_description}")
    
    print("\n" + "=" * 80)
    print("Тест завершен!")
    
    # Предлагаем сохранить результат
    save_test = input("\nСохранить результат тестирования в файл? (y/n): ").lower().strip()
    if save_test == 'y':
        test_results = {
            'Поле': ['SEO Title', 'META Description', 'META Keywords', 'Краткое описание', 'Описание из tech'],
            'Сгенерированный контент': [seo_title, meta_desc, meta_keywords, short_desc, tech_description]
        }
        
        df_test = pd.DataFrame(test_results)
        df_test.to_csv('ai_test_results.csv', sep=';', index=False, encoding='utf-8-sig')
        print("Результаты тестирования сохранены в ai_test_results.csv")

if __name__ == "__main__":
    test_ai_generator()