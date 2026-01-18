import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы (должна быть первой командой)
st.set_page_config(layout="wide", page_title="VPR Dashboard")

# --- CSS ДЛЯ ЗАКРЕПЛЕНИЯ ПАНЕЛИ И СТИЛИЗАЦИИ ---
st.markdown("""
    <style>
    /* Закрепление контейнера с фильтрами */
    div[data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 2.875rem; /* Высота стандартного хедера Streamlit */
        z-index: 999;
        background-color: #0e1117; /* Цвет фона (темная тема) */
        padding-bottom: 20px;
        border-bottom: 1px solid #262730;
    }
    
    /* Скрытие стандартного меню гамбургера если нужно (опционально) */
    /* #MainMenu {visibility: hidden;} */
    
    /* Стиль для карточек метрик и инфо-блоков */
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        color: white;
    }
    .bias-warning {
        color: #ff4b4b;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА ДАННЫХ ---
@st.cache_data
def load_data():
    # Загрузка основных данных (предполагаемое имя файла из твоего описания)
    # ВАЖНО: Убедись, что файл с результатами называется так или поменяй имя здесь
    try:
        df = pd.read_excel('marks.xlsx') 
    except FileNotFoundError:
        st.error("Файл marks.xlsx не найден. Пожалуйста, добавьте его в корень проекта.")
        df = pd.DataFrame() # Пустой датафрейм для предотвращения падения

    # Загрузка данных по необъективности
    try:
        bias_df = pd.read_excel('bias.xlsx')
        # Приведение типов для корректного сравнения
        bias_df['Год'] = bias_df['Год'].astype(int)
        bias_df['Логин'] = bias_df['Логин'].astype(str)
    except FileNotFoundError:
        st.error("Файл bias.xlsx не найден. Пожалуйста, добавьте его в корень проекта.")
        bias_df = pd.DataFrame()
        
    return df, bias_df

df, bias_df = load_data()

if df.empty:
    st.stop()

# --- ЗАКРЕПЛЕННАЯ ПАНЕЛЬ ФИЛЬТРОВ ---
# Используем st.container для группировки, CSS выше делает его "липким"
filter_container = st.container()

with filter_container:
    st.title("Аналитическая панель ВПР")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Сортировка годов по убыванию
        years = sorted(df['Год'].unique(), reverse=True)
        selected_year = st.selectbox("Год", years, help="Выберите год")

    with col2:
        municipalities = sorted(df['Муниципалитет'].unique())
        selected_muni = st.selectbox("Муниципалитет", municipalities, help="Выберите муниципалитет")

    # Фильтрация списка школ по муниципалитету
    available_schools = df[
        (df['Год'] == selected_year) & 
        (df['Муниципалитет'] == selected_muni)
    ][['Наименование', 'Логин']].drop_duplicates()
    
    # Создаем словарь для маппинга Имя -> Логин
    school_map = dict(zip(available_schools['Наименование'], available_schools['Логин']))
    school_options = ['Все'] + sorted(list(school_map.keys()))

    with col3:
        selected_school_name = st.selectbox("Образовательная организация", school_options, help="Выберите школу")
        # Получаем логин выбранной школы
        selected_school_login = school_map.get(selected_school_name) if selected_school_name != 'Все' else None

    with col4:
        subjects = sorted(df['Предмет'].unique())
        selected_subject = st.selectbox("Предмет", subjects, help="Выберите предмет")

    with col5:
        grades = sorted(df['Класс'].unique())
        selected_grade = st.selectbox("Класс", grades, help="Выберите класс")

# --- ФИЛЬТРАЦИЯ ОСНОВНОГО ДАТАСЕТА ---
filtered_df = df[
    (df['Год'] == selected_year) &
    (df['Муниципалитет'] == selected_muni) &
    (df['Предмет'] == selected_subject) &
    (df['Класс'] == selected_grade)
]

if selected_school_name != 'Все':
    filtered_df = filtered_df[filtered_df['Наименование'] == selected_school_name]

# --- МЕТРИКИ (СВОДНЫЕ ПОКАЗАТЕЛИ) ---
st.markdown("### Сводные показатели")
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    # ЛОГИКА ПУНКТА 2: Если выбрано "Все", показываем кол-во школ
    if selected_school_name == 'Все':
        school_count = filtered_df['Логин'].nunique()
        st.metric("Кол-во ОО (участников)", school_count)
    else:
        st.metric("Выбранная ОО", "1")

with m_col2:
    # Пример существующей метрики (средний балл или подобное)
    # Если в твоем датасете есть колонка 'Оценка' или 'Балл'
    if 'Оценка' in filtered_df.columns:
        avg_score = filtered_df['Оценка'].mean()
        st.metric("Средняя оценка", f"{avg_score:.2f}" if not pd.isna(avg_score) else "-")
    else:
        st.metric("Кол-во записей", len(filtered_df))

with m_col3:
    # Пример еще одной метрики
    st.metric("Муниципалитет", selected_muni)


# --- СУЩЕСТВУЮЩИЙ ФУНКЦИОНАЛ (ПЛЕЙСХОЛДЕР) ---
# Сюда вставь свои графики и таблицы из текущего приложения, которые были ниже фильтров
st.markdown("---")
st.subheader("Результаты анализа (Существующий функционал)")
# Пример графика (замени на свой код)
if not filtered_df.empty and 'Оценка' in filtered_df.columns:
    fig_main = px.histogram(filtered_df, x='Оценка', title=f"Распределение оценок: {selected_subject}, {selected_grade} класс")
    st.plotly_chart(fig_main, use_container_width=True)
else:
    st.info("Нет данных для отображения основного графика по выбранным фильтрам.")


# --- НОВЫЙ РАЗДЕЛ: ПРИЗНАКИ НЕОБЪЕКТИВНОСТИ ---
st.markdown("---")
st.markdown("## | ПРИЗНАКИ НЕОБЪЕКТИВНОСТИ")

# Контейнер для раздела необъективности
bias_container = st.container()

with bias_container:
    # Подготовка данных для необъективности
    # Фильтруем bias_df только по году и муниципалитету для графиков и таблиц
    current_bias_muni = bias_df[
        (bias_df['Год'] == selected_year) & 
        (bias_df['Муниципалитет'] == selected_muni)
    ]
    
    b_col1, b_col2 = st.columns([1, 1])
    
    # 1. АНАЛИЗ ВЫБРАННОЙ ШКОЛЫ
    with b_col1:
        st.subheader(f"АНАЛИЗ ВЫБРАННОЙ ШКОЛЫ ({selected_year})")
        
        if selected_school_name == 'Все':
            st.info("ℹ️ Выберите конкретную школу в фильтрах сверху для детального анализа маркеров.")
            
            # Показываем общую статистику по муниципалитету
            count_biased = current_bias_muni['Логин'].nunique()
            st.metric("Школ с признаками в муниципалитете", count_biased)
            
        else:
            # Данные по текущему году
            school_bias_current = current_bias_muni[current_bias_muni['Логин'] == str(selected_school_login)]
            
            # Проверка истории (предыдущие 2 года)
            history_years = [selected_year - 1, selected_year - 2]
            history_text = []
            
            for y in history_years:
                in_list = not bias_df[
                    (bias_df['Год'] == y) & 
                    (bias_df['Логин'] == str(selected_school_login))
                ].empty
                if in_list:
                    history_text.append(str(y))
            
            # Карточка отображения
            with st.container():
                st.markdown(f"**Школа:** {selected_school_name}")
                
                if not school_bias_current.empty:
                    row = school_bias_current.iloc[0]
                    markers_count = row['Количество маркеров']
                    st.error(f"⚠️ Школа имеет признаки необъективности в {selected_year} году.")
                    st.write(f"**Количество маркеров:** {markers_count}")
                    
                    # Детализация маркеров
                    markers_found = []
                    if row.get('4 РУ', 0) > 0: markers_found.append("4 РУ")
                    if row.get('4 МА', 0) > 0: markers_found.append("4 МА")
                    if row.get('5 РУ', 0) > 0: markers_found.append("5 РУ")
                    if row.get('5 МА', 0) > 0: markers_found.append("5 МА")
                    
                    if markers_found:
                        st.write("Обнаруженные маркеры: " + ", ".join(markers_found))
                else:
                    st.success(f"✅ В {selected_year} году признаков необъективности не выявлено.")

                st.markdown("---")
                st.markdown("**История (предыдущие 2 года):**")
                if history_text:
                    st.warning(f"Школа попадала в список необъективных в: {', '.join(history_text)} гг.")
                else:
                    st.write("В предыдущие два года в списках необъективных не числилась.")

    # 2. ДОЛЯ ШКОЛ С ПРИЗНАКАМИ (ГРАФИК)
    with b_col2:
        st.subheader("ДОЛЯ ОО С ПРИЗНАКАМИ НЕОБЪЕКТИВНОСТИ (%)")
        
        # Нам нужны данные за последние 3 года для графика
        graph_years = [selected_year - 2, selected_year - 1, selected_year]
        chart_data = []
        
        for y in graph_years:
            # Числитель: кол-во школ в bias_df в этом муницип. за этот год
            num = bias_df[
                (bias_df['Год'] == y) & 
                (bias_df['Муниципалитет'] == selected_muni)
            ]['Логин'].nunique()
            
            # Знаменатель: кол-во школ в marks (df) участвовавших в Русс. Яз 4 класс
            # ВАЖНО: Используем 'Предмет' и 'Класс' как указано в ТЗ для расчета базы
            denom = df[
                (df['Год'] == y) & 
                (df['Муниципалитет'] == selected_muni) & 
                (df['Предмет'] == 'Русский язык') & 
                (df['Класс'].astype(str) == '4') # Приводим к строке на всякий случай
            ]['Логин'].nunique()
            
            percent = (num / denom * 100) if denom > 0 else 0
            
            # Цвет столбца: оранжевый для текущего года, серый для прошлых
            color = "#ff9f1c" if y == selected_year else "#7f8c8d"
            
            chart_data.append({
                'Год': str(y),
                'Доля (%)': round(percent, 1),
                'Color': color
            })
            
        chart_df = pd.DataFrame(chart_data)
        
        if not chart_df.empty:
            fig_bar = px.bar(
                chart_df, 
                x='Год', 
                y='Доля (%)', 
                text='Доля (%)',
                color='Год',
                color_discrete_map={row['Год']: row['Color'] for _, row in chart_df.iterrows()}
            )
            fig_bar.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
            fig_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("Нет данных для построения графика.")

    # 3. СПИСОК ОО С МАРКЕРАМИ
    st.subheader(f"СПИСОК ОО РЕГИОНА С МАРКЕРАМИ ({selected_year})")
    st.write("Список образовательных организаций муниципалитета, попавших в список необъективных:")
    
    if not current_bias_muni.empty:
        # Оформляем таблицу красиво
        display_table = current_bias_muni[['ОО', 'Количество маркеров', '4 РУ', '4 МА', '5 РУ', '5 МА']].copy()
        
        # Переименуем колонки для красоты если нужно
        display_table.rename(columns={'ОО': 'Наименование организации', 'Количество маркеров': 'МАРКЕРОВ'}, inplace=True)
        
        # Создаем колонку "Дисциплины" для соответствия макету (где маркер = 1)
        def get_disciplines(row):
            discs = []
            if row['4 РУ'] > 0: discs.append("РУ 4")
            if row['4 МА'] > 0: discs.append("МА 4")
            if row['5 РУ'] > 0: discs.append("РУ 5")
            if row['5 МА'] > 0: discs.append("МА 5")
            return " ".join(discs)

        display_table['ДИСЦИПЛИНЫ'] = display_table.apply(get_disciplines, axis=1)
        
        # Убираем технические колонки
        final_table = display_table[['Наименование организации', 'МАРКЕРОВ', 'ДИСЦИПЛИНЫ']]
        
        # Показываем таблицу, растянутую по ширине
        st.dataframe(
            final_table, 
            use_container_width=True, 
            hide_index=True
        )
        st.caption(f"Найдено школ: {len(final_table)}")
    else:
        st.success("В выбранном муниципалитете за этот год школ с признаками необъективности не найдено.")
