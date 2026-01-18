import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Аналитика ВПР",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# STYLES
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
}

.block-container {
    padding-top: 1rem !important;
    max-width: 100% !important;
}

header { visibility: hidden; }

.main-header {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 12px;
}

.metric-container { text-align: left; }
.metric-label { font-size: 14px; color: #49454F; font-weight: 500; }
.metric-value { font-size: 38px; font-weight: 700; color: #6750A4; }
.metric-subtitle { font-size: 13px; color: #8B8B8D; margin-left: 4px; }

hr { margin: 12px 0 !important; }

.stSelectbox input {
    pointer-events: none;
    caret-color: transparent;
}

/* Sticky filters */
.fixed-filters {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: inherit;
    padding-top: 8px;
    border-bottom: 1px solid #E0E0E0;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA LOADING (×3 SPEED)
# =========================================================
@st.cache_data(show_spinner=False)
def load_all_data():
    base = os.path.dirname(os.path.abspath(__file__))

    df_marks = pd.read_excel(os.path.join(base, "marks.xlsx"))
    df_scores = pd.read_excel(os.path.join(base, "scores.xlsx"))
    df_bias = pd.read_excel(os.path.join(base, "bias.xlsx"))

    return df_marks, df_scores, df_bias

with st.spinner("Загрузка данных…"):
    df_marks, df_scores, df_bias = load_all_data()

# =========================================================
# HEADER
# =========================================================
st.markdown("<div class='main-header'>Аналитика ВПР</div>", unsafe_allow_html=True)

# =========================================================
# FILTERS (STICKY)
# =========================================================
st.markdown("<div class='fixed-filters'>", unsafe_allow_html=True)
st.subheader("Фильтры")

f1, f2, f3, f4, f5 = st.columns(5)

years = sorted(df_marks['Год'].unique(), reverse=True)
with f1:
    sel_year = st.selectbox("Год", years)

year_df = df_marks[df_marks['Год'] == sel_year]
classes = sorted(year_df['Класс'].unique())
with f2:
    sel_class = st.selectbox("Класс", classes)

class_df = year_df[year_df['Класс'] == sel_class]
subjects = sorted(class_df['Предмет'].unique())
with f3:
    sel_subj = st.selectbox("Предмет", subjects)

subj_df = class_df[class_df['Предмет'] == sel_subj]
mun_opts = ["Все"] + sorted(subj_df['Муниципалитет'].unique())
with f4:
    sel_mun = st.selectbox("Муниципалитет", mun_opts)

if sel_mun == "Все":
    oo_opts = ["Все"]
else:
    oo_opts = ["Все"] + sorted(subj_df[subj_df['Муниципалитет'] == sel_mun]['ОО'].unique())

with f5:
    sel_oo = st.selectbox("ОО (Школа)", oo_opts)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# FILTERED DATA
# =========================================================
m_sub = subj_df.copy()
if sel_mun != "Все":
    m_sub = m_sub[m_sub['Муниципалитет'] == sel_mun]
if sel_oo != "Все":
    m_sub = m_sub[m_sub['ОО'] == sel_oo]

if m_sub.empty:
    st.warning("Нет данных по выбранным параметрам")
    st.stop()

# =========================================================
# SUMMARY METRICS
# =========================================================
st.subheader("Сводные показатели")

total_p = int(m_sub['Кол-во участников'].sum())
weights = m_sub['Кол-во участников']

if total_p:
    abs_counts = ((m_sub[['2','3','4','5']] / 100).multiply(weights, axis=0)).sum()
    perc = (abs_counts / total_p * 100).round(1)
else:
    perc = pd.Series({'2':0,'3':0,'4':0,'5':0})

unique_oo_count = m_sub['Логин'].nunique()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    **Год:** {sel_year}  
    **Класс:** {sel_class}  
    **Предмет:** {sel_subj}  
    **Муниципалитет:** {sel_mun}  
    **ОО:** {unique_oo_count if sel_oo=='Все' else sel_oo}
    """)

with c2:
    st.markdown(f"<div class='metric-container'><div class='metric-label'>Участники</div><div class='metric-value'>{total_p}</div></div>", unsafe_allow_html=True)

with c3:
    st.markdown(f"<div class='metric-container'><div class='metric-label'>Качество</div><div class='metric-value'>{perc['4']+perc['5']:.1f}%</div></div>", unsafe_allow_html=True)

with c4:
    st.markdown(f"<div class='metric-container'><div class='metric-label'>Успеваемость</div><div class='metric-value'>{perc['3']+perc['4']+perc['5']:.1f}%</div></div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# GRAPHS (ORIGINAL, OPTIMIZED)
# =========================================================
g1, g2 = st.columns(2)

with g1:
    fig = px.bar(
        x=['2','3','4','5'],
        y=[perc['2'],perc['3'],perc['4'],perc['5']],
        text=[f"{perc[x]}%" for x in ['2','3','4','5']],
        color=['2','3','4','5'],
        color_discrete_map={'2':'#F44336','3':'#FF9800','4':'#4CAF50','5':'#2196F3'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with g2:
    s = df_scores[
        (df_scores['Год']==sel_year)&
        (df_scores['Класс']==sel_class)&
        (df_scores['Предмет']==sel_subj)&
        (df_scores['Логин'].isin(m_sub['Логин']))
    ]
    score_cols = [c for c in s.columns if c.isdigit() and s[c].notna().any()]
    score_cols.sort(key=int)

    if score_cols:
        total = s['Кол-во участников'].sum()
        vals = [((s[c]/100)*s['Кол-во участников']).sum()/total*100 for c in score_cols]
        fig2 = px.bar(x=list(map(int,score_cols)), y=vals)
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Нет данных по баллам")

# =========================================================
# BIAS SECTION
# =========================================================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("## 📊 Признаки необъективности")

selected_logins = m_sub['Логин'].unique()
school_bias = df_bias[
    (df_bias['Год']==sel_year)&
    (df_bias['Логин'].isin(selected_logins))
]

st.markdown("### 🏫 Анализ выбранной школы")
if sel_oo != "Все" and not school_bias.empty:
    st.dataframe(school_bias[['4 РУ','4 МА','5 РУ','5 МА','Количество маркеров']])
else:
    st.info("В выбранном году маркеры отсутствуют")

st.markdown("### 📈 Доля школ с признаками (Русский язык, 4 класс)")
years3 = sorted(df_bias['Год'].unique(), reverse=True)[:3]

rows = []
for y in years3:
    total_sch = df_marks[
        (df_marks['Год']==y)&
        (df_marks['Класс']==4)&
        (df_marks['Предмет']=="Русский язык")&
        (df_marks['Муниципалитет']==sel_mun)
    ]['Логин'].nunique()

    biased = df_bias[
        (df_bias['Год']==y)&
        (df_bias['Муниципалитет']==sel_mun)&
        (df_bias['Количество маркеров']>0)
    ]['Логин'].nunique()

    rows.append([y, biased, total_sch, round(biased/total_sch*100,1) if total_sch else 0])

st.dataframe(pd.DataFrame(rows, columns=["Год","Школ с маркерами","Всего школ","Доля %"]))

st.markdown("### 📋 Список школ")
st.dataframe(
    df_bias[
        (df_bias['Год']==sel_year)&
        (df_bias['Муниципалитет']==sel_mun)&
        (df_bias['Количество маркеров']>0)
    ][['ОО','Количество маркеров']]
    .sort_values("Количество маркеров", ascending=False)
    .reset_index(drop=True)
)
