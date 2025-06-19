import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="經濟學（下）期末考題庫", layout="centered")
st.title("📘 經濟學（下）期末考題庫")

NUM_QUESTIONS = 20

# Use st.cache_data to load the full question bank only once per session
@st.cache_data(show_spinner=False)
def load_all_questions():
    """Loads the entire question bank from the CSV."""
    try:
        df = pd.read_csv("題庫.csv")
        return df
    except FileNotFoundError:
        st.error("錯誤：找不到 '題庫.csv' 文件，請確保文件與應用程式在同一目錄下。")
        st.stop()

# Load the full question bank into session state the very first time the app runs
if "all_questions_df" not in st.session_state:
    st.session_state.all_questions_df = load_all_questions()

# Function to initialize or reset the quiz state with new questions
def initialize_quiz_state():
    """Resets all quiz-related session state variables and loads NEW questions."""
    # Ensure there are enough questions to sample
    if len(st.session_state.all_questions_df) < NUM_QUESTIONS:
        st.error(f"錯誤：題庫中只有 {len(st.session_state.all_questions_df)} 題，不足以抽取 {NUM_QUESTIONS} 題。請增加題庫題目數量。")
        st.stop()
    
    st.session_state.questions = st.session_state.all_questions_df.sample(n=NUM_QUESTIONS, replace=False).reset_index(drop=True)
    st.session_state.user_answers = [None] * NUM_QUESTIONS
    st.session_state.results = [None] * NUM_QUESTIONS
    st.session_state.all_answered = False
    # Set a flag to indicate the quiz has been initialized or reset
    st.session_state.quiz_active = True 

# Check if the quiz needs to be initialized (first run or reset requested)
# We use 'quiz_active' to control the main quiz flow
if "quiz_active" not in st.session_state or not st.session_state.quiz_active:
    initialize_quiz_state()

# --- MODIFICATION START ---
# Define a callback for the restart button
def restart_quiz_callback():
    st.session_state.quiz_active = False # Signal to re-initialize on next run
    # No st.experimental_rerun() here
# --- MODIFICATION END ---

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
                f"""❌ 答錯。你選的是 {selected}) {user_answer_text}
正確答案是 {correct_answer}) {correct_answer_text}"""
            )
            st.session_state.results[i] = False
    else:
        st.session_state.results[i] = None
        st.session_state.user_answers[i] = None
        all_questions_attempted = False # If any question is not answered, set this flag to False

    st.markdown("---") # Separator between questions

# Update all_answered state
st.session_state.all_answered = all_questions_attempted

# Display results only if all questions have been attempted AND all results are non-None
if st.session_state.all_answered and all(res is not None for res in st.session_state.results):
    score = sum(1 for result in st.session_state.results if result is True)
    st.markdown("---")
    st.subheader("📊 答題結果")
    st.markdown(f"### 🎯 你總共答對：{score} / {NUM_QUESTIONS}")

# Restart button - always available
st.button(
    "🔄 重新開始",
    key="restart_button_bottom",
    on_click=restart_quiz_callback # Use the callback function here
)
