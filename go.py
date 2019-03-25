from bs4 import BeautifulSoup
from tkinter import *
import os
import requests

class Learn(object):
    def __init__(self):
        os.system("clear")
        print("HELLO TO JAPANESE WORDS LERANIGN!!!")
        print("Select one:")
        print("   1. JLPT different kinds of words learnig")
        print("   2. Different grades kanji learning")

    def wordCategories(self):
        os.system("clear")
        print("Input JLPT grade(1 - 5):")
        jpltGrade = input()
        os.system("clear")
        print("Select one:")
        print("   1.Noun")
        print("   2.Adverb")
        print("   3.Adjective")
        print("   4.All")
        kindStr = ""
        menu2 = input()
        if(menu2 == "1"):
            kindStr = "noun"
        elif(menu2 == "2"):
            kindStr = "adverb"
        else:
            kindStr = "adjective"
        
        jishoHref = "https://jisho.org/search/%%23jlpt-n%s%%20%%23%s%%20%%23word" % (jpltGrade, kindStr)
        print("\nPlease waiting........")
        self.onlineWords(jishoHref)
    
    def onlineWords(self, jishoHref):
        html = requests.get(jishoHref)
        os.system("clear")


    def main(self):
        menu1 = input()
        if(menu1 == "1"):
            self.wordCategories()

if __name__ == "__main__":
    Learn().main()