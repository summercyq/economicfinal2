import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="經濟學（下）期末考題庫", layout="centered")
st.title("📘 經濟學（下）期末考題庫")

NUM_QUESTIONS = 20

@st.cache_data
def load_all_questions():
    """Loads the entire question bank from the CSV."""
    try:
        df = pd.read_csv("題庫.csv")
        return df
    except FileNotFoundError:
        st.error("錯誤：找不到 '題庫.csv' 文件，請確保文件與應用程式在同一目錄下。")
        st.stop()

# Load the full question bank once
if "all_questions_df" not in st.session_state:
    st.session_state.all_questions_df = load_all_questions()

# Function to initialize or reset the quiz state
def initialize_quiz_state():
    """Resets all quiz-related session state variables and loads new questions."""
    st.session_state.questions = st.session_state.all_questions_df.sample(n=NUM_QUESTIONS, replace=False).reset_index(drop=True)
    st.session_state.user_answers = [None] * NUM_QUESTIONS
    st.session_state.results = [None] * NUM_QUESTIONS
    st.session_state.all_answered = False
    # No need for a separate 'restart_quiz' flag if we call this directly

# Initialize quiz state on first run
if "questions" not in st.session_state:
    initialize_quiz_state()

questions = st.session_state.questions

# Flag to check if all questions have been attempted
all_questions_attempted = True

# Display questions
for i, row in questions.iterrows():
    question_text = str(row['題目']).strip()
    st.markdown(f"**Q{i+1}. {question_text}**")

    options_dict = {}
    for opt_key in ["A", "B", "C", "D", "E"]:
        if pd.notna(row.get(opt_key)):
            options_dict[opt_key] = row[opt_key]
    
    display_options_keys = list(options_dict.keys())
    
    initial_index = None
    if st.session_state.user_answers[i] in options_dict:
        try:
            initial_index = display_options_keys.index(st.session_state.user_answers[i])
        except ValueError:
            initial_index = None

    selected = st.radio(
        label="",
        options=display_options_keys,
        format_func=lambda x: f"{x}) {options_dict[x]}",
        key=f"q{i}",
        index=initial_index
    )
    
    # Store the user's selected answer and provide immediate feedback
    if selected is not None:
        st.session_state.user_answers[i] = selected
        
        correct_answer = str(row["答案"]).strip().upper()
        user_answer_text = options_dict.get(selected, "")
        correct_answer_text = options_dict.get(correct_answer, "")

        if selected == correct_answer:
            st.success(f"✅ 答對！你選的是 {selected}) {user_answer_text}")
            st.session_state.results[i] = True
        else:
            st.error(
                f"❌ 答錯。你選的是 {selected}) {user_answer_text}\n
