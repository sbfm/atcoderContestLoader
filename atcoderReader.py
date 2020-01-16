# coding: utf-8
#
# Licence : MIT Licence
# owner   : Fumiya Shibamata
#
import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


SLEEP_PAGE = 1
ATCODER_TOP_PAGE = r'https://atcoder.jp'
TEST_CODE = '#include <cstring> \\n#include <iostream> \\nusing namespace std;\\nint main() {\\nstring a;\\ncin >> a;\\ncout << a;\\n}'

class atcoderContestLoader:
    def __init__(self, contest_code, headless="true", debug="false"):
        self.contest_code = contest_code;
        chromeDriverPath=r'chromedriver.exe'
        options = webdriver.ChromeOptions()
        if(headless=="true"):
            options.add_argument('--headless')
            options.add_argument("--remote-debugging-port=9222") 
            #options.add_argument('disable-infobars')
            #options.add_argument('start-maximized')
            #options.add_argument('--disable-extensions')
            #options.add_argument('--no-sandbox')
            #options.add_argument('--disable-dev-shm-usage')
            #options.add_argument('--disable-gpu')
        options.add_argument('--lang=ja')
        options.add_argument('--user-data-dir=user')
        options.add_argument('--profile-directory=Profile2')
        self.driver = webdriver.Chrome(executable_path=chromeDriverPath, options=options)
        ## ----------------------------
        ## Cookieデータの読み込み
        ## ----------------------------
        try:
            cookies = pickle.load(open("wcookies.pkl", "rb"))
            self.driver.get("https://www.google.com/")
            for cookie in cookies:
                try:
                    cookie['expiry']=round(cookie['expiry']);
                    self.driver.add_cookie(cookie)
                except:
                    pass
        except:
            print("pass")
        
    def hasLoginSession(self, page=""):
        """Login Check."""
        ## ----------------------------
        ## トップページに接続し、ログインボタンの有無を確認
        ## ----------------------------
        self.driver.get(ATCODER_TOP_PAGE)
        time.sleep(SLEEP_PAGE)
        try:
            self.driver.find_element_by_partial_link_text("ログイン").click()
            print("ログイン処理実施");
        except:
            # ログインされている場合、処理を終了する
            print("login");
            return 1
        ## ----------------------------
        ## ログイン処理を行います
        ## ----------------------------
        time.sleep(SLEEP_PAGE)
        self.driver.find_element_by_id("username").send_keys('アカウント')
        self.driver.find_element_by_id("password").send_keys('パスワード')
        time.sleep(1)
        self.driver.find_element_by_id("submit").click()
        # ログインセッションの保持
        pickle.dump(self.driver.get_cookies() , open("wcookies.pkl","wb"))
        return 0
         
    def judge(self, language=r"C++14 (GCC 5.4.1)", waitTime=30):
        self.driver.get(ATCODER_TOP_PAGE + r"/contests/" + self.contest_code + r"/custom_test/")
        time.sleep(SLEEP_PAGE)
        ### ----------------------------
        ## 言語を選択
        ### ----------------------------
        Select(self.driver.find_element_by_name("data.LanguageId")).select_by_visible_text(language)
        ## ----------------------------
        # ソースコードを打ち込む
        ## ----------------------------
        try:
            self.driver.find_element_by_name("sourceCode").clear()
        except:
            self.driver.find_element_by_css_selector('.btn.btn-default.btn-sm.btn-toggle-editor').click()
            WebDriverWait(self.driver, 5).until(expected_conditions.presence_of_element_located((By.NAME, "sourceCode")))
            self.driver.find_element_by_name("sourceCode").clear()
        # ソースコード入力
        self.driver.execute_script('document.getElementsByName("sourceCode")[0].value="%s";' % TEST_CODE)
        #self.driver.find_element_by_name("sourceCode").send_keys(TEST_CODE)
        # 標準入力
        self.driver.find_element_by_name("input").clear()
        self.driver.execute_script('document.getElementsByName("input")[0].value="%s";' % "wwww")
        #self.driver.find_element_by_name("input").send_keys("wwww")
        # 実行ボタンを押す
        #self.driver.find_element_by_partial_link_text("実行").click()
        #time.sleep(3)
        ## ----------------------------
        ## 実行結果の待機
        ## ----------------------------
        try:
            WebDriverWait(self.driver, waitTime).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".table.table-bordered")))
        except:
            print("no")
        
        ## ----------------------------
        ## 実行結果の取得
        ## ----------------------------
        # 実行結果
        aa = self.driver.find_element_by_css_selector('.table.table-bordered').find_elements_by_class_name('text-right')[0].text
        # 実行時間
        ab = self.driver.find_element_by_css_selector('.table.table-bordered').find_elements_by_class_name('text-right')[1].text
        # メモリ
        ac = self.driver.find_element_by_css_selector('.table.table-bordered').find_elements_by_class_name('text-right')[2].text
        # 標準出力
        ad = self.driver.find_element_by_id('stdout').text
        # エラー出力
        ae = self.driver.find_element_by_id('stderr').text
        print("acsepted")
        return aa,ab,ac,ad,ae
        
    def getTasks(self):
        self.driver.get(ATCODER_TOP_PAGE + r"/contests/" + self.contest_code + r"/tasks/")
        time.sleep(SLEEP_PAGE)
        taskList = []
        taskTable = self.driver.find_element_by_xpath('//table/tbody')
        for taskTr in taskTable.find_elements_by_xpath('tr'):
            taskList.append({\
                    'taskindex': taskTr.find_elements_by_xpath('td')[0].text, \
                    'taskname': taskTr.find_elements_by_xpath('td')[1].text, \
                    'tasklink': taskTr.find_elements_by_xpath('td')[1].find_element_by_tag_name("a").get_attribute("href"), \
                    'timelimit': taskTr.find_elements_by_xpath('td')[2].text, \
                    'memorylimit': taskTr.find_elements_by_xpath('td')[3].text, \
                    })
        #print(d[0]['taskindex'])
        return taskList
    
    def getTest(self,url):
        self.driver.get(url)
        time.sleep(SLEEP_PAGE)
        no = 0
        testList = []
        while 1:
            try:
                testInput = self.driver.find_element_by_id("pre-sample" + str(no)).text
                no+=1
                testOutput = self.driver.find_element_by_id("pre-sample" + str(no)).text
                no+=1
                if(testOutput!=""):
                    testList.append({\
                        'input': testInput, \
                        'output': testOutput, \
                    })
            except:
                break
        return testList
        
        
    def __del__(self):
        """ Finaly. """
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass

def _test():
    hogehoge = atcoderContestLoader("agc041",headless="false")
    ##ログインcheck
    hogehoge.hasLoginSession()
    #a,b,c,d,e = hogehoge.judge()
    #print(a)
    po = hogehoge.getTasks()
    print(po)
    popo = hogehoge.getTest(po[0]['tasklink'])
    print(popo)
    del hogehoge

_test()
