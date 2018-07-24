# -*- coding: utf-8 -*-
import sys
import os
import re
import logging
from itertools import islice
import json
from sqlalchemy import Column, String, Integer, create_engine, DateTime, func, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

logging.basicConfig(level=logging.INFO)
item_txt_path = 'item.txt'
name_path = 'Language.lang'
role_txt_path = 'role.txt'


def get_file_path():
    # 获取脚本路径
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


class GetData:
    def __init__(self):
        self.idArr = []
        self.nameArr = self.readName()
        self.readItemID()
        self.readRoleID()

    def readItemID(self):
        item_object = open(item_txt_path, "rU")
        try:
            for line in islice(item_object, 1, None):
                id_str = re.split(r"\t", line)
                id_list = {'id': '30000_' + id_str[0], 'name': id_str[1]}
                # logging.info('id_str: {}'.format(id_str))
                self.idArr.append(id_list)
        finally:
            item_object.close()

    def readRoleID(self):
        role_object = open(role_txt_path, "rU")
        try:
            for line in islice(role_object, 0, None):
                id_str = re.split(r"\t", line)
                # logging.info('idStr: {}'.format(id_str))
                id_list = {'id': '70000_' + id_str[0], 'name': id_str[6]}
                self.idArr.append(id_list)
        finally:
            role_object.close()

    def readName(self):
        name_arr = []
        file_str = open(name_path, "rU")
        file_object = json.load(file_str)['strings']
        try:
            for index, item in enumerate(file_object):
                # logging.info('idStr: {}: {}'.format(index, item['k']))
                name_arr.append(item)
        finally:
            file_str.close()
        return name_arr

    def match(self):
        match_arr = []

        for index_id in range(len(self.idArr)):
            for index_name in range(len(self.nameArr)):
                if self.idArr[index_id]['name'] == self.nameArr[index_name]['k']:
                    # logging.info('self.idArr:{}'.format(self.idArr[index_id]['name']))
                    match_list = {'value': self.idArr[index_id]['id'],
                                  'label': self.nameArr[index_name]['v']}
                    match_arr.append(match_list)
        return match_arr

    def getFile(self):
        file_path = os.path.join(get_file_path(), 'hello.txt')
        if not os.path.isfile(file_path):
            os.makedirs('file_path')

        file = open(file_path, "w")
        for item in self.match():
            file.write(str(item) + ",")

        file.close()

    def uploadData(self):
        for item in self.match():
            # logging.info('item:{}'.format(item))
            SaveEvent().uploadItem(item)


class ItemEvent(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    item_id = Column(String(length=50))
    name = Column(String(length=50))
    remark = Column(String(length=50))


class SaveEvent(object):
    def __init__(self):
        self.init_db()

    def init_db(self):
        engine = create_engine('mysql+mysqlconnector://game_stat_user:pNgR0bS^TfOLTu7M@192.168.1.120:3306/game_stat',
                               echo=True)
        self.session = sessionmaker(bind=engine)()

    def uploadItem(self, query):
        item = {
            'item_id': query['value'],
            'name': query['label'],
            'remark': ''
        }
        self.session.add(ItemEvent(**item))
        self.session.commit()


GetData().uploadData()
