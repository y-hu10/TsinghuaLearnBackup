import urllib2
import urllib
import re
import os
import HTMLParser
import sys
try:
    import cookielib
except Exception as hehe:
    import http.cookiejar as cookielib

def SettingUp():
    Cookie = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(Cookie))  #Setting about cookies
    urllib2.install_opener(opener)                                      #What is the cookies usage

def GetHeaders():
    _HEADER = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection':'keep-alive',
                'Accept-Encoding':'gzip,deflate,sdch',
                'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'}
    return _HEADER


def _SEE(_URL):   #get html with no data update
    req = urllib2.Request(url = _URL,headers = GetHeaders())  
    try:
        response = urllib2.urlopen(req)
    except urllib2.URLError, e:
        print e
    return response.read()
    
def _POST(_URL,_DATA):     #get html with method post
    req = urllib2.Request(url = _URL,data = _DATA,headers = GetHeaders())
    try:
        response = urllib2.urlopen(req)
    except urllib2.URLError, e:
        print e
    return response.read()

def _GET(_URL,_DATA):      #get html with method get
    _URL = _URL + '?'
    for data in _DATA:
        _URL = _URL + data[0] + '=' + data[1] + '&'
    _URL = _URL[0:-1]
    return _SEE(_URL)

def _DOWNLOAD(_url,_filename):      #download file
    try:
        req = urllib2.Request(url = _url,headers = GetHeaders())
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            print e
        responsehead = response.info().getheaders('Content-Length')
        filesize = int(responsehead[0])
        responsehead = response.info().getheaders('Content-Disposition')
        ext = responsehead[0].split('.')[-1][0:-1]
        _filename = _filename + ext
##    print _filename
        f = open(_filename , 'wb')
        print 'downloading '+ _filename.split('/')[-1] + ' ' + str(filesize) + ' Bytes'
        CACHE = 1000 * 1024
        filesizenow = 0
        while(True):
            data = response.read(CACHE)
            if not data:
                break
            f.write(data)
            filesizenow += len(data)
            stat = r"[%3.2f%%]" % (float(filesizenow) / float(filesize) * 100.0)
            stat = 'Complete: ' + stat
            print stat
    except Exception, e:
        print e

def removeblank(string):
    return string.replace(' ','').replace('\t','').replace('\r','').replace('\n','')

def MakeDirectory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def GetCourseList():
    _url = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=2'  
    html = _SEE(_url)
    unicodePage = html.decode("utf-8")
    items = re.findall('<a href="/MultiLanguage/lesson/student/course_locate\.jsp\?course_id=(\d+)" target="_blank">(.*?)</a>',html,re.S)
    course = []
    for item in items:
        courseName = removeblank(item[1])
        courseName = re.findall('(.*?)\(.*\)',courseName,re.S)
        courseName = courseName[0].decode('utf-8')
 ##       print courseName
        course.append([item[0],courseName])
    return course

def GetCoursePATH(_COURSE):
    return '/course/' + _COURSE[1]

def String_Convert(string):
    string = string.decode('utf-8')
    html_parser = HTMLParser.HTMLParser()
    txt = html_parser.unescape(string).encode('utf-8')  #these encode or decode things still to be understood
    txt = txt.replace('<br />','\n')
    return txt

def NotAllowedFilename(string):
    link = re.compile('[\:,\<,\>,\|,\\,\/,\?,\"]')
    blanklink = re.compile(' +')
    string = re.sub(link,'_',string)
    return re.sub(blanklink,' ',string)

def GetCourseAnn(_COURSE):
    _url = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/getnoteid_student.jsp?course_id=' + _COURSE[0]
    html = _SEE(_url)
    #print html
    Anns = re.findall('<a  href=\'(.*?)\'>(.*?)</a>',html,re.S)
    for ann in Anns:
        ann_in_red = re.findall('<font color=red>(.*?)</font>',ann[1],re.S)
        if len(ann_in_red):
            ann_name = ann_in_red[0]
        else:
            ann_name = ann[1]
        ann_name = ann_name.decode('utf-8').replace('&nbsp;',' ')
        ann_name = NotAllowedFilename(ann_name)
        ann_url = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/' + ann[0]
        Ann_PATH = GetCoursePATH(_COURSE) + '/Announcement/'
        MakeDirectory(Ann_PATH)
        print Ann_PATH+ann_name+'.txt'
        f = open(Ann_PATH + ann_name + '.txt' , 'w')
        
        html = _SEE(ann_url)
        Content = re.findall('overflow:hidden;">(.*?)</td>',html,re.S)
        f.write(String_Convert(Content[0]))
        f.close()

def GetCourseFile(_COURSE):
    _url = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/download.jsp?course_id=' + _COURSE[0]
    html = _SEE(_url)
    Files = re.findall('<a target="_top" href="(.*?)" >(.*?)</a>',html,re.S)
    for _file in Files:
        filename_in_red = re.findall('<font color=red>(.*?)</font>',_file[1],re.S)
        if(len(filename_in_red)):
            filename = filename_in_red[0]
        else:
            filename = _file[1]
        filename = String_Convert(removeblank(filename)).decode('utf-8').replace('&nbsp;',' ')
        filename = NotAllowedFilename(filename)
        fileadd = 'http://learn.tsinghua.edu.cn' + _file[0]
        filepath = GetCoursePATH(_COURSE) + '/Files/'
        MakeDirectory(filepath)
        filepath = filepath + filename + '.'
        _DOWNLOAD(fileadd,filepath)

def GetHomeWork(_COURSE):
    _url = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id=' + _COURSE[0]
    html = _SEE(_url)
    HomeWorks = re.findall('<a href="(.*?)">(.*?)</a>',html,re.S)
    for homework in HomeWorks:
        homeworkname = homework[1]
        homeworkname = String_Convert(removeblank(homeworkname)).decode('utf-8').replace('&nbsp;',' ')
        homeworkname = NotAllowedFilename(homeworkname)
        homeworkadd = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/' + homework[0]
        homeworkpath = GetCoursePATH(_COURSE) + '/Homeworks/' + homeworkname + '/'
        MakeDirectory(homeworkpath)
        html2 = _SEE(homeworkadd)
        hh = re.findall('a target="_top" href="(.*?)">(.*?)</a>',html2,re.S)
        for hhh in hh:
            file1 = hhh[1]
            file1 = String_Convert(removeblank(file1)).decode('utf-8').replace('&nbsp;',' ')
            file1 = NotAllowedFilename(file1)
            file1add = 'http://learn.tsinghua.edu.cn' + hhh[0]
            file1path = homeworkpath + file1 + '.'
            _DOWNLOAD(file1add,file1path)

SettingUp()

while(1):
    
    username = raw_input()
    passwd = raw_input()

    _url = 'https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp'
    DATA = (('userid',username),('userpass',passwd))
    _A = _GET(_url,DATA)

    loginS = re.findall('loginteacher_action',_A,re.S)
    if(len(loginS)):
        print "Login Successfully"
        break
    else:
        print "Error Username or Password, Please Try Again"

_url = "https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher_action.jsp"
_B = _SEE(_url)
_url = "http://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/mainteacher.jsp"
_C = _SEE(_url)
_url = "http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/mainstudent.jsp"
_D = _SEE(_url)
#print(_D)

_CourseList = GetCourseList()


for course in _CourseList:
    CourseForTest = course
    GetCourseAnn(CourseForTest)
    GetCourseFile(CourseForTest)
    GetHomeWork(course)
    raw_input()
