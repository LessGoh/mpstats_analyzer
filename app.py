"""
Главное приложение анализатора ниш mpstats
"""

import streamlit as st
import pandas as pd
from src.data_loader import DataLoader
from src.niche_scorer import NicheScorer
from src.table_formatter import TableFormatter

# Конфигурация страницы
st.set_page_config(
    page_title="Анализатор ниш mpstats",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .info-box {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    
    .success-box {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Основная функция приложения"""
    
    # Заголовок приложения
    st.markdown('<h1 class="main-header">📊 Анализатор ниш mpstats</h1>', unsafe_allow_html=True)
    
    # Описание приложения
    st.markdown("""
    <div class="info-box">
        <h3>🎯 О приложении</h3>
        <p>Автоматический анализ и оценка ниш Wildberries на основе отчетов mpstats. 
        Система оценивает ниши по 6 критериям и выдает топ-30 результатов с цветовой индикацией.</p>
        
        <h4>📋 Критерии оценки:</h4>
        <ul>
            <li><strong>Выручка</strong> - емкость рынка</li>
            <li><strong>Средняя цена с продажами</strong> - средний чек</li>
            <li><strong>Оборачиваемость</strong> - скорость продаж</li>
            <li><strong>% товаров с движением</strong> - активность ниши</li>
            <li><strong>% продавцов с продажами</strong> - уровень конкуренции</li>
            <li><strong>Выручка на продавца</strong> - прибыльность для продавца</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Боковая панель для загрузки файла
    with st.sidebar:
        st.header("📁 Загрузка данных")
        
        uploaded_file = st.file_uploader(
            "Выберите Excel файл mpstats",
            type=['xlsx', 'xls'],
            help="Загрузите отчет 'Выбор ниши' из mpstats в формате Excel"
        )
        
        if uploaded_file:
            st.success("✅ Файл загружен!")
            
            # Информация о файле
            file_details = {
                "Название": uploaded_file.name,
                "Размер": f"{uploaded_file.size / 1024:.1f} KB"
            }
            
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
    
    # Основная логика приложения
    if uploaded_file is None:
        # Показываем инструкции, если файл не загружен
        show_instructions()
    else:
        # Обрабатываем загруженный файл
        process_uploaded_file(uploaded_file)


def show_instructions():
    """Показывает инструкции по использованию"""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 Как использовать:
        
        1. **Экспортируйте отчет** из mpstats:
           - Войдите в mpstats
           - Перейдите в раздел "Выбор ниши"
           - Выберите период (рекомендуется 2+ месяца)
           - Экспортируйте данные в Excel
        
        2. **Загрузите файл** в боковой панели
        
        3. **Получите анализ** топ-30 ниш с оценками
        """)
    
    with col2:
        st.markdown("""
        ### 🎨 Цветовая индикация:
        
        - 🟢 **Отличные ниши** (70-90 баллов)
        - 🟡 **Хорошие ниши** (50-69 баллов)  
        - 🟠 **Средние ниши** (30-49 баллов)
        - 🔴 **Слабые ниши** (0-29 баллов)
        
        ### 📊 Что вы получите:
        - Рейтинг топ-30 ниш
        - Детальные баллы по каждому критерию
        - Сводную статистику
        - Диаграмму распределения
        """)


def process_uploaded_file(uploaded_file):
    """Обрабатывает загруженный файл"""
    
    # Инициализируем компоненты
    data_loader = DataLoader()
    scorer = NicheScorer()
    formatter = TableFormatter()
    
    # Показываем прогресс
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Шаг 1: Загрузка данных
        status_text.text("📥 Загрузка и валидация данных...")
        progress_bar.progress(20)
        
        df = data_loader.load_excel_file(uploaded_file)
        
        if df is None:
            st.error("❌ Не удалось загрузить данные. Проверьте формат файла.")
            return
        
        # Шаг 2: Расчет баллов
        status_text.text("🧮 Расчет баллов ниш...")
        progress_bar.progress(50)
        
        df_scored = scorer.calculate_niche_scores(df)
        
        # Шаг 3: Получение топ-ниш
        status_text.text("🏆 Формирование рейтинга...")
        progress_bar.progress(70)
        
        df_top = scorer.get_top_niches(df_scored)
        
        # Шаг 4: Форматирование для отображения
        status_text.text("🎨 Подготовка к отображению...")
        progress_bar.progress(90)
        
        df_display = formatter.format_display_table(df_top)
        scoring_summary = scorer.get_scoring_summary(df_scored)
        
        # Завершение
        progress_bar.progress(100)
        status_text.text("✅ Анализ завершен!")
        
        # Очищаем индикаторы прогресса
        progress_bar.empty()
        status_text.empty()
        
        # Показываем результаты
        show_results(df_display, df_top, scoring_summary, scorer)
        
    except Exception as e:
        st.error(f"❌ Произошла ошибка при обработке файла: {str(e)}")
        progress_bar.empty()
        status_text.empty()


def show_results(df_display, df_original, scoring_summary, scorer):
    """Отображает результаты анализа"""
    
    # Успешное сообщение
    st.markdown(f"""
    <div class="success-box">
        <h3>🎉 Анализ завершен успешно!</h3>
        <p>Обработано <strong>{scoring_summary.get('total_niches', 0)}</strong> ниш. 
        Показаны топ-30 результатов с лучшими оценками.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Создаем экземпляр форматтера
    formatter = TableFormatter()
    
    # Основные метрики
    st.markdown("---")
    st.subheader("📊 Основные показатели")
    formatter.create_summary_metrics(scoring_summary)
    
    # Диаграмма распределения
    st.markdown("---")
    distribution = scoring_summary.get('distribution', {})
    formatter.create_distribution_chart(distribution)
    
    # Таблица результатов
    st.markdown("---")
    st.subheader("🏆 Топ-30 ниш по оценке")
    
    # Фильтры для таблицы
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score_filter = st.slider(
            "Минимальный балл",
            min_value=0,
            max_value=90,
            value=0,
            help="Фильтр ниш по минимальному баллу"
        )
    
    with col2:
        category_filter = st.selectbox(
            "Категория ниш",
            options=['Все'] + list(distribution.keys()),
            help="Фильтр по категории оценки"
        )
    
    with col3:
        search_term = st.text_input(
            "Поиск по названию",
            placeholder="Введите название ниши...",
            help="Поиск конкретной ниши"
        )
    
    # Применяем фильтры
    df_filtered = apply_filters(
        df_display, df_original, min_score_filter, category_filter, search_term
    )
    
    # Отображаем отфильтрованную таблицу
    if df_filtered.empty:
        st.warning("😔 Нет ниш, соответствующих выбранным фильтрам")
    else:
        st.info(f"📋 Показано {len(df_filtered)} из {len(df_display)} ниш")
        
        # Отображаем таблицу
        st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Дополнительная информация о лучшей нише
        if len(df_filtered) > 0:
            show_top_niche_info(df_original.iloc[0])


def apply_filters(df_display, df_original, min_score, category, search_term):
    """Применяет фильтры к таблице"""
    
    # Создаем маски для фильтрации
    score_mask = df_original['Общий балл'] >= min_score
    
    category_mask = True
    if category != 'Все':
        category_mask = df_original['Категория'] == category
    
    search_mask = True
    if search_term:
        search_mask = df_original['Предметы'].str.contains(
            search_term, case=False, na=False
        )
    
    # Применяем все фильтры
    combined_mask = score_mask & category_mask & search_mask
    
    return df_display[combined_mask].reset_index(drop=True)


def show_top_niche_info(top_niche):
    """Показывает детальную информацию о лучшей нише"""
    
    st.markdown("---")
    st.subheader("🥇 Лучшая ниша по результатам анализа")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        **Ниша:** {top_niche['Предметы']}  
        **Общий балл:** {top_niche['Общий балл']:.0f} {top_niche['Эмодзи']}  
        **Категория:** {top_niche['Категория']}
        """)
    
    with col2:
        st.markdown(f"""
        **Выручка:** {top_niche['Выручка']:,.0f} ₽  
        **Средняя цена:** {top_niche['Средняя цена с продажами']:,.0f} ₽  
        **Оборачиваемость:** {top_niche['Оборачиваемость, дн.']:.0f} дней  
        **Выручка на продавца:** {top_niche['Выручка на продавца']:,.0f} ₽
        """)


if __name__ == "__main__":
    main()
