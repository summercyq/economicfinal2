import streamlit as st
import pandas as pd
import numpy as np # Import numpy for potential future use or robust data handling

st.set_page_config(page_title="經濟學（下）期末考題庫", layout="centered")
st.title("📘 經濟學（下）期末考題庫")

NUM_QUESTIONS = 20 # Changed to 20 questions as requested

# Use st.session_state to ensure questions are loaded only once per session
@st.cache_data
def load_all_questions():
    """Loads the entire question bank from the CSV."""
    try:
        df = pd.read_csv("題庫.csv")
        return df
    except FileNotFoundError:
        st.error("錯誤：找不到 '題庫.csv' 文件，請確保文件與應用程式在同一目錄下。")
        st.stop() # Stop the app if the file is not found

# Initialize session state variables
if "all_questions_df" not in st.session_state:
    st.session_state.all_questions_df = load_all_questions()

if "questions" not in st.session_state or st.session_state.restart_quiz:
    # Sample NUM_QUESTIONS from the full dataframe
    st.session_state.questions = st.session_state.all_questions_df.sample(n=NUM_QUESTIONS, replace=False).reset_index(drop=True)
    st.session_state.user_answers = [None] * NUM_QUESTIONS
    st.session_state.results = [None] * NUM_QUESTIONS
    st.session_state.restart_quiz = False # Reset restart flag

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# This flag helps control when to load new questions
if "restart_quiz" not in st.session_state:
    st.session_state.restart_quiz = False

questions = st.session_state.questions

# Display questions
for i, row in questions.iterrows():
    st.markdown(f"**Q{i+1}. {row['題目']}**")

    # Automatically determine number of options (supports A~E)
    options_dict = {}
    for opt_key in ["A", "B", "C", "D", "E"]:
        if pd.notna(row.get(opt_key)):
            options_dict[opt_key] = row[opt_key]
    
    # Add a "請選擇" option as the first choice
    display_options_keys = ["_請選擇_"] + list(options_dict.keys())
    display_options_values = {"_請選擇_": "請選擇"} # Placeholder for 'Please Select'
    display_options_values.update(options_dict)

    # Determine the initial index for the radio button
    initial_index = 0 # Default to "請選擇"
    if st.session_state.user_answers[i] in options_dict:
        try:
            initial_index = display_options_keys.index(st.session_state.user_answers[i])
        except ValueError:
            # Fallback if somehow the answer is not in current options (shouldn't happen with proper data)
            initial_index = 0

    selected = st.radio(
        label="請選擇答案：",
        options=display_options_keys,
        format_func=lambda x: f"{x}) {display_options_values[x]}" if x != "_請選擇_" else "請選擇",
        key=f"q{i}",
        index=initial_index
    )
    
    # Store the user's selected answer, but only if it's not the placeholder
    if selected != "_請選擇_":
        st.session_state.user_answers[i] = selected
        
        # Immediate feedback moved here to only trigger when a real answer is selected
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
        # If "_請選擇_" is selected (initial state or user unselected), clear previous feedback
        st.session_state.results[i] = None
        st.session_state.user_answers[i] = None # Ensure user_answers is None when nothing is selected

    st.markdown("---") # Separator between questions

# This part is for overall score after all questions are answered, not immediately after each
if st.button("✅ 提交最終結果", key="submit_button"):
    st.session_state.submitted = True

# Display overall results after final submission
if st.session_state.submitted:
    # Filter out None values before calculating score, only count True results
    score = sum(1 for result in st.session_state.results if result is True)
    st.markdown("---")
    st.subheader("📊 最終得分")
    st.markdown(f"### 🎯 你總共答對：{score} / {NUM_QUESTIONS}")

# Restart button
if st.button("🔄 重新開始", key="restart_button"):
    st.session_state.restart_quiz = True # Set flag to true to trigger new question loading
    # Reset other session states for a fresh start
    st.session_state.user_answers = [None] * NUM_QUESTIONS
    st.session_state.submitted = False
    st.session_state.results = [None] * NUM_QUESTIONS
    st.experimental_rerun() # Rerun the app to load new questions
