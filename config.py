__author__ = 'multiangle'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table,Column,String
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
    def __repr__(self):
        return('<ready_to_get(uid=%s)>'%(self.uid))


