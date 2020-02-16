# -*- coding: utf-8 -*-

from threading import Thread
from time import sleep, time
from selenium.webdriver import Chrome
# from selenium.webdriver.chrome.options import Options
from requests import get, post
import json
from pickle import dump, load
from uuid import uuid1
from re import findall
from random import sample
from string import ascii_letters, digits
import socket
import os
from traceback import print_exc

def my_encode(mac):
    maclist = list(mac)
    for i in range(len(maclist)):
        maclist[i] = chr((ord(maclist[i])+i**3) % 128)
    newmac = "".join(maclist) + ''.join(sample(ascii_letters + digits, 10))
    return newmac.encode('utf-8')

def my_decode(newmac):
    newmac = newmac.decode('utf-8')
    l = len(newmac) - 10
    mac = newmac[:l]
    maclist = list(mac)
    for i in range(len(maclist)):
        maclist[i] = chr((ord(maclist[i])-i**3) % 128)
    newmac = "".join(maclist)
    return newmac

def register():
    # 获取mac
    mac = "-".join(findall(r".{2}",uuid1().hex[-12:].upper()))
    # 上传mac
    # 脑洞：每次开始时都下载下一次连接
    link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # LAN = '127.0.0.1'
    domain = 'www.live4dreamch.xyz'
    IP = '111.231.137.179'
    IP = socket.gethostbyname(domain)
    port = 42319
    link.connect((IP, port))
    print('连接注册服务器端成功！')
    link.send(my_encode(mac))
    registered = my_decode(link.recv(1024))
    if registered == '1':
        link.close()
        return 1
    rkey = input('请输入注册码：')
    link.send(my_encode(rkey))
    register_result = my_decode(link.recv(1024))
    if register_result == '1':
        print('\n注册成功！\n')
        link.close()
        return 1
    else:
        link.close()
        input('注册失败！按回车退出')
        exit(0)

def login():
    print('欢迎试用！本程序仅用于学习、交流程序设计方法，不当使用责任自负！\n')
    sleep(1)
    register()

    try:
        with open('/GrabLessons/Cookies.json', 'r', encoding='utf-8') as f:
            cookie2 = f.readline().rstrip('\n')
            StuID = f.readline()
            listCookies = json.loads(cookie2)
        cookie = [item["name"] + "=" + item["value"]
                for item in listCookies]
        cookiestr = '; '.join(item for item in cookie)

        # 获取token
        url_gettoken = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/student/register.do?number=' + StuID
        headers_1 = {
            'Cookie': cookiestr
        }
        res = get(url_gettoken, headers=headers_1).json()
    except Exception:
        print(print_exc())
        StuID = input('输入学号：')
        if StuID == '0':
            StuID = '2186114147'
        Psw = input('输入密码：')
        if Psw == '0':
            Psw = 'lchAK47.423'
        # eBC = input('输入选课批次代码electiveBatchCode：')
        # eBC = '01ffc28d54e1452cbf1e954ccd138ab9'

        # 获取登录Cookie
        # option = Options()
        # option.headless = True
        # driver = Chrome(options = option)
        driver = Chrome()
        driver.minimize_window()
        driver.get("http://xkfw.xjtu.edu.cn/")
        sleep(1)
        user_name = driver.find_element_by_xpath(r'//*[@id="form1"]/input[1]')
        user_name.send_keys(StuID)
        pass_word = driver.find_element_by_xpath(r'//*[@id="form1"]/input[2]')
        pass_word.send_keys(Psw)
        button_3 = driver.find_element_by_xpath(r'//*[@id="account_login"]')
        button_3.click()
        while driver.current_url != "http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/*default/index.do":
            sleep(1)
        cookie = driver.get_cookies()
        driver.close()
        jsonCookies = json.dumps(cookie)
        with open('/GrabLessons/Cookies.json', 'w') as f:
            f.writelines([jsonCookies+'\n', StuID])
        with open('/GrabLessons/Cookies.json', 'r', encoding='utf-8') as f:
            listCookies = json.loads(f.readline().rstrip('\n'))
        cookie = [item["name"] + "=" + item["value"]
                for item in listCookies]
        cookiestr = '; '.join(item for item in cookie)

        # 获取token
        url_gettoken = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/student/register.do?number=' + StuID
        headers_1 = {
            'Cookie': cookiestr
        }
        res = get(url_gettoken, headers=headers_1).json()
    token = res['data']['token']

    headers = {
        'Cookie': cookiestr,
        'token': token
    }
    # print('headers =\n', json.dumps(headers, sort_keys=True, indent=4, separators=(',', ': ')))
    eBC = get_eBC(StuID, headers)
    print('登录成功！\n')
    sleep(0.5)
    return StuID, headers, eBC

def get_eBC(StuID, headers):
    timestamp = str(round(time() *1000))
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/student/' + StuID + '.do?timestamp=' + timestamp
    res = get(url, headers=headers).json()
    eBC = res['data']['electiveBatchList'][0]['code']
    # print('\nelectiveBatchCode =\n', eBC)
    return eBC

def download(StuID, headers, eBC):
    try:
        with open('/GrabLessons/Caches.data', 'rb') as f:
            feBC = load(f)
            if feBC != eBC:
                print('大人，轮次变了\n')
                raise FileNotFoundError
            check = input('检测到之前曾经加载过本轮选课的课程，是否重新加载？[是/否]（仅在网络极差时选择否,如直接回车,则默认选是）：')
            if check != '否':
                raise FileNotFoundError
            courses = load(f)
    except:
        courses = dict()
        for mode in 'TJKC', 'XGXK', 'FANKC', 'FAWKC', 'TYKC', 'CXKC':
            do = {
                'TJKC':'recommendedCourse.do',
                'FANKC':'programCourse.do',
                'FAWKC':'programCourse.do',
                'XGXK':'publicCourse.do',
                'CXKC':'programCourse.do',
                'TYKC':'programCourse.do',
                'QXKC':'queryCourse.do'
            }
            url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/'+do[mode]
            data = {
                'querySetting': '{"data":{"studentCode":' + StuID + ',"campus":"1","electiveBatchCode":"' + eBC + '","isMajor":"1","teachingClassType":"' + mode + '","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10000","pageNumber":"' + '0' + '","order":""}'
            }
            try:
                res = post(url, headers = headers, data = data).json()
                if mode != 'XGXK':
                    for course in res["dataList"]:
                        # print(str(course).replace(', ', ',\n'), end='\n\n')
                        this_course = dict()
                        this_course["courseNatureName"] = course["courseNatureName"]
                        this_course['courseName'] = course['courseName']
                        this_course['typeName'] = course['typeName']
                        this_course['hours'] = course['hours']
                        this_course['credit'] = course['credit']
                        # this_course['selected'] = course['selected']
                        this_course['type'] = mode
                        this_course['number'] = course['number']
                        for tclass in course["tcList"]:
                            this_class = dict()
                            this_class["isConflict"] = tclass["isConflict"]
                            this_class['teachingPlace'] = tclass['teachingPlace']
                            this_class['isChoose'] = tclass['isChoose']
                            this_class['teacherName'] = tclass['teacherName']
                            if mode in 'TYKC':
                                this_class['sportName'] = tclass['sportName']
                            this_class['teachingMethod'] = tclass['teachingMethod']
                            this_class['teachingClassID'] = tclass['teachingClassID']
                            this_course[int(tclass["courseIndex"])] = this_class
                        courses[course['courseNumber']] = this_course
                elif mode == 'XGXK': # 有覆盖问题，已解决
                    for course in res["dataList"]:
                        this_class = dict()
                        this_class["isConflict"] = course["isConflict"]
                        this_class['teachingPlace'] = course['teachingPlace']
                        # 还是有'isChoose'
                        this_class['isChoose'] = course['isChoose']                        
                        this_class['teacherName'] = course['teacherName']
                        # 有'teacherNameList'
                        this_class['teacherNameList'] = course['teacherNameList']
                        this_class['teachingMethod'] = course['teachingMethod']
                        #多出'campusName'
                        # this_class['campusName'] = course['campusName']
                        this_class['teachingClassID'] = course['teachingClassID']
                        if courses.get(course['courseNumber'], False) == False:
                            this_course = dict()
                            this_course['courseName'] = course['courseName']
                            # 没有'typeName'，有'publicCoursetypeName'
                            this_course['publicCourseTypeName'] = course['publicCourseTypeName']
                            this_course['hours'] = course['hours']
                            this_course['credit'] = course['credit']
                            this_course['type'] = mode
                            this_course['number'] = 1
                            
                            this_course[int(course["courseIndex"])] = this_class
                            courses[course['courseNumber']] = this_course
                        else:
                            this_course['number'] += 1
                            courses[course['courseNumber']][int(course["courseIndex"])] = this_class
                with open('/GrabLessons/Caches.data', 'wb') as f:
                    dump(eBC, f)
                    dump(courses, f)
                global a
                print(a[mode], '加载成功！')
            except Exception:
                print(print_exc())
                print('此类课程无法加载:', a[mode])
        print('加载完毕！\n')
        os.system('pause')
    # f.close()
    # print(courses)
    return courses

def search(courses):
    print('\n')
    ID = input('输入(exit为结束输入):')
    if ID == 'exit':
        return True, 0
    if ID == '':
        return False, 0
    ID = ID.replace('[', ' ').rstrip(']').strip()
    courseID = ID.split()[0]
    if len(ID.split()) == 2:
        classID = int(ID.split()[1])
        if courses.get(courseID, False) == False:
            print('课程编号错误，无此课程！\n')
            # 跳出此次循环，重新输入
            return False, 0
        else:
            if courses[courseID].get(classID,False) == False:
                print('班级编号错误，无此班级！\n')
                # 跳出此次循环，重新输入
                return False, 0
            else:
                print('查询成功：\n')
                course = courses[courseID]
                tclass = course[classID]
                show_course(courseID, course)
                print('')
                show_class(course, classID, tclass)
                c = input('是否加入抢课队列中？[是/否](直接回车为否):')
                if c == '是':
                    if tclass['isChoose'] == '1':
                        print('此班级:', classID, '已选，不加入')
                        return False, 0
                    elif tclass['isConflict'] == '1':
                        print('此班级:', classID, '已冲突，不加入')
                        return False, 0
                    return [(courses[courseID][classID]['teachingClassID'], courses[courseID]['type'])], courseID
                else:
                    # 跳出此次循环，重新输入
                    return False, 0
    else:
        if courses.get(courseID, False) == False:
            print('课程编号错误，无此课程！\n')
            # 跳出此次循环，重新输入
            return False, 0
        required_list = list()
        print('查询成功：\n')
        course = courses[courseID]
        show_course(courseID, course)
        print('')
        classID = 0
        i = 0
        while i < course['number']:
        # for i in range(1, courses[courseID]['number'] + 1):
            classID += 1
            if course.get(classID, False) == False:
                continue
            i += 1
            tclass = course[classID]
            if tclass['isChoose'] == '1':
                print('此班级:', classID, '已选，不加入')
                continue
            elif tclass['isConflict'] == '1':
                print('此班级:', classID, '已冲突，不加入')
                continue
            show_class(course, classID, tclass)
            required = (courses[courseID][classID]['teachingClassID'], courses[courseID]['type'])
            required_list.append(required)
        c = input('是否加入抢课队列中？[是/否](直接回车为否):')
        if c == '是':
            return required_list, courseID
        else:
            # 跳出此次循环，重新输入
            return False, 0

def show_course(courseID, course):
    global a
    # global form
    # global form1
    if course['type'] == 'XGXK':
        # form = "{0:<16}{1:{7}<16}{2:{7}<15}{3:{7}<7}{4:<12}{5:<11}{6:<}"
        form = "{0:<16}{1:{7}<16}{2:{7}<11}{4:<12}{5:<11}{6:<}"        
        print(form.format("number", "课程名称", "通识课类别", '课程性质', 'credit', 'hours', '所属栏', chr(12288)))
        print(form.format(courseID, course['courseName'], course['publicCourseTypeName'], 1, course['credit'], course['hours'], a[course['type']], chr(12288)))
    else:
        form = "{0:<16}{1:{7}<16}{2:{7}<15}{3:{7}<7}{4:<12}{5:<11}{6:<}"
        print(form.format("number", "课程名称", "课程类别", '课程性质', 'credit', 'hours', '所属栏', chr(12288)))
        # form = "{0:{7}<4}\t{1:{7}<7}\t{2:{7}<4}\t{3:{7}<4}\t{4:{7}<2}\t{5:{7}<2}\t{6:<}"
        print(form.format(courseID, course['courseName'], course['typeName'], course['courseNatureName'], course['credit'], course['hours'], a[course['type']], chr(12288)), '\n')

def show_class(course, classID, tclass):
    global a
    choosable = '可选'
    if tclass['isChoose'] == '1':
        choosable = '已选，不可选'
    elif tclass['isConflict'] == '1':
        choosable = '冲突，不可选'
    if course['type'] == 'XGXK':
        print(classID, choosable, tclass['teacherName'], tclass['teachingMethod'], tclass['teachingPlace'], sep='\t')
    elif course['type'] == 'TYKC':
        print(classID, choosable, tclass['sportName'],tclass['teacherName'], tclass['teachingMethod'], tclass['teachingPlace'], sep='\t')
    else:
        print(classID, choosable, tclass['teacherName'], tclass['teachingMethod'], tclass['teachingPlace'], sep='\t')


class myThread (Thread):
    def __init__(self, StuID, eBC, ID, ctype, flag, courseID, delay = 0.5):
        Thread.__init__(self)
        self.delay = delay
        self.StuID = StuID
        self.eBC = eBC
        self.ID = ID
        self.ctype = ctype
        self.flag = flag
        self.courseID = courseID
    def run(self):
        print ("\n开始抢课：" + self.ID)
        grabbing(self.StuID, self.eBC, self.ID, self.ctype, self.delay, self.flag, self.courseID)
        print ("\n结束抢课：" + self.ID)


def grabbing(StuID, eBC, ID, ctype, delay, flag, courseID):
    c = '想不到'
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do'
    param = {
        'addParam': '{"data":{"operationType":"1","studentCode":"' + StuID + '",'
                                                                                '"electiveBatchCode":"' + eBC + '","teachingClassId":' + ID +
                    ',"isMajor":"1","campus":"1","teachingClassType":"' + ctype + '"}} '
    }
    while True:
        try:
            if flag[courseID] != 1:
                print('\n无法选择本课程， 或本课程已有其他班级被选中，不再尝试此班级：', ID)
                break
            res = post(url, headers=headers, params=param).json()
            sleep(delay)
            if res['code'] == '1':
                if res['msg'] == '添加选课志愿成功':
                    flag[courseID] = 0
                    print('\n选课成功！，课程号：', ID)
                    break
                else:
                    if c == '想不到':
                        c = input('出现未知情况' + res['msg'] +',是否继续（且不再提示，反复尝试）？[是/否]（默认为否）')
                        if c == '是':
                            pass
                        else:
                            break
            elif res['code'] == '2':
                if res['msg'] == '该课程超过课容量':
                    pass
                elif res['msg'] == '该课程与已选课程时间冲突':
                    print('\n', res['msg'], '，无法选此班级！,班级号：', ID)
                    break
                else:
                    flag[courseID] = dict()
                    flag[courseID]['code'] = 2
                    flag[courseID]['reason'] = res['msg']
                    print('\n', res['msg'], '，无法选此课程！,课程号：', ID)
                    break
        except Exception:
            print('\n异常:')
            print(print_exc())
            print('\n线程出错了！请检查选课服务器状态、电脑运行环境。此课程号：', ID)
            if c == '想不到':
                c = input('是否继续（且不再提示，反复尝试）？[是/否]（默认为否）')
                if c == '是':
                    pass
                else:
                    break


if __name__ == '__main__':
    try:
        if os.path.exists('/GrabLessons') == False:
            os.mkdir('/GrabLessons')
        # form = "{0:{7}<4}\t{1:{7}<7}\t{2:{7}<4}\t{3:{7}<4}\t{4:{7}<2}\t{5:{7}<2}\t{6:<}"
        # form1 = "{0:{7}<4}{1:{7}<7}{2:{7}<4}{3:{7}<4}{4:{7}<2}{5:{7}<2}{6:<}"
        a = {'TJKC':'推荐课程', 'FANKC':'方案内跨年级课程', 'FAWKC':'方案外课程', 'XGXK':'基础通识类(核心/选修)', 'CXKC':'重修课程', 'TYKC':'主修课程(体育)'}
        StuID, headers, eBC = login()
        # grabbing(StuID, eBC, '201920202COMP55040501', "FAWKC", 0.2)
        courses = download(StuID, headers, eBC)
        print('\n请输入需要抢的课程编号、班级编号，允许的格式:\nCORE100101[01]\nCORE100101 01(不要忘记01的0)\nCORE100101(如果不输入班级编号，则在此课程下随机选择一个班级)\n若输入exit，则结束添加待选课程\n')
        sleep(3)
        grab_list = list()
        flag = dict()
        while True:
            required_list, courseID = search(courses)
            if required_list == True:
                break
            elif required_list == False:
                continue
            flag[courseID] = 1
            for i in range(len(required_list)):
                grab_list.append((required_list[i][0], required_list[i][1], courseID))
        print('\n在出现结束提示，允许关闭程序前不要关闭程序！')
        print('\n请尽可能在开始一段时间内保持注意，以应对特殊情况，过程中请保持网络通畅')
        d = input('\n请输入尝试周期（单位：秒，默认：0.5）：')
        if d == '':
            d = 0.5
        else:
            d = float(d)
        input('按回车开始抢课')
        print('以下是抢课实时情况：\n')
        thread_list = list()
        for i in range(len(grab_list)):
            thread = myThread(StuID, eBC, grab_list[i][0], grab_list[i][1], flag, grab_list[i][2], d)
            thread_list.append(thread)
            thread.start()
            sleep(0.1)
        for thread in thread_list:
            thread.join()

        print('\n\n选课结果：')
        for courseID in list(flag.keys()):
            name = courses[courseID]['courseName']
            if flag[courseID] == 0:
                print(name, '：选课成功')
            elif flag[courseID]['code'] == 2:
                print(name, '：选课失败,原因：', flag[courseID]['reason'])
            else:
                print(name, '：选课失败')
        print('\n')
        input('所有抢课任务都已结束，去网页抢课端看看吧！您现在可以安全地关闭程序，回车退出')
    except Exception:
        print(print_exc())
        os.system('pause')
# 现有问题：会把英语自习所有能选的班都选一遍，导致其他课程冲突        已解决