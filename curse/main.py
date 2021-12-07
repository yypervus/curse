from random import randrange
import re
import vk_api
import json
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk import VkSearch
from database import save_database



token_bot = ''


vk = vk_api.VkApi(token=token_bot)
longpoll = VkLongPoll(vk)


keyboard = VkKeyboard(one_time=True)

keyboard.add_button('Нравится', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Не нравится', color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()
keyboard.add_button('Пропустить', color=VkKeyboardColor.SECONDARY)
keyboard.add_button('Новые параметры', color=VkKeyboardColor.PRIMARY)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

def write_jpg_keyboadr(user_id, attachment):
    vk.method('messages.send', {'user_id': user_id, 'random_id': randrange(10 ** 7), 'attachment': attachment, 'keyboard': keyboard.get_keyboard()})


def show_photo_keyboadr(user):
    for photo in user['photo']:
        write_jpg_keyboadr(event.user_id, photo['id'])
    with open('output.json', "a", encoding='utf-8') as f:
        json.dump(user, f, ensure_ascii=False, indent=4)

def show_profile():
    profile_user = new_search.get_user()
    if profile_user is None:
        write_msg(event.user_id, 'Введите новые параметры поиска')
    else:
        name_last_name_url = profile_user['name'] + ' ' + profile_user['last_name'] + ' ' + profile_user['url']
        write_msg(event.user_id, name_last_name_url)
        show_photo_keyboadr(profile_user)
        return profile_user


if __name__ == '__main__':
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            query = event.text

            if 'возраст' in query.lower().split():
                age_text = int(''.join(re.compile(r'\d+').findall(query)[:1]))
                write_msg(event.user_id, f"Спасибо. Вы выбрали возраст")
            elif 'город' in query.lower().split():
                city_text = re.compile(r'[Гг]ород\s').sub(r'', query).strip(" ").capitalize()
                write_msg(event.user_id, "Спасибо. Вы выбрали город.")
            elif 'пол' in query.lower().split():
                gender_text = re.compile(r'[Пп]ол').sub(r'', query).strip(" ")
                write_msg(event.user_id, "Спасибо. Вы выбрали пол.")
            elif 'статус' in query.lower().split():
                status_text = re.compile(r'[Сс]татус').sub(r'', query).strip(" ")
                write_msg(event.user_id, "Спасибо. Вы выбрали семейное положение.")
            elif 'ок' in query.lower().split():
                try:
                    age_text
                except NameError:
                    age = None
                    age_text = 'Любой'
                else:
                    if type(age_text) == int:
                        age = age_text
                    else:
                        age = None
                        age_text = 'любой'

                try:
                    gender_text
                except NameError:
                    gender = 0
                    gender_text = 'любой'
                else:
                    if gender_text.lower() == 'мужской' or gender_text.lower() == 'м' or gender_text.lower() == 'мужчина':
                        gender = 2
                    elif gender_text.lower() == 'женский' or gender_text.lower() == 'ж' or gender_text.lower() == 'женщина':
                        gender = 1
                    else:
                        gender = 0
                        gender_text = 'любой'

                dict_status = {'не женат': 1, 'не замужем': 1, 'встречается': 2, 'помолвлен': 3, 'помолвлена': 3,
                               'женат': 4, 'замужем': 4, 'всё сложно': 5, 'в активном поиске': 6, 'влюблен': 7,
                               'влюблена': 7, 'в гражданском браке': 8}
                try:
                    status_text
                except NameError:
                    status = None
                    status_text = 'любой'
                else:
                    if status_text.lower() in dict_status:
                        status = dict_status[status_text.lower()]
                    else:
                        status = None
                        status_text = 'любой'

                try:
                    city_text
                except NameError:
                    city = None
                    city_text = 'любой'
                else:
                    if city_text == 'Не выбран' or city_text == 'любой':
                        city = None
                    else:
                        city = city_text

                write_msg(event.user_id, f"Выполняем поиск с параметрами: Возраст - {age_text}, Пол - {gender_text}, Город - {city_text}, Семейное положение - {status_text}")

                new_search = VkSearch(age, gender, city, status)
                new_search.user_search()

                profile_user = show_profile()
            elif 'Нравится' in query:
                save_database(profile_user, 1)
                profile_user = show_profile()
            elif 'Не нравится' in query:
                save_database(profile_user, 0)
                profile_user = show_profile()
            elif 'Пропустить' in query:
                new_search.download_list_skipped(profile_user)
                profile_user = show_profile()
            elif 'Новые параметры' in query:
                write_msg(event.user_id, f"Измените ваши предпочтения. Просто введите новые параметры: возраст, город, пол, статус. Например: возраст 23, город Москва и т.п. Как только параметры будут заданы напишите Ок.")

            else:
                write_msg(event.user_id,
                          f"Здравствуйте https://vk.com/id{event.user_id}. Вас приветствует бот Vkinder. Расскажите о ваших предпочтениях. Можно ввести параметры: возраст, город, пол, статус. Например: пол женский, статус в активном поиске и т.п. Как только параметры будут заданы напишите Ок.")

