from bs4 import BeautifulSoup
from tkinter import *
import os
import requests
import pymysql
import random
import math
import functools
from getch import getch

class Learn(object):
    def __init__(self):
        self.exp = math.exp(1)
        os.system("clear")
        print("WELCOME TO JAPANESE WORDS LERANIGN!!!")
        print("ENTER NUMBER TO SELECT:")
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
        confirmAgain = input("ENTER 2147483647 TO CERTAIN")
        if confirmAgain != "2147483647":
            return
        #update each JLPT grade
        os.system("clear")
        print("Please waiting...")
        for grade in range(1, 6):
            print("-------------------------------------")
            print("UPDATE JLPT N%d" % (grade))
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
        if(wType == "5"):
            self.cursor.execute('''
                SELECT id,kanji,kana,meaning,other,weight from words
                WHERE grade = %d
                ORDER BY weight DESC;
            ''' % (grade))
        else:
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
        cirIndex = 0
        while True:
            os.system("clear")
            now = self.data[order[cirIndex]]
            print(now[1])
            getKey = getch()
            if getKey == "q":
                return
            
            print(now[2])
            self.myPrint(now[3], now[4])
            print("")
            print("RIGHT: [SPACE]")
            print("WRONG: [F]")
            getKey = getch()
            if getKey == "q":
                return
            elif getKey == " ":
                self.changeWeight(now[0], -1)
            elif getKey == "f":
                self.changeWeight(now[0], 1)

            cirIndex += 1
            if cirIndex == allNum:
                cirIndex = 0
    
    def changeWeight(self, order, value):
        self.cursor.execute('''
            SELECT weight from words
            WHERE id = %d
        ''' % (order))
        now = self.cursor.fetchall()[0][0]
        now += value
        now = max(0, min(100, now))
        self.cursor.execute('''
            UPDATE words
            SET weight = %d
            WHERE id = %d
        ''' % (now, order))
        self.connection.commit()
        # getch()

    
    def myPrint(self, meanings, others):
        print("")
        print(meanings.replace("#Other forms", "").replace("#", '\n').replace(">", "\n"))
        if(others != ""):
            print("\nOTHER FORMS:")
            print(others)
        

    def wordCategories(self):
        os.system("clear")
        print("ENTER JLPT GRADE: 1 - 5")
        jpltGrade = int(getch())
        os.system("clear")
        print("ENTER NUMBER TO SELECT:")
        print("   1. NOUN")
        print("   2. VERB")
        print("   3. ADVERB")
        print("   4. ADJECTIVE")
        print("   5. ALL")
        menu2 = getch()
        self.myPractice(jpltGrade, menu2)

    def main(self):
        menu1 = getch()
        if menu1 == "0":
            self.updateData()
        elif menu1 == "1":
            self.wordCategories()
        else:
            print("LOADING...")
        self.connection.close()

if __name__ == "__main__":
    Learn().main()