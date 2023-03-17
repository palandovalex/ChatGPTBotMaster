from logging import warning
import os
import json
from typing import Dict
from settings import Settings, DEFAULT

SESSIONS_DIR = os.getenv("BOT_SESSIONS_DIR")

if not SESSIONS_DIR:
    dir_path = os.path.dirname(os.path.realpath(__file__));
    SESSIONS_DIR = os.path.join(dir_path,'../.sessions')

class Session:
    activeSessions = {}

    def __init__(self, session_id, message_history=None, settings=None):
        if not message_history:
            message_history = []

        self.session_id = session_id
        self.user_is, self.chat_id = session_id.split('_')

        self.message_history: list[dict] = message_history
        self.settings: None|Settings = settings
        Session.activeSessions[session_id] = self 


    def addMessage(self, role, message):
        self.message_history.append({"role":role, "content": message})
        if len(self.message_history) > self.getSettings().history_length:
            self.message_history.pop(0)
        self.save()
        

    def getContext(self):
        context = self.message_history[:-1]
        message:dict = self.message_history[-1].copy()

        bot_personality = self.getSettings().bot_personality
        message['content'] = bot_personality + " " + message['content']
        context.append(message)
        return context
        

    def getSettings(self)->Settings:
        settings = self.settings
        if settings is None:
            settings = DEFAULT

        return settings


    def cleanHistory(self, input):
        self.message_history = [] 
        self.save()
        return 'message_history cleaned'

        
    def setDefault(self, input):
        if self.settings:
            del self.settings
        self.save()
        return 'your settings setted to default'


    def changeSettings(self, input):
        if self.settings is None:
            self.settings = Settings()
        if not input or input == 'show':
            help = f"/opt command can change thouse settings:\n{list(self.settings.__dict__.keys())} \nexample:\n"
            help += "/opt option=value\n\n"
            help += "current options:"
            opt_dict = self.getSettings().getDict()
            for key in opt_dict.keys():
                help += f"\n {key}={opt_dict[key]}"
            return help

        try:
            input = input.strip().split('=')
            if len(input)!=2:
                return "invalid setting message"
            setattr(self.settings, input[0], input[1])
            self.save()
            return 'updated'
        except Exception as e:
            print(e)
            return str(e)

    def save(self):
        #ensure state to be equal to settings
        if self.settings and len(self.message_history)>self.getSettings().history_length:
            self.message_history = self.message_history[-self.settings.history_length:]

        filePath = os.path.join(SESSIONS_DIR, str(self.session_id))
        with open(filePath, 'w') as file:
            sessionDict = {
                "message_history": self.message_history,
            }
            if self.settings:
                sessionDict["settings"]=self.settings.getDict()
            
            json.dump(sessionDict, file)


    @classmethod
    def load(cls, jsonStr):
        sessionData= json.loads(jsonStr)
        message_history = sessionData["message_history"] 
        settings = None
        if "settings" in sessionData.keys():
            settings = sessionData["settings"] 
            settings = Settings.fromDict(settings)

        return Session(session_id, message_history, settings)


    @classmethod
    def addHandelers(cls, handelers):
        handelers["/opt"] = Session.changeSettings
        handelers["/clean"] =  Session.cleanHistory
        handelers["/default"] = Session.setDefault
        


    @classmethod
    def getSession(cls, session_id):
        try:
            session = cls.activeSessions[session_id]
        except KeyError:
            session = cls(session_id) 
        return session


sessionFiles = os.scandir(SESSIONS_DIR);

for sessionFile in sessionFiles:
    session_id = sessionFile.name

    with open(os.path.join(SESSIONS_DIR, sessionFile), 'r') as file:
        jsonStr = file.read()

    Session.load(jsonStr)
