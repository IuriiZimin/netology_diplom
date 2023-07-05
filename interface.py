import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import community_token, access_token, db_url_object
from core import VkTools
from sqlalchemy import create_engine
from data_store import add_user, check_user
from pprint import pprint


class BotInterface:
    def __init__(self, some_community_token, some_access_token):
        self.interface = vk_api.VkApi(token=some_community_token)
        self.vk_tools = VkTools(some_access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0
        self.long_poll = VkLongPoll(self.interface)

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет, {self.params["name"]}')
                    if self.params['city'] is None:
                        self.message_send(event.user_id, 'Введите Ваш город')
                        city = event.text.lower()
                        self.message_send(event.user_id, city)
                        self.params['city'] = city
                    if self.params['year'] is None:
                        self.message_send(event.user_id, 'Введите Ваш возраст')
                        year = event.text
                        self.message_send(event.user_id, year)
                        self.params['year'] = year

                elif command == 'поиск':
                    if not self.worksheets:
                        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)

                    worksheet = self.worksheets.pop()
                    print(worksheet)
                    if not check_user(engine, event.user_id, worksheet["id"]):
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_str = ''
                        for photo in photos:
                            photo_str += f'photo{photo["owner_id"]}_{photo["id"]},'
                        self.offset += 10
                        nl = '\n'
                        self.message_send(event.user_id, f'Встречайте: {worksheet["name"]}{nl}'
                                                         f'Страница ВК: vk.com/{worksheet["id"]}', attachment=photo_str)
                        add_user(engine, event.user_id, worksheet["id"])

                elif command == 'пока':
                    self.message_send(event.user_id, 'До скорых встреч')

                else:
                    self.message_send(event.user_id, 'Неправильная команда')


if __name__ == '__main__':
    engine = create_engine(db_url_object)
    bot = BotInterface(community_token, access_token)
    bot.event_handler()
