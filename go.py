from bs4 import BeautifulSoup
from tkinter import *
import os
import requests
import pymysql
import random
import math
import functools
import getch

class Learn(object):
    def __init__(self):
        self.exp = math.exp(1)
        os.system("clear")
        print("WELCOME TO JAPANESE WORDS LERANIGN!!!")
        print("Select one:")
        print("   0. Update the databases")
        print("   1. JLPT different kinds of words learnig")
        print("   2. Different grades kanji learning")

        #mysql
        self.connection = pymysql.connect(
            host = "localhost",
            user = "root",
            password = "ss9905110013",
            db = "japanese_words",
            charset='utf8'
        )
        self.cursor = self.connection.cursor()
    
    def updateDataHTML(self, html, grade):
        soup = BeautifulSoup(html, features = "html.parser")
        for box in soup.find_all(class_ = "concept_light clearfix"):
            #kanji
            kanji = ""
            for text in box.find(class_ = "text").contents:
                kanji += text.string.replace('\n', '').replace(' ', '')
            
            #furikana
            kana = ""
            for text in box.find(class_ = "furigana").find_all("span"):
                if text.string:
                    kana += text.string.replace('\n', '').replace(' ', '')
            if box.find(class_ = "furigana").rt:
                for text in box.find(class_ = "furigana").find_all("rt"):
                    if text.string:
                        kana += text.string.replace('\n', '').replace(' ', '')
            
            #meaning, other and type
            meaning = ""
            other = ""
            wType = ""
            meaningBox = box.find(class_ = "meanings-wrapper")
            for kid in meaningBox.contents:
                if kid["class"][0] == "meaning-tags":
                    meaning += "#" + kid.string
                if kid["class"][0] == "meaning-wrapper":
                    temp = kid.find(class_ = "meaning-meaning")
                    if temp == None:
                        continue;
                    if temp.string:
                        meaning += ">" + kid.find(class_ = "meaning-meaning").string
                    else:
                        for i in temp.contents:
                            other += i.string
            if meaning.lower().find("noun") != -1:
                wType += "1"
            if meaning.lower().find("verb") != -1:
                wType += "2"
            if meaning.lower().find("adverb") != -1:
                wType += "3"
            if meaning.lower().find("adjective") != -1:
                wType += "4"
            meaning = meaning.replace(chr(34), '\\"')
            
            # print('''
            #     INSERT IGNORE INTO words (kanji, kana, type, grade, meaning, other)
            #     VALUES ("%s", "%s", "%s", %d, "%s", "%s");
            # '''%(kanji, kana, wType, grade, meaning, other))
            self.cursor.execute('''
                INSERT IGNORE INTO words (kanji, kana, type, grade, meaning, other)
                VALUES ("%s", "%s", "%s", %d, "%s", "%s");
            '''%(kanji, kana, wType, grade, meaning, other))
            self.connection.commit()
            #HTML end

        #HTML Dealing don't put here
        #Judge is end
        more = soup.find(class_ = "more")
        if more == None:
            return 1;
        return 0

    def updateDataInGrade(self, grade):
        page = 1
        while True:
            print("ACQUIRE %d PAGE..." % (page))
            href = "https://jisho.org/search/%%23jlpt-n%d%%20%%23words?page=%d" % (grade, page)
            html = requests.get(href)
            if self.updateDataHTML(html.text, grade):
                break
            page += 1

    def updateData(self):
        #update each JLPT grade
        os.system("clear")
        print("Please waiting...")
        for grade in range(1, 6):
            print("-------------------------------------")
            print("Update JLPT N%d" % (grade))
            self.updateDataInGrade(grade)
            # break
    
    def onlineWords(self, jishoHref):
        html = requests.get(jishoHref)
        os.system("clear")

    def logRand(self, num):
        fRand = random.uniform(1, 11)
        logRand = math.log10(fRand)
        rRand = logRand * num
        return int(rRand)
        
    def myCmp(self, x, y):
        myRange = 0
        if self.data[x][-1] > self.data[y][-1]:
            myRange = 10
        else:
            myRange = 6
        result = random.randint(1, myRange)
        if result > 3:
            return -1;
        return 1;

    def myPractice(self, grade, wType):
        self.cursor.execute('''
            SELECT id,kanji,kana,meaning,other,weight from words
            WHERE grade = %d
            AND type LIKE '%%%s%%'
            ORDER BY weight DESC;
        ''' % (grade, wType))
        self.data = self.cursor.fetchall()
        order = []
        allNum = len(self.data)
        for i in range(0, allNum):
            order.append(i)
        order.sort(key = functools.cmp_to_key(self.myCmp))

        #Everything is ready, remember use order

    def wordCategories(self):
        os.system("clear")
        print("Input JLPT grade(1 - 5):")
        jpltGrade = int(getch.getch())
        os.system("clear")
        print("Select one:")
        print("   1. Noun")
        print("   2. Verb")
        print("   3. Adverb")
        print("   4. Adjective")
        print("   5. All")
        menu2 = getch.getch()
        self.myPractice(jpltGrade, menu2)

    def main(self):        
        menu1 = getch.getch()
        if menu1 == "0":
            self.updateData()
        elif menu1 == "1":
            self.wordCategories()
        else:
            print("Loading...")
        self.connection.close()

if __name__ == "__main__":
    Learn().main()