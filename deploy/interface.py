# 1 - Imports ======================================================================
import os
import json
import requests  # Biblioteca responsvel por fazer a comunicação com o servidor
import streamlit as st

AGENT_ID = "analista_tecnologico"
AGENT_URL = os.getenv("AGENT_URL", "http://localhost:7777")
ENDPOINT_URL = f"{AGENT_URL}/agents/{AGENT_ID}/runs"

# 2 - Conexão com o Agno (SERVER) ===================================================
def get_response_stream(message:str):
    response = requests.post(
        ENDPOINT_URL,
        data={
           "message": message,
            "stream": "true"
        },
        stream=True
    )

# 2.1 - Streaming (processamento) ====================================================
    for line in response.iter_lines():
        if line.startswith(b"data: "):
            data = line[6:] # Remove "data: " prefix
            try:
                event = json.loads(data)
                yield event
            except json.JSONDecodeError:
                continue

# 3 - Streamlit ====================================================================
st.set_page_config(page_title="Ciencia tecnologia")
st.title("Ciencia tecnologia")

# 3.1 - Historico ====================
if ("messages" not in st.session_state):
    st.session_state.messages = []

# 3.2 Mostrar historico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("process"):
            with st.expander(msg["role"]):
                st.json(msg["process"])
        st.markdown(msg["content"])


# 3.3 - Input do usuario ============================================================
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adiciona a mensagem do usuario na memoria do streamlit
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta do assistente
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        # Processamento streaming
        for event in get_response_stream(prompt):
            event_type = event.get("event", "")

            # Chamada de tool
            if event_type == "ToolCallStarted":
                tool_name = event.get("tool", {}).get("tool_name")
                with st.status(f"Executando tool {tool_name}...", expanded=True):
                    st.json(event.get("tool", {}).get("tool_args", {}))

            # Conteudo da resposta
            elif event_type == "RunContent":
                content = event.get("content", "")
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)

    # Salva a resposta no historico
    st.session_state.messages.append({"role": "assistant", "content": full_response})