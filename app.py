import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
from io import BytesIO

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("📘 English Correction Assistant")

if "step" not in st.session_state:
    st.session_state.step = 0

if "text" not in st.session_state:
    st.session_state.text = ""

if "conversation" not in st.session_state:
    st.session_state.conversation = []

uploaded_file = st.file_uploader("Upload your copy", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image)

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

    st.write("Extracted text:")
    st.write(text)

    if st.button("Start correction"):
        st.session_state.step = 1
        st.session_state.conversation = []

if st.session_state.step == 1:

    prompt = f"""
Find ONE mistake. Do not give answer. Give hint.

{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response.choices[0].message.content
    st.write(reply)

    st.session_state.conversation.append(reply)
    st.session_state.step = 2

if st.session_state.step >= 2 and st.session_state.step <= 4:

    user_input = st.text_input("Your correction:")

    if st.button("Submit"):

        st.session_state.conversation.append(user_input)
        attempt = st.session_state.step - 1

        prompt = f"""
Student attempt {attempt}/3.

If wrong → give hint.
If correct → say correct.
If attempt 3 → give answer.

Conversation:
{st.session_state.conversation}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        reply = response.choices[0].message.content
        st.write(reply)

        st.session_state.conversation.append(reply)
        st.session_state.step += 1

if st.session_state.step == 5:

    if st.button("Finish"):

        prompt = f"""
Give level, exercises, and table of errors.

{text}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.write(response.choices[0].message.content)
