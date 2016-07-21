PyCTP
=========  
上期信息技术CTP开发(Python实现)  

开发环境
--------

    windows10 64, lang:Python3.4.3  
开发顺序
--------  

    PyCTP_API -> PyCTP_QT -> PyCPT_SOCKT

## 各个目录说明  
* PyCTP_API  
  * 针对CTP的API库进行的API测试，分为Market(市场行情),Trader(交易)   
* PyCTP_Integration
  * 将CTP的Market、Trader集成到一起的版本,并实现多账户管理
* PyCTP_QT
  * 在PyCTP_Integration基础上实现界面操作
* PyCTP_SOCKET  
  * 实现PyCTP与Server之间的socket通信版本  

### 更新时间:2016.07.21  
