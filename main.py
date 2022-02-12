# -*- coding: utf-8 -*-
# require pypiwin32, can be install by pip
from wox import Wox, WoxAPI
import win32con
import win32clipboard
import time


# class getTimeStamp():
class getTimeStamp(Wox):
    @classmethod
    def query(cls, queryString):
        folderIcon = 'Images/app.png'
        result = list()
        if queryString == "":
            outPut = 'Enter Time or TimeStamp'
            SubTitle = 'TIME FORMAT : YYYY MM DD HH MM SS ; TIMESTAMP FORMAT : TS <timestamp>'
        else:
            timeDataList = queryString.split(" ")
            if timeDataList[0] == 'TS':
                SubTitle = 'Press Enter to Copy Time'
                if len(timeDataList) == 1:
                    outPut = 'Enter TimeStamp'
                    SubTitle = 'TIME FORMAT : YYYY MM DD HH MM SS ; TIMESTAMP FORMAT : TS <timestamp>'
                else:
                    timeStamp = int(timeDataList[1])
                    timeArray = time.localtime(timeStamp)
                    otherStyleTime = time.strftime("%Y %m %d %H %M %S", timeArray)
                    outPut = otherStyleTime
            else:
                SubTitle = 'Press Enter to Copy TimeStamp'
                defaultTimeList = ["1975", "01", "01", "00", "00", "00"]
                for item in range(0, 6):
                    try:
                        defaultTimeList[item] = timeDataList[item]
                    except IndexError:
                        pass
                timeStr = ""
                for timeItem in defaultTimeList:
                    timeStr = timeStr + timeItem + " "
                try:
                    outPut = time.mktime(time.strptime(timeStr, "%Y %m %d %H %M %S "))
                except OverflowError:
                    outPut = "OverflowError"
        result.append(
            {
                'Title': outPut,
                'SubTitle': SubTitle,
                'IcoPath': folderIcon,
                'ContextData': "timestamp",
                'JsonRPCAction': {
                    'method': 'copyData',
                    'parameters': [str(outPut)],
                    "doNotHideAfterAction".replace('oNo', 'on'): False
                }
            }
        )
        return result

    @classmethod
    def copyData(cls, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, data)
        win32clipboard.CloseClipboard()


if __name__ == '__main__':
    getTimeStamp()
