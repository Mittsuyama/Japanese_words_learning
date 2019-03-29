from tkinter import *
import pymysql
import random
import os
from getch import getch
import functools
import re

class GUI:
    counter = 0
    
    def __init__(self):
        #mysql
        self.connection = pymysql.connect(
            host = "localhost",
            user = "user",
            password = "password",
            db = "japanese_words",
            charset='utf8'
        )
        self.cursor = self.connection.cursor()

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
    
    def dataInit(self, grade, wType):
        if wType == "5" and grade != 0:
            self.cursor.execute('''
                SELECT id,kanji,kana,meaning,other,weight from words
                WHERE grade = %d
                ORDER BY weight DESC;
            ''' % (grade))
        elif wType != "5" and grade == 0:
            self.cursor.execute('''
                SELECT id,kanji,kana,meaning,other,weight from words
                WHERE type LIKE '%%%s%%'
                ORDER BY weight DESC;
            ''' % (wType))
        elif wType == "5" and grade == 0:
            self.cursor.execute('''
                SELECT id,kanji,kana,meaning,other,weight from words
                ORDER BY weight DESC;
            ''')
        else:
            self.cursor.execute('''
                SELECT id,kanji,kana,meaning,other,weight from words
                WHERE grade = %d
                AND type LIKE '%%%s%%'
                ORDER BY weight DESC;
            ''' % (grade, wType))
        self.data = self.cursor.fetchall()
        self.order = []
        self.allNum = len(self.data)
        for i in range(0, self.allNum):
            self.order.append(i)
        self.order.sort(key = functools.cmp_to_key(self.myCmp))

        # for now in range(0, allNum):
        #     self.data[now][3] = self.data[now][3].replace("#Other forms", "").replace("#", '\n').replace(">", "\n")
        #     if(self.data[now][4] != ""):
        #         self.data[now][4] = "OTHER FORMS:\n" + self.data[now][4]

    def windsQuit(self, event):
        getKey = event.char
        now = self.order[self.index]
        if getKey == "q":
            self.root.destroy()
        else:
            if self.counter == 0 and getKey == " ":
                self.counter = 1
                self.kanaVal.set(self.data[now][2])
                nowM = self.data[now][3].replace("#Other forms", "")
                # nowM = re.sub(r'#.+>', "\n\n", nowM)
                nowM = nowM.replace(">", "\n")
                nowM = nowM.replace("#", "\n# ")
                nowO = ""
                if self.data[now][4] != "":
                    nowO = "OTHER FORMS:\n" + self.data[now][4]
                self.meaningVal.set(nowM)
                self.otherVal.set(nowO)
            elif self.counter == 1 and (getKey == " " or getKey == "f"):
                self.counter = 0
                if getKey == " ":
                    self.changeWeight(self.data[now][0], -1)
                elif getKey == "f":
                    self.changeWeight(self.data[now][0], 1)

                self.index += 1
                if self.index >= self.allNum:
                    self.index = 0
                now = self.order[self.index]
                self.kanjiVal.set(self.data[now][1])
                self.kanaVal.set("")
                self.meaningVal.set("")
                self.otherVal.set("")

    def changeWeight(self, order, value):
        # print("CHANGE WEIGHT " + str(value))
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

    def jpWindow(self):
        self.index = 0;
        self.root = Tk()
        self.root.geometry("1000x600")
        self.root.bind("<Key>", self.windsQuit)

        now = self.order[self.index]

        fontSize = 30
        fontSizeSmall = 18

        self.kanjiVal = StringVar()
        self.kanaVal = StringVar()
        self.meaningVal = StringVar()
        self.otherVal = StringVar()

        self.kanjiVal.set(self.data[now][1])

        blankLabel = Label(self.root, font = ("", 50), height = 2)
        kanjiLabel = Label(self.root, textvariable = self.kanjiVal, font = ("", 70), height = 1)
        kanaLabel = Label(self.root, textvariable = self.kanaVal, font = ("", 40))
        blankLabel2 = Label(self.root, font = ("", 5), height = 1)
        meaningLabel = Label(self.root, textvariable = self.meaningVal, font = ("", fontSizeSmall), fg = "gray")
        otherLable = Label(self.root, textvariable = self.otherVal, font = ("", fontSizeSmall), fg = "gray")

        blankLabel.pack()
        kanjiLabel.pack()
        kanaLabel.pack()
        blankLabel2.pack()
        meaningLabel.pack()
        otherLable.pack()

        self.root.mainloop()

    def main(self):
        os.system("clear")
        print("ENTER JLPT GRADE: 0 - 5")
        jpltGrade = int(getch())
        os.system("clear")
        print("ENTER NUMBER TO SELECT:")
        print("   1. NOUN")
        print("   2. VERB")
        print("   3. ADVERB")
        print("   4. ADJECTIVE")
        print("   5. ALL")
        menu2 = getch()
        self.dataInit(jpltGrade, menu2)
        self.jpWindow()

if __name__ == "__main__":
    GUI().main()