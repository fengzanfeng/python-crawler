#-*- encoding: utf8 -*-
import sys
import shutil
import urllib2,gzip,os,time,re
from StringIO import StringIO
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8') #@UndefinedVariable

def openUrl(url):
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
        return data

def get_category_page():
    # 抓分类页面
    failTag = 'no-result-box'
    f = open('./brand.txt')
    content = f.read()
    f.close()
    brandList = content.split('\n')
    for brand in brandList:
        if not brand:
            continue
        brandUrl, brandName = brand.split('^')
        print "brand name: %s, brand url: %s" % (brandName, brandUrl)
        path = './data/' + brandName + '/'
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        page = openUrl(brandUrl + '1.html')
        print "fetching " + brandUrl + '1.html'
        i = 1
        while failTag not in page:
            filePath = path + str(i)
            f = open(filePath, 'w')
            f.write(unicode(page, 'gbk'))
            f.close
            i += 1
            time.sleep(5)
            # 抓取分页: brandUrl + {page} + ".html"
            page = openUrl(brandUrl + str(i) + '.html')
            print "fetching " + brandUrl + str(i) + '.html'
        print brandName + ' finished'

def get_detail_page():
    # 抓参数页
    dirList = os.listdir('./data')
    for directory in dirList:
        path = './data/' + directory
        pageList = os.listdir(path)
        for page in pageList:
            detailPath = './data/' + directory + '/detail_page/'
            if os.path.exists(detailPath):
                shutil.rmtree(detailPath)
            os.makedirs(detailPath)
            pagePath = './data/' + directory + '/' + page
            print pagePath
            content = open(pagePath).read()
            paramList = re.findall('/\d+/\d+/param.shtml',content)
            for param in paramList:
                detail = openUrl('http://detail.zol.com.cn' + param)
                detail = unicode(detail, 'gbk')
                title = re.search('<h1 class="ptitle">(.*)</h1>',detail).group(1)
                title = title.replace('/','-')
                print 'fetching ' + param + ' - ' + title
                fullPath = detailPath + title
                print fullPath
                f = open(fullPath, 'w')
                f.write(detail)
                f.close()

def get_dom_objectid_text(htmlContent, objectid):
    return BeautifulSoup(htmlContent).find(id=objectid).get_text()

def detail_parser():
    # 处理数据
    brandList = os.listdir('./data')
    for brand in brandList:
        print "parser brand: %s" % brand
        brandDir = './data/' + brand + "/detail_page/"
        resultDir = './data/' + brand + "/result/"
        if os.path.exists(resultDir):
            shutil.rmtree(resultDir)
        os.makedirs(resultDir)
        phoneList = os.listdir(brandDir)
        for phone in phoneList:
            print "parser phone: %s" % phone
            phoneFile = brandDir + '/' + phone
            content = open(phoneFile).read()
            text = get_dom_objectid_text(content, "newTb")
            issue_date = get_dom_objectid_text(content, "newPmVal_1")
            screen_size = get_dom_objectid_text(content, "newPmVal_4")
            screen_resolution = get_dom_objectid_text(content, "newPmVal_7")
            android_version = get_dom_objectid_text(content, "newPmVal_14")
            cpu_mhz = get_dom_objectid_text(content, "newPmVal_15")
            memory = get_dom_objectid_text(content, "newPmVal_16")
            print "issue date: %s, screen_size: %s, screen_resolution: %s, android_version: %s, cpu_mhz: %s, memory: %s" % (issue_date, screen_size, screen_resolution, android_version, cpu_mhz, memory)
            resultPath = resultDir + phone
            f = open(resultPath, 'w')
            f.write(text)
            f.close()

get_category_page()
get_detail_page()
detail_parser()
