import re
import os

import ruamel.yaml as yaml
from typing import *


class Logger(object):
    def __init__(self, fp: str, group: Union[str, int]):
        self.fp = fp
        self.__group = group if isinstance(group, int) else int(group)
        self.yaml_file: dict = yaml.safe_load(open(fp, 'w+', encoding='utf-8'))
        # self.yaml_type = yaml.load(self.file)
        self.filename = os.path.basename(fp)
        if self.yaml_file is None:
            self.yaml_file = {}

    def __str__(self) -> str:
        return f'<Logger at {self.fp}>'

    @property
    def group(self) -> int:
        return self.__group

    __repr__ = __str__

    def log(self, d: dict):
        # print('\n\n\n\nlog: %s\n\n\n\n' % d)
        if d['post_type'] == 'message' and d['message_type'] == 'group' and d['sub_type'] == 'normal' and d['group_id'] == self.__group:
            print('logged')
            doc = " ".join((x['data']['text'] if x['type'] == 'text' else '') for x in d['message'])
            doc = re.sub(r'[^\w\u4e00-\u9fa5]', '', doc)
            print('---logging---')
            print(doc)
            if d['user_id'] not in self.yaml_file.keys():
                self.yaml_file[d['user_id']] = [doc]
            else:
                self.yaml_file[d['user_id']].append(doc)
            yaml.dump(self.yaml_file,
                      open(self.fp, 'w+', encoding='utf-8'),
                      default_flow_style=False,
                      allow_unicode=True,
                      Dumper=yaml.RoundTripDumper,
                      width=1000)
            print('logged')

    def get(self, *sid: Union[int, str]) -> dict:
        if sid is not ...:
            sid = int(sid)
            if sid not in self.yaml_file.keys():
                raise ValueError("Invalid sid: {}".format(sid))
            return self.yaml_file[sid]
        return self.yaml_file
