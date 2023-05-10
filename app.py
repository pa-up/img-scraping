import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import cv2
import numpy as np
import requests
from io import BytesIO
import zipfile
from PIL import Image
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome import service as fs


item_ls = []

def browser_setup():
    """ブラウザを起動する関数"""
    #ブラウザの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #ブラウザの起動
    # webdriver_managerによりドライバーをインストール
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

    st.write("画像検索窓の表示が成功")

    # サムネイル画像のURL取得
    browser.get(url.format(q=KEYWORD))

    # ページの一番下へスクロールして新しいサムネイル画像を表示させる
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(1)

    # サムネイル画像のリンクを取得
    thumbnail_elements = browser.find_elements(By.CSS_SELECTOR, "img.rg_i")
    thumbnail_URLS = [element.get_attribute('src') for element in thumbnail_elements]
    tmb_alts = [tmb.get_attribute('alt') for tmb in thumbnail_elements]

    # # ダウンロードする枚数の上限
    # download_number = 100
    # # クリックなど動作後に待つ時間(秒)
    # sleep_between_interactions = 2

    # count = 0
    # for img_url in thumbnail_URLS:
    #     if count + 1 >= download_number:
    #         break
    #     data = {
    #         '画像URL':img_url,
    #     }
    #     item_ls.append(data)
    #     count = count + 1

    # 少し待たないと正常終了しなかったので3秒追加
    time.sleep(5)
    browser.quit()
    
    return item_ls , thumbnail_URLS , thumbnail_elements


def url_to_img_folda(thumbnail_URLS , saved_img_folder , thumbnail_elements):
    count = 0
    for thumbnail_element in thumbnail_elements:
        # サムネイル画像をクリック
        thumbnail_element.click()

        # url取得
        url = thumbnail_element.get_attribute('src')  # サムネイル画像のsrc属性値

        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = np.array(img)
        
        file_name = saved_img_folder + str(count) + ".jpg"
        cv2.imwrite(file_name , img)


def main():
    KEYWORD = ""
    st.title("画像を一括取得")
    st.write("<p></p>", unsafe_allow_html=True)
    KEYWORD = st.text_input("検索キーワード")
    st.write("<p></p>", unsafe_allow_html=True)

    if KEYWORD != "":
        browser = browser_setup()
        item_ls , thumbnail_URLS , thumbnail_elements = get_url(KEYWORD , browser)

        saved_img_folder = "./img/"
        if not os.path.exists(saved_img_folder):
            os.makedirs(saved_img_folder)
        
        # 全ての画像URLを画像ファイルを格納したファイルに格納
        url_to_img_folda(thumbnail_URLS , saved_img_folder , thumbnail_elements)

        # フォルダを圧縮してバイトストリームに変換
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(saved_img_folder):
                for file in files:
                    zf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), saved_img_folder))
        zip_buffer.seek(0)

        # ダウンロードボタンを作成
        st.download_button(
            label="Download folder",
            data=zip_buffer.getvalue(),
            file_name="img.zip",
            mime="application/zip"
        )

        # df = pd.DataFrame(item_ls)
        # csv = df.to_csv(index=False)

        # # CSVファイルのダウンロードボタンを表示
        # st.download_button(
        #     label='CSVをダウンロード',
        #     data=csv,
        #     file_name='画像データ.csv',
        #     mime='text/csv'
        # )


if __name__ == '__main__':
    main()
