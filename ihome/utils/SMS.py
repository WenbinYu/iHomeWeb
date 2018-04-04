#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8a216da86276486901628563908e060d';

#主帐号Token
accountToken= '186d306eda3c4ceeb2edf6c27f07e946';

#应用Id
appId='8a216da8627648690162856390f30614';

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

class CCP(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(CCP,'_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
        cls._instance.rest = REST(serverIP, serverPort, softVersion)
        cls._instance.rest.setAccount(accountSid, accountToken)
        cls._instance.rest.setAppId(appId)

        return cls._instance

    def send_sms(self,to,datas,tempId):
        result = self.rest.sendTemplateSMS(to,datas,tempId)
        if result.get("statusCode") == "000000":
            return 0
        else:
            return -1

#
# def sendTemplateSMS(to,datas,tempId):
#
#
#     #初始化REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)
#
   
#sendTemplateSMS(手机号码,内容数据,模板Id)