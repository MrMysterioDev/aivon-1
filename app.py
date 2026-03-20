import gradio as gr
import requests
import json
import os

# ============================================
# AIVON 1.0 - FREE CLOUD AI AGENT
# Powered by Groq API with Ollama fallback
# ============================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

OLLAMA_URL = "https://api.ollama.com/v1/chat/completions"

def call_groq(prompt, model="llama-3.1-8b-instant"):
    """Call Groq API"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    try:
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Groq Error: {response.status_code} - Try Ollama fallback"
    except Exception as e:
        return f"Groq Error: {str(e)}"

def call_ollama(prompt, model="llama3"):
    """Call Ollama API as fallback"""
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    try:
        response = requests.post(OLLAMA_URL, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Ollama Error: {response.status_code}"
    except Exception as e:
        return f"Ollama Error: {str(e)}"

def ai_response(message, history, mode="auto"):
    """Main AI response function"""
    if not GROQ_API_KEY:
        return "⚠️ Groq API key not set! Add GROQ_API_KEY in Space settings."
    
    # Auto mode: Try Groq first, fallback to Ollama
    if mode == "auto":
        response = call_groq(message)
        if "Error" in response or "not set" in response:
            response = call_ollama(message)
    elif mode == "groq":
        response = call_groq(message)
    else:
        response = call_ollama(message)
    
    return response

# Gradio Interface
with gr.Blocks(title="Aivon 1.0", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 Aivon 1.0 - Free Cloud AI Agent
    
    **Powered by Groq API with Ollama fallback**
    
    | Feature | Description |
    |---------|-------------|
    | 🚀 Fast | Groq's lightning-fast inference |
    | 💰 Free | 14,400 tokens/day free |
    | 🔄 Backup | Ollama cloud fallback |
    | 💻 Code | Python, JS, Bash experts |
    | 📊 Analysis | Financial & business |
    """)
    
    mode = gr.Dropdown(
        ["auto", "groq", "ollama"],
        value="auto",
        label="AI Mode",
        info="auto = Groq first, fallback to Ollama"
    )
    
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(placeholder="Ask me anything...", label="Your Message")
    
    def respond(message, history, mode):
        response = ai_response(message, history, mode)
        history.append((message, response))
        return "", history
    
    msg.submit(respond, [msg, chatbot, mode], [msg, chatbot])
    
    gr.Markdown("""
    ---
    ### 📋 Instructions
    1. Get free API key: https://console.groq.com/keys
    2. Add to Space Settings → Repository Secrets → `GROQ_API_KEY`
    3. Restart the Space!
    """)

demo.launch(server_name="0.0.0.0", server_port=7860)
