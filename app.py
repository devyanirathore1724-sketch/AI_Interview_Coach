import streamlit as st
from resume_parser import (
extract_text
)
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "question" not in st.session_state:
    st.session_state.question=""
if "history" not in st.session_state:
    st.session_state.history=[]
if "question_number" not in st.session_state:
    st.session_state.question_number=1
if "interview_completed" not in st.session_state:
    st.session_state.interview_completed=False
if "scores" not in st.session_state:
    st.session_state.scores=[]
if "result" not in st.session_state:
    st.session_state.result=""


def analyze_resume_with_ai(resume_text):
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""
Analyze this resume.

Give:
1. Top 5 Skills
2. Top 3 Strengths
3. Top 3 Weaknesses

Do NOT generate interview questions.

Resume:
{resume_text}
"""
            }
        ]
    )

    return message.choices[0].message.content


def generate_question(resume_text,history):
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[
{
                "role": "user",
                "content": f"""
You are an HR interviewer.

Based on this resume:

{resume_text}

Previous Interview History:

{history}

Based on the resume and previous interview history:

- Ask ONLY ONE next interview question.
- If there is no history, ask the first interview question.
- If there is history, ask a follow-up question based on the previous answer.
- Do not give explanations.
- Return only the question.
"""
            }
        ]
    )

    return message.choices[0].message.content
    
def evaluate_answer(question, answer):
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""
You are an expert interviewer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer in EXACTLY this format:

Score: X/10

Strengths:
- ...

Weaknesses:
- ...

Better Answer:
...

Tips for Improvement:
- ...
"""
            }
        ]
    )

    return message.choices[0].message.content
    
st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🤖"
)
def create_pdf(report_text):
    doc = SimpleDocTemplate("Interview_Report.pdf")
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>AI Interview Report</b>", styles["Heading1"]))
    story.append(Paragraph(report_text, styles["Normal"]))

    doc.build(story)
st.title("🤖 AI Interview Coach")
st.write("Welcome! Upload your resume and start your AI interview.")
uploaded_file = st.file_uploader("upload your resume(PDF)",
     type=["pdf"]
     )
if uploaded_file is not None:
    st.success("Resume Uploaded Successfully!")
    st.write("File Name:", uploaded_file.name)

    resume_text = extract_text(uploaded_file)

    st.subheader("📜Resume Content")
    st.write(resume_text)

    if st.button("🚀Analyze Resume"):
        with st.spinner("AI is thinking..."):
            st.session_state.feedback = analyze_resume_with_ai(resume_text)

    if st.session_state.feedback:
        if st.session_state.interview_completed:
            st.success("🏆Interview Completed!")

        average = 0
        if len(st.session_state.scores) > 0:
               average = (
            sum(st.session_state.scores) /
            len(st.session_state.scores)
    )

               st.subheader("⭐ OverallScore")
               st.write(f"{average:.1f}/10")
               st.subheader("AI Feedback")
        st.write(st.session_state.feedback)
        if st.button("👍Start Interview"):
            st.session_state.question_number=1
            st.session_state.history=[]
            st.session_state.question=generate_question(resume_text,
            st.session_state.history)
        if st.session_state.question:
            st.write(f"question{st.session_state.question_number} /5")
            progress = st.session_state.question_number/5
            st.progress(progress)
            st.subheader("🎤Interview Question")
            st.write(st.session_state.question)
            st.subheader("Your Answer")

            user_answer = st.text_area("Write Your Answer Here")

            if st.button("Evaluate Answer"):
                with st.spinner("Evaluating your answer..."):
                 result = evaluate_answer(
                    st.session_state.question,
                    user_answer
                )
                st.session_state.result=result
                try:
                       score_line = result.split("\n")[0]
                       score = int(score_line.split(":")[1].split("/")[0].strip())
                       st.session_state.scores.append(score)
                except:
                       pass
                st.session_state.history.append({
                    "question":
                st.session_state.question,
                "answer": user_answer,
                "evaluation": result
                })
                
        if st.session_state.result:
            st.subheader("⭐Evaluation Result")
            st.write(st.session_state.result)
            if st.button("⏭️ Next Question"):
              if st.session_state.question_number >= 5:
               st.session_state.interview_completed = True
              else:
                 st.session_state.question_number += 1
                 st.session_state.question = generate_question(
              resume_text,
              st.session_state.history
        )
                 st.rerun()