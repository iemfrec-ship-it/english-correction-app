import streamlit as st
import pytesseract
from PIL import Image
from openai import OpenAI
import os

# 🔑 API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("📘 English Correction Assistant")

# 🧠 Mémoire (important pour les 3 essais)
if "step" not in st.session_state:
    st.session_state.step = 0

if "text" not in st.session_state:
    st.session_state.text = ""

if "conversation" not in st.session_state:
    st.session_state.conversation = []

# 📸 Upload image
uploaded_file = st.file_uploader("Upload your copy", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your copy")

    # OCR (simple version)
    import base64
from io import BytesIO

buffered = BytesIO()
image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract the English text from this student copy."},
                {"type": "image_url", "image_url": f"data:image/png;base64,{img_str}"}
            ],
        }
    ],
)

text = response.choices[0].message.content
st.session_state.text = text

    st.subheader("Extracted text:")
    st.write(text)

    if st.button("Start correction"):
        st.session_state.step = 1

# 🚀 Étape 1 : première analyse
if st.session_state.step == 1:

    prompt = f"""
You are an English assistant for vocational high school students.

TASK:
- Find ONE important mistake only
- Do NOT correct it
- Give a SIMPLE hint
- Ask the student to try

TEXT:
{st.session_state.text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response.choices[0].message.content

    st.session_state.conversation.append(reply)
    st.write(reply)

    st.session_state.step = 2

# ✏️ Réponse élève
if st.session_state.step >= 2 and st.session_state.step <= 4:

    user_input = st.text_input("Your correction:")

    if st.button("Submit"):

        st.session_state.conversation.append(user_input)

        attempt = st.session_state.step - 1

        prompt = f"""
You are an English assistant.

RULES:
- Student has {attempt}/3 attempts
- If not correct → give another hint (a bit clearer)
- If correct → say it's correct
- If attempt == 3 and still wrong → give correction + simple explanation

Conversation:
{st.session_state.conversation}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        reply = response.choices[0].message.content

        st.session_state.conversation.append(reply)
        st.write(reply)

        st.session_state.step += 1

# 🧠 Étape finale
if st.session_state.step == 5:

    if st.button("Finish and get feedback"):

        prompt = f"""
You are an English teacher.

Based on this student work:

{st.session_state.text}

Do:
1. Give CEFR level (A1 to B2)
2. Give 2 exercises (minimum 6 sentences each)
3. Make a simple table:
- Vocabulary errors + rule
- Grammar errors + rule
- Structure errors + rule
- Other errors + rule

Use SIMPLE English.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.write(response.choices[0].message.content)
