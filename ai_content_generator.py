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
    
    def generate_description_from_tech(self, row: pd.Series, tech_data: dict) -> str:
        """Генерирует описание товара на основе технических характеристик"""
        name = str(row['Наименование'])
        category = str(row['Категория: 1'])
        
        tech_text = ""
        if 'tech' in tech_data:
            tech_clean = re.sub(r'<[^>]+>', '', tech_data['tech'])
            tech_text += f"Технические характеристики: {tech_clean[:300]}..."
        
        if 'equipment' in tech_data:
            equipment_clean = re.sub(r'<[^>]+>', '', tech_data['equipment'])
            tech_text += f" Комплектация: {equipment_clean[:200]}..."
        
        prompt = f"""
        Создай описание товара на основе технических данных:
        Название: {name}
        Категория: {category}
        Технические данные: {tech_text}
        
        Требования:
        - 2-3 абзаца
        - Описание назначения и преимуществ
        - Основные технические особенности
        - Привлекательно для покупателя
        - На русском языке
        
        Верни только описание без дополнительного текста.
        """
        
        return self._make_request(prompt, max_tokens=300)
    
    def _make_request(self, prompt: str, max_tokens: int = 150) -> str:
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
                "max_tokens": max_tokens,
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
            

            
        if pd.isna(row.get('Краткое описание')) or row.get('Краткое описание') == '':
            results['Краткое описание'] = self.generate_short_description(name, category, price)
        
        return results

