import requests
import json
import pandas as pd
import time
import re
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class AIContentGenerator:
    def __init__(self, api_key: str = None, model: str = None):
        """
        Инициализация генератора контента
        
        Args:
            api_key: API ключ для OpenRouter (если None, загружается из .env)
            model: Модель для использования (если None, загружается из .env)
        """
        self.api_key = api_key or os.getenv('API_KEY')
        self.model = model or os.getenv('MODEL', 'deepseek/deepseek-chat')
        
        if not self.api_key:
            raise ValueError("Не указан API ключ. Укажите в параметрах или в файле .env")
        
        self.delay = 1  # Задержка между запросами в секундах
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate_seo_title(self, name: str, category: str, price: str) -> str:
        """Генерирует SEO заголовок для товара"""
        prompt = f"""
        Создай SEO заголовок для товара:
        Название: {name}
        Категория: {category}
        Цена: {price} руб.
        
        Требования:
        - Длина до 60 символов
        - Включи ключевые слова
        - Привлекательный для поисковых систем
        - На русском языке
        
        Верни только заголовок без дополнительного текста.
        """
        
        return self._make_request(prompt)
    
    def generate_meta_description(self, name: str, category: str, price: str, description: str = "") -> str:
        """Генерирует META описание для товара"""
        desc_part = f" {description[:100]}..." if description else ""
        
        prompt = f"""
        Создай META описание для товара:
        Название: {name}
        Категория: {category}
        Цена: {price} руб.
        Описание: {desc_part}
        
        Требования:
        - Длина 150-160 символов
        - Привлекательное для пользователей
        - Включи цену и основные характеристики
        - На русском языке
        
        Верни только описание без дополнительного текста.
        """
        
        return self._make_request(prompt)
    
    def generate_meta_keywords(self, name: str, category: str) -> str:
        """Генерирует META ключевые слова"""
        prompt = f"""
        Создай META ключевые слова для товара:
        Название: {name}
        Категория: {category}
        
        Требования:
        - 5-10 ключевых слов через запятую
        - Релевантные товару
        - На русском языке
        - Без повторений
        
        Верни только ключевые слова через запятую.
        """
        
        return self._make_request(prompt)
    
    def generate_h1(self, name: str, category: str) -> str:
        """Генерирует H1 заголовок"""
        prompt = f"""
        Создай H1 заголовок для товара:
        Название: {name}
        Категория: {category}
        
        Требования:
        - Краткий и информативный
        - До 70 символов
        - Включи основные ключевые слова
        - На русском языке
        
        Верни только H1 заголовок без дополнительного текста.
        """
        
        return self._make_request(prompt)
    
    def generate_short_description(self, name: str, category: str, price: str) -> str:
        """Генерирует краткое описание товара"""
        prompt = f"""
        Создай краткое описание для товара:
        Название: {name}
        Категория: {category}
        Цена: {price} руб.
        
        Требования:
        - 1-2 предложения
        - До 200 символов
        - Основные преимущества товара
        - Привлекательно для покупателя
        - На русском языке
        
        Верни только краткое описание без дополнительного текста.
        """
        
        return self._make_request(prompt)
    
    def generate_url_slug(self, name: str, artikul: str) -> str:
        """Генерирует URL slug для товара"""
        # Простая транслитерация и очистка
        name_clean = re.sub(r'[^\w\s-]', '', name.lower())
        name_clean = re.sub(r'[-\s]+', '-', name_clean)
        
        # Простая транслитерация основных символов
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        result = ""
        for char in name_clean:
            result += translit_map.get(char, char)
        
        # Добавляем артикул в конец
        result = f"{result}-{artikul}".strip('-')
        return result[:100]  # Ограничиваем длину
    
    def _make_request(self, prompt: str) -> str:
        """Выполняет запрос к OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Ты эксперт по SEO и созданию контента для интернет-магазинов."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"].strip()
                # Убираем теги <think> если есть
                result = result.replace('<think>', '').replace('</think>', '')
                time.sleep(self.delay)  # Задержка между запросами
                return result
            else:
                print(f"Ошибка API: {response.status_code}")
                return ""
            
        except Exception as e:
            print(f"Ошибка при запросе к API: {e}")
            return ""
    
    def process_catalog_row(self, row: pd.Series) -> Dict[str, str]:
        """Обрабатывает одну строку каталога и генерирует весь контент"""
        name = str(row['Наименование'])
        category = str(row['Категория: 1'])
        price = str(row['Цена'])
        artikul = str(row['Артикул'])
        description = str(row.get('Описание', ''))
        
        results = {}
        
        # Генерируем только если поле пустое
        if pd.isna(row.get('SEO Titile')) or row.get('SEO Titile') == '':
            results['SEO Titile'] = self.generate_seo_title(name, category, price)
            
        if pd.isna(row.get('SEO Meta Description')) or row.get('SEO Meta Description') == '':
            results['SEO Meta Description'] = self.generate_meta_description(name, category, price, description)
            
        if pd.isna(row.get('SEO Meta Keywords')) or row.get('SEO Meta Keywords') == '':
            results['SEO Meta Keywords'] = self.generate_meta_keywords(name, category)
            
        if pd.isna(row.get('SEO H1')) or row.get('SEO H1') == '':
            results['SEO H1'] = self.generate_h1(name, category)
            
        if pd.isna(row.get('Краткое описание')) or row.get('Краткое описание') == '':
            results['Краткое описание'] = self.generate_short_description(name, category, price)
        
        return results

def fill_empty_fields_with_ai(csv_file: str, api_key: str, output_file: str = None, batch_size: int = 10):
    """
    Заполняет пустые поля в каталоге с помощью ИИ
    
    Args:
        csv_file: Путь к CSV файлу
        api_key: API ключ OpenAI
        output_file: Путь для сохранения результата (по умолчанию добавляется _ai_filled)
        batch_size: Количество строк для обработки за раз
    """
    if output_file is None:
        output_file = csv_file.replace('.csv', '_ai_filled.csv')
    
    # Загружаем каталог
    df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
    
    # Инициализируем генератор
    ai_generator = AIContentGenerator(api_key)
    
    print(f"Начинаю обработку {len(df)} товаров...")
    
    # Обрабатываем по батчам
    for i in range(0, len(df), batch_size):
        batch_end = min(i + batch_size, len(df))
        print(f"Обрабатываю товары {i+1}-{batch_end}...")
        
        for idx in range(i, batch_end):
            row = df.iloc[idx]
            
            # Генерируем контент для пустых полей
            generated_content = ai_generator.process_catalog_row(row)
            
            # Обновляем DataFrame
            for field, content in generated_content.items():
                if content:  # Только если контент был сгенерирован
                    df.at[idx, field] = content
                    print(f"  {field}: {content[:50]}...")
        
        # Сохраняем промежуточный результат
        df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
        print(f"Промежуточный результат сохранен в {output_file}")
    
    print(f"Обработка завершена! Результат сохранен в {output_file}")
    return df

if __name__ == "__main__":
    # Пример использования
    API_KEY = "your-openai-api-key-here"  # Замените на ваш API ключ
    
    # Заполняем пустые поля
    fill_empty_fields_with_ai(
        csv_file="catalog6_new.csv",
        api_key=API_KEY,
        output_file="catalog6_ai_filled.csv",
        batch_size=5  # Обрабатываем по 5 товаров за раз
    )