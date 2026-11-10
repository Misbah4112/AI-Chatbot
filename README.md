# 🤖 AI Chatbot

An interactive AI chatbot built using **Python, Streamlit, LangChain, and Groq**. It supports real-time conversations, multiple AI models, and persistent chat history through SQLite.

## ✨ Features

- **AI-Powered Conversations** — Generate responses using Groq-hosted LLMs.
- **Multiple Chat Sessions** — Create, switch between, and delete conversations.
- **Persistent Chat History** — Store and retrieve conversations using SQLite.
- **Model Selection** — Switch between GPT-OSS 20B and GPT-OSS 120B.
- **Response Streaming** — Display AI responses in real time.
- **Customizable Settings** — Adjust temperature and maximum response tokens.
- **Interactive UI** — Modern dark-themed interface built with Streamlit.

## 🛠️ Tech Stack

- **Language:** Python
- **Frontend:** Streamlit
- **LLM Framework:** LangChain
- **LLM Provider:** Groq
- **Database:** SQLite

## 🚀 Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/Misbah4112/AI-Chatbot.git
cd AI-Chatbot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

Create a `.env` file and add your Groq API key:
```env
GROQ_API_KEY=your_api_key_here
```

**4. Run the application**
```bash
streamlit run chatbot.py
```

## 🔮 Future Improvements

- PDF-based question answering using RAG.
- Conversation memory optimization.
- Regenerate AI responses.

## 📌 About

A personal Generative AI project developed to gain hands-on experience with LLM integration, conversation management, database storage, and interactive AI applications.