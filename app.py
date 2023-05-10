import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
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
    # サムネイル画像のリンクを取得(ここでコケる場合はセレクタを実際に確認して変更する)
    thumbnail_results = browser.find_element(By.CSS_SELECTOR,"img.rg_i")

    st.write("thumbnail_results : ")
    st.write(thumbnail_results)
    st.write("")

    # ダウンロードする枚数
    download_number = 50
    # クリックなど動作後に待つ時間(秒)
    sleep_between_interactions = 2

    # サムネイルをクリックして、各画像URLを取得
    image_urls = set()
    for img in thumbnail_results[:download_number]:

        st.write("img : ")
        st.write(img)
        st.write("")

        try:
            img.click()
            time.sleep(sleep_between_interactions)
        except Exception:
            continue
        # 一発でurlを取得できないので、候補を出してから絞り込む
        # 'n3VNCb'は変更されることあるので、クリックした画像のエレメントをみて適宜変更する
        url_candidates = browser.find_element(By.CSS_SELECTOR,'n3VNCb')

        st.write("")
        st.write("url_candidates : ", url_candidates)
        st.write("")

        for candidate in url_candidates:
            url = candidate.get_attribute('src')
            if url and 'https' in url:
                image_urls.add(url)
                st.write("url : ",url)
    # 少し待たないと正常終了しなかったので3秒追加
    time.sleep(sleep_between_interactions+3)
    browser.quit()
    return image_urls


def get_data(image_urls):
    for image_url in image_urls:
        data = {
            '画像URL':image_url,
        }
        item_ls.append(data)


def main():
    KEYWORD = ""
    st.title("画像を一括取得")
    st.write("<p></p>", unsafe_allow_html=True)
    KEYWORD = st.text_input("検索キーワード")
    st.write("<p></p>", unsafe_allow_html=True)

    if KEYWORD != "":
        browser = browser_setup()
        image_urls = get_url(KEYWORD , browser)
        get_data(image_urls)
        df = pd.DataFrame(item_ls)
        csv = df.to_csv(index=False)

        # CSVファイルのダウンロードボタンを表示
        st.download_button(
            label='CSVをダウンロード',
            data=csv,
            file_name='画像データ.csv',
            mime='text/csv'
        )


if __name__ == '__main__':
    main()