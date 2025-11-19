from openai import OpenAI

import os
from dotenv import load_dotenv

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Form, Request      # Form is used to retrieve data from an HTML form.
from typing import Annotated
from fastapi.templating import Jinja2Templates  # Integrates the "template engine" named Jinja2 into FastAPI.
from fastapi.responses import HTMLResponse

# Jinja2 is used to place the data coming from Jinja2 Backend into HTML.

load_dotenv()  # load .enf file

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")  # For the photo add a static path

templates = Jinja2Templates(directory="templates")  # My HTML files are located in the following folder: templates/

@app.get("/",response_class=HTMLResponse)      # to display the interface use get
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})  # When rendering HTML template with Jinja2, the request object MUST be provided.

chat_log = [{
    "role": "system",
    "content": """You are the ECHO AI Chatbot Assistant, designed to support users during and after earthquakes.
Your primary responsibilities are:

1. Psychological Support
- Provide calm, empathetic, non-judgmental, emotionally supportive guidance.
- Help users manage panic, stress, fear, or confusion.
- Offer breathing exercises, grounding techniques, and positive reinforcement.
- Never give clinical diagnoses or medical advice.

2. Crisis Communication Helper
- Communicate clearly and simply, optimized for stressful situations.
- Guide the user step-by-step.
- Prioritize user safety, clarity, and emotional stability.

3. Information & Assistance Guidance
- Explain how ECHO features work when asked (status update, trusted contacts, shelters, alerts, filters, etc.)
- You do NOT perform actions on behalf of the user.
- You only guide, clarify, and support.

4. Tone & Behavior
- Always be calm, warm, reassuring.
- Keep messages short and easy to understand.
- Never make unrealistic promises (“Help is definitely coming”).
- Respect user privacy; never ask unnecessary data.

5. Safety Protocol
- If user expresses fear, panic, or danger: reassure them, help them breathe, keep them calm.
- Encourage using the app’s emergency features, but you are not emergency services.

Your goal is to keep the user calm, supported, and informed."""
}]

chat_responses = []  # chat_responses is the list used to display on an HTML page.

@app.post("/", response_class=HTMLResponse)                          # post is used for send some data from api
async def chat(request: Request, user_input: Annotated[str, Form()]):     # async means the function can respond to multiple requests at the same time

    # The user_input value coming to this function will come from a form and will be in string type (Annotated[str, Form()] part
    # Form() → FastAPI’ye take this data from HTML Form

    # A data named user_input will come, this data will be in string type and will be sent via HTML form.

    chat_log.append({"role": "user", "content": user_input})
    chat_responses.append({"sender": "user", "text": user_input})

    response = openai.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = chat_log,
        temperature = 0.6
    )

    bot_response = response.choices[0].message.content # This only takes the content part of the response
    chat_log.append({"role": "assistant", "content": bot_response})
    chat_responses.append({"sender": "bot", "text": bot_response})

    return templates.TemplateResponse("home.html", {"request": request, "chat_responses":chat_responses})

# Take the home.html file, pass the request and chat_responses data into it, and return it to the browser as HTML.
