# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 16:16:00
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-11-23 04:53:43
# FilePath: \Wox.Plugin.TimeStamp\WoxQuery.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
from wox import Wox, WoxAPI
import win32con
import win32clipboard
import traceback

class WoxQuery(Wox):
# class WoxQuery():
    @classmethod
    def copyData(cls, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        # modified from origin to just the copy needs(only for this project)
        # win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, data)
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, data[1:-1])
        win32clipboard.CloseClipboard()
    
    @classmethod
    def getCopyDataResult(cls, type, titleData, iconPath) -> dict:
        title = type + ": " + titleData
        subTitle = 'Press Enter to Copy ' + type
        return WoxResult(title, subTitle, iconPath, None, cls.copyData.__name__, True, titleData).toDict()

class Debug:
    # 静态变量
    Instance=None
    _flag=False
    def __new__(cls, *args, **kwargs):
        if cls.Instance is None:
            cls.Instance=super().__new__(cls)
        return cls.Instance
    def __init__(self):
        if Debug._flag:
            return
        Debug._flag=True

    Logs = list[str]()
    
    @staticmethod
    def Log(*info):
        Debug.Instance.Logs.append([len(Debug.Instance.Logs), str(list(info))[1:-1] + "\n" + "\n".join(traceback.format_stack())])

class WoxResult:
    def __init__(self, title:str, subTitle:str, icoPath:str, contextData , method:str, hideAfterAction:bool, *args) -> None:
        self.title = title
        self.subTitle = subTitle
        self.icoPath = icoPath
        self.method = method
        self.parameters = args
        self.contextData = contextData
        self.hideAfterAction = hideAfterAction
    
    def toDict(self):
        jsonResult = {
            'Title': self.title, 
            'SubTitle': self.subTitle, 
            'IcoPath': self.icoPath, 
            'ContextData': self.contextData
        }
        if self.method is not None:
            jsonResult['JsonRPCAction'] = {
                'method': self.method, 
                'parameters': self.parameters, 
                "doNotHideAfterAction".replace('oNo', 'on'): (not self.hideAfterAction), 
            }
        return jsonResult
