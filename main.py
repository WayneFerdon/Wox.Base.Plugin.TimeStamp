# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-03-04 12:45:58
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-03 01:09:33
# FilePath: \Wox.Base.Plugin.TimeStamp\main.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
# require pypiwin32, can be install by pip
from datetime import datetime
import traceback

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from WoxBasePluginQuery import *

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

class UnixTimeQuery(QueryPlugin):
    def init(self):
        # region init icon
        self.folderIcon = './Images/app.png'
        # endregion init icon

        # region init separator data
        self.replaceDict = {
            '/':'-', 
            ' ':':'
        }
        separations = [['-', ':'], ['-', ':'], ['T', ':'], [':'], [':'], ['+', '-'], [':']]
        self.separators = ['T', '+', ':', '-']
        self.legitseparations = [['-'], ['-'], ['T'], [':'], [':'], ['+', '-'], [':']]
        # endregion init separator data

        # region init check list
        maxCount = [4, 2, 2, 2, 2, 2, 2, 2]
        minCount = [4, 1, 1, 1, 1, 1, 1, 1]
        floatCount = [0, 0, 0, 0, 0, 6, 0, 0]
        self.checkList = list()
        for i in range(len(maxCount)):
            if i != 0:
                self.checkList.append(separations[i-1])
            self.checkList.append([maxCount[i], minCount[i], floatCount[i]])
        self.maxSplit = len(self.checkList)
        self.patterns = [
            [0, 5], # current date
            [0, self.maxSplit, {"CanReplaceZone":False}], # full
            [2, 3], # current year with at less month and date
            [6, 3], # current date with at less hour and minute
            [11, 2, {"CanReplaceZone":False}, [0, ['+', '-']]], # current time with at less timezone hour
        ]
        self.EMPTY_SPLITED = ["1970","-","01","-","01","T","00",":","00",":","00","+","00",":","00"]
        # endregion init check list

        # region init Error Results
        output = 'OSError'
        SubTitle = 'TIMESTAMP RANGE : [-43200, 32536850399]'
        self.OSErrorResult = QueryResult(output, SubTitle, self.folderIcon, None, None, True).toDict()

        output = 'Enter UnixTime'
        SubTitle = 'TIMESTAMP(Unix) :  u<timestamp>'
        self.UnixTimeErrorResult = QueryResult(output, SubTitle, self.folderIcon, None, None, True).toDict()

        output = 'Enter Time'
        SubTitle = 'TIME(ISO 8601 with Time Zone) : <YYYY>-<MM>-<DD>T<HH>:<MM>:<SS>.<ssssss>+<ZZ>:<zz>'
        self.TimeErrorResult = QueryResult(output, SubTitle, self.folderIcon, None, None, True).toDict()
        # endregion init Error Results
        return

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
        while "" in splited:
            splited.remove("")
        return splited

    def checkSplited(self, splited:list[str], pattern:list):
        if len(splited) < pattern[1]:
            return None
        canReplaceTimeZone = True
        if len(pattern) >= 3:
            for rule in pattern[2:len(pattern)]:
                if type(rule) is dict:
                    for key in rule:
                        if key == "CanReplaceZone":
                            canReplaceTimeZone = rule[key]
                elif type(rule) is list:
                    if len(splited) < rule[0] or splited[rule[0]] not in rule[1]:
                        return None
        splited = self.queryTime[0:pattern[0]] + splited + self.EMPTY_SPLITED[len(splited):len(self.EMPTY_SPLITED)]
        for i in range(len(splited)):
            if splited[i] in self.separators:
                if splited[i] not in self.checkList[i]:
                    return None
                if splited[i] not in self.legitseparations[int(i/2)]:
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
                return None
            if self.floatCount != 0:
                splited[i] = formatFloatDigits(float(splited[i]), max, self.floatCount)
                if len(splited[i]) > totalMax:
                    return None
                pass
            else:
                splited[i] = formatIntDigits(int(splited[i]), max)
        result = [splited]
        if canReplaceTimeZone and "+00:00" in "".join(splited):
            zoneReplaced = splited.copy()
            zoneReplaced[-4] = self.timezone[0]
            zoneReplaced[-3] = self.timezone[1]
            zoneReplaced[-1] = self.timezone[2]
            result.append(zoneReplaced)
        return result

    def reloadTimeZoneInfo(self):
        timezone = (datetime.now() - datetime.utcnow()).total_seconds()
        sign = "+"
        if timezone > 12*3600:
            timezone = 24*3600-timezone
            sign = "-"
        hour = int(timezone/3600)
        minute = round((timezone % 3600)/60)
        if minute >= 60:
            minute-=60
            hour +=1
        self.timezone = [sign, formatIntDigits(hour,2), formatIntDigits(minute,2)]
    
    def getFormatedTimeZone(self):
        return "{}{}:{}".format(self.timezone[0],self.timezone[1],self.timezone[2])

    def getDisplayReplaceList(self):
        return  [
            "".join(self.queryTime[0:6]), # current date
            "".join(self.queryTime[0:2]), # current year
            self.getFormatedTimeZone(), # current zone
            "T00:00:00.000000", # zeroTime
            ":00.000000", # zeroSecond
            ".000000" # zeroMicrosecond
        ]

    def getDisplayFromISO(self, iso:str):
        isoDisplay = iso
        if iso == "".join(self.queryTime):
            return iso
        
        for each in self.getDisplayReplaceList():
            if each not in isoDisplay:
                continue
            isoDisplay = isoDisplay.replace(each,"")
        isoDisplay = isoDisplay.replace("T", " ")
        isoDisplay = isoDisplay.replace("00000+","+")
        isoDisplay = isoDisplay.replace("0000+","+")
        isoDisplay = isoDisplay.replace("000+","+")
        return isoDisplay

    def query(self, queryString:str):
        self.init()
        self.reloadTimeZoneInfo()
        self.queryTime = self.getSplited(str(datetime.now()).replace(" ","T") + "{}{}:{}".format(self.timezone[0],self.timezone[0], self.timezone[1]))
        results = list()
        errorResults = list()
        try:
            outputs = list()
            isoList = list[str]()
            if len(queryString) == 0:
                results.append(self.TimeErrorResult)
                results.append(self.UnixTimeErrorResult)
                iso = datetime.now().isoformat() + self.getFormatedTimeZone()
                isoList.append(iso)
            elif queryString.lower()[0] == 'u':
                if len(queryString) == 1:
                    iso = datetime.now().isoformat() + self.getFormatedTimeZone()
                else:
                    timeDataList = queryString.replace('U', '').replace('u', '')
                    iso = datetime.utcfromtimestamp(float(timeDataList)).isoformat() + "+00:00"
                isoList.append(iso)
            else:
                # YYYY-MM-DDTHH:mm:SS+ZZ:ZZ
                splited = self.getSplited(queryString)
                matched = False
                for pattern in self.patterns:
                    checkedSpliteds = self.checkSplited(splited, pattern)
                    if checkedSpliteds is None:
                        continue
                    for each in checkedSpliteds:
                        if each is not None:
                            matched = True
                            iso = ''.join(each)
                            isoList.append(iso)
                if not matched:
                    raise ValueError()

            checkedISOList = list[str]()
            for iso in isoList:
                try:
                    stamp = datetime.fromisoformat(iso).timestamp()
                except ValueError:
                    tb = traceback.format_exc()
                    if "month must be in" not in tb:
                        QueryDebug.Log(traceback.format_exc())
                    continue
                utcISO = datetime.utcfromtimestamp(stamp).isoformat()+"+00:00"
                utcISO = utcISO.replace(":00+",":00.000000+").replace(":00-",":00.000000-")
                localISO = datetime.fromtimestamp(stamp).isoformat()+self.getFormatedTimeZone()
                localISO = localISO.replace(":00+",":00.000000+").replace(":00-",":00.000000-")
                checkedISOList.append(iso)
                checkedISOList.append(utcISO)
                checkedISOList.append(localISO)

            TimeSubTitle = 'ISO: {}\tPress Enter to Copy ISO Time'
            TimeStampSubTitle = 'ISO: {}\tPress Enter to Copy UnixTime of {}'
            for iso in checkedISOList:
                stamp = datetime.fromisoformat(iso).timestamp()
                if stamp.is_integer():
                    stamp = int(stamp)
                isoDisplay = self.getDisplayFromISO(iso)
                outputs.append([isoDisplay, TimeSubTitle.format(iso), iso])
                outputs.append(["{}".format(stamp), TimeStampSubTitle.format(iso, isoDisplay), str(stamp)])

            for output in outputs:
                result = QueryResult(output[0], output[1], self.folderIcon, 'timestamp', self.copyData.__name__, True, repr(output[2])).toDict()
                isExisted = False
                for existed in results:
                    if existed == result:
                        isExisted = True
                        break
                if isExisted:
                    continue
                results.append(result)
            if len(results) == 0:
                raise ValueError()
        except Exception as e:
            tc = traceback.format_exc()
            if type(e) is OSError:
                errorResults.append(self.OSErrorResult)
            errorResults.append(self.TimeErrorResult)
            errorResults.append(self.UnixTimeErrorResult)
            errorResults.append(
                QueryResult(tc, 'Press Enter to copy traceback', self.folderIcon, None, self.copyData.__name__, True, repr(tc)).toDict()
            )
        results += errorResults
        for log in QueryDebug.Logs:
            results.append(
                QueryResult(str(log[1]), "[Log {}] Press Enter to copy".format(log[0]), self.folderIcon, 'timestamp', self.copyData.__name__, True, log).toDict()
            )
        return results

if __name__ == '__main__':
    QueryDebug()
    UnixTimeQuery()
