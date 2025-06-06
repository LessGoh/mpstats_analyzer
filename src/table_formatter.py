"""
Модуль для форматирования таблицы результатов анализа ниш
"""

import pandas as pd
import streamlit as st
from typing import Dict, List


class TableFormatter:
    """Класс для форматирования и отображения таблицы результатов"""
    
    def __init__(self):
        self.display_columns = [
            'Позиция',
            'Предметы', 
            'Общий балл',
            'Категория',
            'Выручка',
            'Средняя цена с продажами',
            'Оборачиваемость, дн.',
            '% товаров с движением',
            '% продавцов с продажами',
            'Выручка на продавца'
        ]
        
        self.column_names = {
            'Позиция': '#',
            'Предметы': 'Ниша',
            'Общий балл': 'Балл',
            'Категория': 'Оценка',
            'Выручка': 'Выручка',
            'Средняя цена с продажами': 'Ср. цена',
            'Оборачиваемость, дн.': 'Оборач.',
            '% товаров с движением': '% тов. движ.',
            '% продавцов с продажами': '% прод. прод.',
            'Выручка на продавца': 'Выр./прод.'
        }
    
    def format_display_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Форматирует DataFrame для отображения в Streamlit
        
        Args:
            df: DataFrame с данными ниш
            
        Returns:
            Отформатированный DataFrame для отображения
        """
        # Выбираем только нужные колонки
        df_display = df[self.display_columns].copy()
        
        # Переименовываем колонки
        df_display = df_display.rename(columns=self.column_names)
        
        # Форматируем числовые значения
        df_display = self._format_numeric_columns(df_display)
        
        # Добавляем эмодзи к категориям
        df_display = self._add_category_emojis(df_display, df)
        
        return df_display
    
    def _format_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Форматирует числовые колонки для лучшего отображения"""
        df_formatted = df.copy()
        
        # Форматируем выручку
        if 'Выручка' in df_formatted.columns:
            df_formatted['Выручка'] = df_formatted['Выручка'].apply(self._format_currency)
        
        # Форматируем среднюю цену
        if 'Ср. цена' in df_formatted.columns:
            df_formatted['Ср. цена'] = df_formatted['Ср. цена'].apply(self._format_price)
        
        # Форматируем оборачиваемость
        if 'Оборач.' in df_formatted.columns:
            df_formatted['Оборач.'] = df_formatted['Оборач.'].apply(self._format_days)
        
        # Форматируем проценты
        percentage_columns = ['% тов. движ.', '% прод. прод.']
        for col in percentage_columns:
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].apply(self._format_percentage)
        
        # Форматируем выручку на продавца
        if 'Выр./прод.' in df_formatted.columns:
            df_formatted['Выр./прод.'] = df_formatted['Выр./прод.'].apply(self._format_currency)
        
        # Форматируем балл
        if 'Балл' in df_formatted.columns:
            df_formatted['Балл'] = df_formatted['Балл'].apply(lambda x: f"{x:.0f}")
        
        return df_formatted
    
    def _add_category_emojis(self, df_display: pd.DataFrame, df_original: pd.DataFrame) -> pd.DataFrame:
        """Добавляет эмодзи к категориям оценки"""
        df_with_emojis = df_display.copy()
        
        if 'Оценка' in df_with_emojis.columns and 'Эмодзи' in df_original.columns:
            # Объединяем эмодзи с названием категории
            emojis = df_original['Эмодзи'].values
            categories = df_with_emojis['Оценка'].values
            
            df_with_emojis['Оценка'] = [
                f"{emoji} {category}" for emoji, category in zip(emojis, categories)
            ]
        
        return df_with_emojis
    
    def _format_currency(self, value: float) -> str:
        """Форматирует денежные значения"""
        if pd.isna(value) or value == 0:
            return "0 ₽"
        
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}М ₽"
        elif value >= 1_000:
            return f"{value/1_000:.0f}К ₽"
        else:
            return f"{value:.0f} ₽"
    
    def _format_price(self, value: float) -> str:
        """Форматирует цены"""
        if pd.isna(value) or value == 0:
            return "0 ₽"
        
        if value >= 1_000:
            return f"{value/1_000:.1f}К ₽"
        else:
            return f"{value:.0f} ₽"
    
    def _format_percentage(self, value: float) -> str:
        """Форматирует проценты"""
        if pd.isna(value):
            return "0%"
        return f"{value:.1f}%"
    
    def _format_days(self, value: float) -> str:
        """Форматирует количество дней"""
        if pd.isna(value):
            return "0 дн."
        return f"{value:.0f} дн."
    
    def create_styled_table(self, df_display: pd.DataFrame, df_original: pd.DataFrame) -> None:
        """
        Создает стилизованную таблицу в Streamlit с цветовой индикацией
        
        Args:
            df_display: Отформатированный DataFrame для отображения
            df_original: Исходный DataFrame с данными о цветах
        """
        # Получаем цвета для строк
        colors = df_original['Цвет категории'].values
        
        # Создаем HTML стили для строк
        styles = []
        for i, color in enumerate(colors):
            styles.append(f"""
                <style>
                .row-{i} {{
                    background-color: {color}20 !important;
                    border-left: 4px solid {color} !important;
                }}
                </style>
            """)
        
        # Применяем стили
        for style in styles:
            st.markdown(style, unsafe_allow_html=True)
        
        # Отображаем таблицу
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=800
        )
    
    def create_summary_metrics(self, scoring_summary: Dict) -> None:
        """
        Создает карточки с основными метриками
        
        Args:
            scoring_summary: Словарь с основными метриками
        """
        if not scoring_summary:
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Всего ниш",
                value=scoring_summary.get('total_niches', 0)
            )
        
        with col2:
            avg_score = scoring_summary.get('avg_score', 0)
            st.metric(
                label="⭐ Средний балл",
                value=f"{avg_score:.1f}"
            )
        
        with col3:
            excellent_count = scoring_summary.get('excellent_niches', 0)
            st.metric(
                label="🟢 Отличные ниши",
                value=excellent_count
            )
        
        with col4:
            good_count = scoring_summary.get('good_niches', 0)
            st.metric(
                label="🟡 Хорошие ниши",
                value=good_count
            )
    
    def create_distribution_chart(self, distribution: Dict[str, int]) -> None:
        """
        Создает диаграмму распределения ниш по категориям
        
        Args:
            distribution: Словарь с распределением по категориям
        """
        if not distribution:
            return
        
        # Подготавливаем данные для диаграммы
        categories = list(distribution.keys())
        counts = list(distribution.values())
        
        # Цвета для категорий
        colors = ['#22c55e', '#eab308', '#f97316', '#ef4444']
        
        # Создаем DataFrame для диаграммы
        chart_data = pd.DataFrame({
            'Категория': categories,
            'Количество': counts,
            'Цвет': colors[:len(categories)]
        })
        
        # Отображаем диаграмму
        st.subheader("📈 Распределение ниш по категориям")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.bar_chart(
                chart_data.set_index('Категория')['Количество'],
                height=300
            )
        
        with col2:
            st.write("**Легенда:**")
            for category, count, color in zip(categories, counts, colors):
                st.markdown(
                    f'<div style="display: flex; align-items: center; margin: 5px 0;">'
                    f'<div style="width: 20px; height: 20px; background-color: {color}; '
                    f'margin-right: 10px; border-radius: 3px;"></div>'
                    f'<span>{category}: {count}</span></div>',
                    unsafe_allow_html=True
                )
