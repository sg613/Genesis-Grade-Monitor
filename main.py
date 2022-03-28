# Python Genesis Grade Monitor

import requests
from bs4 import BeautifulSoup
import time
from discord import Webhook, RequestsWebhookAdapter

i = 0

grades = []
classes = []

with open(r"login.txt", 'r') as f:
    schoolID = f.readlines()[3]
    sklID = schoolID.split('\n')
    sID = sklID[0]
with open(r"login.txt", 'r') as f:
    webhookUrl = f.readlines()[4]


loginUrl = f"https://students.genesisedu.com/{sID}/sis/j_security_check"


webhook = Webhook.from_url(f"{webhookUrl}", adapter=RequestsWebhookAdapter())



with open(r"login.txt", 'r') as f:
    email = f.readlines()[0]

with open(r"login.txt", 'r') as f:
    password = f.readlines()[1]

with open(r"login.txt", 'r') as f:
    aID = f.readlines()[2]
    bID = aID.split('\n')
    id = bID[0]

payload = {'j_username': email, 'j_password': password}


with requests.session() as s:
    a = s.post(loginUrl, data = payload)
    result = s.get(f'https://students.genesisedu.com/{sID}/parents?tab1=studentdata&tab2=gradebook&tab3=weeklysummary&action=form&studentid={id}')
    soup = BeautifulSoup(result.text, "html.parser")
    graderaw = soup.find_all("div", {"style": "text-decoration: underline"})
    for i in len(graderaw):
        grade = graderaw[i].text.strip()
        grades.append(grade)
        className = soup.find_all("span", {"class": "categorytab"})[i]
        classer = className.text.strip()
        classes.append(classer)
    print(grades)
    print(classes)


x = 1
n = 0
newgrades = []

while x == 1:
    print("Monitoring...")
    with requests.session() as h:
        h.post(loginUrl, data = payload)
        result2 = h.get(f'https://students.genesisedu.com/{sID}/parents?tab1=studentdata&tab2=gradebook&tab3=weeklysummary&action=form&studentid={id}')
        zoup = BeautifulSoup(result2.text, "html.parser")
        
        for allC in classes:
            
            newgraderaw = zoup.find_all("div", {"style": "text-decoration: underline"})[n]
            newgrade = newgraderaw.text.strip()
            newgrades.append(newgrade)
            n += 1

    p = 0
    for allClasses in classes:
        if newgrades[p] != grades[p]:
            webhook.send(f"Your {classes[p]} grade changed from a {grades[p]} to a {newgrades[p]}.")
            grades[p] = newgrades[p]
        p += 1
    
    time.sleep(300)
