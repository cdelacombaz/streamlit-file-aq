import openai
import requests
import streamlit as st

# st.session_state['openai_api_key'] = st.secrets['OPENAI_API_KEY'] or ''
# st.session_state['api_key_valid'] = True
st.session_state['openai_api_key'] = ''


def validate_api_key(api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://api.openai.com/v1/engines"
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except Exception:
        return False


def on_api_key_submit():
    user_input = st.session_state.user_api_key
    if user_input:
        is_valid = validate_api_key(user_input)
        if is_valid:
            st.session_state['openai_api_key'] = user_input
            st.session_state['api_key_valid'] = True
            openai.api_key = user_input
        else:
            st.error("Invalid API key. Please try again.")


def on_remove_api_key():
    if 'openai_api_key' in st.session_state:
        del st.session_state['openai_api_key']
        del st.session_state['api_key_valid']
        st.session_state['user_api_key'] = ''


with st.sidebar:
    api_key_valid = st.session_state.get('api_key_valid', False)

    if api_key_valid:
        st.text_input("OpenAI API Key", key="user_api_key", type="password", disabled=True)
        st.button("Remove API Key", on_click=on_remove_api_key)
    else:
        st.text_input("OpenAI API Key", key="user_api_key", type="password")
        st.button("Submit API Key", on_click=on_api_key_submit)


st.title("ChatGPT-like clone")
file = st.file_uploader('Upload an article', type=('txt', 'md'))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if file:
    article = file.read().decode()
    if 'article_text' not in st.session_state:
        st.session_state['article_text'] = article

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.insert(0, {"role": "system", "content": f"You are a helpful assistant with knowledge "
                                                                          f"about an uploaded file from a user. File "
                                                                          f"content: "
                                                                          f"{st.session_state['article_text']}"})

    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
