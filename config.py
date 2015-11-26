__author__ = 'multiangle'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table,Column,String,Integer
Base=declarative_base()



# MYSQL CONNECTION CONFIG
mysql_config={
    'user':'root',
    'passwd':'',
    'host':'localhost',
    'db':'microblog_spider',
    'port':'3306',
    'charset':'utf8'
}
conn_query='mysql+mysqlconnector://%s:%s@%s:%s/%s?charset=%s'%(
    mysql_config['user'],
    mysql_config['passwd'],
    mysql_config['host'],
    mysql_config['port'],
    mysql_config['db'],
    mysql_config['charset']
)

# TABLE PROPERTY CONFIG
class ready_to_get(Base):
    __tablename__='ready_to_get'
    uid=Column(String,primary_key=True)
    basic_page=Column(String)
    name=Column(String)
    gender=Column(String)
    blog_num=Column(Integer)
    description=Column(String)
    fans_num=Column(Integer)
    def __repr__(self):
        return('<ready_to_get(name=%s,gender=%s,description=%s ,fans num=%s ,blog num=%s, '
               'basic page=%s , uid=%s)>'%(self.name,self.gender,self.description,self.fans_num,
        self.blog_num,self.basic_page,self.uid))

class user_info_table(Base):
    __tablename__='user_info_table'
    uid=Column(String,primary_key=True)
    container_id=Column(String)
    basic_page=Column(String)
    name=Column(String)
    gender=Column(String)
    blog_num=Column(Integer)
    description=Column(String)
    fans_num=Column(Integer)
    attends_num=Column(Integer)
    def __repr__(self):
        return('<user_info(name=%s,gender=%s,description=%s ,fans num=%s ,blog num=%s, attends num=%s , '
               'basic page=%s , container id=%s , uid=%s)>'%(self.name,self.gender,self.description,self.fans_num,
        self.blog_num,self.attends_num,self.basic_page,self.container_id,self.uid))





