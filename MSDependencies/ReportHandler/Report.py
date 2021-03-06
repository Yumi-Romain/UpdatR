#!/usr/bin/python37
# -*- coding: utf-8 -*-

import request
import json
class Report:

    #npm list <package>

    """report = {
        "discord.js":  {
            "packageVersion": "",
            "lastVersion": "",
            "url": "...",
            "doc": "..",
            "packageType": "...",
            "homepage": "...",
            "outdated": bool
        }
    }"""

    def __init__(self):
        self.reports = {}

    def loadReports(self, listDependencies):
        if listDependencies is not None:
            rep = json.loads(listDependencies)
            for package in rep:
                name = str
                if str(package).startswith("@vue"):
                    name = str(package).split('/')[1]
                else:
                    name = package

                packageVersion = rep[package]['wanted']
                lastVersion = rep[package]['latest']
                packageType = rep[package]['type']
                url = "https://www.npmjs.com/package/{}".format(name)
                outdated = self.isOutdated(packageVersion, lastVersion)

                self.reports[name] = {
                    "packageVersion": packageVersion,
                    "lastVersion": lastVersion,
                    "outdated": outdated,
                    "url": url,
                    "packageType": packageType
                }

    def isOutdated(self, actualVersion, lastVersion):
        tabActualVersion = str(actualVersion).split('.')
        tabLastVersion = str(lastVersion).split('.')

        for i in range(3):
            if int(tabActualVersion[i]) < int(tabLastVersion[i]):
                return False
        return True

    def hasOutdatedPackage(self):
        result = False
        for package in self.reports:
            if self.reports[package]['outdated']:
                result = True
        return result

    def getReport(self):
        return self.reports