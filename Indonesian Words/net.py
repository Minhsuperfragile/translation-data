from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
import json
import random
from tkinter import *
import tkinter.messagebox
from sys import platform
import ctypes  # An included library with Python install.  

word_dict = json.load(open("result.json"))

alphabet = 'A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z'
alphabet = alphabet.lower().split(',')

user_agents = [
    # Add your list of user agents here
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]

PROXY = "103.237.144.232:1311"
PROXY_PASS = "vvcknvzt:hnqek9w3h7i5"
LINK = "https://vi.glosbe.com/id/vi"
edge_option = webdriver.EdgeOptions()
edge_option.add_argument(f"--proxy-server={PROXY}")
# edge_option.add_argument("--headless") # this option will not show up edge window
edge_option.add_argument('--disable-blink-features=AutomationControlled')
edge_option.add_argument('--disable-popup-blocking')
edge_option.add_argument('--disable-extensions')
edge_option.add_argument('--no-sandbox')
edge_option.add_argument('--disable-dev-shm-usage')

user_agent = random.choice(user_agents)
edge_option.add_argument(f'user-agent={user_agent}')

# driver = webdriver.Edge(seleniumwire_options=options, options=edge_option)
driver = webdriver.Edge(options = edge_option)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
try:
    driver.get(LINK)
except WebDriverException as e:
    print(f'Error : {e.msg}')

def pop_up_message(msg:str):
    if platform == "linux":
        window = Tk()
        window.wm_withdraw()

        #message at x:200,y:200
        window.geometry("1x1+200+200")#remember its .geometry("WidthxHeight(+or-)X(+or-)Y")
        tkinter.messagebox.showerror(title="error",message=msg,parent=window)
    else:
        ctypes.windll.user32.MessageBoxW(0, msg, "Hit a capcha", 2)

def log_when_stop(file, word):
    with open(file, 'w') as f:
        word_index = word_dict[word[0].lower()].index(word)
        letter_index = alphabet.index(word[0].lower())
        f.write(f'{letter_index} {word_index-1}')

def search_word(driver:webdriver, word, delay = 3, test=False):
    MAXTRY = 1
    count = 0
    while True:
        try:
            try:
                myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME,"q")))
            except TimeoutException:
                print( "Searching took too much time!")
            # driver.get("https://vi.glosbe.com/id/vi/" + word)
            search_bar = driver.find_element(By.NAME,"q")
            search_bar.clear()
            search_bar.send_keys(word)
            search_bar.send_keys(Keys.RETURN)
            break
        except NoSuchElementException:
            driver.refresh()
            count += 1
            if count >= MAXTRY:
                print("Encounter a capcha")
                if not test:
                    log_when_stop("stop_log.txt", word)
                
                pop_up_message(f"Data scraper stopped at {word}")
                raise Exception
    
def get_translation(driver, div1, div2):
    lang1 = driver.find_elements(By.CSS_SELECTOR, div1)
    lang2 = driver.find_elements(By.CSS_SELECTOR, div2)

    return lang1,lang2

def write_to_csv(lang1, lang2, file):
    if len(lang1) < 1 or len(lang2) < 1:
        return
    with open(file, 'a', encoding='utf-8') as f:    
        for i, _ in enumerate(lang1):
            f.write(f'{lang1[i].text}ッ{lang2[i].text}\n')
            
def load_all(driver,button_css,try_again ,delay=3):
    while True:
        try:
            try:
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, button_css)))
            except TimeoutException:
                try:
                    print("try again")
                    load_more = driver.find_element(By.CSS_SELECTOR, try_again)
                    webdriver.ActionChains(driver).move_to_element(load_more).click(load_more).perform()
                except NoSuchElementException:
                    break
            load_more = driver.find_element(By.CSS_SELECTOR, button_css)
        
            webdriver.ActionChains(driver).move_to_element(load_more).click(load_more).perform()
                
            # time.sleep(2)
        except NoSuchElementException:
            print("no more")
            break

def continue_from_last(file):
    text:str
    with open(file,'r') as f:
        text = f.readline()
  
    return tuple(map(int,text.split()))

button_class = "button[class='button-xs']"
try_again_button_class = "button[class='m-auto text-button-xs']"
div1 = "div[class='w-1/2 dir-aware-pr-1 '][lang='id']"
div2 = "div[class='w-1/2 dir-aware-pl-1 '][lang='vi']"
log_file = "stop_log.txt"
link = "https://vi.glosbe.com/id/vi/"
csv_file = "result_net.csv"


i,j = continue_from_last(log_file)
print(f'{i} {j}')
try:
    for letter in alphabet[i:]:
        if letter != alphabet[i]:
            j = 0
        for word in word_dict[letter][j:]:
            search_word(driver, word, delay=20)
            load_all(driver, button_class,try_again_button_class, delay=5)
            id,vi = get_translation(driver, div1, div2)
            write_to_csv(id, vi, csv_file)
except KeyboardInterrupt:
    print(word)
    log_when_stop(log_file, word)
    raise KeyboardInterrupt
