__author__ = 'multiangle'

"""
loginin to weibo.cn via python
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from File_Interface import save_pickle
from config import mysql_config,conn_query,ready_to_get

class Control():

    def __init__(self):
        self.engine=create_engine(conn_query,echo=False)
        Session=sessionmaker(bind=self.engine)
        self.session=Session()

        self.init_uid=[]    #待处理的 用户的 id, 在start_up中获得
        self.start_up()


    def start_up(self):    #获取存在数据库中的待处理列表
        self.init_uid=[x.uid for x in self.session.query(ready_to_get).all()]



if __name__ == '__main__':

    Control()




