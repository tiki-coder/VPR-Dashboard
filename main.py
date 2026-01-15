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
    
    .stSelectbox input {
        pointer-events: none;
        caret-color: transparent;
    }
    
    /* Фиксированная панель фильтров */
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
    }
    
    /* Уменьшенный отступ под панелью (было 90px → теперь 50px) */
    .main-content {
        margin-top: 50px;
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
        .main-header { color: #E6E6E6; }
        .metric-value { color: #A688FF; }
        .metric-label { color: #B3B3B3; }
        .metric-subtitle { color: #A0A0A0; }
        hr { border-color: #333333; }
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
default_year_idx = years.index(st.session_state.get("year", years[0])) if st.session_state.get("year") in years else 0
with f1:
    sel_year = st.selectbox("Год", years, index=default_year_idx, key="year")

year_df = df_marks[df_marks['Год'] == sel_year]
classes = sorted(year_df['Класс'].unique())
default_class_idx = classes.index(st.session_state.get("class", classes[0])) if st.session_state.get("class") in classes else 0
with f2:
    sel_class = st.selectbox("Класс", classes, index=default_class_idx, key="class")

class_df = year_df[year_df['Класс'] == sel_class]
subjects = sorted(class_df['Предмет'].unique())
default_subj_idx = subjects.index(st.session_state.get("subj", subjects[0])) if st.session_state.get("subj") in subjects else 0
with f3:
    sel_subj = st.selectbox("Предмет", subjects, index=default_subj_idx, key="subj")

subj_df = class_df[class_df['Предмет'] == sel_subj]
mun_options = ["Все"] + sorted(subj_df['Муниципалитет'].unique().tolist())
default_mun_idx = mun_options.index(st.session_state.get("mun", "Все")) if st.session_state.get("mun") in mun_options else 0
with f4:
    sel_mun = st.selectbox("Муниципалитет", mun_options, index=default_mun_idx, key="mun")

if sel_mun == "Все":
    oo_options = ["Все"]
else:
    mun_df = subj_df[subj_df['Муниципалитет'] == sel_mun]
    oo_options = ["Все"] + sorted(mun_df['ОО'].unique().tolist())
default_oo_idx = oo_options.index(st.session_state.get("oo", "Все")) if st.session_state.get("oo") in oo_options else 0
with f5:
    sel_oo = st.selectbox("ОО (Школа)", oo_options, index=default_oo_idx, key="oo")

st.markdown('</div>', unsafe_allow_html=True)

# --- Основной контент с уменьшенным отступом ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- ФИЛЬТРАЦИЯ (всё из marks.xlsx) ---
m_sub = subj_df.copy()
if sel_mun != "Все":
    m_sub = m_sub[m_sub['Муниципалитет'] == sel_mun]
if sel_oo != "Все":
    m_sub = m_sub[m_sub['ОО'] == sel_oo]

if m_sub.empty:
    st.warning("Нет данных. Измените фильтры.")
    st.stop()

# --- СВОДНЫЕ ПОКАЗАТЕЛИ ---
st.subheader("Сводные показатели")
total_p = m_sub['Кол-во участников'].sum()

if total_p == 0:
    perc_2 = perc_3 = perc_4 = perc_5 = 0
else:
    weights = m_sub['Кол-во участников']
    abs_counts = ((m_sub[['2', '3', '4', '5']] / 100).multiply(weights, axis=0)).sum()
    percentages = (abs_counts / total_p * 100).round(1)
    perc_2 = min(100.0, percentages.get('2', 0))
    perc_3 = min(100.0, percentages.get('3', 0))
    perc_4 = min(100.0, percentages.get('4', 0))
    perc_5 = min(100.0, percentages.get('5', 0))

perc_quality = min(100.0, round(perc_4 + perc_5, 1))
perc_success = min(100.0, round(perc_3 + perc_4 + perc_5, 1))

col_params, col_participants, col_quality, col_success = st.columns(4)
with col_params:
    st.markdown(f"<p style='margin: 0; padding: 0;'><b>Год:</b> {sel_year}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin: 0; padding: 0;'><b>Класс:</b> {sel_class}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin: 0; padding: 0;'><b>Предмет:</b> {sel_subj}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin: 0; padding: 0;'><b>Муниципалитет:</b> {sel_mun if sel_mun != 'Все' else 'Все'}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin: 0; padding: 0; white-space: nowrap; overflow: visible;'><b>ОО:</b> {sel_oo if sel_oo != 'Все' else 'Все'}</p>", unsafe_allow_html=True)

with col_participants:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Участники</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{int(total_p)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_quality:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Качество знаний<span class="metric-subtitle">(отметки «4» и «5»)</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{perc_quality}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_success:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Успеваемость<span class="metric-subtitle">(без двоек)</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{perc_success}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- ГРАФИКИ (полностью восстановлены оригинальные настройки) ---
g1, g2 = st.columns(2)

with g1:
    st.subheader("Статистика по отметкам")
    percs_capped = [min(100.0, p) for p in [perc_2, perc_3, perc_4, perc_5]]
    max_perc = max(percs_capped) if any(percs_capped) else 100
    fig_m = px.bar(
        x=['2','3','4','5'], y=percs_capped, color=['2','3','4','5'],
        color_discrete_map={'2':'#F44336','3':'#FF9800','4':'#4CAF50','5':'#2196F3'},
        text=[f"{p:.1f}%" for p in percs_capped]
    )
    fig_m.update_traces(textposition='outside', hovertemplate='%{text}')
    fig_m.update_layout(
        height=300, showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title="Доля учащихся (%)", ticksuffix="%", range=[0, max_perc + 10]),
        xaxis=dict(title="Отметка", tickmode='array', tickvals=['2','3','4','5'], ticktext=['2','3','4','5'], fixedrange=True),
        xaxis_fixedrange=True, yaxis_fixedrange=True
    )
    st.plotly_chart(fig_m, use_container_width=True, config={
        'toImageButtonOptions': {'format': 'png'},
        'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'toggleSpikelines'],
        'displaylogo': False
    })

with g2:
    st.subheader("Распределение первичных баллов")
    sub_scores = df_scores[
        (df_scores['Год'] == sel_year) &
        (df_scores['Класс'] == sel_class) &
        (df_scores['Предмет'] == sel_subj)
    ]
    score_cols = [col for col in sub_scores.columns if col.isdigit() and sub_scores[col].notna().any()]
    if score_cols:
        score_cols = sorted(score_cols, key=int)
        max_score = int(score_cols[-1])
    else:
        max_score = 0
    
    logins = m_sub['Логин'].unique()
    s_agg = df_scores[(df_scores['Логин'].isin(logins)) & (df_scores['Год'] == sel_year) &
                      (df_scores['Класс'] == sel_class) & (df_scores['Предмет'] == sel_subj)]
    
    if max_score == 0 or s_agg.empty:
        st.info("Нет данных по баллам для выбранных параметров")
    else:
        total_s = s_agg['Кол-во участников'].sum() or 1
        y_vals = []
        for c in score_cols:
            val = ((s_agg[c] / 100) * s_agg['Кол-во участников']).sum() / total_s * 100
            y_vals.append(min(100.0, round(val, 1)))
        
        fig_s = px.bar(
            x=score_cols, y=y_vals,
            text=[f"{v}%" if v > 0 else "" for v in y_vals],
            color_discrete_sequence=['#6750A4']
        )
        fig_s.update_traces(textposition='outside')
        fig_s.update_layout(
            height=300, showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="Доля учащихся (%)", ticksuffix="%", range=[0, max(y_vals)+10 or 100]),
            xaxis=dict(title="Первичный балл")
        )
        st.plotly_chart(fig_s, use_container_width=True)

# --- РАЗДЕЛ ПРИЗНАКИ НЕОБЪЕКТИВНОСТИ (логика перепроверена и подтверждена) ---
st.markdown("<hr>", unsafe_allow_html=True)
st.header("Признаки необъективности")

marker_cols = ['4 РУ', '4 МА', '5 РУ', '5 МА']  # поправьте при необходимости
marker_display = {'4 РУ': 'РУ4', '4 МА': 'МА4', '5 РУ': 'РУ5', '5 МА': 'МА5'}

# Блок 1: Анализ выбранной школы (только по году и логину из marks)
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
            active_markers = [marker_display.get(col, col) for col in marker_cols if col in row.index and row[col] == 1]
            num_markers = sum(row.get(col, 0) for col in marker_cols if col in row.index)
            
            if active_markers:
                st.warning(f"Выявленные маркеры: {', '.join(active_markers)}")
            st.write(f"🔴 Количество маркеров: **{int(num_markers)}**")
        
        # История за предыдущие 2 года
        prev_years = [y for y in [sel_year-1, sel_year-2] if y in df_bias['Год'].unique()]
        if prev_years:
            st.markdown("**Попадание в списки предыдущих лет**")
            for py in sorted(prev_years):
                prev_row = df_bias[(df_bias['Год'] == py) & (df_bias['Логин'] == login)]
                status = "попадала в список" if not prev_row.empty else "не попадала"
                st.write(f"• {py} год: {status}")

# Блок 2: Доля ОО (логика: школы с ≥1 маркером / школы, участвовавшие в РУ 4 кл)
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Доля ОО с признаками необъективности (%) по муниципалитету")

years_chart = sorted([sel_year-2, sel_year-1, sel_year])
percs = []
bar_colors = []

for y in years_chart:
    if y not in df_bias['Год'].unique():
        percs.append(0)
        bar_colors.append('#B0BEC5')
        continue
    
    # Деноминатор: уникальные логины школ в Русский язык 4 класс (из marks)
    ru4 = df_marks[(df_marks['Год'] == y) & (df_marks['Класс'] == 4) & (df_marks['Предмет'] == 'Русский язык')]
    if sel_mun != "Все":
        ru4 = ru4[ru4['Муниципалитет'] == sel_mun]
    total_schools = ru4['Логин'].nunique() if not ru4.empty else 1
    
    # Числитель: уникальные логины школ с ≥1 маркером (из bias)
    bias_y = df_bias[df_bias['Год'] == y]
    if sel_mun != "Все":
        bias_y = bias_y[bias_y['Муниципалитет'] == sel_mun]
    bias_y['has_markers'] = bias_y[marker_cols].sum(axis=1) > 0
    biased_schools = bias_y[bias_y['has_markers']]['Логин'].nunique()
    
    perc = int(round(min(100.0, biased_schools / total_schools * 100)))
    percs.append(perc)
    bar_colors.append('#FF9800' if y == sel_year else '#B0BEC5')

fig_bias = px.bar(
    x=[str(y) for y in years_chart], y=percs,
    text=[f"{p}%" for p in percs],
    color=[str(y) for y in years_chart],
    color_discrete_sequence=bar_colors
)
fig_bias.update_traces(textposition='outside')
fig_bias.update_xaxes(type='category')
fig_bias.update_layout(
    height=350, showlegend=False, margin=dict(l=10, r=10, t=30, b=10),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(title="", range=[0, max(percs) + 10 or 100], ticksuffix="%"),
    xaxis=dict(title="")
)
st.plotly_chart(fig_bias, use_container_width=True)

# Блок 3: Список ОО с маркерами (школы из bias с ≥1 маркером, названия из bias['ОО'])
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader(f"Список ОО с маркерами ({sel_year})")

bias_current = df_bias[df_bias['Год'] == sel_year].copy()
if sel_mun != "Все":
    bias_current = bias_current[bias_current['Муниципалитет'] == sel_mun]

bias_current['num_markers'] = bias_current[marker_cols].sum(axis=1)
bias_current['disciplines'] = bias_current.apply(
    lambda row: ' '.join([marker_display.get(col, col) for col in marker_cols if col in row.index and row[col] == 1]), axis=1
)

display_df = bias_current[bias_current['num_markers'] > 0].copy()
if not display_df.empty:
    display_df = display_df.sort_values('num_markers', ascending=False)
    display_df['МАРКЕРОВ'] = display_df['num_markers'].apply(lambda x: f"🔴 {int(x)}")
    display_df = display_df.rename(columns={'ОО': 'НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ', 'disciplines': 'ДИСЦИПЛИНЫ'})
    display_df = display_df[['НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ', 'МАРКЕРОВ', 'ДИСЦИПЛИНЫ']]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown(f"<div style='color:#D32F2F; font-weight:bold; text-align:right; margin-top:10px;'>Найдено школ: {len(display_df)}</div>", unsafe_allow_html=True)
else:
    st.info("В выбранном году и муниципалитете школы с маркерами не найдены.")

st.markdown('</div>', unsafe_allow_html=True)  # закрытие main-content
