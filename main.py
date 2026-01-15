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
    
    header { visibility: hidden; }
    
    .main-header {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 12px;
        padding-top: 8px;
    }
    
    hr {
        margin: 12px 0 !important;
        border: 1px solid #E0E0E0;
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
    
    /* Минимальный отступ под панелью */
    .main-content {
        margin-top: 50px;
    }
    
    /* Тёмная тема */
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #121212; }
        .sticky-filters {
            background-color: #121212;
            border-bottom: 2px solid #333333;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        hr { border-color: #333333; }
    }
    </style>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА И ОЧИСТКА ДАННЫХ (strip пробелов во всех строках) ---
script_dir = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner=False)
def load_marks():
    path = os.path.join(script_dir, "marks.xlsx")
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df

@st.cache_data(show_spinner=False)
def load_scores():
    path = os.path.join(script_dir, "scores.xlsx")
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df

@st.cache_data(show_spinner=False)
def load_bias():
    path = os.path.join(script_dir, "bias.xlsx")
    if not os.path.exists(path):
        st.error("Файл bias.xlsx не найден.")
        return pd.DataFrame()
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df

with st.spinner("Загрузка данных..."):
    df_marks = load_marks()
    df_scores = load_scores()
    df_bias = load_bias()

if df_marks.empty or df_scores.empty:
    st.stop()

st.markdown("<div class='main-header'>Аналитика ВПР</div>", unsafe_allow_html=True)

# --- ПАНЕЛЬ ФИЛЬТРОВ ---
st.markdown('<div class="sticky-filters">', unsafe_allow_html=True)
f1, f2, f3, f4, f5 = st.columns(5)

years = sorted(df_marks['Год'].unique(), reverse=True)
with f1:
    sel_year = st.selectbox("Год", years, index=0, key="year")

year_df = df_marks[df_marks['Год'] == sel_year]
classes = sorted(year_df['Класс'].unique())
with f2:
    sel_class = st.selectbox("Класс", classes, key="class")

class_df = year_df[year_df['Класс'] == sel_class]
subjects = sorted(class_df['Предмет'].unique())
with f3:
    sel_subj = st.selectbox("Предмет", subjects, key="subj")

subj_df = class_df[class_df['Предмет'] == sel_subj]
mun_options = ["Все"] + sorted(subj_df['Муниципалитет'].unique().tolist())
with f4:
    sel_mun = st.selectbox("Муниципалитет", mun_options, key="mun")

if sel_mun == "Все":
    oo_options = ["Все"]
else:
    mun_df = subj_df[subj_df['Муниципалитет'] == sel_mun]
    oo_options = ["Все"] + sorted(mun_df['ОО'].unique().tolist())
with f5:
    sel_oo = st.selectbox("ОО (Школа)", oo_options, key="oo")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- ФИЛЬТРАЦИЯ ---
m_sub = subj_df.copy()
if sel_mun != "Все":
    m_sub = m_sub[m_sub['Муниципалитет'] == sel_mun]
if sel_oo != "Все":
    m_sub = m_sub[m_sub['ОО'] == sel_oo]

if m_sub.empty:
    st.warning("Нет данных по выбранным фильтрам.")
    st.stop()

# --- СВОДНЫЕ ПОКАЗАТЕЛИ (с капом 100%) ---
st.subheader("Сводные показатели")
total_p = m_sub['Кол-во участников'].sum()

if total_p == 0:
    perc_2 = perc_3 = perc_4 = perc_5 = 0
else:
    weights = m_sub['Кол-во участников']
    abs_counts = ((m_sub[['2', '3', '4', '5']] / 100) * weights).sum()
    percentages = (abs_counts / total_p * 100).round(1)
    perc_2 = min(100.0, percentages.get('2', 0))
    perc_3 = min(100.0, percentages.get('3', 0))
    perc_4 = min(100.0, percentages.get('4', 0))
    perc_5 = min(100.0, percentages.get('5', 0))

perc_quality = min(100.0, round(perc_4 + perc_5, 1))
perc_success = min(100.0, round(perc_3 + perc_4 + perc_5, 1))

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write(f"**Год:** {sel_year}<br>**Класс:** {sel_class}<br>**Предмет:** {sel_subj}<br>**Муниципалитет:** {sel_mun}<br>**ОО:** {sel_oo}", unsafe_allow_html=True)
with col2:
    st.metric("Участники", int(total_p))
with col3:
    st.metric("Качество знаний (4+5)", f"{perc_quality}%")
with col4:
    st.metric("Успеваемость (без 2)", f"{perc_success}%")

st.markdown("<hr>", unsafe_allow_html=True)

# --- ГРАФИКИ (полные оригинальные настройки + одинаковый config) ---
plot_config = {
    'toImageButtonOptions': {'format': 'png'},
    'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'toggleSpikelines'],
    'displaylogo': False
}

g1, g2 = st.columns(2)

with g1:
    st.subheader("Статистика по отметкам")
    percs_capped = [min(100.0, p) for p in [perc_2, perc_3, perc_4, perc_5]]
    fig_m = px.bar(x=['2','3','4','5'], y=percs_capped, color=['2','3','4','5'],
                   color_discrete_map={'2':'#F44336','3':'#FF9800','4':'#4CAF50','5':'#2196F3'},
                   text=[f"{p:.1f}%" for p in percs_capped])
    fig_m.update_traces(textposition='outside')
    fig_m.update_layout(height=300, showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        yaxis=dict(title="Доля учащихся (%)", ticksuffix="%", range=[0, max(percs_capped or [100]) + 10]),
                        xaxis=dict(title="Отметка", fixedrange=True),
                        xaxis_fixedrange=True, yaxis_fixedrange=True)
    st.plotly_chart(fig_m, use_container_width=True, config=plot_config)

with g2:
    st.subheader("Распределение первичных баллов")
    logins = m_sub['Логин'].unique()
    s_agg = df_scores[(df_scores['Логин'].isin(logins)) & (df_scores['Год'] == sel_year) &
                      (df_scores['Класс'] == sel_class) & (df_scores['Предмет'] == sel_subj)]
    score_cols = [col for col in df_scores.columns if str(col).isdigit()]
    score_cols = sorted([int(c) for c in score_cols if s_agg[c].notna().any()])
    
    if not score_cols or s_agg.empty:
        st.info("Нет данных по первичным баллам")
    else:
        max_score = max(score_cols)
        total_s = s_agg['Кол-во участников'].sum() or 1
        y_vals = [min(100.0, round(((s_agg[str(c)] / 100) * s_agg['Кол-во участников']).sum() / total_s * 100, 1)) for c in score_cols]
        
        fig_s = px.bar(x=score_cols, y=y_vals, text=[f"{v}%" if v > 0 else "" for v in y_vals],
                       color_discrete_sequence=['#6750A4'])
        fig_s.update_traces(textposition='outside')
        fig_s.update_layout(height=300, showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            yaxis=dict(title="Доля учащихся (%)", ticksuffix="%", range=[0, max(y_vals)+10 or 100]),
                            xaxis=dict(title=f"Первичный балл (максимум: {max_score})"))
        st.plotly_chart(fig_s, use_container_width=True, config=plot_config)

# --- РАЗДЕЛ ПРИЗНАКИ НЕОБЪЕКТИВНОСТИ (полностью перепроверенная логика) ---
st.markdown("<hr>", unsafe_allow_html=True)
st.header("Признаки необъективности")

marker_cols = ['4 РУ', '4 МА', '5 РУ', '5 МА']
marker_display = {'4 РУ': 'РУ4', '4 МА': 'МА4', '5 РУ': 'РУ5', '5 МА': 'МА5'}

# Блок 1: Анализ школы (по логину и году из marks, независимо от предмета)
if sel_oo == "Все":
    st.info("👈 Выберите школу для анализа")
else:
    school_logins = m_sub['Логин'].unique()
    if len(school_logins) != 1:
        st.warning("У школы несколько логинов")
    else:
        login = school_logins[0]
        st.subheader(f"Анализ выбранной школы ({sel_year})")
        bias_school = df_bias[(df_bias['Год'] == sel_year) & (df_bias['Логин'] == login)]
        if bias_school.empty:
            st.success("Признаки необъективности не выявлены")
        else:
            row = bias_school.iloc[0]
            active_markers = [marker_display[col] for col in marker_cols if row.get(col, 0) == 1]
            num_markers = sum(row.get(col, 0) for col in marker_cols)
            if active_markers:
                st.warning(f"Выявленные маркеры: {', '.join(active_markers)}")
            st.write(f"🔴 Количество маркеров: **{num_markers}**")
        
        prev_years = [y for y in [sel_year-1, sel_year-2] if y in df_bias['Год'].unique()]
        if prev_years:
            st.markdown("**Попадание в предыдущие годы**")
            for py in sorted(prev_years):
                prev = df_bias[(df_bias['Год'] == py) & (df_bias['Логин'] == login)]
                st.write(f"• {py} год: {'попадала' if not prev.empty else 'не попадала'}")

# Блок 2: Доля (исправлена защита от 0 школ в РУ 4 + strip)
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Доля ОО с признаками необъективности (%) по муниципалитету")

years_chart = sorted([sel_year-2, sel_year-1, sel_year])
percs = []
texts = []
bar_colors = []

for y in years_chart:
    # Деноминатор — школы, участвовавшие в РУ 4 кл (из marks)
    ru4 = df_marks[(df_marks['Год'] == y) & (df_marks['Класс'] == 4) & (df_marks['Предмет'] == 'Русский язык')]
    if sel_mun != "Все":
        ru4 = ru4[ru4['Муниципалитет'] == sel_mun]
    total_schools = ru4['Логин'].nunique()
    
    # Числитель — школы с ≥1 маркером (из bias)
    bias_y = df_bias[df_bias['Год'] == y]
    if sel_mun != "Все":
        bias_y = bias_y[bias_y['Муниципалитет'] == sel_mun]
    biased_schools = bias_y[bias_y[marker_cols].sum(axis=1) > 0]['Логин'].nunique()
    
    if total_schools == 0:
        perc = 0
        text = "Нет данных по РУ 4"
    else:
        perc = int(round(min(100.0, biased_schools / total_schools * 100)))
        text = f"{perc}%"
    
    percs.append(perc)
    texts.append(text)
    bar_colors.append('#FF9800' if y == sel_year else '#B0BEC5')

fig_bias = px.bar(x=[str(y) for y in years_chart], y=percs, text=texts,
                  color=[str(y) for y in years_chart], color_discrete_sequence=bar_colors)
fig_bias.update_traces(textposition='outside')
fig_bias.update_xaxes(type='category')
fig_bias.update_layout(height=350, showlegend=False, margin=dict(l=10,r=10,t=30,b=10),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       yaxis=dict(title="", range=[0, max(percs or [100]) + 10], ticksuffix="%"),
                       xaxis=dict(title=""))
st.plotly_chart(fig_bias, use_container_width=True)

# Блок 3: Список школ (из bias, названия полные)
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader(f"Список ОО с маркерами ({sel_year})")

bias_current = df_bias[df_bias['Год'] == sel_year].copy()
if sel_mun != "Все":
    bias_current = bias_current[bias_current['Муниципалитет'] == sel_mun]

bias_current['num_markers'] = bias_current[marker_cols].sum(axis=1)
bias_current['disciplines'] = bias_current.apply(
    lambda row: ' '.join([marker_display.get(col, col) for col in marker_cols if row.get(col, 0) == 1]), axis=1)

display_df = bias_current[bias_current['num_markers'] > 0].copy()
if not display_df.empty:
    display_df = display_df.sort_values('num_markers', ascending=False)
    display_df['МАРКЕРОВ'] = display_df['num_markers'].apply(lambda x: f"🔴 {int(x)}")
    display_df = display_df.rename(columns={'ОО': 'НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ', 'disciplines': 'ДИСЦИПЛИНЫ'})
    display_df = display_df[['НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ', 'МАРКЕРОВ', 'ДИСЦИПЛИНЫ']]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown(f"<div style='color:#D32F2F; font-weight:bold; text-align:right;'>Найдено школ: {len(display_df)}</div>", unsafe_allow_html=True)
else:
    st.info("Школы с маркерами не найдены")

st.markdown('</div>', unsafe_allow_html=True)
