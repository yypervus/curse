import requests
from database import check_id_user


class VkSearch:

    url = 'https://api.vk.com/method/'

    def __init__(self, age=None, gender=0, city=None, status=None):
        self.list_skipped = []
        self.TOKEN_VK = ''
        self.age = age
        self.gender = gender
        self.city = city
        self.status = status


    def user_search(self):
        search_users_url = self.url + 'users.search'
        search_users_params = {
            'access_token': self.TOKEN_VK,
            'v': '5.126',
            'age_from': self.age,
            'age_to': self.age,
            'status': self.status,
            'sex': self.gender,
            'count': 1000,
            'hometown': self.city,
            'has_photo': 1,
            'fields': 'screen_name'
        }
        response = requests.get(search_users_url, params=search_users_params)
        result = response.json()
        if 'response' in result:
            self.list_users = result['response']['items']
            return self.list_users

    def photos_get(self, user_id):
        photos_get_url = self.url + 'photos.get'
        photos_get_params = {
            'access_token': self.TOKEN_VK,
            'v': '5.126',
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '0',
        }
        response = requests.get(photos_get_url, params=photos_get_params)
        self.user_foto_dict = response.json()
        return self.user_foto_dict

    def photo_selection(self, user_foto_dict):
        list_foto = []
        for photo in user_foto_dict['response']['items']:
            dict_foto = {}
            dict_foto['id'] = 'photo' + str(photo['owner_id']) + '_' + str(photo['id'])
            dict_foto['popular'] = photo['likes']['count'] + photo['comments']['count']
            list_foto.append(dict_foto)
        self.sort_list = sorted(list_foto, key=lambda x: x['popular'], reverse=True)[:3]
        return self.sort_list


    def user_profile(self, list_users):
        check_photo = {}
        check_database = 0
        while 'response' not in check_photo or check_database != True:
            if len(list_users) != 0:
                user = list_users.pop(0)
                check_database = check_id_user(user['id'])
                check_photo = self.photos_get(user['id'])
            else:
                break
        self.user_profile_dict = {}
        self.user_profile_dict['name'] = user['first_name']
        self.user_profile_dict['last_name'] = user['last_name']
        self.user_profile_dict['id'] = user['id']
        self.user_profile_dict['url'] = 'https://vk.com/id' + str(user['id'])
        self.user_profile_dict['photo'] = self.photo_selection(check_photo)
        return self.user_profile_dict

    def download_list_skipped(self, user):
        self.list_skipped.append(user)

    def get_user(self):
        if len(self.list_users) != 0:
            return self.user_profile(self.list_users)
        elif len(self.list_skipped) != 0:
            return self.list_skipped.pop(0)
        elif len(self.list_users) == 0 and len(self.list_skipped) == 0:
            return None

