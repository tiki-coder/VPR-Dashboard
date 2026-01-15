import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Аналитика ВПР", layout="wide", initial_sidebar_state="collapsed")

# --- STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Roboto', sans-serif; 
        background-color: #F8F9FB; 
        color: #1C1B1F; 
    }
    .stApp { background-color: #F8F9FB; }
    
    .block-container {
        padding-top: 1rem !important;   
        max-width: 100% !important;
    }
    header { visibility: hidden; }
    
    .main-header {
        font-size: 32px;
        font-weight: 700;
        margin-top: 0px !important;
        margin-bottom: 12px;
        padding-top: 8px;
    }
    
    .metric-container {
        text-align: left;
    }
    .metric-label {
        font-size: 14px;
        color: #49454F;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #6750A4; 
        font-weight: 700; 
        font-size: 38px;
    }
    
    .metric-subtitle {
        font-size: 13px;
        color: #8B8B8D;
        margin-left: 4px;
    }
    
    h2, h3 {
        margin-bottom: 8px !important;
    }
    
    hr {
        margin: 12px 0 !important;
        border: 1px solid #E0E0E0;
    }
    
    /* Усиленное закрепление панели фильтров */
    .sticky-filters {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: #F8F9FB;
        z-index: 1000;
        padding: 10px 0;
        border-bottom: 2px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Отступ для основного контента под фиксированной панелью */
    .main-content {
        margin-top: 80px;
    }
    
    /* Тёмная тема */
    @media (prefers-color-scheme: dark) {
        html, body, [class*="css"] { 
            background-color: #121212; 
            color: #E6E6E6; 
        }
        .stApp { background-color: #121212; }
        .sticky-filters {
            background-color: #121212;
            border-bottom: 2px solid #333333;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА ДАННЫХ ---
script_dir = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner=False)
def load_marks():
    marks_path = os.path.join(script_dir, "marks.xlsx")
    return pd.read_excel(marks_path)

@st.cache_data(show_spinner=False)
def load_scores():
    scores_path = os.path.join(script_dir, "scores.xlsx")
    return pd.read_excel(scores_path)

@st.cache_data(show_spinner=False)
def load_bias():
    bias_path = os.path.join(script_dir, "bias.xlsx")
    if not os.path.exists(bias_path):
        st.error("Файл bias.xlsx не найден в корне репозитория.")
        return pd.DataFrame()
    return pd.read_excel(bias_path)

with st.spinner("Загрузка данных..."):
    df_marks = load_marks()
    df_scores = load_scores()
    df_bias = load_bias()

if df_marks.empty or df_scores.empty:
    st.stop()

st.markdown("<div class='main-header'>Аналитика ВПР</div>", unsafe_allow_html=True)

# --- ПАНЕЛЬ ФИЛЬТРОВ (фиксированная) ---
st.markdown('<div class="sticky-filters">', unsafe_allow_html=True)
f1, f2, f3, f4, f5 = st.columns(5)

years = sorted(df_marks['Год'].unique(), reverse=True)
default_year_idx = 0 if st.session_state.get("year") not in years else years.index(st.session_state.get("year", years[0]))
with f1:
    sel_year = st.selectbox("Год", years, index=default_year_idx, key="year")

year_df = df_marks[df_marks['Год'] == sel_year]
classes = sorted(year_df['Класс'].unique())
default_class_idx = 0 if st.session_state.get("class") not in classes else classes.index(st.session_state.get("class", classes[0]))
with f2:
    sel_class = st.selectbox("Класс", classes, index=default_class_idx, key="class")

class_df = year_df[year_df['Класс'] == sel_class]
subjects = sorted(class_df['Предмет'].unique())
default_subj_idx = 0 if st.session_state.get("subj") not in subjects else subjects.index(st.session_state.get("subj", subjects[0]))
with f3:
    sel_subj = st.selectbox("Предмет", subjects, index=default_subj_idx, key="subj")

subj_df = class_df[class_df['Предмет'] == sel_subj]
mun_options = ["Все"] + sorted(subj_df['Муниципалитет'].unique().tolist())
default_mun_idx = 0 if st.session_state.get("mun") not in mun_options else mun_options.index(st.session_state.get("mun", "Все"))
with f4:
    sel_mun = st.selectbox("Муниципалитет", mun_options, index=default_mun_idx, key="mun")

if sel_mun == "Все":
    oo_options = ["Все"]
else:
    mun_df = subj_df[subj_df['Муниципалитет'] == sel_mun]
    oo_options = ["Все"] + sorted(mun_df['ОО'].unique().tolist())
default_oo_idx = 0 if st.session_state.get("oo") not in oo_options else oo_options.index(st.session_state.get("oo", "Все"))
with f5:
    sel_oo = st.selectbox("ОО (Школа)", oo_options, index=default_oo_idx, key="oo")

st.markdown('</div>', unsafe_allow_html=True)

# Отступ для контента под фиксированной панелью
st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- ФИЛЬТРАЦИЯ ДАННЫХ ---
m_sub = subj_df.copy()
if sel_mun != "Все":
    m_sub = m_sub[m_sub['Муниципалитет'] == sel_mun]
if sel_oo != "Все":
    m_sub = m_sub[m_sub['ОО'] == sel_oo]

if m_sub.empty:
    st.warning("Нет данных по выбранным фильтрам.")
    st.stop()

# --- СВОДНЫЕ ПОКАЗАТЕЛИ (с защитой от >100%) ---
# (ваш оригинальный код сводных метрик здесь — оставлен без изменений)

# --- ВСЕ ОСТАЛЬНЫЕ РАЗДЕЛЫ (графики отметок, баллов и т.д.) ---
# Вставьте сюда весь ваш существующий код графиков и таблиц из оригинального main.py
# (всё, что было ниже фильтров до моего предыдущего добавления раздела необъективности)

# --- РАЗДЕЛ ПРИЗНАКИ НЕОБЪЕКТИВНОСТИ (в самом низу) ---
st.markdown("<hr>", unsafe_allow_html=True)
st.header("Признаки необъективности")

marker_cols = ['4 РУ', '4 МА', '5 РУ', '5 МА']
marker_display = {'4 РУ': 'РУ4', '4 МА': 'МА4', '5 РУ': 'РУ5', '5 МА': 'МА5'}

# Блок 1: Анализ выбранной школы
if sel_oo == "Все":
    st.info("👈 Выберите конкретную школу для детального анализа признаков необъективности")
else:
    school_logins = m_sub['Логин'].unique()
    if len(school_logins) != 1:
        st.warning("У выбранной школы несколько логинов — анализ маркеров невозможен.")
    else:
        login = school_logins[0]
        st.subheader(f"Анализ выбранной школы ({sel_year})")
        
        bias_school = df_bias[(df_bias['Год'] == sel_year) & (df_bias['Логин'] == login)]
        
        if bias_school.empty:
            st.success("Признаки необъективности в текущем году не выявлены.")
        else:
            row = bias_school.iloc[0]
            active_markers = [marker_display[col] for col in marker_cols if col in row and row[col] == 1]
            num_markers = sum(row.get(col, 0) for col in marker_cols if col in row)
            
            if active_markers:
                st.warning(f"Выявленные маркеры: {', '.join(active_markers)}")
            st.write(f"🔴 Количество маркеров: **{int(num_markers)}**")
        
        # История за предыдущие 2 года
        prev_years = [y for y in [sel_year-1, sel_year-2] if y >= df_bias['Год'].min()]
        if prev_years:
            st.markdown("**Попадание в списки предыдущих лет**")
            for py in sorted(prev_years):
                prev_row = df_bias[(df_bias['Год'] == py) & (df_bias['Логин'] == login)]
                if not prev_row.empty:
                    st.write(f"• {py} год: попадала в список")
                else:
                    st.write(f"• {py} год: не попадала")

# Блок 2: Доля ОО с признаками
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Доля ОО с признаками необъективности (%) по муниципалитету")

years_chart = sorted([sel_year-2, sel_year-1, sel_year], reverse=False)
percs = []
bar_colors = []

for y in years_chart:
    if y not in df_bias['Год'].unique():
        percs.append(0)
        bar_colors.append('#B0BEC5')
        continue
    
    ru4 = df_marks[(df_marks['Год'] == y) & (df_marks['Класс'] == 4) & (df_marks['Предмет'] == 'Русский язык')]
    if sel_mun != "Все":
        ru4 = ru4[ru4['Муниципалитет'] == sel_mun]
    total_schools = ru4['Логин'].nunique() if not ru4.empty else 1
    
    bias_y = df_bias[df_bias['Год'] == y]
    if sel_mun != "Все":
        bias_y = bias_y[bias_y['Муниципалитет'] == sel_mun]
    bias_y['has_markers'] = bias_y[marker_cols].sum(axis=1) > 0
    biased_schools = bias_y[bias_y['has_markers']]['Логин'].nunique()
    
    perc = int(round(min(100.0, biased_schools / total_schools * 100), 0))
    percs.append(perc)
    bar_colors.append('#FF9800' if y == sel_year else '#B0BEC5')

fig_bias = px.bar(
    x=[str(y) for y in years_chart], y=percs,
    text=[f"{p}%" for p in percs],
    color=[str(y) for y in years_chart],
    color_discrete_sequence=bar_colors
)
fig_bias.update_traces(textposition='outside')
fig_bias.update_layout(
    height=350, showlegend=False, margin=dict(l=10,r=10,t=30,b=10),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(title="", range=[0, max(percs)+10 or 100], ticksuffix="%"),
    xaxis=dict(title="")
)
st.plotly_chart(fig_bias, use_container_width=True)

# Блок 3: Список ОО с маркерами
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader(f"Список ОО с маркерами ({sel_year})")

bias_current = df_bias[df_bias['Год'] == sel_year].copy()
if sel_mun != "Все":
    bias_current = bias_current[bias_current['Муниципалитет'] == sel_mun]

bias_current['num_markers'] = bias_current[marker_cols].sum(axis=1)
bias_current['disciplines'] = bias_current.apply(
    lambda row: ' '.join([marker_display[col] for col in marker_cols if col in row and row[col] == 1]), axis=1
)

display_df = bias_current[bias_current['num_markers'] > 0].copy()
if not display_df.empty:
    display_df = display_df.sort_values('num_markers', ascending=False)
    display_df['МАРКЕРОВ'] = display_df['num_markers'].apply(lambda x: f"🔴 {int(x)}")
    display_df = display_df.rename(columns={
        'ОО': 'НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ',
        'disciplines': 'ДИСЦИПЛИНЫ'
    })
    display_df = display_df[['НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ', 'МАРКЕРОВ', 'ДИСЦИПЛИНЫ']]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown(f"<div style='color:#D32F2F; font-weight:bold; text-align:right; margin-top:10px;'>Найдено школ: {len(display_df)}</div>", unsafe_allow_html=True)
else:
    st.info("В выбранном году и муниципалитете школы с маркерами не найдены.")

st.markdown('</div>', unsafe_allow_html=True)  # закрытие main-content
