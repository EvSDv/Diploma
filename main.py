import json
import time
import sys
import requests
import math


class User:

    version_api = '5.92'
    token_netology = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'

    def __init__(self):
        self.short_name = ''
        self.id = 0
        self.friends = list()
        self.communities = list()
        self.friends_communities = set()
        self.unique_groups = list()

    def get_id(self):
        self.id = requests.get('https://api.vk.com/method/users.get', params={
            'v': self.version_api,
            'access_token': self.token_netology,
            'user_ids': self.short_name
        }).json()['response'][0]['id']

    def get_friends(self):
        self.friends = requests.get('https://api.vk.com/method/friends.get', params={
            'v': self.version_api,
            'user_id': self.id,
            'access_token': self.token_netology
        }).json()['response']['items']

    def get_communities(self, users):
        communities = []
        bar_len = 100
        count = len(users)

        for i, user in enumerate(users):
            position = math.floor(bar_len / count * (i + 1))
            text = f'\r|{"#" * position}{"-" * (bar_len - position)}|'
            print(text, i, end='')
            sys.stdout.write(text)
            sys.stdout.flush()
            successful = False
            while not successful:
                try:

                    resp = requests.get('https://api.vk.com/method/groups.get', params={
                        'v': self.version_api,
                        'user_id': user,
                        'access_token': self.token_netology
                    }).json()
                    communities.extend(resp['response']['items'])
                    successful = True

                except KeyError:
                    if resp['error']['error_code'] == 7 or resp['error']['error_code'] == 18:
                        successful = True

                    if resp['error']['error_code'] == 6:
                        time.sleep(0.3)




        print('\r\n')
        return set(communities)

    def communities_get_info(self, communities):
        if not communities:
            return []

        communities_str = ''

        for i, community in enumerate(communities):
            communities_str += str(community) + ','

        communities_str = communities_str[:len(communities_str) - 1]

        response = requests.get('https://api.vk.com/method/groups.getById', params={
            'group_ids': communities_str,
            'v': self.version_api,
            'access_token': self.token_netology,
            'fields': 'members_count'
        })

        communities_info = response.json()['response']
        communities = list()

        for group in communities_info:
            try:
                tmp_group = dict()
                tmp_group['name'] = group['name']
                tmp_group['id'] = group['id']
                tmp_group['members_count'] = group['members_count']
            except KeyError:
                continue

            communities.append(tmp_group)

        return communities

    def find_unique_communities(self):

        bar_len = 100
        count = len(self.communities)

        for i, group in enumerate(self.communities):
            position = math.floor(bar_len / count * (i + 1))
            text = f'\r|{"#" * position}{"-" * (bar_len - position)}|'
            print(text, i, end='')
            sys.stdout.write(text)
            sys.stdout.flush()

            if group not in self.friends_communities:
                self.unique_groups.append(group)

            time.sleep(0.3)
        print('\r\n')
        self.unique_groups = self.communities_get_info(self.unique_groups)

    def input_user_id(self):
        self.short_name = input('Введите id или имя пользователя: ')
        if not str(self.short_name).isdigit():
            self.get_id()
        else:
            self.id = self.short_name

    # def ban_friends_clear(self):
    #     print('Поиск удаленных и забанненых друзей пользователя')
    #     bar_len = 100
    #     count = len(self.friends)
    #     for i, friend in enumerate(self.friends):
    #         position = math.floor(bar_len / count * (i + 1))
    #         text = f'\r|{"#" * position}{"-" * (bar_len - position)}|'
    #         print(text, i, end='')
    #         sys.stdout.write(text)
    #         sys.stdout.flush()
    #
    #         resp = requests.get('https://api.vk.com/method/users.get', params={
    #             'v': self.version_api,
    #             'access_token': self.token_netology,
    #             'user_id': friend
    #         }).json()
    #         if 'deactivated' in resp['response'][0]:
    #             self.friends.remove(friend)
    #     print('\r\n')

    def get_user_communities(self):
        print('Поиск сообществ пользователя')
        self.communities = self.get_communities([self.id])

    def get_friends_communities(self):
        print('Поиск сообществ друзей пользователя')
        self.friends_communities = self.get_communities(self.friends)

    def find_unique_groups(self):
        self.input_user_id()
        self.get_friends()
        #self.ban_friends_clear()
        self.get_user_communities()
        self.get_friends_communities()

        print('Поиск уникальных сообществ')
        self.find_unique_communities()


def write_unique_communities(user):
    if user.unique_groups:
        with open(f'groups{user.id}.json', 'w', encoding='utf8') as file:
            json.dump(user.unique_groups, file, indent=4, ensure_ascii=False)
    else:
        print('Уникальных сообществ не найдено')


if __name__ == '__main__':
    vk_user = User()
    vk_user.find_unique_groups()
    write_unique_communities(vk_user)
