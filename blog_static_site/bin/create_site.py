#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
from htmltmpl import TemplateManager, TemplateProcessor
import subprocess
from operator import itemgetter
import random
import shutil
import pickle
import time
# 定义变量 
base_dir,cur_dir = os.path.split(os.path.abspath(os.path.dirname(sys.argv[0])))
txt_source = "%s/t2t_document" % base_dir
out_html_dir = "%s/web_root" % base_dir
category_html_template = "%s/template/list.html" % base_dir
index_html_template = "%s/template/index.html" % base_dir
guestbook_html_template = "%s/template/guestbook.html" % base_dir
article_html_template = "%s/template/article.html" % base_dir
rss_xml_template = "%s/template/rss.html" % base_dir
cache_db = "%s/bin/cache_db" % base_dir

# 定义文章分类(根据目录结构来定)
site_category = { 'system_install' : '系统安装',
                  'system_manage' : '系统管理',
                  'system_monitor' : '系统监控',
                  'system_performance' : '性能调优',
                  'system_security' : '系统安全',
                  'system_base' : '系统基础', 
                  'system_other' : '网海拾贝' 
                 }

# 将文章分类
article_category = {}	# 文章分类
article_href = {}	# 文章链接
article_path = {}	# 文章相对引用路径
article_title = {}	# 文章标题
article_keyword = {}	# 文章关键字
article_lastmodify = {}	# 文章最新更新时间
article_uuid = {}	# 文章唯一序列 uuidgen生成

# 读取cache文章修改时间
cache_dict = {}
if os.path.isfile(cache_db):
    fin = open(cache_db, "r")
    cache_dict = pickle.load(fin)
    fin.close()

# 遍历子目录
fileList = []
rootdir = txt_source
for root, subFolders, files in os.walk(rootdir):
    if '.svn' in subFolders: subFolders.remove('.svn')  # don't visit CVS directories
    if 'incomplete' in subFolders: subFolders.remove('incomplete')  # don't visit CVS directories
    for file in files:
        if file.find(".t2t") != -1: 
            file_dir_path = os.path.join(root,file)
            fileList.append(file_dir_path)


for file in fileList:
    for key, val in site_category.items():
        if file.find(key) != -1 : 
            article_category[file] = key
            root,path =  file.split(key)
            path.strip()
            article_path[file] = path
            strinfo = re.compile('t2t$')
            article_href[file] =  strinfo.sub('html',path)

# 生成文档的title和最新更新时间列表
for file_path,category in article_category.items():
    fd = open(file_path)
    fd.seek(0)
    title = fd.readline()
    keyword = fd.readline()
    uuid = fd.readline()
    fd.close()
    article_title[file_path] = title
    article_keyword[file_path] = keyword
    article_uuid[file_path] = uuid
    article_lastmodify[file_path] = "%d" % os.stat(file_path).st_mtime

#============ 生成首页 =============#
template = TemplateManager().prepare(index_html_template)
tproc = TemplateProcessor(html_escape=0)

# Create the 'Menuitem' loop.
Menuitems = []
for category,cn_name in site_category.items():
    if category in article_category.values():
        menuitem = {}
        menuitem["menu_href"] = "/%s/index.html" % (category)
        menuitem["menu_name"] = cn_name
        Menuitems.append(menuitem)


# 首页显示最新的一篇文章内容
index_article = []
# create new article list
Newarticles = []
article_lastmodify_sort = sorted(article_lastmodify.items(), key=itemgetter(1),reverse=True)
new_count = 1
for file_path,mtime in article_lastmodify_sort:
#    print "%s = %s" % (file_path,mtime)
    if new_count == 11: break
    newarticle = {}
    newarticle["article_href"] = "/%s%s" % (article_category[file_path],article_href[file_path].strip())
    newarticle["article_name"] = article_title[file_path].strip()
    Newarticles.append(newarticle)
    if not index_article: index_article.append(file_path)
    new_count = new_count + 1

#print index_article
# Create the 'article_content'
#cmd = "txt2tags --no-toc --no-headers -o - %s/site_update.t2t" % (txt_source)
index_article_path = index_article.pop()
#url = "/%s%s" % (article_category[index_article_path],article_href[index_article_path].strip())
cmd = "txt2tags --mask-email --no-toc --no-headers -o - %s" % (index_article_path)
res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
#article_content = res.stdout.readlines()
article_content = []
article_line = res.stdout.readlines()

# 替换首页文章的图片目录
# <IMG ALIGN="middle" SRC="cdn_overview.gif" BORDER="0" ALT="">
article_dir,article_filename = os.path.split(article_path[index_article_path])
img_dir = "/%s%s" % (article_category[index_article_path],article_dir)
for line in article_line:
    #print line
    mo = re.compile(r'<IMG.*SRC="(.*)" BORDER="0".*>',re.I).search(line)
    if mo:
        img_src = mo.group(1)
        new_img_src = "%s/%s" % (img_dir,img_src)
        myrep = line.replace(img_src,new_img_src)
        article_content.append(myrep)
    else:
        article_content.append(line)
# template replace 
tproc.set("title",article_title[index_article_path].strip())
#tproc.set("url",url)
tproc.set("article_content","".join(article_content))
tproc.set("Menuitem", Menuitems)
tproc.set("Newarticle",Newarticles)
# set update time and uuid
#mo = re.compile(r'(\w+)-(\w+)-(\w+)-(\w+)-(\w+)',re.I)
#uuid = article_uuid[index_article_path].strip()
#if mo.match(uuid):
#    tproc.set("uuid",uuid)
#else:
#    print "UUID Not Match,please check"
#    sys.exit()

updatetime = float(article_lastmodify[index_article_path].strip())
updatetime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(updatetime))
tproc.set("updatetime",updatetime)

# save to file
filename = "%s/index.html" % (out_html_dir)
FILE = open(filename,"w")
FILE.writelines(tproc.process(template))
FILE.close()

#========== guestbook 留言板 ===============================#

template = TemplateManager().prepare(guestbook_html_template)
tproc = TemplateProcessor(html_escape=0)

# template replace 
tproc.set("Menuitem", Menuitems)

# save to file
filename = "%s/guestbook.html" % (out_html_dir)
FILE = open(filename,"w")
FILE.writelines(tproc.process(template))
FILE.close()

#========== 生成每个分类的index.html页面 ====================#
template = TemplateManager().prepare(category_html_template)
tproc = TemplateProcessor(html_escape=0)


# 分类列表页面生成
category_list = [x for x in site_category.keys() if x in article_category.values()]
for current_category in category_list:
    # Create the 'Menuitem' loop.
    Menuitems = []
    for category in category_list:
        cn_name = site_category[category]
        menuitem = {}
        menuitem["menu_href"] = "/%s/index.html" % (category)
        menuitem["menu_name"] = cn_name
        if category == current_category: menuitem["menu_class"] = "webgen-menu-item-selected"
        Menuitems.append(menuitem)

    # 每个分类显示随机文章列表
    Randomarticles = []
    random_list = random.sample(article_title.keys(),10)
    for file_path in random_list:
        newarticle = {}
        newarticle["article_href"] = "/%s%s" % (article_category[file_path],article_href[file_path].strip())
        newarticle["article_name"] = article_title[file_path].strip()
        Randomarticles.append(newarticle)

    # 本分类中的文章列表
    article_lists = []
    for file_path,title in article_title.items():
        if article_category[file_path] != current_category : continue
        article = {}
        article["list_href"] = "/%s%s" % (article_category[file_path],article_href[file_path].strip())
        article["list_name"] = article_title[file_path].strip()
        article_lists.append(article)
    
    # template replace 
    tproc.set("title",site_category[current_category])
    tproc.set("Menuitem", Menuitems)
    tproc.set("Randomarticles",Randomarticles)
    tproc.set("Article_list",article_lists)
    
    # save to file
    file_dir = "%s/%s" % (out_html_dir,current_category)
    if not os.path.exists(file_dir): os.makedirs(file_dir)
    filename = "%s/index.html" % (file_dir)
    FILE = open(filename,"w")
    FILE.writelines(tproc.process(template))
    FILE.close()

#========== 生成文章页面(Cache功能)====================#
template = TemplateManager().prepare(article_html_template)
tproc = TemplateProcessor(html_escape=0)

category_list = [x for x in site_category.keys() if x in article_category.values()]
article_lastmodify_sort = sorted(article_lastmodify.items(), key=itemgetter(1),reverse=True)
rss_items = []
#for file_path,title in article_title.items():
for file_path,mtime in article_lastmodify_sort:
    # 判断文章的最后修改时间 
    title = article_title[file_path]
    url = "/%s%s" % (article_category[file_path],article_href[file_path].strip())
    # 生成 rss item
    if len(rss_items) < 10:
        rss_item = {}
        rss_item['title'] = title.strip()
        rss_item['link'] = url
        #rss_item['content'] = ""
        rss_items.append(rss_item)
    if cache_dict.has_key(file_path) and cache_dict[file_path] == article_lastmodify[file_path]:
        continue 
    else:
        cache_dict[file_path] = article_lastmodify[file_path]
   
    print "file_path = %s" % file_path
    print "tilte = %s" % title.strip()
    print "keyword = %s" % article_keyword[file_path].strip()
    print "UUID = %s" % article_uuid[file_path].strip()
    print "URL = %s" % (url)
    print "=" * 100
    # Create the 'Menuitem' loop.
    Menuitems = []
    for category in category_list:
        cn_name = site_category[category]
        menuitem = {}
        menuitem["menu_href"] = "/%s/index.html" % (category)
        menuitem["menu_name"] = cn_name
        if category == article_category[file_path]: menuitem["menu_class"] = "webgen-menu-item-selected"
        Menuitems.append(menuitem)

    # 显示随机文章列表
    Randomarticles = []
    random_list = random.sample(article_title.keys(),10)
    for key in random_list:
        newarticle = {}
        newarticle["article_href"] = "/%s%s" % (article_category[key],article_href[key].strip())
        newarticle["article_name"] = article_title[key].strip()
        Randomarticles.append(newarticle)
    
    # 文章章节
    sections = []
    cmd = "txt2tags --toc-only --toc-level=1 %s" % (file_path)
    res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
    cmd_exec_out = res.stdout.readlines()
    for li_href in cmd_exec_out:
        mo = re.compile(r'<a href="(.*?)">(.*?)</a>',re.I).search(li_href)
        if mo:
            section_href = mo.group(1)
            section_name = mo.group(2)
            section = {}
            section["section_href"] = section_href
            section["section_name"] = section_name
            sections.append(section)

    # Create the 'article_content'
    cmd = "txt2tags --mask-email --toc-level=1 --no-headers -o - %s" % (file_path)
    res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
    article_content = res.stdout.readlines()
    nav = False
    only_one = True
    article_content_list = []
    for line in article_content:
        if only_one:
            if line.find("<OL>") != -1: 
                nav = True
                continue
            elif line.find("</OL>") != -1:    
                nav = False
                only_one = False
                continue
            if nav: continue
        # 替换图片属性
        mo = re.compile(r'<IMG.*SRC="(.*)" BORDER="0"(.*)>',re.I).search(line)
        if mo:
            img_src = mo.group(1)
            img_replace = mo.group(2)
            img_class = ' ALT="%s" class="magnify" data-magnifyby="1.45"' % (img_src)
            myrep = line.replace(img_replace,img_class)
            article_content_list.append(myrep)
        else:
            article_content_list.append(line)

    # template replace 
    tproc.set("title",article_title[file_path].strip())
    tproc.set("keyword",article_keyword[file_path].strip())
    tproc.set("url",url)

    tproc.set("article_content","".join(article_content_list))
    tproc.set("Menuitem", Menuitems)
    tproc.set("Randomarticles",Randomarticles)
    tproc.set("Section",sections)
    # set update time and uuid
    #mo = re.compile(r'[a-zA-Z0-9]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+',re.I)
    uuid = article_uuid[file_path].strip()
    if re.match(r'^[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+$',uuid):
        tproc.set("uuid",uuid)
    else:
        print "UUID Not Match,please check"
        sys.exit()
    
    updatetime = float(article_lastmodify[index_article_path].strip())
    updatetime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(updatetime))
    tproc.set("updatetime",updatetime)

    
    # save to file
    #print "file_path = %s" % file_path
    #print "article href = %s" % article_href[file_path].strip()
    article_dir,article_filename = os.path.split(article_href[file_path].strip())
    #print "article_dir = %s dirpath = %s" % (article_dir,article_href[file_path].strip())
    #print "=" * 50
    #print "article_dir = %s" % article_dir
    file_dir = "%s/%s%s" % (out_html_dir,article_category[file_path],article_dir)
    if not os.path.exists(file_dir): os.makedirs(file_dir)
    
    # 拷贝文章引用的文件(图片或者下载文件等)
    if not re.match('/$',article_dir):
        src_dir = "%s/%s%s" % (txt_source,article_category[file_path],article_dir)
        copy_file_list = [x for x in os.listdir(src_dir) if not re.compile(r'.dia$|.t2t$|.svn$',re.I).search(x)]
        for copy_file in copy_file_list:
            dest_file = "%s/%s" % (file_dir,copy_file) 
            if not os.path.isfile(dest_file):
                src_copy_file = "%s/%s" % (src_dir,copy_file)
                shutil.copyfile(src_copy_file,dest_file)

    filename = "%s/%s" % (file_dir,article_filename)
    FILE = open(filename,"w")
    FILE.writelines(tproc.process(template))
    FILE.close()

# ======= 生成rss xml文件 =========

template = TemplateManager().prepare(rss_xml_template)
tproc = TemplateProcessor()
# template replace 
tproc.set("Rss",rss_items)
# save to file
filename = "%s/rss.xml" % (out_html_dir)
FILE = open(filename,"w")
FILE.writelines(tproc.process(template))
FILE.close()


# ===== 持久化dict,用来cache文章修改时间 ========
fout = open(cache_db, "w")
pickle.dump(cache_dict, fout, protocol=0)
fout.close()
