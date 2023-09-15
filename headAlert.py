import time
import datetime
import requests
import base64
from connMongoDB import ConnDB

class Notify():
    def __init__(self) -> None:
        self.token=base64.b64decode(('ZTdkM085ajRWVTFQZVB2OThWNFpYazVJS3hEU00wT0J5QlRTaXE0T2hlOA=='.encode())).decode()
        self.header={
            "Authorization": "Bearer " + self.token
        }

    def makeNotify(self, nData):
        msg = f"\n{nData['msg']} \nTime: {nData['time']} \nIP: {nData['ip']}"
        data={'message' : msg}
        file={'imageFile' : nData['img']}

        r = requests.post("https://notify-api.line.me/api/notify", headers = self.header, data = data, files = file)
        print(f'Sending at {time.ctime()}')

def MakeAlert(alertMsg, notify = False, insertdb = True):
    if notify:
        ntfy = Notify()
        ntfy.makeNotify(alertMsg)
    if insertdb:
        db = ConnDB()
        db.insert(alertMsg)

if __name__=="__main__":

    timestr = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    msg = 'test msg'
    img = open('./000005.jpg', 'rb')
    ip = '8.8.8.8'
    alertMsg={'time':timestr, 'ip': ip, 'msg': msg, 'img': img}
    # MakeAlert(alertMsg, 1, 0)
    MakeAlert(alertMsg)
    
    #############

    # print('Make notify...')
    # ntfy = Notify()
    # image = open('./image.png', 'rb')
    # msg=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # sendData={'msg': msg, 'img': image}
    # ntfy.makeNotify(sendData)
    




