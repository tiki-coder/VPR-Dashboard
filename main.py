import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Аналитика ВПР", layout="wide", initial_sidebar_state="collapsed")

# --- STYLING (Адаптировано для светлой и тёмной тем + уплотнение) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Базовые стили */
    html, body, [class*="css"] { 
        font-family: 'Roboto', sans-serif; 
        background-color: #F8F9FB; 
        color: #1C1B1F; 
    }
    .stApp { background-color: #F8F9FB; }
    
    /* Убираем лишнее пространство сверху */
    .block-container {
        padding-top: 1rem !important;   
        max-width: 100% !important;
    }
    header { visibility: hidden; }
    
    /* Главный заголовок */
    .main-header {
        font-size: 32px;
        font-weight: 700;
        margin-top: 0px !important;
        margin-bottom: 12px;
        padding-top: 8px;
    }
    
    /* Метрики */
    [data-testid="stMetricValue"] { 
        color: #6750A4; 
        font-weight: 700; 
        font-size: 38px!important; 
    }
    [data-testid="stMetricLabel"] { 
        font-size: 14px!important; 
        color: #49454F; 
        margin-bottom: 4px;
    }
    
    /* Пояснения в скобках — меньший шрифт, серый цвет */
    .metric-subtitle {
        font-size: 13px;
        color: #8B8B8D;
        margin-left: 6px;
    }
    
    /* Заголовки разделов */
    h2, h3 {
        margin-bottom: 8px !important;
    }
    
    /* HR линии */
    hr {
        margin: 12px 0 !important;
        border: 1px solid #E0E0E0;
    }
    
    /* Запрет ввода в selectbox */
    .stSelectbox input {
        pointer-events: none;
        caret-color: transparent;
    }
    
    /* Адаптация для тёмной темы */
    @media (prefers-color-scheme: dark) {
        html, body, [class*="css"] { 
            background-color: #121212; 
            color: #E6E6E6; 
        }
        .stApp { background-color: #121212; }
        
        .main-header { color: #E6E6E6; }
        [data-testid="stMetricValue"] { color: #A688FF; }
        [data-testid="stMetricLabel"] { color: #B3B3B3; }
        .metric-subtitle { color: #A0A0A0; }
        hr { border-color: #333333; }
    }
    </style>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА ДАННЫХ ---
@st.cache_data(show_spinner=False)
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    marks_path = os.path.join(script_dir, "marks.xlsx")
    scores_path = os.path.join(script_dir, "scores.xlsx")
    
    if not os.path.exists(marks_path) or not os.path.exists(scores_path):
        st.error("Файлы не найдены. Проверьте наличие marks.xlsx и scores.xlsx в корне репозитория.")
        return None, None
    
    try:
        df_marks = pd.read_excel(marks_path)
        df_scores = pd.read_excel(scores_path)
        return df_marks, df_scores
    except Exception as e:
        st.error(f"Ошибка чтения файлов: {e}")
        return None, None

with st.spinner("Загрузка данных ВПР..."):
    df_marks, df_scores = load_data()

if df_marks is None or df_scores is None:
    st.stop()

st.markdown("<div class='main-header'>Аналитика ВПР</div>", unsafe_allow_html=True)

# --- ФИЛЬТРЫ ---
st.subheader("Фильтры")
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

st.markdown("<hr>", unsafe_allow_html=True)

# --- ФИЛЬТРАЦИЯ ---
m_sub = subj_df.copy()
if sel_mun != "Все":
    m_sub = m_sub[m_sub['Муниципалитет'] == sel_mun]
if sel_oo != "Все":
    m_sub = m_sub[m_sub['ОО'] == sel_oo]

if m_sub.empty:
    st.warning("Нет данных. Попробуйте изменить параметры в фильтрах.")
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
    perc_2 = percentages.get('2', 0)
    perc_3 = percentages.get('3', 0)
    perc_4 = percentages.get('4', 0)
    perc_5 = percentages.get('5', 0)

col_params, col_participants, col_quality, col_success = st.columns(4)

with col_params:
    st.markdown(f"<p style='margin: 0; padding: 0;'><b>Год:</b> {sel_year}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin: 0; padding: 0;'><b>Класс:</b> {sel_class}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin: 0; padding: 0;'><b>Предмет:</b> {sel_subj}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin: 0; padding: 0;'><b>Муниципалитет:</b> {sel_mun if sel_mun != 'Все' else 'Все'}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin: 0; padding: 0; white-space: nowrap; overflow: visible;'><b>ОО:</b> {sel_oo if sel_oo != 'Все' else 'Все'}</p>", unsafe_allow_html=True)

with col_participants:
    st.metric("Участники", f"{int(total_p)}")

with col_quality:
    st.metric("Качество знаний", f"{perc_4 + perc_5:.1f}%")
    st.markdown("<span class='metric-subtitle'>(отметки «4» и «5»)</span>", unsafe_allow_html=True)

with col_success:
    st.metric("Успеваемость", f"{perc_3 + perc_4 + perc_5:.1f}%")
    st.markdown("<span class='metric-subtitle'>(без двоек)</span>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- ГРАФИКИ ---
g1, g2 = st.columns(2)

with g1:
    st.subheader("Статистика по отметкам (%)")
    fig_m = px.bar(
        x=['2', '3', '4', '5'],
        y=[perc_2, perc_3, perc_4, perc_5],
        color=['2', '3', '4', '5'],
        color_discrete_map={'2': '#F44336', '3': '#FF9800', '4': '#4CAF50', '5': '#2196F3'},
        text=[f"{perc_2:.1f}%", f"{perc_3:.1f}%", f"{perc_4:.1f}%", f"{perc_5:.1f}%"]
    )
    fig_m.update_traces(textposition='outside')
    fig_m.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title="Доля учащихся (%)", ticksuffix="%"),
        xaxis=dict(title="Отметка", tickmode='array', tickvals=['2', '3', '4', '5'], ticktext=['2', '3', '4', '5'])
    )
    st.plotly_chart(fig_m, use_container_width=True)

with g2:
    st.subheader("Распределение первичных баллов (%)")
    sub_scores = df_scores[
        (df_scores['Год'] == sel_year) &
        (df_scores['Класс'] == sel_class) &
        (df_scores['Предмет'] == sel_subj)
    ]
    score_cols = [col for col in sub_scores.columns if col.isdigit() and 0 <= int(col) <= 39 and sub_scores[col].notna().any()]
    score_cols.sort(key=int)
    max_score = max(map(int, score_cols)) if score_cols else 0

    logins = m_sub['Логин'].unique()
    s_agg = df_scores[
        (df_scores['Логин'].isin(logins)) &
        (df_scores['Год'] == sel_year) &
        (df_scores['Класс'] == sel_class) &
        (df_scores['Предмет'] == sel_subj)
    ]

    if max_score == 0:
        st.info("Нет данных по баллам для этого предмета")
    else:
        total_s = s_agg['Кол-во участников'].sum() or 1
        y_vals = []
        for c in score_cols:
            val = ((s_agg[c] / 100) * s_agg['Кол-во участников']).sum() / total_s * 100
            y_vals.append(val)

        full_x = list(range(0, max_score + 1))
        full_y = [0.0] * len(full_x)
        score_map = {int(c): y for c, y in zip(score_cols, y_vals)}
        for i in full_x:
            full_y[i] = score_map.get(i, 0.0)

        fig_s = px.bar(x=full_x, y=full_y, color_discrete_sequence=['#6750A4'])

        step = 5
        tickvals = list(range(0, max_score + 1, step))
        if max_score % step != 0:
            tickvals.append(max_score)
        ticktext = [f'<b>{val}</b>' if val in [0, max_score] else str(val) for val in tickvals]

        fig_s.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="Доля учащихся (%)", ticksuffix="%"),
            xaxis=dict(title="Первичный балл", tickvals=tickvals, ticktext=ticktext)
        )
        st.plotly_chart(fig_s, use_container_width=True)
