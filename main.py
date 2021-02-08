# -*- coding: utf-8 -*-
import os
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

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

# MAIN

# Open out_file
out_file = open('out.txt', 'w')

# Processing of dictionaries
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
