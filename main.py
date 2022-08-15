import datetime
import os
import threading
import requests
from selenium import webdriver
import time, random
from bs4 import BeautifulSoup
import collections
collections.Callable = collections.abc.Callable
import warnings
warnings.filterwarnings(action='ignore')

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
headers = {
    'User-Agent': ua
}

threads = []

def scroll(driver):
    try:
        last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            #pause_time = random.uniform(1, 2)
            pause_time = 0.3
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(pause_time)
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight-50)")
            time.sleep(pause_time)
            new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_page_height == last_page_height:
                break
            else:
                last_page_height = new_page_height
    except Exception as e:
        print("[오류] 에러 발생: ", e)

def getHTML(url):
    global channelname, channelprofile
    print('[INFO] 동영상 정보 불러오는중...')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument(f'--user-agent={ua}')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options, executable_path='./driver/chromedriver.exe')
    driver.get(url)
    driver.implicitly_wait(10)
    scroll(driver)
    html = driver.page_source
    #open('test.txt', 'w', encoding='utf-8').write(html)
    channelprofile = ""
    try:
        channelprofile = html.split('<img id="img" class="style-scope yt-img-shadow" width="80" alt="" src="')[1].split('"')[0]
    except:
        pass
    channelname = html.split('<yt-formatted-string id="text" title="" class="style-scope ytd-channel-name">')[1].split('</yt-formatted-string>')[0]
    bs = BeautifulSoup(html, 'html.parser')
    product_list = bs.select("a[class^='yt-simple-endpoint style-scope ytd-grid-video-renderer']")
    for goods in product_list:
        try:
            goods = str(goods)
            title = goods.split('title="')[1].split('">')[0]
            runtime = goods.split(' 전 ')[1].split(' 조회수 ')[0].replace(" ", "").replace("시간", "h").replace("분", "m").replace("초", "s")
            try:
                id = goods.split('href="/watch?v=')[1].split('"')[0] #href="/shorts/-HpaIPHilPU"
            except:
                id = goods.split('href="/shorts/')[1].split('"')[0]
            video[id] = runtime + " " + title
        except Exception as e:
            pass
    driver.quit()
    print('[INFO] 동영상 정보 불러오기 완료')
    print('[INFO] 동영상 개수:', len(video))

        
def getImage():
    dirname = channelname.rstrip().replace('?', '').replace('!', '').replace('.', '').replace('"', '').replace("'", '').replace('<', '').replace('>', '').replace(':', '').replace('|', '').replace('/', '')
    dir = "./image/"+dirname+"/"
    print('[INFO] 저장경로: ' + dir)
    now = datetime.datetime.now().strftime('%Y.%m.%d ')
    if not os.path.exists(dir):
        os.makedirs(dir)
    if channelprofile == "":
        print('[오류] 썸네일 추출 실패')
    else:
        try:
            with open(f"{dir}{now}-프로필-{channelname}.jpg", 'wb') as photo:
                pic = requests.get(channelprofile)
                photo.write(pic.content)
            print('[INFO] 썸네일 추출 성공')
        except Exception as e:
            pass
    for id in video:
        try:
            th = threading.Thread(target=download, args=(id, dir,))
            th.start()
            threads.append(th)
            #print("[INFO] 추출완료: " + video[id]) #제목  \ / : * ? " < > |
            #savename = video[id].replace('?', '').replace('!', '').replace('.', '').replace('"', '').replace("'", '').replace('<', '').replace('>', '').replace(':', '').replace('|', '').replace('/', '')
            #date = datetime.datetime.strftime(datetime.datetime.strptime(requests.get(f"https://www.youtube.com/watch?v={id}").text.split(',"dateText":{"simpleText":"')[1].split('"')[0].replace(" ", ''),"%Y.%m.%d."),"%Y.%m.%d")
            #with open(f"{dir}{date} {savename}.jpg", 'wb') as photo:
            #    pic1 = requests.head(f"http://img.youtube.com/vi/{id}/maxresdefault.jpg")
            #    pic2 = requests.head(f"http://img.youtube.com/vi/{id}/sddefault.jpg")
            #    pic3 = requests.head(f"http://img.youtube.com/vi/{id}/hqdefault.jpg")
            #    h1 = pic1.headers['content-length']
            #    h2 = pic2.headers['content-length']
            #    h3 = pic3.headers['content-length']
            #    if int(h1) >= int(h2) >= int(h3) or int(h1) >= int(h3) >= int(h2):
            #        photo.write(requests.get(f"http://img.youtube.com/vi/{id}/maxresdefault.jpg").content)
            #    elif int(h2) >= int(h1) >= int(h3) or int(h2) >= int(h3) >= int(h1):
            #        photo.write(requests.get(f"http://img.youtube.com/vi/{id}/sddefault.jpg").content)
            #    else:
            #        photo.write(requests.get(f"http://img.youtube.com/vi/{id}/hqdefault.jpg").content)
            #    #photo.write(pic.content)
        except:
            pass
    for th in threads:
        th.join()
    
def download(id, dir,):
    try:
        print("[INFO] 추출완료: " + video[id]) #제목  \ / : * ? " < > |
        savename = video[id].replace('?', '').replace('!', '').replace('.', '').replace('"', '').replace("'", '').replace('<', '').replace('>', '').replace(':', '').replace('|', '').replace('/', '')
        date = datetime.datetime.strftime(datetime.datetime.strptime(requests.get(f"https://www.youtube.com/watch?v={id}").text.split(',"dateText":{"simpleText":"')[1].split('"')[0].replace(" ", '').replace('최초공개:', ''),"%Y.%m.%d."),"%Y.%m.%d")
        with open(f"{dir}{date} {savename}.jpg", 'wb') as photo:
            pic1 = requests.head(f"http://img.youtube.com/vi/{id}/maxresdefault.jpg")
            pic2 = requests.head(f"http://img.youtube.com/vi/{id}/sddefault.jpg")
            pic3 = requests.head(f"http://img.youtube.com/vi/{id}/hqdefault.jpg")
            h1 = pic1.headers['content-length']
            h2 = pic2.headers['content-length']
            h3 = pic3.headers['content-length']
            if int(h1) >= int(h2) >= int(h3) or int(h1) >= int(h3) >= int(h2):
                photo.write(requests.get(f"http://img.youtube.com/vi/{id}/maxresdefault.jpg").content)
            elif int(h2) >= int(h1) >= int(h3) or int(h2) >= int(h3) >= int(h1):
                photo.write(requests.get(f"http://img.youtube.com/vi/{id}/sddefault.jpg").content)
            else:
                photo.write(requests.get(f"http://img.youtube.com/vi/{id}/hqdefault.jpg").content)
            #photo.write(pic.content)
    except:
        pass

if __name__ == '__main__':
    global video
    video = {}
    link = input('[INFO] 유튜브 링크를 입력해주세요 > ')
    getHTML(link)
    getImage()
    print('[INFO] 작업 종료')