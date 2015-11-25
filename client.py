__author__ = 'multiangle'

import http.cookiejar
import urllib.request as request
import urllib.parse as parse
from bs4 import BeautifulSoup

import time,json,re

from client_config import MAX_PROCESS,MAX_THREAD

class WeiboConnector(object):
    """
    This is a container of login to weibo.cn
    """

    def __init__(self, nickname, pwd):

        self.nickname=nickname
        self.pwd=pwd

        self.__header = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) '
                                       'AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'}
        self.__cj = http.cookiejar.CookieJar()

        # self.proxy_manager=proxy_manager(10)
        self.proxy_manager=None
        # self.current_proxy=self.proxy_manager.request_proxy(1)[0]
        self.current_proxy='120.195.195.6:80'
        self.proxy_handler=request.ProxyHandler({'http':self.current_proxy})
        # proxy_auth_handler=request.ProxyBasicAuthHandler()
        print('current proxy: ',self.current_proxy)
        # self.opener = request.build_opener(request.HTTPCookieProcessor(self.__cj),self.proxy_handler)
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.__cj))
        self.__login_url = 'http://login.weibo.cn/login/'

        request.install_opener(self.opener)

        self.__login(nickname, pwd)

    def getData(self, url,timeout=8,reconn_num=5,proxy_num=5):
        try:
            result=self.__getData_inner(url,timeout=timeout)
            return result
        except Exception as e:
            print('*** connect fail,ready to reconnect ***')
            print('reason: ',e)
            proxy_count=1
            while(proxy_count<=proxy_num):
                reconn_count=1
                while (reconn_count<=reconn_num):
                    print('--- the ',reconn_count,'th reconnect ---')
                    try:
                        result=self.__getData_inner(url,timeout=timeout)
                        return result
                    except:
                        reconn_count+=1
                print('*** reconnect fail, ready to change proxy ***')
                self.change_proxy()
                print('--- change proxy for ',proxy_count,' times ---')
                self.__login(self.nickname,self.pwd)
                proxy_count+=1
            raise StopIteration('*** run out of reconn and proxy times, ')

    def __getData_inner(self,url,timeout=20):
        req = request.Request(url, headers=self.__header)
        time.sleep(0.4)
        result = self.opener.open(req,timeout=timeout)
        return result.read().decode('utf-8')
        # print(result.read())

    def postData(self, url, data,timeout=20):
        try:
            res=self.__postData_inner(url,data,timeout=timeout)
            return res
        except Exception as e:
            print("Request Error，urls" + url)
            print(e)
            proxy_count=1
            while (proxy_count<10):
                self.change_proxy()
                print('--- change proxy in post for ',proxy_count,' times ---')
                try:
                    res=self.postData(url,data,timeout=timeout)
                    return res
                except:
                    proxy_count+=1
            raise StopIteration('*** unable to post data ***')

    def __postData_inner(self,url,data,timeout=20):
        data = parse.urlencode(data).encode('utf-8')
        req = request.Request(url, data, headers=self.__header)
        result = self.opener.open(req,timeout=timeout)
        return result.read().decode('utf-8')

    def __login(self, nickname, pwd):
        print('......Login ing......')
        res_weibo_login = self.getData(self.__login_url)
        html = BeautifulSoup(res_weibo_login)

        login_post_url = self.__login_url + html.find('form')['action']
        vk = html.find('input', attrs={'name': 'vk'})['value']
        pwd_name = html.find('input', attrs={'type': 'password'})['name']

        data = {
            'mobile': nickname,
            pwd_name: pwd,
            'remember': 'on',
            'backURL': 'http://weibo.cn',
            'backTitle': '手机新浪网',
            'tryCount': '',
            'vk': vk,
            'submit': '登录'
        }


        self.postData(login_post_url, data)
        home_url = "http://m.weibo.cn/u/5648132747"
        res_login=self.getData(home_url)
        htmlofhome = BeautifulSoup(res_login)
        title = htmlofhome.find('title').string
        if title == '个人主页':
            print('~~~~~~Login Success~~~~~~')
            for i in range(1, 20):
                print('-', end='')
        else:
            print('******Login Fail******')
            exit(0)

    def change_proxy(self):
        self.current_proxy=self.proxy_manager.request_proxy(1,drop=[self.current_proxy])[0]
        print('--- change proxy to ',self.current_proxy,' --- ')
        self.__cj = http.cookiejar.CookieJar()
        proxy_handler=request.ProxyHandler({'http':self.current_proxy})
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.__cj),proxy_handler)
        request.install_opener(self.opener)

class getInfo(object):
    def __init__(self,Connector,uid):
        self.__uid = str(uid)
        self.__con=Connector
        self.user_basic_info=self.getBasicInfo()
        self.attends=self.getAttends(self.user_basic_info['containerid'])
        # self.getFans('1005051496822520')

    def card_group_item_parse(self,sub_block):
        """
        :param user_block   : json type
        :return:  user      : dict type
        """
        user_block=sub_block['user']
        user_block_keys=user_block.keys()
        user={}

        if 'profile_url' in user_block_keys:
            user['basic_page']=user_block['profile_url']

        if 'screen_name' in user_block_keys:
            user['name']=user_block['screen_name']

        if 'desc2' in user_block_keys:
            user['recent_update_time']=user_block['desc2']

        if 'desc1' in user_block_keys:
            user['recent_update_content']=user_block['desc1']

        if 'gender' in user_block_keys:
            user['gender']=('male' if user_block['gender']=='m' else 'female')

        if 'verified_reason' in user_block_keys:
            user['verified_reason']=user_block['verified_reason']

        if 'profile_image_url' in user_block_keys:
            user['profile']=user_block['profile_image_url']

        if 'statuses_count' in user_block_keys:
            temp=user_block['statuses_count']
            if isinstance(temp,str):
                temp=int(temp.replace('万','0000'))
            user['blog_num']=temp

        if 'description' in user_block_keys:
            user['description']=user_block['description']

        if 'follow_me' in user_block_keys:
            user['follow_me']=user_block['follow_me']

        if 'id' in user_block_keys:
            user['uid']=user_block['id']

        if 'fansNum' in user_block_keys:
            temp=user_block['fansNum']
            if isinstance(temp,str):
                temp=int(temp.replace('万','0000'))
            user['fans_num']=temp

        return user
    # 获取当前用户的关注人列表
    def getAttends(self,container_id,constrain=-1):
        # follower_url = 'http://m.weibo.cn/page/tpl?containerid='+str(container_id)+'_-_FOLLOWERS'
        # page = self.__con.getData(follower_url)
        # # html = BeautifulSoup(res)
        # info_str=re.findall(r'{.+?};',page)[1].replace("'","\"")
        # info_str=info_str[0:info_str.__len__()-1]
        # infno_json=json.loads(info_str)
        # atten_block=infno_json['stage']['page'][1]['card_group']
        # atten_list=[self.card_group_item_parse(x) for x in atten_block]
        if constrain>0:
            pass
        else:
            constrain=int(self.user_basic_info['attends_num']/10)
        attends_list=[]
        for i in range(constrain):
            follower_url = 'http://m.weibo.cn/page/tpl?containerid='+str(container_id)+'_-_FOLLOWERS'+'&page='+str(i)
            page = self.__con.getData(follower_url)
            try:                     #第一次获取页面，获得不正常页面，解析失败
                page=re.findall(r'"card_group":.+?]}]',page)[0]
                page='{'+page[:page.__len__()-1]
                page=json.loads(page)
                temp_list=[self.card_group_item_parse(x) for x in page['card_group']]
                attends_list=attends_list+temp_list
                print('Page ',i,' is done')

            except Exception as e:
                print(e)
                try:                #分析是否是因为 “没有内容” 出错，如果是，当前的应对措施是休眠5秒，再次请求。
                    page=page.strip()
                    page="{\"test\":"+page+"}"
                    data=json.loads(page)
                    if data['test'][1]['msg']=='没有内容':
                        time.sleep(5)
                        print('--- fail to get valid page, sleep for 5 seconds ---')
                        page = self.__con.getData(follower_url)
                        try:
                            page=re.findall(r'"card_group":.+?]}]',page)[0]
                            page='{'+page[:page.__len__()-1]
                            page=json.loads(page)
                            temp_list=[self.card_group_item_parse(x) for x in page['card_group']]
                            attends_list=attends_list+temp_list
                            print('Page ',i,' is done')
                        except:
                            pass    #如果再次失败，当前措施是直接跳过

                except Exception as e:  #如果不是因为 “没有内容出错” 则出错原因不明，直接跳过
                    print(e)
                    print('*** ERROR: Unknown page type, fail to parse *** :',follower_url)
                    print(page)
                    print('--- skip this page ---')
                    pass
        return attends_list

    def getFans(self,container_id,constrain=200):
        count=0
        for i in range(constrain):
            try:
                follower_url = 'http://m.weibo.cn/page/tpl?containerid='+str(container_id)+'_-_FANS'+'&page='+str(i)
                page = self.__con.getData(follower_url)
                page=re.findall(r'"card_group":.+?]}]',page)[0]
                page='{'+page[:page.__len__()-1]
                page=json.loads(page)
                atten_list=[self.card_group_item_parse(x) for x in page['card_group']]
                for x in atten_list:
                    count+=1
                    print(x['name'],'\t',count)
            except Exception as e:
                print(e)

    def getfolloweruid(self, req_url):
        res = self.__con.getData(req_url)
        html = BeautifulSoup(res)
        tables = html.find_all('table')
        pass

    def getBasicInfo(self):
        homepage_url = 'http://m.weibo.cn/u/' + str(self.__uid)
        homepage_str = self.__con.getData(homepage_url)
        user_basic_info={}
        info_str = re.findall(r'{(.+?)};', homepage_str)[1].replace("'", "\"")
        info_str = '{'+ info_str +'}'
        info_json = json.loads(info_str)

        user_basic_info['containerid'] = info_json['common']['containerid']     #containerid
        info = json.loads(info_str)['stage']['page'][1]
        user_basic_info['uid'] = info['id']                                         #uid
        user_basic_info['name'] = info['name']                                     #name
        user_basic_info['description'] = info['description']                     #description
        user_basic_info['gender'] = ('male' if info['ta'] == '他' else 'female')   #sex
        user_basic_info['verified'] = info['verified']
        user_basic_info['verified_type'] = info['verified_type']
        user_basic_info['native_place'] = info['nativePlace']

        user_basic_info['fans_num'] = info['fansNum']
        if isinstance(info['fansNum'],str):
            temp=info['fansNum'].replace('万','0000')
            temp=int(temp)
            user_basic_info['fans_num']=temp

        user_basic_info['blog_num'] = info['mblogNum']
        if isinstance(info['mblogNum'],str):
            temp=info['mblogNum'].replace('万','0000')
            temp=int(temp)
            user_basic_info['blog_num']=temp

        user_basic_info['attends_num'] = info['attNum']
        if isinstance(info['attNum'],str):
            temp=info['attNum'].replace('万','0000')
            temp=int(temp)
            user_basic_info['attends_num']=temp

        user_basic_info['detail_page']="http://m.weibo.cn/users/"+str(user_basic_info['uid'])
        user_basic_info['basic_page']='http://m.weibo.cn/u/'+str(user_basic_info['uid'])
        print('\n','CURRENT USER INFO ','\n','Name:',user_basic_info['name'],'\t','Fans Num:',user_basic_info['fans_num'],'\t',
              'Attens Num:',user_basic_info['attends_num'],'\t','Blog Num:',user_basic_info['blog_num'],'\n',
              'Atten Page Num:',int(user_basic_info['attends_num']/10),'\n',
              'description:',user_basic_info['description']
        )
        return user_basic_info
        # userInfo_url = 'http://m.weibo.cn/users/' + str(self.__uid)
        # print(name,'\t',id)
        # print(attendsNum)
        # userInfo_str = self.__con.getData(userInfo_url)
        # birthday = re.findall(r'<span>生日</span><p>(.+?)-[\d]{2}-[\d]{2}</p>', userInfo_str)
        # age = -1 if len(birthday) == 0 else 2015 - int(birthday[0])
        # print(name)





        # try:
        #     file = open('out.html', 'w', encoding='utf-8')
        #     file.write(res)
        # except Exception as e:
        #     print('写入失败')
        #     print(e)
        # finally:
        #     file.close()

class proxy_manager():
    """
    如果创建类返回-1 表示创建失败 返回1 表示成功 0表示不完全创建（有异常）
    """
    def __init__(self,list_len=10):
        self.__proxy_contain_num=list_len       #proxy 池的容量
        self.__proxy_list=[]                     #proxy 列表
        self.__proxy_state=[]                    #0 表示不可用或者锁定， 1表示当前可用
        self.__valid_num=0
        self.__get_proxy__(self.__proxy_contain_num)
        if self.__proxy_list.__len__()==0:
            print("ERROR From proxy_manager:Unable to initial proxy_manager")
        elif self.__proxy_list.__len__()<self.__proxy_contain_num:
            print("WARNING From proxy_manager:Unable to get sufficient proxy")
        elif self.__proxy_list.__len__()==self.__proxy_contain_num:
            pass
        else:
            print("ERROR From proxy_manager: self.__proxy_list.__len__()>self.__proxy_contain_num")

    def __get_proxy__(self,num):
        url='http://vxer.daili666api.com/ip/?tid=557469148308119&num=%s&category=2&foreign=none'%(str(num))
        try:
            req=request.urlopen(url).read()
            req=str(req,encoding='utf-8')
            list=req.split('\r\n')
            if list.__len__()<num:
                print('WARNING FROM proxy_manager.get_proxy:proxy len < wanted length')
            self.__proxy_list=self.__proxy_list+list
            self.__proxy_state=self.__proxy_state+[1]*list.__len__()
            self.__valid_num=self.__valid_num+list.__len__()
        except Exception as e:
            print("!!!ERROR!!! Unable to get proxy from daili666api",e)


    def request_proxy(self,num,drop=[],rtn=[]):
        # check if the input is valid
        if not isinstance(drop,list):
            print("ERROR From proxy_manager.request_proxy: invalid input")
            return []
        if not isinstance(rtn,list):
            print("ERROR From proxy_manager.request_proxy: invalid input")
            return []
        # check if there are data in drop and rtn(return) list
        if drop!=[]:
            for item in drop:
                if item in self.__proxy_list:
                    index=self.__proxy_list.index(item)
                    self.__drop_proxy_asIndex(index)
        if rtn!=[]:
            for item in rtn:
                if item in self.__proxy_list:
                    if self.__proxy_state[self.__proxy_list.index(item)]==0:
                        self.__valid_num+=1
                    self.__proxy_state[self.__proxy_list.index(item)]=1

        if self.__proxy_list.__len__()<int(self.__proxy_contain_num/2):     #if the proxy is not enough ,request more
            self.__get_proxy__(self.__proxy_contain_num-self.__proxy_list.__len__())
        if num==0:
            return []
        if num>self.__valid_num+self.__proxy_contain_num-self.__proxy_list.__len__():
            num=self.__valid_num+self.__proxy_contain_num-self.__proxy_list.__len__()
        if num>self.__valid_num:
            self.__get_proxy__(self.__proxy_contain_num-self.__proxy_list.__len__())
        count=0
        out_list=[]
        for i in range(self.__proxy_list.__len__()):
            if self.__proxy_state[i]==1:
                out_list.append(self.__proxy_list[i])
                count+=1
                self.__valid_num-=1
                self.__proxy_state[i]=0
            if count>=num:
                break
        return out_list

    def __drop_proxy_asIndex(self,index):
        if index>=self.__proxy_list.__len__():
            print("ERROR FROM proxy_manager.__drop_proxy_asIndex: invalid index!")
        else:
            if self.__proxy_state[index]==1:
                self.__valid_num-=1
            del(self.__proxy_list[index])
            del(self.__proxy_state[index])

if __name__ == '__main__':
    con=WeiboConnector('weilidian@126.com', 'z123456')
    res=getInfo(Connector=con,uid=1496822520)
    # for i in res.attends:
    #     print(i['name'],'\t',i['uid'],'\t',i['fans_num'],'\t')
    print('Done Successfully')
