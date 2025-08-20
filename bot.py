import json
import vk_api
import openai
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from gigachat import GigaChat

#Парсер
from bs4 import BeautifulSoup
from urllib.request import urlopen

urls = [
    "https://education.vk.company/",
    "https://education.vk.company/students",
    "https://education.vk.company/news?target_audience=students&page=1",
    "https://internship.vk.company/internship",
    "https://internship.vk.company/vacancy",
    "https://education.vk.company/products_for_education",
    "https://education.vk.company/education_projects",
]

with open('text.txt', 'w', encoding='utf-8') as file:
    for url in urls:
        try:
            response = urlopen(url)
            html_code = response.read().decode('utf-8')

            soup = BeautifulSoup(html_code, 'html.parser')

            title = soup.find('title').text.strip() if soup.find('title') else 'No Title'
            file.write(title + '\n\n')
            #print(title)

            paragraphs = soup.find_all('p')
            for paragraph in paragraphs:
                text = paragraph.get_text(strip=True)
                #print(text)
                file.write(text + '\n')

        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

#Gigachat
def ask_giga(question):
    prompt1 = (f"Ответь на вопрос на основе информации с сайтов:\n{text_data}\n\nВопрос: {question}\nОтвет: . Ты "
              f"помощник, который помогает пользователям разобраться на платформе VK Education и найти ответы на их "
              f"вопросы. Ответы должны быть не очень длинными и лаконичнми с самйо важной информацией по вопросу "
              f"пользователя, без кучи лишней информации. Отвечай в дружелюбной форме. Если не знаешь ответ на "
              f"вопрос/не можешь найти ответ в тексте, то отвечает скриптами, которые позволяют пользователям найти "
              f"информацию самостоятельно ( по сайту https://education.vk.company/). Пиши сайт только если не знаешь ответ"
              f"Также если стобой здороваютс, поприветсвуй в ответ и скажи что можешь ответить на вопросы по VK Education"
              f"Дополнительные требования к боту:Умеет отвечать на закрытые вопросы (да/нет). Например: «Возможно ли взять несколько проектов?» (Да.)Способен анализировать открытые источники из интернета в случае, если вопросы пользователей не относятся к сайту VK Education Projects.Выдаёт предупреждающие сообщения о неприличном стиле общения, если в тексте вопросов содержится нецензурная брань или некорректные высказывания. Способен анализировать открытые источники из интернета в случае, если вопросы пользователей не относятся к сайту VK Education Projects.")

    with GigaChat(credentials="ТОКЕН", verify_ssl_certs=False) as giga:
        response = giga.chat(prompt1)
    return response.choices[0].message.content.strip()



with open("text.txt", "r", encoding="utf-8") as file:
    text_data = file.read()


vk_session = vk_api.VkApi(token="vk1.a.Jl14HQKX3di_6NVTNayQI6Fexz5QcVMVdRa-5eEX7Kpoz75D6_DSszXKbkKlbLx2XSBXIvD1u2j1_zdMJa6COrc2NMgH8Bq-d9zKzJMN9MdyUwHH6qekibtdvs9Wohv-AnstpG8C5Z16GwBAnYwE586Xqn2xHqHn5qkBHQq1Wf-g3cdSSe-L4U_nV13ObKOJnOQwynds_bVPzEH6U3UYAA")
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

keyboard = VkKeyboard(one_time=True)
keyboard.add_button("Привет", color=VkKeyboardColor.SECONDARY)
keyboard.add_button("Клавиатура", color=VkKeyboardColor.POSITIVE)


def sender(id, text):
    vk_session.method("messages.send", {"user_id":id, "message":text, "random_id":0})

def send_stick(id, number):
    vk.messages.send(user_id=id, sticker_id=number, random_id=0)

def send_photo(id, url):
    vk.messages.send(user_id=id, attachment=url, random_id=0)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id
            if msg == "start":
                sender(id, "Привет! Я чат-бот ВК, разработанный на python для проекта VK Education Projects.")
                #send_stick(id, 107462)
            else:
                response = ask_giga(msg)
                vk.messages.send(user_id=event.user_id, message=response, random_id=0)
 
