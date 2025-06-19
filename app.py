import streamlit as st
import pandas as pd

st.set_page_config(page_title="經濟學（下）期末考題庫", layout="centered")
st.title("📘 經濟學（下）期末考題庫")

NUM_QUESTIONS = 20 # Changed to 20 questions as requested

@st.cache_data
def load_questions():
    df = pd.read_csv("題庫.csv")
    return df.sample(n=NUM_QUESTIONS).reset_index(drop=True)

# Initialize
if "questions" not in st.session_state:
    st.session_state.questions = load_questions()
    st.session_state.user_answers = [None] * NUM_QUESTIONS
    st.session_state.submitted = False
    st.session_state.results = [None] * NUM_QUESTIONS # To store immediate feedback

questions = st.session_state.questions

# Display questions
for i, row in questions.iterrows():
    st.markdown(f"**Q{i+1}. {row['題目']}**")

    # Automatically determine number of options (supports A~E)
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
    
    # Store the user's selected answer
    st.session_state.user_answers[i] = selected

    # Immediate feedback
    if selected is not None:
        correct_answer = str(row["答案"]).strip().upper()
        user_answer_text = options.get(selected, "")
        correct_answer_text = options.get(correct_answer, "")

        if selected == correct_answer:
            st.success(f"✅ 答對！你選的是 {selected}) {user_answer_text}")
            st.session_state.results[i] = True
        else:
            st.error(
                f"❌ 答錯。你選的是 {selected}) {user_answer_text}\n\n正確答案是 {correct_answer}) {correct_answer_text}"
            )
            st.session_state.results[i] = False
    st.markdown("---") # Separator between questions

# This part is for overall score after all questions are answered, not immediately after each
if st.button("✅ 提交最終結果"): # Changed button text to reflect final submission
    st.session_state.submitted = True

# Display overall results after final submission
if st.session_state.submitted:
    score = sum(1 for result in st.session_state.results if result is True)
    st.markdown("---")
    st.subheader("📊 最終得分")
    st.markdown(f"### 🎯 你總共答對：{score} / {NUM_QUESTIONS}")

# Restart button
if st.button("🔄 重新開始"):
    st.session_state.questions = load_questions()
    st.session_state.user_answers = [None] * NUM_QUESTIONS
    st.session_state.submitted = False
    st.session_state.results = [None] * NUM_QUESTIONS
    st.experimental_rerun()
