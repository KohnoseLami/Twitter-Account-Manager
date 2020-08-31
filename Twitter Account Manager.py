#Copyright © 2020 KohnoseLami All Rights Reserved.
#This software is released under the LGPL 3.0 License, see LICENSE.
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys as keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import PySimpleGUIWx as sg
import webbrowser
import threading
import time
import sys
import os

#ログイン状態 0=ログインしてない 1=ログインしている
account = 0

#今いるパスの検出
path = os.getcwd()

#レイアウトの設定と起動
sg.theme('Material2')

frame1 = sg.Frame('Twitterのアカウント情報を入力してください',[[sg.Text('電話、メールまたはユーザー名')],
                  [sg.InputText('', size=(80, 1), key='LoginID')],
                  [sg.Text('パスワード')],
                  [sg.InputText('', size=(80, 1), key='LoginPASS')],
                  [sg.Checkbox('セッション情報をファイルに出力しますか？', default=False)],
                  [sg.Text('セッションファイル'), sg.Input(path + '/cookies.pkl', size=(40, 1)), sg.FileBrowse('ファイルを選択', key='inputFilePath')],
                  [sg.Button('ログイン', key='login'),sg.Button('ログアウト', key='logout'),sg.Button('セッションログイン', key='session_login')],]
                  )

frame2 = sg.Frame('\n項目選択',[[sg.Checkbox('全フォロワーブロ解', default=False)],
                  [sg.Checkbox('全リム', default=False)],
                  [sg.Checkbox('Bio削除', default=False)],
                  [sg.Checkbox('ミュート、ブロック解除', default=False)],
                  [sg.Checkbox('連携解除', default=False)],
                  [sg.Checkbox('ツイ消し', default=False)],
                  [sg.Checkbox('ふぁぼ取り消し', default=False)],
                  [sg.Checkbox('DM削除', default=False)],
                  [sg.Button('利用規約を確認', key='terms'),sg.Checkbox('利用規約に同意する', default=False)],
                  [sg.Button('操作開始', key='start')],]
                  )

frame3 = sg.Frame('\n個別操作',[[sg.Text('\nツイート')],
                  [sg.InputText('', size=(40, 1), key='tweet_text')],
                  [sg.Button('ツイートする', key='tweeting')],
                  [sg.Text('\nフォロー')],
                  [sg.InputText('', size=(40, 1), key='follow_user')],
                  [sg.Button('フォローする', key='following')],
                  [sg.Text('\nリムーブ')],
                  [sg.InputText('', size=(40, 1), key='unfollow_user')],
                  [sg.Button('リムーブする', key='unfollowing')],]
                  )

layout = [
    [frame1],
    [frame2,frame3],
    [sg.Text('このソフトウェア内にはLGPL 3.0でライセンスされたPySimpleGUI、Apache License 2.0でライセンスされたSelenium、BSDでライセンスされたChromium、ChromeDriverを含みます。\nこのソフトウェアはLGPL3.0でライセンスされています。', size=(80, 3))],
    [sg.Text('↓以下のコンソールに作業履歴が表示されます。')],
    [sg.Output(size=(80,10))],
    [sg.Text('Copyright © 2018-2020 KohnoseLami All Rights Reserved.')]
]

window = sg.Window('Twitter Account Manager', layout)

options = Options()
options.binary_location = path + '/chrome.exe'
options.add_argument('--headless')
options.add_argument('--lang=ja-JP')
driver = webdriver.Chrome(options=options)
driver.set_window_size(945,1020)

#セッションログイン
def t_session_login():
    global URL
    global account
    try:
        print("Login start")
        driver.get("https://google.com")
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get('https://twitter.com/home')
        time.sleep(1)
        if driver.current_url == "https://twitter.com/home":
            account = 1
            print("\nLogin successful\n------------------------------------------------------")
            driver.implicitly_wait(1)
            driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[7]').click()
            URL = driver.current_url
        else:
            account = 0
            print("\nLogin failed\n------------------------------------------------------")
    except Exception as e:
        print("\n!Please inform the software maker of the error, situation and error code.!")
        print(e)
        print("------------------------------------------------------")

#ログイン
def t_login():
    global URL
    global account
    try:
        print("Login start")
        driver.get('https://twitter.com/login')
        driver.implicitly_wait(3)
        driver.find_element_by_name('session[username_or_email]').send_keys(values["LoginID"])
        driver.find_element_by_name('session[password]').send_keys(values["LoginPASS"])
        driver.find_element_by_name('session[password]').send_keys(keys.ENTER)
        if driver.find_elements_by_xpath('/html/body/div[2]/div/div[1]'):
            print("\nTwo-factor authentication detected.")
            authorization_code = text = sg.popup_get_text('認証コード', '')
            driver.find_element_by_id('challenge_response').send_keys(authorization_code)
            driver.find_element_by_id('challenge_response').send_keys(keys.ENTER)
            if driver.find_elements_by_id('error-message'):
                print("Error, try typing again.\n")
                authorization_code = sg.popup_get_text('認証コード', '')
                driver.find_element_by_id('challenge_response').send_keys(authorization_code)
                driver.find_element_by_id('challenge_response').send_keys(keys.ENTER)
                if driver.find_elements_by_id('error-message'):
                    account = 0
                    print("\nLogin failed\n------------------------------------------------------")
                else:
                    time.sleep(1)
                    if driver.current_url == "https://twitter.com/home":
                        account = 1
                        print("\nLogin successful\n------------------------------------------------------")
                        driver.implicitly_wait(1)
                        driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[7]').click()
                        URL = driver.current_url
                        if values[0] == True:
                            pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
                            print("Cookies output completed.\n------------------------------------------------------")
                    else:
                        account = 0
                        print("\nLogin failed\n------------------------------------------------------")
            else:
                time.sleep(1)
                if driver.current_url == "https://twitter.com/home":
                    account = 1
                    print("\nLogin successful\n------------------------------------------------------")
                    driver.implicitly_wait(1)
                    driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[7]').click()
                    URL = driver.current_url
                    if values[0] == True:
                        pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
                        print("Cookies output completed.\n------------------------------------------------------")
                else:
                    account = 0
                    print("\nLogin failed\n------------------------------------------------------")
        else:
            time.sleep(1)
            if driver.current_url == "https://twitter.com/home":
                account = 1
                print("\nLogin successful\n------------------------------------------------------")
                driver.implicitly_wait(1)
                driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[7]').click()
                URL = driver.current_url
                if values[0] == True:
                    pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
                    print("Cookies output completed.\n------------------------------------------------------")
            else:
                account = 0
                print("\nLogin failed\n------------------------------------------------------")
    except Exception as e:
        print("\n!Please inform the software maker of the error, situation and error code.!")
        print(e)
        print("------------------------------------------------------")

#ログアウトする
def t_logout():
    global account
    try:
        print("Login start")
        driver.get('https://twitter.com/logout')
        driver.implicitly_wait(1)
        driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
        account = 0
        print("\nLogout successful\n------------------------------------------------------")
    except Exception as e:
        print("\n!Please inform the software maker of the error, situation and error code.!")
        print(e)
        print("------------------------------------------------------")

#ツイートする
def t_tweeting():
   try:
       driver.get('https://twitter.com/intent/tweet?text=' + values["tweet_text"])
       driver.implicitly_wait(1)
       driver.find_element_by_xpath('//*[@data-testid="tweetButton"]').click()
       time.sleep(1)
       if driver.find_elements_by_xpath('/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[3]/div/div/div[1]'):
           print("Could not tweet.")
       else:
           print("Tweeted:" + values["tweet_text"])
   except Exception as e:
       print("\n!Please inform the software maker of the error, situation and error code.!")
       print(e)
       print("------------------------------------------------------")

#フォローする
def t_following():
    try:
        driver.get('https://twitter.com/' + values["follow_user"])
        if driver.find_elements_by_xpath('//*[contains(@data-testid,"-follow")]'):
            driver.find_element_by_xpath('/html/body/div/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div[3]/div/div').click()
            time.sleep(1)
            if driver.find_elements_by_xpath('//*[contains(@data-testid,"-unfollow")]'):
                print("Followed:@" + values["follow_user"])
            elif driver.find_elements_by_xpath('//*[contains(@data-testid,"-follow")]'):
                print("Could not follow.")
        else:
            if driver.find_elements_by_xpath('//*[contains(@data-testid,"-unfollow")]'):
                print("Followed:@" + values["follow_user"])
            else:
                print("User not found.")
    except Exception as e:
        print("\n!Please inform the software maker of the error, situation and error code.!")
        print(e)
        print("------------------------------------------------------")

#リムーブする
def t_unfollowing():
    try:
        driver.get('https://twitter.com/' + values["unfollow_user"])
        driver.implicitly_wait(1)
        if driver.find_elements_by_xpath('//*[contains(@data-testid,"-unfollow")]'):
            driver.find_element_by_xpath('//*[contains(@data-testid,"-unfollow")]').click()
            driver.implicitly_wait(1)
            driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
            time.sleep(1)
            if driver.find_elements_by_xpath('//*[contains(@data-testid,"-follow")]'):
                print("Unfollowed:@" + values["unfollow_user"])
            elif driver.find_elements_by_xpath('//*[contains(@data-testid,"-unfollow")]'):
                print("Could not unfollow.")
        else:
            if driver.find_elements_by_xpath('//*[contains(@data-testid,"-follow")]'):
                print("Unfollowed:@" + values["unfollow_user"])
            else:
                print("User not found.")
    except Exception as e:
        print("\n!Please inform the software maker of the error, situation and error code.!")
        print(e)
        print("------------------------------------------------------")

#メイン処理
def main():
    try:
        print("Start")
#チェックボックス1
        if values[2] == True:
            try:
                print("------------------------------------------------------\nStart:Block&Release")
                driver.get(URL + '/followers')
                count = int(0)
                cur_url = driver.current_url
                while True:
                    try:
                        if cur_url == URL:
                            print("\nDetect logout")
                            driver.get('https://twitter.com/login')
                            driver.implicitly_wait(10)
                            driver.find_element_by_name('session[username_or_email]').send_keys(values["LoginID"])
                            driver.find_element_by_name('session[password]').send_keys(values["LoginPASS"])
                            driver.find_element_by_name('session[password]').send_keys(keys.ENTER)
                            if driver.find_elements_by_xpath('/html/body/div[2]/div/div[1]'):
                                print("\nTwo-factor authentication detected.")
                                authorization_code = text = sg.popup_get_text('認証コード', '')
                                driver.find_element_by_id('challenge_response').send_keys(authorization_code)
                                driver.find_element_by_id('challenge_response').send_keys(keys.ENTER)
                                if driver.find_elements_by_id('error-message'):
                                    print("Error, try typing again.\n")
                                    authorization_code = sg.popup_get_text('認証コード', '')
                                    driver.find_element_by_id('challenge_response').send_keys(authorization_code)
                                    driver.find_element_by_id('challenge_response').send_keys(keys.ENTER)
                                    if driver.find_elements_by_id('error-message'):
                                        account = 0
                                        print("Relogin failed\n")
                                    else:
                                        driver.implicitly_wait(1)
                                        if driver.current_url == "https://twitter.com/home":
                                            account = 1
                                            print("Relogin successful\n")
                                        else:
                                            account = 0
                                            print("Relogin failed\n")
                                else:
                                    driver.implicitly_wait(1)
                                    if driver.current_url == "https://twitter.com/home":
                                        account = 1
                                        print("Relogin successful\n")
                                    else:
                                        account = 0
                                        print("Relogin failed\n")
                            else:
                                driver.implicitly_wait(1)
                                if driver.current_url == "https://twitter.com/home":
                                    account = 1
                                    print("Relogin successful\n")
                                else:
                                    account = 0
                                    print("Relogin failed\n")
                            driver.get(URL + '/followers')
                            driver.implicitly_wait(1)
                            cur_url = driver.current_url
                            driver.find_element_by_xpath('//*[@data-testid="UserCell"]/div/div[2]/div[1]').click()
                            driver.implicitly_wait(1)
                            user_url = driver.current_url
                            driver.find_element_by_xpath('//*[@data-testid="userActions"]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('//*[@data-testid="block"]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('//*[contains(@data-testid,"unblock")]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                            count += 1
                            print(str(count) + ".Block&Release " + user_url.replace('https://twitter.com/', 'Screenname:'))
                        else:
                            driver.get(URL + '/followers')
                            driver.implicitly_wait(1)
                            cur_url = driver.current_url
                            driver.find_element_by_xpath('//*[@data-testid="UserCell"]/div/div[2]/div[1]').click()
                            driver.implicitly_wait(1)
                            user_url = driver.current_url
                            driver.find_element_by_xpath('//*[@data-testid="userActions"]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('//*[@data-testid="block"]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('//*[contains(@data-testid,"unblock")]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                            count += 1
                            print(str(count) + ".Block&Release " + user_url.replace('https://twitter.com/', 'Screenname:'))
                    except Exception as e:
                        if driver.find_elements_by_xpath('/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div[1]/span'):
                            print("Complete success\n------------------------------------------------------")
                            break;
                        else:
                            try:
                                time.sleep(5)
                                cur_url = driver.current_url
                                if cur_url == URL:
                                    print("\nDetect logout")
                                    driver.get('https://twitter.com/login')
                                    driver.implicitly_wait(10)
                                    driver.find_element_by_name('session[username_or_email]').send_keys(values["LoginID"])
                                    driver.find_element_by_name('session[password]').send_keys(values["LoginPASS"])
                                    driver.find_element_by_name('session[password]').send_keys(keys.ENTER)
                                    if driver.find_elements_by_xpath('/html/body/div[2]/div/div[1]'):
                                        print("\nTwo-factor authentication detected.")
                                        authorization_code = text = sg.popup_get_text('認証コード', '')
                                        driver.find_element_by_id('challenge_response').send_keys(authorization_code)
                                        driver.find_element_by_id('challenge_response').send_keys(keys.ENTER)
                                        if driver.find_elements_by_id('error-message'):
                                            print("Error, try typing again.\n")
                                            authorization_code = sg.popup_get_text('認証コード', '')
                                            driver.find_element_by_id('challenge_response').send_keys(authorization_code)
                                            driver.find_element_by_id('challenge_response').send_keys(keys.ENTER)
                                            if driver.find_elements_by_id('error-message'):
                                                account = 0
                                                print("Relogin failed\n")
                                            else:
                                                driver.implicitly_wait(1)
                                                if driver.current_url == "https://twitter.com/home":
                                                    account = 1
                                                    print("Relogin successful\n")
                                                else:
                                                    account = 0
                                                    print("Relogin failed\n")
                                        else:
                                            driver.implicitly_wait(1)
                                            if driver.current_url == "https://twitter.com/home":
                                                account = 1
                                                print("Relogin successful\n")
                                            else:
                                                account = 0
                                                print("Relogin failed\n")
                                    else:
                                        driver.implicitly_wait(1)
                                        if driver.current_url == "https://twitter.com/home":
                                            account = 1
                                            print("Relogin successful\n")
                                        else:
                                            account = 0
                                            print("Relogin failed\n")
                                    driver.get(URL + '/followers')
                                    driver.implicitly_wait(1)
                                    cur_url = driver.current_url
                                    driver.find_element_by_xpath('//*[@data-testid="UserCell"]/div/div[2]/div[1]').click()
                                    driver.implicitly_wait(1)
                                    user_url = driver.current_url
                                    driver.find_element_by_xpath('//*[@data-testid="userActions"]').click()
                                    driver.implicitly_wait(1)
                                    driver.find_element_by_xpath('//*[@data-testid="block"]').click()
                                    driver.implicitly_wait(1)
                                    driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                                    driver.implicitly_wait(1)
                                    driver.find_element_by_xpath('//*[contains(@data-testid,"unblock")]').click()
                                    driver.implicitly_wait(1)
                                    driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                                    count += 1
                                    print(str(count) + ".Block&Release " + user_url.replace('https://twitter.com/', 'Screenname:'))
                                    cur_url = driver.current_url
                                else:
                                    driver.get(URL + '/followers')
                                    driver.implicitly_wait(1)
                                    cur_url = driver.current_url
                                    driver.find_element_by_xpath('//*[@data-testid="UserCell"]/div/div[2]/div[1]').click()
                                    driver.implicitly_wait(1)
                                    user_url = driver.current_url
                                    driver.find_element_by_xpath('//*[@data-testid="userActions"]').click()
                                    driver.implicitly_wait(1)
                                    driver.find_element_by_xpath('//*[@data-testid="block"]').click()
                                    driver.implicitly_wait(1)
                                    driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                                    driver.implicitly_wait(1)
                                    driver.find_element_by_xpath('//*[contains(@data-testid,"unblock")]').click()
                                    driver.implicitly_wait(1)
                                    driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                                    count += 1
                                    print(str(count) + ".Block&Release " + user_url.replace('https://twitter.com/', 'Screenname:'))
                                    cur_url = driver.current_url
                            except Exception as e:
                                print("\nRegulation:Wait 15 minutes.\n")
                                time.sleep(1)
                                driver.refresh()
                                time.sleep(899)
                                driver.get(URL + '/followers')
                                time.sleep(5)
                                cur_url = driver.current_url
            except Exception as e:
                print("\n!Please inform the software maker of the error, situation and error code.!")
                print(e)
                print("------------------------------------------------------")
#チェックボックス2
        if values[3] == True:
            try:
                print("------------------------------------------------------\nStart:Remove")
                count = int(0)
                driver.get(URL + '/following')
                while True:
                    driver.implicitly_wait(1)
                    if driver.find_elements_by_xpath('//*[contains(@data-testid,"-unfollow")]'):
                        driver.find_element_by_xpath('//*[contains(@data-testid,"-unfollow")]').click()
                        driver.implicitly_wait(1)
                        driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                        count += 1
                        print(str(count) + ".Remove")
                    else:
                        print("Complete success\n------------------------------------------------------")
                        break;
            except Exception as e:
                print("\n!Please inform the software maker of the error, situation and error code.!")
                print(e)
                print("------------------------------------------------------")
#チェックボックス3
        if values[4] == True:
            try:
                print("------------------------------------------------------\nStart:Delete Bio")
                driver.get('https://twitter.com/settings/profile')
                driver.implicitly_wait(1)
                driver.find_element_by_name('displayName').clear()
                driver.find_element_by_name('displayName').send_keys("ALL Clear!")
                driver.find_element_by_name('description').clear()
                driver.find_element_by_name('description').send_keys("a")
                driver.find_element_by_name('description').send_keys(keys.BACKSPACE)
                driver.find_element_by_name('location').clear()
                driver.find_element_by_name('location').send_keys("a")
                driver.find_element_by_name('location').send_keys(keys.BACKSPACE)
                driver.find_element_by_name('url').clear()
                driver.find_element_by_name('url').send_keys("a")
                driver.find_element_by_name('url').send_keys(keys.BACKSPACE)
                driver.implicitly_wait(1)
                driver.find_element_by_xpath('//*[@data-testid="Profile_Save_Button"]').click()
                print("Complete success\n------------------------------------------------------")
            except Exception as e:
                print("\n!Please inform the software maker of the error, situation and error code.!")
                print(e)
                print("------------------------------------------------------")
#チェックボックス4
        if values[5] == True:
            try:
                print("------------------------------------------------------\nStart:Unmuting, Unblocking")
                count = int(0)
                while True:
                    driver.get('https://twitter.com/settings/blocked/all')
                    driver.implicitly_wait(1)
                    if driver.find_elements_by_xpath('//*[@data-testid="UserCell"]/div/div[2]/div[1]/div[2]'):
                        driver.find_element_by_xpath('//*[@data-testid="UserCell"]/div/div[2]/div[1]/div[2]').click()
                        count += 1
                        print(str(count) + ".Unblocking")
                    else:
                        break;
                count = int(0)
                while True:
                    driver.get('https://twitter.com/settings/muted/all')
                    driver.implicitly_wait(1)
                    if driver.find_elements_by_xpath('//*[@data-testid="UserCell"]/div/div[2]/div[1]/div[2]'):
                        driver.find_element_by_xpath('//*[@data-testid="UserCell"]/div/div[2]/div[1]/div[2]').click()
                        count += 1
                        print(str(count) + ".Unmuting")
                    else:
                        print("Complete success\n------------------------------------------------------")
                        break;
            except Exception as e:
                print("\n!Please inform the software maker of the error, situation and error code.!")
                print(e)
                print("------------------------------------------------------")
#チェックボックス5
        if values[6] == True:
            try:
                print("------------------------------------------------------\nStart:Unlink")
                count = int(0)
                while True:
                    try:
                        driver.get('https://twitter.com/settings/applications')
                        driver.implicitly_wait(1)
                        if driver.find_elements_by_xpath('/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div[1]/span'):
                            print("Complete success\n------------------------------------------------------")
                            break;
                        else:
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath('/html/body/div/div/div/div[2]/main/div/div/div/div[2]/div/a[1]').click()
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath("/html/body/div/div/div/div[2]/main/div/div/div/div[2]/div/div[6]/div[3]/div/div/div/span").click()
                            count += 1
                            print(str(count) + ".Unlink")
                    except Exception as e:
                        try:
                            driver.implicitly_wait(1)
                            driver.find_element_by_xpath("/html/body/div/div/div/div[2]/main/div/div/div/div[2]/div/div[5]/div[3]/div/div/div/span").click()
                            count += 1
                            print(str(count) + ".Unlink")
                        except Exception as e:
                            print("\n!Please inform the software maker of the error, situation and error code.!")
                            print(e)
                            print("------------------------------------------------------")
                            break;
            except Exception as e:
                print("\n!Please inform the software maker of the error, situation and error code.!")
                print(e)
                print("------------------------------------------------------")
#チェックボックス6
        if values[7] == True:
            try:
                print("------------------------------------------------------\nStart:Delete Tweet")
                count = int(0)
                driver.get("https://twitter.com/search?q=from:" + URL.replace('https://twitter.com/', '') + "&f=live")
                while True:
                    if driver.find_elements_by_xpath('//*[@data-testid="caret"]/div'):
                        time.sleep(0.1)
                        driver.implicitly_wait(1)
                        driver.find_element_by_xpath('//*[@data-testid="caret"]/div').click()
                        driver.implicitly_wait(1)
                        driver.find_element_by_xpath('//*[@role="menu"]/div/div/div/div[1]').click()
                        driver.implicitly_wait(1)
                        driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                        count += 1
                        print(str(count) + ".Tweet")
                    else:
                        print("Complete success\n------------------------------------------------------")
                        break;
            except Exception as e:
                print("\n!Please inform the software maker of the error, situation and error code.!")
                print(e)
                print("------------------------------------------------------")
#チェックボックス7
        if values[8] == True:
            try:
                print("------------------------------------------------------\nStart:Unfavorite")
                count = int(0)
                driver.get(URL + "/likes")
                while True:
                    if driver.find_elements_by_xpath('//*[@data-testid="unlike"]/div/div[1]'):
                        driver.find_element_by_xpath('//*[@data-testid="unlike"]/div/div[1]').click()
                        count += 1
                        print(str(count) + ".Unfavorite")
                    else:
                        print("Complete success\n------------------------------------------------------")
                        break;
            except Exception as e:
                print("\n!Please inform the software maker of the error, situation and error code.!")
                print(e)
                print("------------------------------------------------------")
#チェックボックス8
        if values[9] == True:
            try:
                print("------------------------------------------------------\nStart:Delete DM")
                count = int(0)
                while True:
                    driver.get('https://twitter.com/messages')
                    driver.implicitly_wait(1)
                    driver.find_element_by_xpath('//*[@data-testid="conversation"]').click()
                    driver.implicitly_wait(1)
                    driver.find_element_by_xpath('//*[contains(@href,"info")]').click()
                    driver.implicitly_wait(1)
                    driver.find_element_by_xpath('/html/body/div/div/div/div[2]/main/div/div/div/div[2]/div/div[3]/div[4]/div').click()
                    driver.implicitly_wait(1)
                    driver.find_element_by_xpath('//*[@data-testid="confirmationSheetConfirm"]').click()
                    count += 1
                    print(str(count) + ".DM")
            except NoSuchElementException:
                print("Complete success\n------------------------------------------------------")
            except Exception as e:
                print("\n!Please inform the software maker of the error, situation and error code.!")
                print(e)
                print("------------------------------------------------------")
        print("All Complete Success")
    except Exception as e:
        print("\n!Please inform the software maker of the error, situation and error code.!")
        print(e)
        print("------------------------------------------------------")

#イベント監視
while True:
    global event, values
    event, values = window.read()

#ウィンドウを閉じたとき
    if event == sg.WIN_CLOSED:
        driver.quit()
        break

#セッションログイン
    if event == "session_login":
        threading.Thread(target=t_session_login).start()

#セッションログイン
    if event == "logout":
        threading.Thread(target=t_logout).start()

#ログイン
    if event == 'login':
        threading.Thread(target=t_login).start()

#利用規約表示
    if event == 'terms':
        webbrowser.open(path + "/利用規約.txt")

#ツイートする
    if event == 'tweeting':
        threading.Thread(target=t_tweeting).start()

#フォローする
    if event == 'following':
        threading.Thread(target=t_following).start()

#リムーブする
    if event == 'unfollowing':
        threading.Thread(target=t_unfollowing).start()

#作業開始
    if event == 'start':

#アカウントのログイン状態確認
        if account == 1:

#利用規約に同意しているかの確認
            if values[10] == True:

#スレッドを使用してメインの「項目選択」を実行
                threading.Thread(target=main).start()

#利用規約に同意していない場合
            elif values[10] == False:
                sg.popup('利用規約に同意してください')

#アカウントにログインしていない場合
        elif account == 0:
            sg.popup('アカウントにログインしてください')

window.close()