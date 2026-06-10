import os
import streamlit as st
from groq import Groq
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# carregando a chave da API do arquivo .env (variável de ambiente)
load_dotenv()

# configuração da página Streamlit
st.set_page_config(page_title="Recomenda AI - Livros", page_icon="📚")
st.title("📖 Recomenda AI - Livros")
st.write("Conversando com um chatbot especialista em recomendação de livros!")

# Tenta pegar do st.secrets primeiro (ambiente de deploy Streamlit)
# Se não encontrar, tenta pegar do os.getenv (ambiente local com .env)
try:
    api_key = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.getenv("GROQ_API_KEY")

# inicializando o client da API do groq
client = Groq(api_key=api_key)

# Prompt de sistema: definindo a persona e o domínio de geração do chatbot
SYSTEM_PROMPT = (
    "You are an expert book recommendation assistant."
    "Your only role is to recommend books based on the user's preferences."
    "If the user ask for something that isn't related to books, don't respond and gently redirect the conversation back to books."
    "Always suggest specific book titles, their authors, and briefly explain "
    "why each book matches the user's request."
    "Ask clarifying questions about genres or favorite authors when needed."
    "If the user doesn't specify a particular genre, recommend books that are well-reviewed by critics."
    "ALWAYS respond entirely in Brazilian Portuguese (PT-BR)"
)

# session_state inicializado
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_messages" not in st.session_state:
    st.session_state.model_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# exibindo cada mensagem do histórico de mensagens da conversa na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# caixa de texto de input do usuário
if prompt := st.chat_input("Digite sua mensagem aqui..."):
    
    # mostrando e salvando a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # "Pensando..." -> quando o modelo processa e espera chegar a response da API
    with st.spinner("Pensando..."):
        
        # traduzir o prompt do usuário de PT-BR para inglês
        prompt_en = GoogleTranslator(source='pt', target='en').translate(prompt)
        
        # adicionando a nova entrada (prompt) ao histórico do modelo
        st.session_state.model_messages.append({"role": "user", "content": prompt_en})
        
        # gerando a resposta com a API da Groq para o consumo do llama-3.1-8b-instant
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.model_messages,
            max_tokens=200,
            temperature=0.7,
        )
        
        # extraindo a resposta gerada em inglês
        response_en = completion.choices[0].message.content
        
        # adicionando resposta ao histórico do modelo
        st.session_state.model_messages.append({"role": "assistant", "content": response_en})
        
        # convertendo resposta de inglês -> PT-BR
        response_pt = GoogleTranslator(source='en', target='pt').translate(response_en)
        
    # exibindo e salvando a resposta final na interface
    st.session_state.messages.append({"role": "assistant", "content": response_pt})
    with st.chat_message("assistant"):
        st.markdown(response_pt)