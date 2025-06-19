import streamlit as st
import pandas as pd

st.set_page_config(page_title="經濟學（下）期末考題庫", layout="centered")
st.title("📘 經濟學（下）期末考題庫")

NUM_QUESTIONS = 5

@st.cache_data
def load_questions():
    df = pd.read_csv("題庫.csv")
    return df.sample(n=NUM_QUESTIONS).reset_index(drop=True)

# 初始化
if "submitted" not in st.session_state:
    st.session_state.questions = load_questions()
    st.session_state.answers = [None] * NUM_QUESTIONS
    st.session_state.submitted = False

questions = st.session_state.questions

# 顯示題目
for i, row in questions.iterrows():
    st.markdown(f"**Q{i+1}. {row['題目']}**")

    # 自動判斷有幾個選項（支援 A~E）
    options = {}
    for opt in ["A", "B", "C", "D", "E"]:
        if pd.notna(row.get(opt)):
            options[opt] = row[opt]

    selected = st.radio(
        label="請選擇答案：",
        options=list(options.keys()),
        format_func=lambda x: f"{x}) {options[x]}",
        key=f"q{i}"
    )
    st.session_state.answers[i] = selected

# 提交按鈕
if st.button("✅ 提交答案"):
    st.session_state.submitted = True

# 顯示結果
if st.session_state.submitted:
    score = 0
    st.markdown("---")
    st.subheader("📊 結果")

    for i, row in questions.iterrows():
        correct = str(row["答案"]).strip().upper()
        user_ans = str(st.session_state.answers[i]).strip().upper()

        correct_text = row.get(correct, "")
        user_text = row.get(user_ans, "")

        if user_ans == correct:
            score += 1
            st.success(f"Q{i+1}: ✅ 答對！你選的是 {user_ans}) {user_text}")
        else:
            st.error(
                f"Q{i+1}: ❌ 答錯。你選的是 {user_ans}) {user_text}\n\n正確答案是 {correct}) {correct_text}"
            )

    st.markdown(f"### 🎯 你總共答對：{score} / {NUM_QUESTIONS}")

# 重新出題按鈕
if st.button("🔄 重新開始"):
    st.session_state.questions = load_questions()
    st.session_state.answers = [None] * NUM_QUESTIONS
    st.session_state.submitted = False
    st.experimental_rerun()
