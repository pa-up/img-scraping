import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import shutil
import cv2
import numpy as np
import requests
from io import BytesIO
import base64
import io
import zipfile
from PIL import Image
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome import service as fs


def browser_setup():
    """ブラウザを起動する関数"""
    #ブラウザの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #ブラウザの起動（webdriver_managerによりドライバーをインストール）
    CHROMEDRIVER = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()  # chromiumを使用したいので引数でchromiumを指定しておく
    service = fs.Service(CHROMEDRIVER)
    browser = webdriver.Chrome(
        options=options,
        service=service
    )
    browser.implicitly_wait(3)
    return browser


def get_url(KEYWORD , browser):
    # 画像検索窓を表示
    url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    browser.get(url)
    browser.implicitly_wait(5)

    # サムネイル画像のURL取得
    browser.get(url.format(q=KEYWORD))

    # ページの一番下へスクロールして新しいサムネイル画像を表示させる
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(1)

    # サムネイル画像のリンクを取得
    thumbnail_elements = browser.find_elements(By.CSS_SELECTOR, "img.rg_i")
    thumbnail_URLS = [element.get_attribute('src') for element in thumbnail_elements]

    # 少し待たないと正常終了しなかったので5秒待機
    time.sleep(5)
    browser.quit()
    
    return thumbnail_URLS


def url_to_img_folda(thumbnail_URLS , saved_img_folder):
    count = 0
    for url in thumbnail_URLS:
        is_url_valid = True

        if url is not None:
            # 画像URLの先頭が「data:」or「https:」で場合分け
            if url.startswith('data:'):
                pil_img = Image.open(io.BytesIO(base64.b64decode(url.split(',')[1])))
            elif url.startswith('https:'):
                response = requests.get(url)
                pil_img = Image.open(BytesIO(response.content))
            else:
                is_url_valid = False
        else:
            is_url_valid = False

        # 画像URLの先頭が「data:」or「https:」なら画像を保存
        if is_url_valid == True:
            rgb_img = np.array(pil_img)
            file_name = saved_img_folder + str(count) + ".jpg"
            bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_name , bgr_img)
        count = count + 1


def main():
    KEYWORD = ""
    st.title("画像を一括取得")
    st.write("<p></p>", unsafe_allow_html=True)
    KEYWORD = st.text_input("検索キーワード")
    st.write("<p></p>", unsafe_allow_html=True)

    if KEYWORD != "":
        browser = browser_setup()
        thumbnail_URLS = get_url(KEYWORD , browser)

        # 画像を格納するフォルダを新規生成
        saved_img_folder = "./img/"
        if os.path.exists(saved_img_folder):
            shutil.rmtree(saved_img_folder)
            os.makedirs(saved_img_folder)
        else:
            os.makedirs(saved_img_folder)
        
        # 全ての画像URLを画像ファイルを格納したファイルに格納
        url_to_img_folda(thumbnail_URLS , saved_img_folder)

        # フォルダ内のファイル数を取得
        files_count = len( os.listdir(saved_img_folder) )
        st.write("取得した画像数 : " , files_count , "枚")

        # フォルダを圧縮してバイトストリームに変換
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(saved_img_folder):
                for file in files:
                    zf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), saved_img_folder))
        zip_buffer.seek(0)

        # ダウンロードボタンを作成
        st.download_button(
            label="全画像をダウンロード",
            data=zip_buffer.getvalue(),
            file_name="img.zip",
            mime="application/zip"
        )

if __name__ == '__main__':
    main()
