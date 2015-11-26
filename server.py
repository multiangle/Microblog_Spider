__author__ = 'multiangle'

"""
loginin to weibo.cn via python
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from File_Interface import save_pickle,load_pickle
from config import mysql_config,conn_query,ready_to_get,user_info_table,Base

from client import WeiboConnector,getInfo

class Control():

    def __init__(self):
        self.engine=create_engine(conn_query,echo=False)
        Session=sessionmaker(bind=self.engine)
        self.session=Session()

        self.init_uid=[]    #待处理的 用户的 id, 在start_up中获得
        self.create_table()
        # self.start_up()
        self.execute()

    def __del__(self):
        self.session.close()

    def create_table(self):
        Base.metadata.create_all(self.engine,checkfirst=True)

    def start_up(self):    #获取存在数据库中的待处理列表
        self.init_uid=self.session.query(ready_to_get).all()[0:5]
        print(self.init_uid)

    def execute(self):
        # self.conn=WeiboConnector('weilidian@126.com', 'z123456')
        self.conn=WeiboConnector('shalv4848@163.com','8rr77b')
        while(True):
            current_user=self.session.query(ready_to_get).all()[0]
            uid=current_user.uid
            # try:
            info=getInfo(self.conn,uid)
            save_pickle(info.filtered_attends,'filtered_attends.pkl')
            save_pickle(info.user_basic_info,'user_basic_info.pkl')

            print('DEBUG: success to get user info')
            #插入当前用户进入stored_uid
            stored_uid=[x for x in self.session.query(user_info_table.uid).all()]
            b_info=info.user_basic_info
            if b_info['uid'] not in stored_uid:
                temp_table=user_info_table(uid=b_info['uid'],container_id=b_info['container_id'],basic_page=b_info['basic_page'],
                                           name=b_info['name'],gender=b_info['gender'],blog_num=b_info['blog_num'],
                                            description=b_info['description'],fans_num=b_info['fans_num'],attends_num=b_info['attends_num'])
                try:
                    self.session.add(temp_table)
                    self.session.commit()
                    print('user ',b_info['uid'],' is inserted into user_info_table')
                except Exception as e:
                    print(e)
                    self.session.rollback()

            ready_uid=[x for x in self.session.query(ready_to_get.uid).all()]
            insert_list=[]
            current_id=[]
            for item in info.filtered_attends:
                if item['uid'] not in ready_uid and item['uid'] not in stored_uid and item['uid'] not in current_id:
                    current_id.append(item['uid'])
                    temp_table=ready_to_get(uid=item['uid'],basic_page=item['basic_page'],name=item['name'],gender=item['gender'],blog_num=item['blog_num'],description=item['description'],fans_num=item['fans_num'])
                    insert_list.append(temp_table)
            try:
                self.session.add_all(insert_list)
                self.session.commit()
            except:
                self.session.rollback()
                for m in insert_list:
                    try:
                        self.session.add(m)
                        self.session.commit()
                    except:
                        self.session.rollback()

            self.session.delete(current_user)
            self.session.commit()

            print(insert_list.__len__(),' users is inserted into ready_to_get table')
            # except Exception as e:
            #     print('ERROR IN GET USER INFO ',uid)
            #     print(e)



def test():
    data=load_pickle('res.pkl')
    engine=create_engine(conn_query,echo=False)
    Session=sessionmaker(bind=engine)
    session=Session()
    insert_list=[]
    current_id=[]
    err_num=0
    err_line=[]
    for item in data:
        temp_table=ready_to_get(uid=item['uid'],basic_page=item['basic_page'],name=item['name'],
                                gender=item['gender'],blog_num=item['blog_num'],description=item['description'],
                                fans_num=item['fans_num'])
        if item['uid'] not in current_id:
            current_id.append(item['uid'])
            insert_list.append(temp_table)
            print(temp_table)
            try:
                session.add(temp_table)
                session.commit()
            except Exception as e:
                session.rollback()
                print(e)
                err_num+=1
                err_line.append(temp_table)
    session.close()

    print(err_num)
def test2():
    from DB_Interface import  MySQL_Interface
    dbi=MySQL_Interface()
    [x,s]=dbi.select_all('ready_to_get')
    print(x)


if __name__ == '__main__':
    Control()
    # test()




