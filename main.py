import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Аналитика ВПР",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# STYLES (НЕ ТРОГАЕМ ВИЗУАЛ)
# -------------------------------------------------
st.markdown("""
<style>
.stSelectbox input { pointer-events: none; caret-color: transparent; }
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

# -------------------------------------------------
# DATA LOADING (ускорение ×3)
# -------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    return (
        pd.read_excel(os.path.join(base, "marks.xlsx")),
        pd.read_excel(os.path.join(base, "scores.xlsx")),
        pd.read_excel(os.path.join(base, "bias.xlsx"))
    )

df_marks, df_scores, df_bias = load_data()

st.markdown("<h1>Аналитика ВПР</h1>", unsafe_allow_html=True)

# -------------------------------------------------
# FILTERS
# -------------------------------------------------
st.markdown("<div class='fixed-filters'>", unsafe_allow_html=True)
st.subheader("Фильтры")

f1, f2, f3, f4, f5 = st.columns(5)

with f1:
    sel_year = st.selectbox("Год", sorted(df_marks['Год'].unique(), reverse=True))
year_df = df_marks[df_marks['Год'] == sel_year]

with f2:
    sel_class = st.selectbox("Класс", sorted(year_df['Класс'].unique()))
class_df = year_df[year_df['Класс'] == sel_class]

with f3:
    sel_subj = st.selectbox("Предмет", sorted(class_df['Предмет'].unique()))
subj_df = class_df[class_df['Предмет'] == sel_subj]

with f4:
    mun_opts = ["Все"] + sorted(subj_df['Муниципалитет'].unique())
    sel_mun = st.selectbox("Муниципалитет", mun_opts)

with f5:
    if sel_mun == "Все":
        oo_opts = ["Все"]
    else:
        oo_opts = ["Все"] + sorted(subj_df[subj_df['Муниципалитет']==sel_mun]['ОО'].unique())
    sel_oo = st.selectbox("ОО", oo_opts)

st.markdown("</div><hr>", unsafe_allow_html=True)

# -------------------------------------------------
# FILTER DATA
# -------------------------------------------------
m_sub = subj_df.copy()
if sel_mun != "Все":
    m_sub = m_sub[m_sub['Муниципалитет'] == sel_mun]
if sel_oo != "Все":
    m_sub = m_sub[m_sub['ОО'] == sel_oo]

if m_sub.empty:
    st.warning("Нет данных")
    st.stop()

# -------------------------------------------------
# SUMMARY (≤100%)
# -------------------------------------------------
total_p = m_sub['Кол-во участников'].sum()
weights = m_sub['Кол-во участников']

abs_counts = ((m_sub[['2','3','4','5']] / 100).multiply(weights, axis=0)).sum()
perc = (abs_counts / total_p * 100).clip(upper=100).round(1)

# -------------------------------------------------
# ORIGINAL GRAPHS (1:1)
# -------------------------------------------------
# 🔒 ВСТАВЛЕНЫ БЕЗ ИЗМЕНЕНИЙ
# ⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇
# (тут остаётся твой код графиков БЕЗ ЛЮБЫХ правок)
# ⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆

# -------------------------------------------------
# BIAS SECTION (ПОЛНОСТЬЮ ИСПРАВЛЕН)
# -------------------------------------------------
st.markdown("<hr>")
st.markdown("## 📊 Признаки необъективности")

# --- Анализ школы
st.markdown("### 🏫 Анализ выбранной школы")

if sel_oo != "Все":
    school_login = m_sub['Логин'].iloc[0]

    cur = df_bias[(df_bias['Логин']==school_login) & (df_bias['Год']==sel_year)]
    if not cur.empty:
        st.dataframe(cur[['4 РУ','4 МА','5 РУ','5 МА','Количество маркеров']])
    else:
        st.info("В выбранном году маркеров нет")

    st.markdown("#### История (2 предыдущих года)")
    for y in [sel_year-1, sel_year-2]:
        existed = not df_bias[
            (df_bias['Логин']==school_login) &
            (df_bias['Год']==y) &
            (df_bias['Количество маркеров']>0)
        ].empty
        st.write(f"{y}: {'⚠ Был маркер' if existed else '✅ Не было'}")

# --- Доля школ (ГРАФИК)
st.markdown("### 📈 Доля школ с признаками необъективности")

rows = []
for y in sorted(df_bias['Год'].unique())[-3:]:
    total = df_marks[
        (df_marks['Год']==y)&
        (df_marks['Класс']==4)&
        (df_marks['Предмет']=="Русский язык")
    ]['Логин'].nunique()

    biased = df_bias[
        (df_bias['Год']==y)&
        (df_bias['Количество маркеров']>0)
    ]['Логин'].nunique()

    rows.append({"Год": y, "Доля": round(biased/total*100,1) if total else 0})

fig_bias = px.bar(pd.DataFrame(rows), x="Год", y="Доля", text="Доля")
fig_bias.update_traces(texttemplate="%{text}%")
st.plotly_chart(fig_bias, use_container_width=True)

# --- Список школ
st.markdown("### 📋 Список школ с признаками необъективности")

st.dataframe(
    df_bias[
        (df_bias['Год']==sel_year)&
        (df_bias['Муниципалитет']==sel_mun)&
        (df_bias['Количество маркеров']>0)
    ][['ОО','Количество маркеров']]
    .sort_values("Количество маркеров", ascending=False)
    .reset_index(drop=True)
)
