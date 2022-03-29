import requests
from discord import Webhook, RequestsWebhookAdapter
import pandas as pd
import time
import os
from dotenv import load_dotenv

class Monitor:
    
    def __init__(self, email: str, password: str, ID: str, schoolID: str, webhook: str, delay: int):
        self.ID = ID
        self.schoolID = schoolID
        self.webhook = webhook
        self.email = email
        self.password = password
        self.delay = delay
    
    def sendWebhook(self, message):
        webHook = Webhook.from_url(f"{self.webhook}", adapter=RequestsWebhookAdapter())
        webHook.send(message)

    def getClasses(self):
        self.data = {'j_username': self.email, 'j_password': self.password}
        self.loginUrl = f'https://students.genesisedu.com/{self.schoolID}/sis/j_security_check'
        self.gBookUrl = f'https://students.genesisedu.com/{self.schoolID}/parents?tab1=studentdata&tab2=gradebook&tab3=weeklysummary&action=form&studentid={self.ID}'
        with requests.session() as s:
            s.post(self.loginUrl, data = self.data)
            gradebook = s.get(self.gBookUrl)
        gradeTables = pd.read_html(gradebook.text)
        gradePage = gradeTables[2]
        classCount = len(gradePage)
        self.classes = []
        for i in range(1, classCount):
            self.classes.append(gradePage[0][i])
        return self.classes
    
    def getInitGrades(self):
        with requests.session() as s:
            s.post(self.loginUrl, data = self.data)
            gradebook = s.get(self.gBookUrl)
        gradeTables = pd.read_html(gradebook.text)
        gradePage = gradeTables[2]
        classCount = len(gradePage)
        self.grades = []
        for i in range(1, classCount):
            self.grades.append(gradePage[2][i])
        return self.grades

    def getLiveGrades(self):
        with requests.session() as s:
            s.post(self.loginUrl, data = self.data)
            gradebook = s.get(self.gBookUrl)
        newGradeTables = pd.read_html(gradebook.text)
        newGradePage = newGradeTables[2]
        newClassCount = len(newGradePage)
        self.newGrades = []
        for i in range(1, newClassCount):
            self.newGrades.append(newGradePage[2][i])
        return self.newGrades
    
    def compare(self, prevGrades, newGrades, classes):
        for i in range(len(prevGrades)):
            if prevGrades[i] != newGrades[i]:
                msg = f"Your {classes[i]} grade went from a {prevGrades[i]} to a {newGrades[i]}."
                Monitor(self.email, self.password, self.ID, self.schoolID, self.webhook, self.delay).sendWebhook(msg)
                print(msg)
                prevGrades[i] = newGrades[i]

    def run(self):
        monitor = Monitor(self.email, self.password, self.ID, self.schoolID, self.webhook, self.delay)
        classes = monitor.getClasses()
        initGrades = monitor.getInitGrades()
        while True:
            print("Monitoring...")
            liveGrades = monitor.getLiveGrades()
            monitor.compare(initGrades, liveGrades, classes)
            time.sleep(self.delay)
        
        
load_dotenv()

app = Monitor(str(os.getenv("EMAIL")), str(os.getenv("PASSWORD")), str(os.getenv("ID")), str(os.getenv("SCHOOLID")), str(os.getenv("WEBHOOK")), int(os.getenv("DELAY")))

app.run()
