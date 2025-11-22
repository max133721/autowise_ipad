import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Moja Apka AI")

# 1. Konfiguracja klucza (pobiera z ustawień Streamlit)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("Brakuje klucza API w sekcji Secrets!")
    st.stop()

# 2. Konfiguracja modelu
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

# 3. Inicjalizacja modelu (Wklej instrukcje w cudzysłowie)
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="Jesteś pomocnym asystentem."
)

# 4. Historia czatu
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])

st.title("Mój Czat AI")

# 5. Wyświetlanie historii
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Obsługa wpisywania
if prompt := st.chat_input("Napisz wiadomość..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Błąd: {e}")
