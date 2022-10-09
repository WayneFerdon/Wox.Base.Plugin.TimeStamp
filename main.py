# -*- coding: utf-8 -*-
# require pypiwin32, can be install by pip
from datetime import datetime
import traceback

from WoxQuery import *
from RegexList import *

def replaceAll(string:str, replaceFrom:str, replaceTo:str) -> str:
    while replaceFrom in string:
        string = string.replace(replaceFrom, replaceTo)
    return string

def formatIntDigits(num:int, targetCount:int, isAppend=False):
    string = str(num)
    zeros = '0' * max(0, targetCount - len(string))
    if isAppend:
        return string + zeros
    return zeros + string

def formatFloatDigits(num:float, frontCount:int, endCount:int):
    splited = str(num).split('.')
    front = splited[0]
    end = splited[1]
    front = formatIntDigits(front, frontCount)
    end = formatIntDigits(end, endCount, True)
    return front + '.' + end

class WoxTimeStamp(WoxQuery):
    folderIcon = './Images/app.png'
    replaceDict = {
        '/':'-', 
        ' ':':'
    }
    separators = ['T', '+', ':', '-']
    maxCount = [4, 2, 2, 2, 2, 2, 2, 2]
    minCount = [4, 1, 1, 1, 1, 1, 1, 1]
    floatCount = [0, 0, 0, 0, 0, 6, 0, 0]
    legitseparations = [['-'], ['-'], ['T'], [':'], [':'], ['+', '-'], [':']]
    separations = [['-', ':'], ['-', ':'], ['T', ':'], [':'], [':'], ['+', '-'], [':']]
    checkList = []
    for i in range(len(maxCount)):
        if i != 0:
            checkList.append(separations[i-1])
        checkList.append([maxCount[i], minCount[i], floatCount[i]])

    def initErrorResults(self):
        outPut = 'OSError'
        SubTitle = 'TIMESTAMP RANGE : [-43200, 32536850399]'
        self.OSErrorResult = WoxResult(outPut, SubTitle, self.folderIcon, None, None, True).toDict()

        outPut = 'Enter TimeStamp'
        SubTitle = 'TIMESTAMP(Unix) :  u<timestamp>'
        self.TimeStampErrorResult = WoxResult(outPut, SubTitle, self.folderIcon, None, None, True).toDict()

        outPut = 'Enter Time'
        SubTitle = 'TIME(ISO 8601 with Time Zone) : <YYYY>-<MM>-<DD>T<HH>:<MM>:<SS>.<ssssss>+<ZZ>:<zz>'
        self.TimeErrorResult = WoxResult(outPut, SubTitle, self.folderIcon, None, None, True).toDict()

    def getSplited(self, string):
        string = replaceAll(string, '  ', ' ')
        for each in self.separators + list(self.replaceDict.keys()):
            string = replaceAll(string, each + ' ', each)
            string = replaceAll(string, ' ' + each, each)
        for key in self.replaceDict.keys():
            string = string.replace(key, self.replaceDict[key])
        for each in self.separators:
            string = string.replace(each, '@' + each + '@')
        splited = string.split('@')
        if not self.checkSplited(splited):
            raise ValueError()
        return splited

    def checkSplited(self, splited):
        if len(splited) != len(self.checkList):
            return False # datetime.fromisoformat(iso).timestamp()
        for i in range(len(splited)):
            if splited[i] in self.separators:
                if splited[i] not in self.checkList[i]:
                    return False
                if splited[i] not in self.legitseparations:
                    splited[i] = self.legitseparations[int(i/2)][0]
                continue
            num = len(splited[i])
            max = self.checkList[i][0]
            self.floatCount = self.checkList[i][2]
            totalMax = max
            if self.floatCount != 0:
                totalMax += 1 + self.floatCount
            min = self.checkList[i][1]
            if (num > totalMax) or (num < min):
                return False
            if self.floatCount != 0:
                splited[i] = formatFloatDigits(float(splited[i]), max, self.floatCount)
                pass
            else:
                splited[i] = formatIntDigits(int(splited[i]), max)
        return True

    def query(self, queryString:str):
        results = list()
        errorResults = list()
        try:
            if queryString.lower()[0] == 'u':
                SubTitle = 'Press Enter to Copy Time'
                timeDataList = queryString.replace('U', '').replace('u', '')
                outPut = str(datetime.utcfromtimestamp(float(timeDataList)).isoformat())
            else:
                SubTitle = 'Press Enter to Copy TimeStamp'
                # YYYY-MM-DDTHH:mm:SS+ZZ:ZZ
                splited = self.getSplited(queryString)
                outPut = str(datetime.fromisoformat(''.join(splited)).timestamp())
            results.append(
                WoxResult(outPut, SubTitle, self.folderIcon, 'timestamp', self.copyData.__name__, True, str(outPut)).toDict()
            )
        except Exception as e:
            tc = traceback.format_exc()
            self.initErrorResults()
            if type(e) is OSError:
                errorResults.append(self.OSErrorResult)
            errorResults.append(self.TimeErrorResult)
            errorResults.append(self.TimeStampErrorResult)
            errorResults.append(
                WoxResult(tc, 'Press Enter to copy traceback', self.folderIcon, None, self.copyData.__name__, True, repr(tc)).toDict()
            )
        results += errorResults
        return results
if __name__ == '__main__':
    WoxTimeStamp()
