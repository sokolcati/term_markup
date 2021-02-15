# -*- coding: utf-8 -*-
import os
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import requests
from bs4 import BeautifulSoup

# set max amount of files (compare with af)
# -1 equal infinity
max_files = -1

# Open and clean tex doc
def next_tex_doc(address):
    doc = "" # returning value, string
    texdoc = []  # a list of string representing the latex document in python
    # read the .tex file, and modify the lines
    with open(address, 'UTF-8') as texdoc:
        for line in texdoc:
            l = unicode(line, 'utf-8')
            if l.find('%') != 0:
                if len(l) > 0:
                    #l = l.lower().replace("~---", "")
                    #don't want to change amount of characters
                    l = l.replace(".~", ". ")
                    l = l.replace("{", ' ').replace("}", ' ')
                    l = l.replace("(", ' ').replace(")", ' ')
                    l = l.replace("[", ' ').replace("]", ' ')
                    l = l.replace("<", ' ').replace(">", ' ')
                    l = l.replace(".", ' ')
                    l = l.replace(",", ' ')
                    l = l.replace("!", ' ')
                    l = l.replace("?", ' ')
                    l = l.replace(";", ' ').replace(":", ' ')
                    doc = doc + l.replace("\n", " ")
    doc = doc + ' '
    return doc

# Print results for one term into out_file
def print_item(item, start, end, text):
    out_file.write('\t<item>\n')
    out_file.write('\t\t<term>' + item[2].encode('utf-8') + '</term>\n')
    out_file.write('\t\t<link>http://libmeta.ru/concept/show/' + item[1] + '</link>\n')
    out_file.write('\t\t<link>http://libmeta.ru/concept/' + item[1] + '</link>\n')
    out_file.write('\t\t<startpos>' + str(start) + '</startpos>\n')
    out_file.write('\t\t<endpos>' + str(end - 1) + '</endpos>\n')
    out_file.write('\t\t<linktext>' + text.encode('utf-8') + '<linktext>\n')
    out_file.write('\t</item>\n')

# Chech char after last '(' in string
def x_pos(st):
    c = st.count(')')
    f = st.find('(')
    while c > 1:
        f = f + st[f + 1 :].find('(') + 1
        c = c - 1
    return f

# add dublicate strings with offset
def round_double(term, num, orig_term):
    term = nitem = morph.parse(term)[0]
    nitem = term.normal_form
    c = nitem.count(" ")
    if c == 0:
        norm_library.append([nitem, num, orig_term])
    else:
        n_lst = nitem.split()
        nitem = ""
        for word in n_lst:
            w = morph.parse(word)[0]
            nitem = nitem + ' ' + w.normal_form
        nitem = nitem[1:]
        norm_library.append([nitem, num, orig_term])
    while c > 0:
        d = nitem.find(" ")
        nitem = nitem[d+1:] + ' ' + nitem[:d]
        norm_library.append([nitem, num, orig_term])
        c = c - 1

# MAIN

# Open out_file
out_file = open('out.txt', 'w')

# Processing of dictionaries
# libmeta.txt
libmeta = []  # a list of string representing the libmeta.txt
norm_library = [] # list of keywords in normal form
                  # with different word order for multi-word terms
                  # order by amount of words
with open('libmeta.txt', 'UTF-8') as libmeta:
    line_type = 0
    for line in libmeta:
        if line_type == 1: # this string contain link with 'show'
            line_type = 0
            link_num = line[41:-12]
            nitem = nitem.normal_form
            c = nitem.count(" ")
            if c == 0:
                norm_library.append([nitem, link_num, item])
            else:
                n_lst = nitem.split()
                nitem = ""
                for word in n_lst:
                    w = morph.parse(word)[0]
                    nitem = nitem + ' ' + w.normal_form
                nitem = nitem[1:]
                norm_library.append([nitem, link_num, item])
            while c > 0:
                d = nitem.find(" ")
                nitem = nitem[d+1:] + ' ' + nitem[:d]
                norm_library.append([nitem, link_num, item])
                c = c - 1
        elif (line.find("<lbm:Concept rdf:about") == 0) and (line[-2] == '>'):
            line_type = 1 # this string contain term
            y = line.find("#")
            keyword = unicode(line[y+1:-3], 'utf-8')
            if len(keyword) > 0:
                item = keyword.replace("_", " ").replace(" - ", "-").lower()
                nitem = morph.parse(item)[0]

# diffthes.txt
library = [] # structure like in libmeta case, but codes instead of terms
useless = 1
with open('diffthes.txt', 'UTF-8') as libmeta:
    line_type = 0
    for line in libmeta:
        if line.find('<lbm:ConceptGroup rdf:about="http://libmeta.ru/thesaurus/group/add"> </lbm:ConceptGroup>') > -1:
            useless = 0
        if line_type == 1: # this string contain link with 'show'
            line_type = 0
            link_num = line[41:-12]
            library.append([item, link_num, item])
        elif (line.find("<lbm:Concept rdf:about") == 0) and (line[-2] == '>') and (useless == 0):
            line_type = 1 # this string contain term
            term_code = line[60:-3]
            item = unicode(line[60:-3], 'utf-8')
# replace codes with terms
for nitem in library:
    url = 'http://libmeta.ru/concept/' + nitem[1]
    web_page = requests.get(url)
    ryy = web_page.text
    ryy.replace('\n', ' ')
    start_desc = ryy.find('<lbm:descriptor><') + 25
    end_desc = ryy.find('></lbm:descriptor>') - 2
    nitem[0] = ryy[start_desc : end_desc].replace("_", " ").replace(',', ' ').lower()
    nitem[0] = nitem[0].replace('&laquo;', '«'.decode('utf-8')).replace('&raquo;', '»'.decode('utf-8'))
    nitem[0] = nitem[0].replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<').replace('&#39;', '\'')
# Processing is specific for this thesaurus
# Need checking for in case of addition new terms 
dop_lib = []
for item in library:
    a1 = not (item[0].find('первого'.decode('utf-8')) == -1)
    a2 = not (item[0].find('второго'.decode('utf-8')) == -1)
    a3 = not (item[0].find('двух'.decode('utf-8')) == -1)
    a4 = not (item[0].find('ОДУ'.decode('utf-8')) == -1)
    a5 = not (item[0].find('.') == -1)
    a6 = not (item[0].find('(') == -1)
    a7 = not (item[0].find(' - ') == -1)
    a8 = not (item[0].find('&') == -1)
    a_neg = a5 or a6 or a7 or a8
    a_pos = a1 or a2 or a3 or a4
    if a_pos:
        if a4:
            if a1 and a2:
                # without combination num and string value
                dop_lib.append([item[0].replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')).replace('второго'.decode('utf-8'), '2-го'.decode('utf-8')), item[1], item[2]])
                dop_lib.append([item[0].replace('ОДУ'.decode('utf-8'), 'обыкновенное дифференциальное уравнение'.decode('utf-8')), item[1], item[2]])
                dop_lib.append([item[0].replace('ОДУ'.decode('utf-8'), 'обыкновенное дифференциальное уравнение'.decode('utf-8')).replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')).replace('второго'.decode('utf-8'), '2-го'.decode('utf-8')), item[1], item[2]])
            elif a1:
                dop_lib.append([item[0].replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')), item[1], item[2]])
                dop_lib.append([item[0].replace('ОДУ'.decode('utf-8'), 'обыкновенное дифференциальное уравнение'.decode('utf-8')), item[1], item[2]])
                dop_lib.append([item[0].replace('ОДУ'.decode('utf-8'), 'обыкновенное дифференциальное уравнение'.decode('utf-8')).replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')), item[1], item[2]])
            elif a2:
                dop_lib.append([item[0].replace('второго'.decode('utf-8'), '2-го'.decode('utf-8')), item[1], item[2]])
                dop_lib.append([item[0].replace('ОДУ'.decode('utf-8'), 'обыкновенное дифференциальное уравнение'.decode('utf-8')), item[1], item[2]])
                dop_lib.append([item[0].replace('ОДУ'.decode('utf-8'), 'обыкновенное дифференциальное уравнение'.decode('utf-8')).replace('второго'.decode('utf-8'), '2-го'.decode('utf-8')), item[1], item[2]])
            elif a3:
                dop_lib.append([item[0].replace('двух'.decode('utf-8'), '2-х'.decode('utf-8')), item[1], item[2]])
                dop_lib.append([item[0].replace('ОДУ'.decode('utf-8'), 'обыкновенное дифференциальное уравнение'.decode('utf-8')), item[1], item[2]])
                dop_lib.append([item[0].replace('ОДУ'.decode('utf-8'), 'обыкновенное дифференциальное уравнение'.decode('utf-8')).replace('двух'.decode('utf-8'), '2-х'.decode('utf-8')), item[1], item[2]])
        elif a3:
            dop_lib.append([item[0].replace('двух'.decode('utf-8'), '2-х'.decode('utf-8')), item[1], item[2]])
        elif a1 and a2:
            # without combination num and string value
            dop_lib.append([item[0].replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')).replace('второго'.decode('utf-8'), '2-го'.decode('utf-8')), item[1], item[2]])
        elif a1:
            dop_lib.append([item[0].replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')), item[1], item[2]])
        elif a2:
            dop_lib.append([item[0].replace('второго'.decode('utf-8'), '2-го'.decode('utf-8')), item[1], item[2]])
library = library + dop_lib
dop_lib = []
for item in library:
    a5 = not (item[0].find('.') == -1)
    a6 = not (item[0].find('(') == -1)
    a7 = not (item[0].find(' - ') == -1)
    a8 = not (item[0].find('&') == -1)
    a_neg = a5 or a6 or a7 or a8
    if a_neg:
        if item[0][-1] == ')':
            item[0] = item[0][: item[0].find('(') - 1]
        if (item[0].find(' - ') > -1):
            item[0] = item[0][item[0].find(' - ') + 3 :]
        if a5:
            i = item[0].find('.')
            j = item[0][i + 1 :].find('.') + i + 1
            k = item[0][j + 2 :].find(' ') + j
            if j - i == 3:
                if i > 1:
                    if k == -1:
                        dop_lib.append([item[0][: i - 1] + item[0][j + 2 :] + item[0][i - 2 : j + 1], item[1], item[2]])
                    else:
                        dop_lib.append([item[0][: i - 1] + item[0][j + 2 : k + 2] + item[0][i - 2 : j + 1] + item[0][k + 2 :], item[1], item[2]])
                else:
                    dop_lib.append([item[0][6 : k + 3] + item[0][: 5] + item[0][k + 2 :], item[1], item[2]])
            else:
                i = item[0].find('ф. хартмана'.decode('utf-8'))
                if (i > -1):
                    if i > 0:
                        dop_lib.append([item[0][: i] + 'хартмана ф.'.decode('utf-8') + item[0][i + 11 :], item[1], item[2]])
                    else:
                        dop_lib.append(['хартмана ф.'.decode('utf-8') + item[0][11:], item[1], item[2]])
                else:
                    dop_lib.append([item[0][i + 2:], item[1], item[2]])
                    item[0] = item[0][: i]
        i = item[0].find(')')
        if (i > -1) and (len(item[0]) - i > 3):
            f = x_pos(item[0])
            if item[0][f + 1] != 'x':
                dop_lib.append([item[0][: f - 1] + item[0][i + 1 :], item[1], item[2]])
                dop_lib.append([item[0][f + 1 :].replace(')', ''), item[1], item[2]])
library = library + dop_lib
# create normal forms and add to norm_library
for item in library:
    round_double(item[0], item[1], item[2])

# specfunc.txt
library = [] 
useless = 1
with open('specfunc.txt', 'UTF-8') as libmeta:
    line_type = 0
    for line in libmeta:
        if line.find('<lbm:ConceptGroup rdf:about="http://libmeta.ru/thesaurus/group/specmain"> </lbm:ConceptGroup>') > -1:
            useless = 0
        if line_type == 1: # this string contain link with 'show'
            line_type = 0
            link_num = line[41:-12]
            library.append([item, link_num, item])
        elif (line.find("<lbm:Concept rdf:about") == 0) and (line[-2] == '>') and (useless == 0):
            line_type = 1 # this string contain term
            term_code = line[60:-3]
            item = unicode(line[60:-3], 'utf-8')
# get terms instead of codes by url
for nitem in library:
    url = 'http://libmeta.ru/concept/' + nitem[1]
    web_page = requests.get(url)
    ryy = web_page.text
    ryy.replace('\n', ' ')
    start_desc = ryy.find('<lbm:descriptor><') + 25
    end_desc = ryy.find('></lbm:descriptor>') - 2
    #print type(end_desc)
    #print ryy[start_desc, end_desc]
    nitem[0] = ryy[start_desc : end_desc].replace("_", " ").replace(',', ' ').lower()
    nitem[0] = nitem[0].replace('&laquo;', '«'.decode('utf-8')).replace('&raquo;', '»'.decode('utf-8'))
    nitem[0] = nitem[0].replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<').replace('&#39;', '\'')
# Process thesaurus
dop_lib = []
for item in library:
    a1 = not (item[0].find('первого'.decode('utf-8')) == -1)
    a2 = not (item[0].find('второго'.decode('utf-8')) == -1)
    a3 = not (item[0].find('двух'.decode('utf-8')) == -1)
    a4 = not (item[0].find('третьего'.decode('utf-8')) == -1)
    a_pos = a1 or a2 or a3 or a4
    if a_pos:
        if a3:
            dop_lib.append([item[0].replace('двух'.decode('utf-8'), '2-х'.decode('utf-8')), item[1], item[2]])
        elif a1 and a2 and a4:
            # without combination num and string value
            st = item[0].replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')).replace('второго'.decode('utf-8'), '2-го'.decode('utf-8'))
            dop_lib.append([st.replace('третьего'.decode('utf-8'), '3-го'.decode('utf-8')), item[1], item[2]])
        elif a1 and a2:
            # without combination num and string value
            dop_lib.append([item[0].replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')).replace('второго'.decode('utf-8'), '2-го'.decode('utf-8')), item[1], item[2]])
        elif a1:
            dop_lib.append([item[0].replace('первого'.decode('utf-8'), '1-го'.decode('utf-8')), item[1], item[2]])
        elif a2:
            dop_lib.append([item[0].replace('второго'.decode('utf-8'), '2-го'.decode('utf-8')), item[1], item[2]])
        elif a4:
            dop_lib.append([item[0].replace('третьего'.decode('utf-8'), '3-го'.decode('utf-8')), item[1], item[2]])
library = library + dop_lib
for item in library:
    a5 = item[0].find(')'.decode('utf-8'))
    if (a5 > -1) and (len(item[0]) - a5 > 5):
        #print item[0][a5 - 3 : a5 + 3]
        if (item[0][a5 - 1] != 'z'):
            a6 = item[0].find('('.decode('utf-8'))
            dop_lib.append([item[0][: a6] + item[0][a5 + 2 :], item[1], item[2]])
            dop_lib.append([item[0][a6 + 1 : a5] + item[0][a5 + 1 :], item[1], item[2]])
library = library + dop_lib

norm_library.sort(key=lambda x: 0 - x[0].count(" "))

# Open files by rotation
out_file.write('<?xml version="1.0" encoding="utf-8"?>\n')
af = 0
tree = os.walk('all_TEX') # create tree of processed file names
for text in tree:
    for j in text[2]: # iteration over processed files
        af = af + 1
        # text[0] == 'all_TEX' == name of processed folder
        # j == name of processed file
        out_file.write('<file name:"' + text[0] + '/' + j + '">\n')
        doc = next_tex_doc(text[0] + '/' + j)
        num = 0
        lst = doc.encode('utf-8').split() # list of words from doc
        lst_num = [] # contain position for words from lst
        norm_lst = [] # future list of words from doc in normal form
        norm_lst_num = [] # contain position for words from norm_lst
        for word in lst: # create norm_lst and norm_lst_num
            w = morph.parse(word.decode('utf-8'))[0]
            norm_lst.append(w.normal_form)
            norm_lst_num.append(num)
            num = num + len(w.normal_form) + 1
        norm_doc = " ".join(norm_lst)
        num = -1
        check = [] # list which store scope of link text
                   # is used for checking conflicts
                   # like link 'word_1' into link 'word_1 word_2'
        for item in lst: # create lst_num
            num = num + 1 + doc[num + 1 :].find(item.decode('utf-8'))
            lst_num.append(num)
        #print lst_num
        #print norm_lst_num
        for item in norm_library:
            num = norm_doc.find(' ' + item[0] + ' ')
            last_num = -2
            a = 0
            while num > -1:
                #print 'NUM ' + str(num)
                if num == last_num:
                    break
                a = norm_lst_num.index(num + 1)
                #print 'A ' + str(a)
                nwords = item[0].count(" ") + 1
                end_link = lst_num[a + 1] - 1
                i = 0
                while nwords > 0:
                    end_link = lst_num[a + i + 1]
                    nwords = nwords - 1
                    i = i + 1
                while doc[lst_num[a] : end_link].count(" ") > item[0].count(" "):
                    end_link = end_link - 1
                if end_link < lst_num[a]:
                    end_link = lst_num[a]
                while doc[end_link] != ' ':
                    end_link = end_link + 1
                if not check:
                    check.append([lst_num[a], end_link])
                    print_item(item, lst_num[a], end_link, doc[lst_num[a]:end_link])
                    #print str(lst_num[a]) + ' till ' + str(end_link)
                t = 1
                for ch in check:
                    if lst_num[a] >= ch[0] and end_link <= ch[1]:
                        t = 0
                if t:
                    check.append([lst_num[a], end_link])
                    print_item(item, lst_num[a], end_link, doc[lst_num[a]:end_link])
                    #print str(lst_num[a]) + ' till ' + str(end_link)
                last_num = num
                num = num + 1 + norm_doc[num + 1:].find(' ' + item[0] + ' ')
        out_file.write('</file>\n')
        if max_files > -1:
            if af == max_files:
                break

# Close out_file
out_file.close()
