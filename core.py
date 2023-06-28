import vk_api
from vk_api.exceptions import ApiError
from datetime import datetime
from config import access_token
from pprint import pprint


class VkTools:
    def __init__(self, some_access_token):
        self.api = vk_api.VkApi(token=some_access_token)

    def get_profile_info(self, user_id):
        try:
            info, = self.api.method('users.get', {'user_id': user_id, 'fields': 'city,b_date,sex,relation'})
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        user_info = {'name': (info['first_name'] + ' ' + info['last_name']) if
                     'first_name' in info and 'last_name' in info else None,
                     'sex': info['sex'],
                     'year': datetime.now().year - int(info.get('b_date').split('.')[2]) if
                     info.get('b date') is not None else None,
                     'city': info.get('city')['title'] if info.get('city') is not None else None,
                     }
        return user_info

    def search_worksheet(self, param, offset):
        try:
            users = self.api.method('users.search',
                                    {'count': 10,
                                     'offset': offset,
                                     'age_from': param['year'] - 3,
                                     'age_to': param['year'] + 3,
                                     'sex': 1 if param['sex'] == 2 else 2,
                                     'hometown': param['city'],
                                     'has_photo': True
                                     }
                                    )
        except ApiError as e:
            users = []
            print(f'error = {e}')

        res = [{'name': item['first_name'] + ' ' + item['last_name'],
                'id': item['id']} for item in users['items'] if item['is_closed'] is False]

        return res

    def get_photos(self, user_id):
        try:
            some_photos = self.api.method('photos.get',
                                          {'user_id': user_id,
                                           'album_id': 'profile',
                                           'extended': 1
                                           }
                                          )
        except ApiError as e:
            some_photos = {}
            print(f'error = {e}')

        res = [{'owner_id': item['owner_id'],
                'id': item['id'],
                'likes': item['likes']['count'],
                'comments': item['comments']['count']
                } for item in some_photos['items']
               ]

        res.sort(key=lambda x: (x['likes'], x['comments']), reverse=True)

        return res[:3]


if __name__ == '__main__':
    bot = VkTools(access_token)
    params = bot.get_profile_info(580670959)
    worksheets = bot.search_worksheet(params, 20)
    worksheet = worksheets.pop()
    photos = bot.get_photos(worksheet['id'])
    pprint(worksheet)
