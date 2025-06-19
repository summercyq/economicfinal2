import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="經濟學（下）期末考題庫", layout="centered")
st.title("📘 經濟學（下）期末考題庫")

NUM_QUESTIONS = 20

@st.cache_data
def load_all_questions():
    try:
        df = pd.read_csv("題庫.csv")
        return df
    except FileNotFoundError:
        st.error("錯誤：找不到 '題庫.csv' 文件，請確保文件與應用程式在同一目錄下。")
        st.stop()

if "all_questions_df" not in st.session_state:
    st.session_state.all_questions_df = load_all_questions()

if "questions" not in st.session_state or st.session_state.restart_quiz:
    st.session_state.questions = st.session_state.all_questions_df.sample(n=NUM_QUESTIONS, replace=False).reset_index(drop=True)
    st.session_state.user_answers = [None] * NUM_QUESTIONS
    st.session_state.results = [None] * NUM_QUESTIONS
    st.session_state.restart_quiz = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "restart_quiz" not in st.session_state:
    st.session_state.restart_quiz = False

questions = st.session_state.questions

# Display questions
for i, row in questions.iterrows():
    # Clean the question string before applying Markdown
    question_text = str(row['題目']).strip() # Ensure it's a string and remove leading/trailing whitespace

    st.markdown(f"**Q{i+1}. {question_text}**") # Use the cleaned string

    # ... (rest of your code remains the same)

    # Automatically determine number of options (supports A~E)
    options_dict = {}
    for opt_key in ["A", "B", "C", "D", "E"]:
        if pd.notna(row.get(opt_key)):
            options_dict[opt_key] = row[opt_key]
    
    display_options_keys = ["_請選擇_"] + list(options_dict.keys())
    display_options_values = {"_請選擇_": "請選擇"}
    display_options_values.update(options_dict)

    initial_index = 0
    if st.session_state.user_answers[i] in options_dict:
        try:
            initial_index = display_options_keys.index(st.session_state.user_answers[i])
        except ValueError:
            initial_index = 0

    selected = st.radio(
        label="請選擇答案：",
        options=display_options_keys,
        format_func=lambda x: f"{x}) {display_options_values[x]}" if x != "_請選擇_" else "請選擇",
        key=f"q{i}",
        index=initial_index
    )
    
    if selected != "_請選擇_":
        st.session_state.user_answers[i] = selected
        
        correct_answer = str(row["答案"]).strip().upper()
        user_answer_text = options_dict.get(selected, "")
        correct_answer_text = options_dict.get(correct_answer, "")

        if selected == correct_answer:
            st.success(f"✅ 答對！你選的是 {selected}) {user_answer_text}")
            st.session_state.results[i] = True
        else:
            st.error(
                f"❌ 答錯。你選的是 {selected}) {user_answer_text}\n\n正確答案是 {correct_answer}) {correct_answer_text}"
            )
            st.session_state.results[i] = False
    else:
        st.session_state.results[i] = None
        st.session_state.user_answers[i] = None

    st.markdown("---")

if st.button("✅ 提交最終結果", key="submit_button"):
    st.session_state.submitted = True

if st.session_state.submitted:
    score = sum(1 for result in st.session_state.results if result is True)
    st.markdown("---")
    st.subheader("📊 最終得分")
    st.markdown(f"### 🎯 你總共答對：{score} / {NUM_QUESTIONS}")

if st.button("🔄 重新開始", key="restart_button"):
    st.session_state.restart_quiz = True
    st.session_state.user_answers = [None] * NUM_QUESTIONS
    st.session_state.submitted = False
    st.session_state.results = [None] * NUM_QUESTIONS
    st.experimental_rerun()
