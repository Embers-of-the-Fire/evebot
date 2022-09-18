import json
from typing import Union

BASE_HELPER_ADMIN_LIST_PATH = 'sup_images/helper_admin_list_image.png'
BASE_HELPER_ADMIN_ROLE_PATH = 'sup_images/helper_admin_role_image.png'
BASE_HELPER_ADMIN_SET_PATH = 'sup_images/helper_admin_set_image.png'
BASE_HELPER_ADMIN_STATUS_PATH = 'sup_images/helper_admin_status_image.png'
BASE_HELPER_ADMIN_BIND_PATH = 'sup_images/helper_admin_bind_image.png'

ADMIN_DICT_PATH = './admin/admin.json'

global ADMIN_DICT


def admin_init():
    global ADMIN_DICT
    ADMIN_DICT = json.load(open(ADMIN_DICT_PATH, 'r', encoding='utf-8'))


def admin(command: str, params: list, group_id, sender_id) -> Union[dict, bool]:
    global ADMIN_DICT
    print('using admin -> %s' % command)
    if not params:
        if command == 'status':
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'image', 'data': {'type': 'image', "file": f"{BASE_HELPER_ADMIN_STATUS_PATH}"}}]}, 'echo': 'apiCallBack'}
        elif command == 'set':
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'image', 'data': {'type': 'image', "file": f'{BASE_HELPER_ADMIN_SET_PATH}'}}]}, 'echo': 'apiCallBack'}
        elif command == 'list':
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'image', 'data': {'type': 'image', "file": f'{BASE_HELPER_ADMIN_LIST_PATH}'}}]}, 'echo': 'apiCallBack'}
        elif command == 'role':
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'image', 'data': {'type': 'image', "file": f'{BASE_HELPER_ADMIN_ROLE_PATH}'}}]}, 'echo': 'apiCallBack'}
        elif command == 'bind':
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'image', 'data': {'type': 'image', "file": f'{BASE_HELPER_ADMIN_BIND_PATH}'}}]}, 'echo': 'apiCallBack'}
    else:
        ...
    return False


class Status:
    @staticmethod
    def group(sender: int):
        ...

    @staticmethod
    def all(sender: int):
        ...


class List:
    @staticmethod
    def admin(sender: int):
        ...

    @staticmethod
    def owner(sender: int):
        ...

    @staticmethod
    def all(sender: int):
        ...


class Role:
    @staticmethod
    def group(sender: int):
        ...

    @staticmethod
    def all(sender: int):
        ...


class Set:
    @staticmethod
    def key(sender: int):
        ...

    @staticmethod
    def admin(sender: int):
        ...

    @staticmethod
    def default(sender: int):
        ...

    @staticmethod
    def list(sender: int):
        ...


class Bind:
    @staticmethod
    def admin(sender: int):
        ...

    @staticmethod
    def owner(sender: int):
        ...


if __name__ == '__main__':
    print('')
