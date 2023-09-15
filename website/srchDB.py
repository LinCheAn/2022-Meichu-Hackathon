#!/Users/w/opt/anaconda3/bin/python3

import pymongo
import sys
import datetime
import re

class ConnDB():
    def __init__(self) -> None:
        uri = "mongodb+srv://hackathon2022.vpsksno.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        client = pymongo.MongoClient(uri,
                            tls=True,
                            tlsCertificateKeyFile='./certification.pem',
                            )
        self.db = client['hackathon2022']
        self.col = self.db['AlertStamp']

    def showAll(self):
        rlt=[]
        for i in self.col.find():
            rlt.append(i)
        return rlt


def imgStrParser(bs64Str):
    if(bs64Str != 'None' and str(bs64Str) !="b''"):
        return f"<img src='data:image/png;base64, {str(bs64Str)[2:-1]}' alt='image error' />"
    else:
        return ""

def msgStrParser(msg):
    return "<p>"+msg+"</p>"



def printPhp(rlt):
    print('<div class="box" data-aos="fade-up">')
    print('<div class="inboxl"><h2>Detail</h2></div>')
    print('<div class="inboxr"><h2>Image<h2></div>')
    print('</div>')

    for r in rlt:
        print('<div class="box" data-aos="fade-up">')
        print('<div class="inboxl">')
        print(msgStrParser(r['msg']))
        print(msgStrParser('Time: '+r['time']))
        print(msgStrParser('IP: '+r['ip']))
        print('</div>')
        
        print('<div class="inboxr">')
        print(imgStrParser(r['img']))
        print('</div>')
        print('</div>')

def timeStr2Dic(timeStr):
    # parser=re.compile("[ ]*([A-Za-z0-9]*)[ ]*")
    parser=re.compile("([0-9]*)/([0-9]*)/([0-9]*) ([0-9]*):([0-9]*):([0-9]*)")
    match=parser.fullmatch(timeStr)
    tDic={}
    if match:
        tDic['yr']=match.group(1)
        tDic['mon']=match.group(2)
        tDic['dy']=match.group(3)
        tDic['hr']=match.group(4)
        tDic['min']=match.group(5)
        tDic['sec']=match.group(6)

        # for k,v in tDic.items():
        #     print(k,': ',v)
        #     print('<br>')
    else:
        print('error')
        return {}
    for k,v in tDic.items():
        tDic[k]=int(v)
    return tDic
    
    
def timeDiff(ts1,ts2):
    # ts1 >= ts2 
    td1=timeStr2Dic(ts1)
    td2=timeStr2Dic(ts2)
    # for k,v in td1.items():
    #     print(k,':',v,'; ')
    # for k,v in td2.items():
    #     print(k,':',v,'; ')

    td1['mon']=(td1['yr']-td2['yr'])*12+td1['mon']
    td1['dy']=(td1['mon']-td2['mon'])*30+td1['dy']
    td1['hr']=(td1['dy']-td2['dy'])*24+td1['hr']
    td1['min']=(td1['hr']-td2['hr'])*60+td1['min']
    td1['sec']=(td1['min']-td2['min'])*60+td1['sec']

    return td1['sec']-td2['sec']
    



def searchDB(dur,uni):
    db = ConnDB()
    uniDic={'month': 259200, 'day': 86400, 'hr': 3600, 'mins': 60}
    # timestr = datetime.datetime.strptime('2022/10/22 22:44:43', "%Y/%m/%d %H:%M:%S")
    # currtime = datetime.datetime.strptime('2022/11/22 22:45:43', "%Y/%m/%d %H:%M:%S")
    # print(timeDiff(timestr2,timestr1))
    # timediff=currtime-timestr
    # print(timediff.days)

    currtime= datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    currtime = datetime.datetime.strptime(currtime, "%Y/%m/%d %H:%M:%S")
    rlt=db.showAll()
    rtn=[]
    for r in rlt:
        rtime = datetime.datetime.strptime(r['time'], "%Y/%m/%d %H:%M:%S")
        tdiff = currtime - rtime
        # print(f"{r['time']} {tdiff.seconds}<br>")
        if(tdiff.seconds < uniDic[uni]*dur):
            rtn.append(r)

        # if(uni == 'month'):
        #     if(tdiff.days <= 30*dur):
        #         rtn.append(r)
        # elif(uni == 'day'):
        #     if(tdiff.days <= dur):
        #         rtn.append(r)
        # elif(uni == 'hr'):
        #     if(tdiff.min <= dur*60):
        #         rtn.append(r)
        # elif(uni == 'mins'):
        #     if(tdiff.min <= dur):
        #         rtn.append(r)
    return rtn



if(len(sys.argv)<=2):
    exit(0)
else:
    rlt=searchDB(int(sys.argv[2]), sys.argv[3])
    # for i in rlt:
    #     print(i['time'],'<br>')
    printPhp(rlt)

