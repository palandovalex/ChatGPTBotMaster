#!/home/lexsilentium/ChatGPTBot/.venv/bin python
#!/usr/bin/env python
from logging import warning, error
from openai.error import RateLimitError 
import telebot
from telebot.types import Chat, Message
import os
from session_storage import Session
import auth
import hashlib
import openai
from command import SimpleCommand

CHATBOT_HANDLE = "@ChatGPTMaster"

try:
    TG_AUTH_TOKEN:str = os.environ["TG_AUTH_TOKEN"]
    openai.api_key = os.environ["OPENAI_API_KEY"]
    bot = telebot.TeleBot(TG_AUTH_TOKEN)
    tg_sha = hashlib.sha1(TG_AUTH_TOKEN.encode(encoding = 'UTF-8', errors = 'strict'))
    ai_sha = hashlib.sha1(openai.api_key.encode(encoding= 'UTF-8', errors = 'strict'))
    warning(f"Tg_key_fingerprint: {tg_sha.hexdigest()}")
    warning(f"AI_key_fingerprint: {ai_sha.hexdigest()}")
except Exception as e:
    error(e)
    exit()
    

def checkMessage(message:Message):
    chat: Chat = message.chat
    user_id = message.from_user.id

    if chat.type == 'group' and auth.checkChat(chat):
        user_message = message.text

        if user_message and CHATBOT_HANDLE in user_message:
            return True

    if chat.type == 'private':
        if auth.checkUser(user_id):
            return True
        warning(f'message from unrecognised user: {message.from_user.id}')
    
    return False


def openAImage(session: Session, prompt: str):
    if not prompt:
        return "this command used to create images by your input. Example:\n /img Draw a 5 apples."
    settings = session.getSettings()
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=settings.imageSize
    )
     
    return response['data'][0]['url']
    


handelers = {
    "/img ": openAImage,
    "/help ": lambda a,b: '''
start your message by space separated tag to use spetial functions:
/img - generate image by prompt
'''
}

Session.addHandelers(handelers)

def openAiHandle(session:Session, message_text):
    session.addMessage('user', message_text)
    context = session.getContext()
    model = session.getSettings().model

    warning(context[-4:])

    try:
        completion = openai.ChatCompletion.create(model=model, messages=context)
        response = completion.choices[0].message.content
        warning(response)
        session.addMessage('assistant', response)
    except RateLimitError as e:
        response = "Server is overloaded. you can try again later."
        session.message_history.pop()

    return response


@bot.message_handler(func=checkMessage)
def messageHandle(message: Message): 
    message_text = message.text
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    if not message or not message_text:
        return
    
    session_id = '_'.join([user_id, chat_id])
    session = Session.getSession(session_id)

    for key in handelers.keys():
        if message_text.startswith(key):
            message_text = message_text.replace(key, '').strip()
            response = handelers[key](session, message_text)
            break
    else:
        response = openAiHandle(session, message_text)

    bot.reply_to(message, response)


warning("running bot")
bot.polling()
