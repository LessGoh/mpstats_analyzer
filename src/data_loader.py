"""
Модуль для загрузки и валидации данных из Excel файлов mpstats
"""

import pandas as pd
import streamlit as st
from typing import Optional, List, Tuple
from config.scoring_weights import REQUIRED_COLUMNS


class DataLoader:
    """Класс для загрузки и валидации данных из Excel файлов"""
    
    def __init__(self):
        self.df = None
        self.validation_errors = []
    
    def load_excel_file(self, uploaded_file) -> Optional[pd.DataFrame]:
        """
        Загружает Excel файл и возвращает DataFrame
        
        Args:
            uploaded_file: Загруженный файл из Streamlit
            
        Returns:
            DataFrame или None в случае ошибки
        """
        try:
            # Загружаем Excel файл
            self.df = pd.read_excel(uploaded_file)
            
            # Валидация данных
            if self._validate_data():
                # Очистка данных
                self.df = self._clean_data(self.df)
                return self.df
            else:
                return None
                
        except Exception as e:
            st.error(f"Ошибка при загрузке файла: {str(e)}")
            return None
    
    def _validate_data(self) -> bool:
        """
        Валидирует структуру загруженных данных
        
        Returns:
            True если данные корректны, False иначе
        """
        self.validation_errors = []
        
        # Проверка на пустой DataFrame
        if self.df is None or self.df.empty:
            self.validation_errors.append("Файл пустой или не содержит данных")
            return False
        
        # Проверка наличия обязательных колонок
        missing_columns = self._check_required_columns()
        if missing_columns:
            self.validation_errors.append(
                f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}"
            )
        
        # Проверка наличия данных в колонках
        empty_columns = self._check_empty_columns()
        if empty_columns:
            self.validation_errors.append(
                f"Колонки не содержат данных: {', '.join(empty_columns)}"
            )
        
        # Проверка типов данных
        invalid_data_types = self._check_data_types()
        if invalid_data_types:
            self.validation_errors.append(
                f"Некорректные типы данных в колонках: {', '.join(invalid_data_types)}"
            )
        
        # Вывод ошибок валидации
        if self.validation_errors:
            for error in self.validation_errors:
                st.error(error)
            return False
        
        return True
    
    def _check_required_columns(self) -> List[str]:
        """Проверяет наличие обязательных колонок"""
        missing_columns = []
        df_columns = list(self.df.columns)
        
        for required_col in REQUIRED_COLUMNS:
            if required_col not in df_columns:
                missing_columns.append(required_col)
        
        return missing_columns
    
    def _check_empty_columns(self) -> List[str]:
        """Проверяет колонки на наличие данных"""
        empty_columns = []
        
        for col in REQUIRED_COLUMNS:
            if col in self.df.columns:
                # Проверяем, что в колонке есть хотя бы одно не-NaN значение
                if self.df[col].isna().all():
                    empty_columns.append(col)
        
        return empty_columns
    
    def _check_data_types(self) -> List[str]:
        """Проверяет корректность типов данных в числовых колонках"""
        invalid_columns = []
        
        # Числовые колонки, которые должны содержать числа
        numeric_columns = [
            'Выручка',
            'Средняя цена с продажами',
            'Оборачиваемость, дн.',
            'Процент товаров с движением',
            'Процент продавцов с продажами',
            'Продавцы с продажами'
        ]
        
        for col in numeric_columns:
            if col in self.df.columns:
                # Проверяем, можно ли преобразовать в числа
                try:
                    pd.to_numeric(self.df[col], errors='coerce')
                except Exception:
                    invalid_columns.append(col)
        
        return invalid_columns
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Очищает и подготавливает данные для анализа
        
        Args:
            df: Исходный DataFrame
            
        Returns:
            Очищенный DataFrame
        """
        df_clean = df.copy()
        
        # Преобразование числовых колонок
        numeric_columns = [
            'Выручка',
            'Средняя цена с продажами',
            'Оборачиваемость, дн.',
            'Процент товаров с движением',
            'Процент продавцов с продажами',
            'Продавцы с продажами'
        ]
        
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Удаление строк с пустыми названиями ниш
        if 'Предметы' in df_clean.columns:
            df_clean = df_clean.dropna(subset=['Предметы'])
            df_clean = df_clean[df_clean['Предметы'].str.strip() != '']
        
        # Заполнение пропущенных значений нулями для числовых колонок
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna(0)
        
        # Удаление дубликатов по названию ниши
        if 'Предметы' in df_clean.columns:
            df_clean = df_clean.drop_duplicates(subset=['Предметы'], keep='first')
        
        # Сброс индекса
        df_clean = df_clean.reset_index(drop=True)
        
        return df_clean
    
    def get_data_summary(self) -> dict:
        """
        Возвращает краткую сводку по загруженным данным
        
        Returns:
            Словарь с информацией о данных
        """
        if self.df is None:
            return {}
        
        return {
            'total_niches': len(self.df),
            'columns_count': len(self.df.columns),
            'has_revenue_data': 'Выручка' in self.df.columns and not self.df['Выручка'].isna().all(),
            'total_revenue': self.df['Выручка'].sum() if 'Выручка' in self.df.columns else 0,
            'avg_price': self.df['Средняя цена с продажами'].mean() if 'Средняя цена с продажами' in self.df.columns else 0
        }
