#!/usr/bin/python
#
# File:   edxStudio.py
# Date:   12-Mar-14
# Author: I. Chuang <ichuang@mit.edu>
#
# upload / download course .tar.gz files to/from edX Studio
#
# usage:  
#
# python edxStudio.py course_id tar_file_name
#
# Put username and passsword in config.py; eg
#    username = "me"
#    password = "my password"


import os, sys
import time
import requests

try:
    from config import *
except:
    pass

class edxStudio(object):

    def __init__(self, base="https://studio.edx.org", username='', password=''):
        self.ses = requests.session()
        self.BASE = base
        self.login(username, password)

    def login(self, username, pw):
        url = '%s/signin' % self.BASE
        r1 = self.ses.get(url)
        csrf = self.ses.cookies['csrftoken']
        url2 = '%s/login_post' % self.BASE
        headers = {'X-CSRFToken':csrf,
                   'Referer': '%s/signin' % self.BASE}
        r2 = self.ses.post(url2, data={'email': username, 'password': pw}, headers=headers)

        if not r2.status_code==200:
            print "Login failed!"
            print r2.text
    
    def do_download(self, course_id):
    
        print "Downloading tar.gz for %s" % (course_id)
    
        (org, num, sem) = course_id.split('/')
        url = '%s/export/%s/branch/draft/block/%s?_accept=application/x-tgz' % (self.BASE, course_id.replace('/','.'), sem)
        r3 = self.ses.get(url)
    
        dt = time.ctime(time.time()).replace(' ','_').replace(':','')
        fn = 'COURSE_DATA/COURSE-%s___%s.tar.gz' % (course_id.replace('/','__'),dt)
    
        open(fn, 'w').write(r3.content)
        print "--> %s" % (fn)
        return fn
    
    def do_upload(self, course_id, tfn, nwait=20):
    
        print "Uploading %s for %s" % (tfn, course_id)
    
        (org, num, sem) = course_id.split('/')
        url = '%s/import/%s/branch/draft/block/%s' % (self.BASE, course_id.replace('/','.'), sem)
    
        files = {'course-data': (tfn, open(tfn, 'rb'), 'application/x-gzip')}
    
        csrf = self.ses.cookies['csrftoken']
        print "csrf=%s" % csrf
        headers = {'X-CSRFToken':csrf,
                   'Referer': url,
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
               }
    
        r2 = self.ses.get(url)
        print r2.status_code
        r3 = self.ses.post(url, files=files, headers=headers)
        # print r3.headers
        print url
        print r3.status_code
    
        print "--> %s" % (r3.content)
    
        url = '%s/import_status/%s/branch/draft/block/%s/%s' % (self.BASE, course_id.replace('/','.'), sem, tfn.replace('/','-'))
    
        for k in range(nwait):
            r4 = self.ses.get(url)
            print r4.content
            sys.stdout.flush()
            time.sleep(2)
            
        dt = time.ctime(time.time()).replace(' ','_').replace(':','')


#-----------------------------------------------------------------------------

if __name__=='__main__':

    if len(sys.argv)>2:
        cid = sys.argv[1]
        tfn = sys.argv[2]
    else:
        print "Usage: python %s course_id tar_file_name.tgz" % (sys.argv[0])
        exit(0)

    es = edxStudio(username=username, password=password)
    es.do_upload(cid, tfn)
    #es.do_download(cid)


