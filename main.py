# app.py

import os
import streamlit as st
from openai import OpenAI

# ─── 1. Streamlit page config ────────────────────────────────────────────────────
st.set_page_config(page_title="LeapBot Chat", page_icon="🤖")

# ─── 2. Load OpenAI key ───────────────────────────────────────────────────────────

client = OpenAI(api_key=st.secrets['KEY'])
# ─── 3. Initialize session state with a detailed system prompt ─────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are LeapBot—an AI assistant for Leap Finance, a study-abroad loan provider.  \n"
                "When a user provides a single line with:\n"
                "  GPA: <float>, GRE: <int>, IELTS: <int>, Country: <string>, Program: <string>, Budget: <int>  \n"
                "You must produce a single reply that includes these parts, in order:\n\n"
                "1. **Leap Finance Loan Offer**  \n"
                "   - Compute an **Estimated Loan Amount (INR)** and **EMI for 5 years** (you can assume a reasonable rule-of-thumb calculation).  \n"
                "   - Explicitly mention Leap Finance’s key features:  \n"
                "     • No collateral required  \n"
                "     • Interest rates starting from 8.49% p.a.  \n"
                "     • Covers both tuition and living expenses  \n"
                "     • Quick, 10-minute online process  \n"
                "2. **Leap Finance Loan Workflow** (briefly or in short):  \n"
                "   • **Application & Offer**: Online Application (see offer in 10 mins, no docs), Claim Offer (choose amount/tenure), Personal Discussion (credit team call).  \n"
                "   • **Sanction & Agreement**: Sanction Letter (pay 1% processing fee, download official letter for I-20/visa), Upload I-20 & Visa to portal, Sign Loan Agreement.  \n"
                "   • **Disbursement & Repayment**: 3% processing fee to request funds; Tuition → University via Flywire; Living → US bank account; Interest-only during school; Full EMI starts after 36 months.  \n"
                "3. **University Recommendations**  \n"
                "   Provide exactly 3 universities in a numbered list. Each entry must follow:\n"
                "     University Name, Country: Tuition XX INR, Living YY INR, Scholarship Chance ZZ%.  \n"
                "   Do NOT add any commentary—ONLY list the three universities.\n\n"
                "**Example user input:**\n"
                "GPA: 3.4, GRE: 310, IELTS: 7.5, Country: Canada, Program: MS Data Science, Budget: 2200000\n"
                "You should parse that, compute loan/EMI, mention key features/workflow, and then list 3 universities."
            )
        }
    ]

# ─── 4. Streamlit page layout ─────────────────────────────────────────────────────
st.title("🤖 LeapBot: Loan Eligibility & University Advisor")
st.write("I am here to help you estimate your education loan eligibility, show EMI schedules, and recommend suitable universities based on your profile.")

# Render the existing conversation (skip the system prompt)
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# ─── 5. Helper: call GPT-4 ────────────────────────────────────────────────────────
def generate_chat_response(messages):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

# ─── 6. Handle new user input ────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me about loan eligibility, EMI, or university recommendations.."):
    # 6.1 Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 6.2 Call GPT-4, passing full conversation (including our detailed system prompt)
    with st.spinner("LeapBot is thinking..."):
        bot_reply = generate_chat_response(st.session_state.messages)

    # 6.3 Append the assistant’s reply and rerun
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.rerun()
