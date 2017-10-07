#!/bin/bin/python
import socket
import time
import os
import re
import sys

import json
import urllib2
import requests

from threading import Timer
from requests.auth import HTTPDigestAuth
from pygerrit.rest import GerritRestAPI

PORT = 80
BaseUrl = 'http://review.android.honeywell.com:8080'

JIRA_ID = ""
COMMIT_LIST = []
COMMIT_INFO = {}
PATCH_NUM = ''
RETRY_COUNT = 10
PATTERN_PRX = ("^(Revert|\[(DUAD|SZMSUS)-(\d)*\])")
PATCH_NUM_PRX = ("\[\d/\d\]")

def gerritChanges(status="open",branch="hon660/nougat/master"):
    apiaction = BaseUrl + '/a/changes/?q=status'
    try:
        auth = HTTPDigestAuth('h127301', 'f8ACkrUqSquzxGSun8awONIrtcD8UtvEM0AytcWz8w')
        rest = GerritRestAPI(url=BaseUrl, auth=auth)
        #searchStr = "/changes/?q=status:"+ status + "+branch:" + branch +"&o=CURRENT_REVISION&o=CURRENT_COMMIT"
        changes0 = rest.get("/changes/?q=status:"+status+"+branch:"+branch+"+before:2017-06-01")
        changes1 = rest.get("/changes/?q=status:" + status + "+branch:" + branch + "+after:2017-06-01+before:2017-07-01")
        changes2 = rest.get("/changes/?q=status:" + status + "+branch:" + branch + "+after:2017-07-01+before:2017-08-01")
        changes3 = rest.get("/changes/?q=status:" + status + "+branch:" + branch + "+after:2017-08-01+before:2017-09-01")
        changes4 = rest.get("/changes/?q=status:" + status + "+branch:" + branch + "+after:2017-09-01+before:2017-10-01")
        changes5 = rest.get("/changes/?q=status:" + status + "+branch:" + branch + "+after:2017-10-01")
        #changes = rest.get(searchStr)
        changes = changes0 + changes1 + changes2 + changes3 + changes4 + changes5
        return changes
    except Exception as err:
        print err
        return None

def checksecuritypatch():
    apiaction = BaseUrl + '/a/changes/?q=status'
    try:
        auth = HTTPDigestAuth('h127301', 'f8ACkrUqSquzxGSun8awONIrtcD8UtvEM0AytcWz8w')
        rest = GerritRestAPI(url=BaseUrl, auth=auth)
        changes = rest.get("/changes/?q=status:open+branch:hon660/nougat/master&o=CURRENT_REVISION&o=CURRENT_COMMIT")
        if changes != None and len(changes) > 0:
            for item in changes:
                context_sub = item['subject']
                if context_sub != None and context_sub == GERRIT_CHANGE_SUBJECT:
                    email_info = item['revisions'][item['current_revision']]['commit']['author']['email']
                    if email_info != None and "Honeywell.com" in email_info:
                        print "Honeywell patch"
                        return False
                    else:
                        print "email_info: %s" % email_info
                        commit = item['project'] + ' ' + str(item['_number']) + '/' + str(
                            item['revisions'][item['current_revision']]['_number'])
                        commands = 'repo download ' + ' ' + commit
                        print '==================download code==============='
                        print commands
                        os.system(commands)
                        return True
    except Exception as err:
        print err
        return False


def getgerritresult():
    apiaction = BaseUrl + '/a/changes/?q=status'
    print apiaction
    # resdata=json.loads(urllib2.urlopen(apiaction).read())
    # response = requests.get(apiaction,auth=('h156930','6gTqZy4gsUyvzug6HJjT7i8i8fPGoSirFtIh2fnvSw'));
    try:
        auth = HTTPDigestAuth('h127301', 'f8ACkrUqSquzxGSun8awONIrtcD8UtvEM0AytcWz8w')
        print auth
        rest = GerritRestAPI(url=BaseUrl, auth=auth)
        changes = rest.get("/changes/?q=status:open+branch:hon660/nougat/master&o=CURRENT_REVISION")
        # print changes
        if changes != None and len(changes) > 0:
            for item in changes:
                print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print item
                print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
                context_sub = item['subject']
                if context_sub != None:
                    print("subject %s" % context_sub)
                    pat_report = re.compile(PATTERN_PRX)
                    match_report = pat_report.search(context_sub)
                    if match_report != None:
                        print("match_report %s" % match_report)
                        context_ID = match_report.group()
                        if context_ID == JIRA_ID:
                            print("context_ID %s" % context_ID)
                            context_change_id = item['change_id']
                            print context_ID
                            print item['project']
                            print item['_number']
                            COMMIT_INFO['commit'] = item['project'] + ' ' + str(item['_number']) + '/' + str(
                                item['revisions'][item['current_revision']]['_number'])
                            print COMMIT_INFO['commit']
                            print item['revisions'][item['current_revision']]['_number']

                            # COMMIT_LIST.append(COMMIT_INFO['commit'])
                            need_append = True
                            for commit in COMMIT_LIST:
                                if commit == COMMIT_INFO['commit']:
                                    need_append = False
                                    break
                            if need_append:
                                index = 0
                                for commit in COMMIT_LIST:
                                    if commit.startswith(item['project'] + ' ' + str(item['_number'])):
                                        del COMMIT_LIST[index]
                                        print "del COMMIT_LIST"
                                    index += 1
                                COMMIT_LIST.append(COMMIT_INFO['commit'])

                            print COMMIT_LIST
                            print len(COMMIT_LIST)
                            # PATCH_NUM='1'
                            if len(COMMIT_LIST) == int(PATCH_NUM):
                                print '==================download code==============='
                                for commit in COMMIT_LIST:
                                    commands = 'repo download ' + ' ' + commit
                                    print commands
                                    os.system(commands)
                                return True
            return False
    except Exception as err:
        print err
        return False


if __name__ == "__main__":
    GERRIT_CHANGE_SUBJECT = os.getenv('GERRIT_CHANGE_SUBJECT')
    if GERRIT_CHANGE_SUBJECT == None:
        print("No Gerrit commit, skip")
        sys.exit(0)

    print GERRIT_CHANGE_SUBJECT
    pat_report = re.compile(PATTERN_PRX)
    match_report = pat_report.search(GERRIT_CHANGE_SUBJECT)
    if not match_report:
        print "commit msg is not correct"
        ret = checksecuritypatch()
        if ret == True:
            sys.exit(0)
        else:
            sys.exit(-1)
    JIRA_ID = match_report.group()
    print JIRA_ID
    pat_report = re.compile(PATCH_NUM_PRX)
    match_report = pat_report.search(GERRIT_CHANGE_SUBJECT)
    if not match_report:
        print "only one commit"
        PATCH_NUM = '1'
        print "patch_number:%s" % PATCH_NUM
        ret = getgerritresult()
        if not ret:
            sys.exit(-1)
    else:
        PATCH_NUM = str(match_report.group().split('/')[1].split(']')[0])
        print "patch_number:%s" % PATCH_NUM
        for i in range(1, RETRY_COUNT + 1):
            ret = getgerritresult()
            print ret
            if not ret:
                time.sleep(60)
            else:
                break
        if i == RETRY_COUNT:
            # print "Not Find all commits"
            # sys.exit(-1)
            print "Not Find all commits, still continue build"
    print "download successfully, patch number:%s" % PATCH_NUM