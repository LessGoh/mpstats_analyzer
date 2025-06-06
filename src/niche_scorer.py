"""
Модуль для расчета баллов ниш на основе 6 критериев оценки
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from config.scoring_weights import SCORING_WEIGHTS, COLOR_CATEGORIES, MAX_RESULTS


class NicheScorer:
    """Класс для расчета баллов ниш по системе критериев"""
    
    def __init__(self):
        self.weights = SCORING_WEIGHTS
        self.color_categories = COLOR_CATEGORIES
        self.max_results = MAX_RESULTS
    
    def calculate_niche_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Рассчитывает баллы для всех ниш в DataFrame
        
        Args:
            df: DataFrame с данными о нишах
            
        Returns:
            DataFrame с добавленными колонками баллов и категорий
        """
        df_scored = df.copy()
        
        # Рассчитываем среднюю выручку на продавца
        df_scored['Выручка на продавца'] = self._calculate_revenue_per_seller(df_scored)
        
        # Рассчитываем баллы по каждому критерию
        df_scored['Балл_Выручка'] = df_scored.apply(
            lambda row: self._get_score_for_metric('выручка', row['Выручка']), axis=1
        )
        
        df_scored['Балл_Цена'] = df_scored.apply(
            lambda row: self._get_score_for_metric('средняя_цена_с_продажами', row['Средняя цена с продажами']), axis=1
        )
        
        df_scored['Балл_Оборачиваемость'] = df_scored.apply(
            lambda row: self._get_score_for_metric('оборачиваемость', row['Оборачиваемость, дн.']), axis=1
        )
        
        df_scored['Балл_Товары_движение'] = df_scored.apply(
            lambda row: self._get_score_for_metric('процент_товаров_с_движением', row['% товаров с движением']), axis=1
        )
        
        df_scored['Балл_Продавцы'] = df_scored.apply(
            lambda row: self._get_score_for_metric('процент_продавцов_с_продажами', row['% продавцов с продажами']), axis=1
        )
        
        df_scored['Балл_Выручка_продавца'] = df_scored.apply(
            lambda row: self._get_score_for_metric('выручка_на_продавца', row['Выручка на продавца']), axis=1
        )
        
        # Рассчитываем общий балл
        df_scored['Общий балл'] = (
            df_scored['Балл_Выручка'] +
            df_scored['Балл_Цена'] +
            df_scored['Балл_Оборачиваемость'] +
            df_scored['Балл_Товары_движение'] +
            df_scored['Балл_Продавцы'] +
            df_scored['Балл_Выручка_продавца']
        )
        
        # Определяем категорию ниши
        df_scored['Категория'] = df_scored['Общий балл'].apply(self._get_category_info)
        df_scored['Цвет категории'] = df_scored['Общий балл'].apply(
            lambda score: self._get_category_color(score)
        )
        df_scored['Эмодзи'] = df_scored['Общий балл'].apply(
            lambda score: self._get_category_emoji(score)
        )
        
        return df_scored
    
    def _calculate_revenue_per_seller(self, df: pd.DataFrame) -> pd.Series:
        """Рассчитывает среднюю выручку на продавца с продажами"""
        revenue_per_seller = df.apply(
            lambda row: row['Выручка'] / row['Продавцы с продажами'] 
            if row['Продавцы с продажами'] > 0 else 0, 
            axis=1
        )
        return revenue_per_seller
    
    def _get_score_for_metric(self, metric_name: str, value: float) -> int:
        """
        Получает балл для конкретной метрики и значения
        
        Args:
            metric_name: Название метрики из конфигурации
            value: Значение метрики
            
        Returns:
            Балл от 1 до 15
        """
        if pd.isna(value) or value < 0:
            return 0
        
        if metric_name not in self.weights:
            return 0
        
        weights_config = self.weights[metric_name]
        
        for (min_val, max_val), weight in weights_config.items():
            if min_val <= value < max_val:
                return weight
        
        # Если значение не попало ни в один диапазон, возвращаем минимальный вес
        return 1
    
    def _get_category_info(self, score: float) -> str:
        """Получает название категории по баллу"""
        for category_data in self.color_categories.values():
            min_score, max_score = category_data['range']
            if min_score <= score <= max_score:
                return category_data['label']
        return 'Неопределено'
    
    def _get_category_color(self, score: float) -> str:
        """Получает цвет категории по баллу"""
        for category_data in self.color_categories.values():
            min_score, max_score = category_data['range']
            if min_score <= score <= max_score:
                return category_data['color']
        return '#6b7280'  # Серый цвет по умолчанию
    
    def _get_category_emoji(self, score: float) -> str:
        """Получает эмодзи категории по баллу"""
        for category_data in self.color_categories.values():
            min_score, max_score = category_data['range']
            if min_score <= score <= max_score:
                return category_data['emoji']
        return '⚪'  # Белый круг по умолчанию
    
    def get_top_niches(self, df_scored: pd.DataFrame) -> pd.DataFrame:
        """
        Возвращает топ-ниши отсортированные по баллу
        
        Args:
            df_scored: DataFrame с рассчитанными баллами
            
        Returns:
            DataFrame с топ-нишами (максимум MAX_RESULTS)
        """
        # Сортировка по общему баллу (убывание)
        df_top = df_scored.sort_values('Общий балл', ascending=False)
        
        # Ограничение количества результатов
        df_top = df_top.head(self.max_results)
        
        # Сброс индекса и добавление позиции
        df_top = df_top.reset_index(drop=True)
        df_top['Позиция'] = df_top.index + 1
        
        return df_top
    
    def get_score_distribution(self, df_scored: pd.DataFrame) -> Dict[str, int]:
        """
        Возвращает распределение ниш по категориям
        
        Args:
            df_scored: DataFrame с рассчитанными баллами
            
        Returns:
            Словарь с количеством ниш в каждой категории
        """
        distribution = {}
        
        for category_key, category_data in self.color_categories.items():
            min_score, max_score = category_data['range']
            count = len(df_scored[
                (df_scored['Общий балл'] >= min_score) & 
                (df_scored['Общий балл'] <= max_score)
            ])
            distribution[category_data['label']] = count
        
        return distribution
    
    def get_scoring_summary(self, df_scored: pd.DataFrame) -> Dict:
        """
        Возвращает сводную информацию по скорингу
        
        Args:
            df_scored: DataFrame с рассчитанными баллами
            
        Returns:
            Словарь с основными метриками
        """
        if df_scored.empty:
            return {}
        
        return {
            'total_niches': len(df_scored),
            'avg_score': df_scored['Общий балл'].mean(),
            'max_score': df_scored['Общий балл'].max(),
            'min_score': df_scored['Общий балл'].min(),
            'top_score_niche': df_scored.loc[df_scored['Общий балл'].idxmax(), 'Предметы'],
            'excellent_niches': len(df_scored[df_scored['Общий балл'] >= 70]),
            'good_niches': len(df_scored[(df_scored['Общий балл'] >= 50) & (df_scored['Общий балл'] < 70)]),
            'distribution': self.get_score_distribution(df_scored)
        }
