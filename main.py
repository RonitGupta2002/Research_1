import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup, SoupStrainer
import requests
import tldextract
import re
import numpy as np
import pandas as pd
import adblockparser
from urllib.parse import urlparse
import argparse
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import random
import pyautogui
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import os
import psutil
from browsermobproxy import Server
import json
import validators
from BidCollector import BidCollector


# ADDING CONSENT-O-MATIC (+CONSENT) [NO NEED!]
# ADDING POP-UP BLOCKERS (+ADDITIONAL) [NO NEED!]

# ADD CHROMEDRIVERMANAGER! [DONE!!]
# BUILD A DIRECTORY STRUCTURE FOR DATA COLLECTION... [DONE!!]
# WHEN VISITING WEBSITES ADD A SCROLL LIMIT [DONE!!]
# PRODUCT VISITING ADD IN FIRST STEP AN AFFIRMATION!! (SEE NOTES) [RONIT!!]
# CLICK ON 'ADD TO BAD' THING! [RONIT!!]
# ALTERNATE "GOOGLE SEARCH BUTTON" (SEE NOTES) [DONE!!] [button = driver.find_element(By.XPATH, "//textarea[@aria-label='Search']")]
# ALTERNATE CLICKING ON THE FIRST GOOGLE SEARCH RESULT (SEE NOTES) [DONE!!] [first_result_xpath = '//div[@id="rso"]//div[1]//a']
# MAYBE ALTERNATE FOR FACEBOOK 'X' [DONE!!] [x_button = driver.find_element(By.XPATH, '//div[@aria-label="Close"]')]
# FIND IF ANY FLAG IN SELENIUM TO DISABLE LOCATION, POP-UPS TO BE HANDLED [YASH!!] ["--disable-geolocation", "--disable-extensions"]
# WHY SSL ERROR???? [RONIT!!]
# INTEGRATE BIDCOLLECTOR MODULE!!
# Intgrate JS execute to get 'MoatSuperV26' object!!
# REAFFIRMATION!!!!! [RONIT!!]
# SCREENSHOT ISSUE?? FIX LENGTH FOR VERRRYYY LONG PAGES? [RONIT!!]
# REMOVE ERROR (MITM) [RONIT!!]

# Your connection is not private! (asks to click on Advanced)
# Google Ad blocks the entire page!
# Study the kind of ads that appear when opening a website! 
# Show notifications!
# Sign up for news letter!
# Customised accept cookies (blocks the page)!
# Customised sign up for newletter (blocks the page)!
# Defo scroll till bottom and go back up and add a waiting time so that ads can load!


# MAKE CHANGES IN THE CODE FOR CONTROLLED AND TREATMENT PHASE!!!!! (2 CHROMEDRIVERS)

# TIGERVNC FOR HEADLESS! [GO HEADLESS]
# LOGGING ERRORS AND EVENTS



NUMBER_OF_PAUSES = 6
RANDOM_SLEEP_MIN = 1
RANDOM_SLEEP_MAX = 5
NUM_MOUSE_MOVES = 3
PERSONAS = 2
THRESHOLD_ADS = 3
WEBSITES_PER_PERSONA = 3



def getChromeOptionsObject():

    chrome_options = webdriver.ChromeOptions()

    # chrome_options.add_argument('--headless')
    
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    # chrome_options.add_argument("--disable-gpu")
    
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1536,864")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    # chrome_options.add_argument(directory)
    # chrome_options.add_argument(profileDirectory)
    # chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

    return chrome_options



class ProxyManger:

    _BMP = r"C:\Users\sdala\OneDrive\Desktop\Crawler\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat"
    

    def __init__ (self):
        self.__server = Server (ProxyManger._BMP)
        self.__client = None

    def start_server(self):
        self.__server.start() 
        return self.__server

    def start_client(self):
        self.__client = self.__server.create_proxy(params={"trustAllservers":"true"})
        return self.__client
    
    @property
    def client(self):
        return self.__client

    @property
    def server(self):
        return self.__server
    


def configureProxy(port):
	'''
	Instatiate and start browsermobproxy to collect HAR files and accordingly configure chrome options
	Killing open ports:
		- lsof -i:<port>
		- kill -9 <PID>
	'''
	ROOT_DIRECTORY = r"C:\Users\sdala\OneDrive\Desktop\Selenium\Brand";
	
	try:
		print("Total browsermobproxy instances currently running:", os.system("ps -aux | grep browsermob | wc -l"))
		os.system("ps -eo etimes,pid,args --sort=-start_time | grep browsermob | awk '{print $2}' | sudo xargs kill")
		print("Total browsermobproxy instances currently running:", os.system("ps -aux | grep browsermob | wc -l"))
		print("Killed all the zombie instances of browsermobproxy from previous visit!")
		for proc in psutil.process_iter():
			if proc.name() == "browsermob-proxy":
				proc.kill()
	except:
		pass
	try:
		from signal import SIGTERM # or SIGKILL
		for proc in psutil.process_iter():  
			for conns in proc.connections(kind='inet'):
				if conns.laddr.port == 8022:
					proc.send_signal(SIGTERM)
	except:
		pass
	
	try:
		proxy.close()
	except:
		pass
	try:
		server.close()
	except:
		pass
	try:
		server = Server(os.path.join(ROOT_DIRECTORY, "browsermob-proxy-2.1.4", "bin", "browsermob-proxy"), options={'port': port})
		server.start()
		time.sleep(2)
		proxy = server.create_proxy()
	except BaseException as error:
		print("\nAn exception occurred:", traceback.format_exc(), "in configureProxy()")
		# logger.write("\n[ERROR] configureProxy():\n" + str(traceback.format_exc()))
		return None, None, None

	# Instantiate chromedriver options
	chrome_options = getChromeOptionsObject()

	# Associate proxy-related settings to the chromedriver
	chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
	chrome_options.add_argument("--ignore-ssl-errors=yes")
	chrome_options.add_argument("--use-littleproxy false")
	chrome_options.add_argument("--proxy=127.0.0.1:%s" % port)
	
	return server, proxy, chrome_options



# Function to move the mouse randomly within the screen boundaries
def move_mouse_randomly(mouseMoves):
    screen_width, screen_height = pyautogui.size()
    
    while mouseMoves:
        # Generate random coordinates within the screen boundaries
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        
        # Move the mouse to the random coordinates
        pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.5))
        
        # Pause for a random duration before the next move
        time.sleep(random.uniform(0.5, 3.0))

        mouseMoves = mouseMoves - 1



def consents(driver):
        print("")
        # ########################## PROBLEM???? #########################################
        # pop-up request to access location - HANDLED!
        try:
            buttonPreciseLocation = driver.find_element(By.XPATH, r"/html/body/div[5]/div/div[4]/div/div[2]/span/div/div[2]/div[3]/g-raised-button/div/div")
            buttonPreciseLocation.click()
            time.sleep(3)
            print("something something")

        except Exception as e:
            print("something something error")
            pass


        try:
            not_now_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Not now')]"))
            )

            # Click on the 'Not now' button
            not_now_button.click()
            print("something something2")

        except Exception as e:
            print("something something error2")
            pass


        # # ########################## PROBLEM???? #########################################
        # # USE PRECISE LOCATION - HANDLED!
        # try:
        #     # ALLOW
        #     # buttonPreciseLocation = driver.find_element(By.XPATH, r"/html/body/div[5]/div/div[6]/div/div[2]/span/div/div[2]/div[2]/update-location/g-raised-button/div/div/div[2]")
        #     # NOT NOW!!
        #     buttonPreciseLocation = driver.find_element(By.XPATH, r"/html/body/div[5]/div/div[6]/div/div[2]/span/div/div[2]/div[3]/g-raised-button/div/div")
        #     # /html/body/div[5]/div/div[7]/div/div[2]/span/div/div[2]/div[3]/g-raised-button/div/div
        #     buttonPreciseLocation.click()
        #     time.sleep(10)

        # except Exception as e:
        #     pass




def createPersona(brand, driver):


    # [1] BRAND.COM
    # [2] FACEBOOK
    # [3] FACEBOOK REDIRECTION
    # [4] INSTAGRAM
    # [5] GET BRAND WEBSITE

    ########################################## PICK A BRAND ####################################################
    # We pick a brand from the pre-compiled list of all the brands
    brand = brand.lower()
    print("The brand is :", brand)
    ############################################################################################################




    # directory = "C:\\Users\\sdala\\AppData\\Local\\Google\\Chrome\\User Data\\"
    # directory = "user-data-dir=" + directory + brand + str(numPersonas)
    # profileDirectory = "profile-directory=" + brand + "Persona" + str(numPersonas)

    # chrome_options = getChromeOptionsObject(directory, profileDirectory)


    # 'user-data-dir=C:\\Users\\gupta\\AppData\\Local\\Google\\Chrome\\User Data'
    # 'profile-directory=Profile 1'
    

    print("it worked!")



    ################################################# PROBLEM?? #########################################################
    # The tag of the button changes every once in a while? What to do about it??
    google_search_button = r"/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea"


    # SEARCHING THE BRANDS DOMAIN ON GOOGLE AND CLICKING ON THE FIRST RESULT
    driver.get("https://google.com")
    flag = 0
    while (flag == 0):
        try:
            button = driver.find_element(By.XPATH, google_search_button)
            flag = 1
        except Exception as e:
            pass
    send = brand + ".com"
    button.send_keys(send)
    button.send_keys(Keys.RETURN)
    time.sleep(2)

    consents(driver)

    print("check1")
    #driver.find_element(By.XPATH, '(//h3)[1]').click() # ?????????????????????????????????
    driver.find_element(By.CSS_SELECTOR, "div.tF2Cxc a").click()
    print("check2")
    time.sleep(3)

    
    # Scrolling the brands website when googled "brand.com"
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    random_integers = random.sample(range(1, total_height + 1), NUMBER_OF_PAUSES)
    move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
    for i in range(1, total_height, 2):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        if i in random_integers:
            move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
            time.sleep(random.randint(RANDOM_SLEEP_MIN, RANDOM_SLEEP_MAX))
    time.sleep(2)
    try:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(1)
    except Exception as e:
        print("error areaaaaaa 1 ", e)



    #################### 5 PRODUCT CLICKING (on product page) or random 5 links!!! #########################################



    # FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK
    driver.execute_script("window.open('');")   
    driver.switch_to.window(driver.window_handles[-1])
    driver.get('https://google.com')
    time.sleep(2)
    # 50 - 50 % CHANCE OF LOCATING THIS BUTTON!!!!!!! (let us see how it works now)
    flag = 0
    while (flag == 0):
        try:
            ################################################# PROBLEM?? #########################################################
            # The tag of the button changes every once in a while? What to do about it??
            button = driver.find_element(By.XPATH, google_search_button)
            flag = 1
        except Exception as e:
            pass
    send = brand + " facebook"
    button.send_keys(send)
    button.send_keys(Keys.RETURN)
    time.sleep(2)

    consents(driver)

    #driver.find_element(By.XPATH, '(//h3)[1]').click()
    driver.find_element(By.CSS_SELECTOR, "div.tF2Cxc a").click()
    time.sleep(3)

    # ERROR PRONE!!! (let us see how it works now)
    # Facebook scrolling and redirection and then scrolling
    try:
        # Finding the 'X' button
        x_button = driver.find_element(By.XPATH, r"/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div")
        x_button.click()
        time.sleep(2)

        # Scrolling the facebook page
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        total_height = total_height * 2
        random_integers = random.sample(range(1, total_height + 1), NUMBER_OF_PAUSES)
        move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
        for i in range(1, total_height, 2):
            driver.execute_script("window.scrollTo(0, {});".format(i))
            if i in random_integers:
                move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
                time.sleep(random.randint(RANDOM_SLEEP_MIN, RANDOM_SLEEP_MAX))
        time.sleep(2)

        # Redirection using the facebook link
        # The class of the 'span' tag does not dynamically change with each run and is the same for every facebook homepage!!!
        try:
            url = driver.find_element(By.XPATH, r'(//span)[@class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm x1qq9wsj x1yc453h"]')
            url.click()
            driver.switch_to.window(driver.window_handles[-1])

            ################################################# ??? #########################################################
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "footer")))
            except Exception as e:
                pass

            # Scrolling the brands website (or not!!)
            total_height = int(driver.execute_script("return document.body.scrollHeight"))
            random_integers = random.sample(range(1, total_height + 1), NUMBER_OF_PAUSES)
            move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
            for i in range(1, total_height, 2):
                driver.execute_script("window.scrollTo(0, {});".format(i))
                if i in random_integers:
                    move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
                    time.sleep(random.randint(RANDOM_SLEEP_MIN, RANDOM_SLEEP_MAX))
            time.sleep(2)


        except Exception as e:
            pass

    except Exception as e:
        pass


    # INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("https://google.com")
    flag = 0
    while (flag == 0):
        try:
            button = driver.find_element(By.XPATH, google_search_button)
            flag = 1
        except Exception as e:
            pass
    send = brand + " instagram"
    button.send_keys(send)
    button.send_keys(Keys.RETURN)
    time.sleep(2)

    consents(driver)

    try:
        #driver.find_element(By.XPATH, '(//h3)[1]').click()
        stored = driver.find_element(By.CSS_SELECTOR, "div.tF2Cxc a")
        stored.click()
        time.sleep(7)

        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        random_integers = random.sample(range(1, total_height + 1), NUMBER_OF_PAUSES)
        move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
        for i in range(1, total_height, 2):
            driver.execute_script("window.scrollTo(0, {});".format(i))
            if i in random_integers:
                move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
                time.sleep(random.randint(RANDOM_SLEEP_MIN, RANDOM_SLEEP_MAX))
        time.sleep(2)
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(1)
        except Exception as e:
            print("error areaaaaaa 2 ", e)

    except Exception as e:
        pass



    # Opens a new window and directly get the website domain on it
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    search = "https://" + brand + ".com"
    try:
        driver.get(search)
        # Scrolling the brands website when directly websearched the domain
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        random_integers = random.sample(range(1, total_height + 1), NUMBER_OF_PAUSES)
        move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
        for i in range(1, total_height, 2):
            driver.execute_script("window.scrollTo(0, {});".format(i))
            if i in random_integers:
                move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
                time.sleep(random.randint(RANDOM_SLEEP_MIN, RANDOM_SLEEP_MAX))
        time.sleep(2)
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(1)
        except Exception as e:
            print("error areaaaaaa 3 ", e)
    except Exception as e:
        print("Website not reachable!!")


    print("FIN.")



def dataCollection(domain_dir, profile1, website, websiteCounter, driver):

    # Example usage
    profile = profile1
    site = "website"
    bid_output_path = domain_dir + "/bids.json"  # Example path to save bids
    bid_collector = BidCollector(profile, site, bid_output_path)


    filename = f"HAR.json"
    har_filepath = os.path.join(domain_dir, filename)

    # har_filepath = "HAR" + str(websiteCounter) + ".json"
    proxy.new_har(har_filepath, options={'captureHeaders': True,'captureContent':True})
    ######################################### ??? ERROR ERROR ERROR ??? ######################################
    try:
        driver.get(website)
        time.sleep(1)
    except Exception as e:
        print("The data collection could not happen for this domain :", domain_dir)
        return
         
    
    try:
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        if total_height > 2500:
            total_height = 2500
        random_integers = random.sample(range(1, total_height + 1), NUMBER_OF_PAUSES)
        move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
        for i in range(1, total_height, 2):
            driver.execute_script("window.scrollTo(0, {});".format(i))
            if i in random_integers:
                move_mouse_randomly(random.randint(0, NUM_MOUSE_MOVES))
                time.sleep(random.randint(RANDOM_SLEEP_MIN, RANDOM_SLEEP_MAX))
        time.sleep(2)
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(1)
        except Exception as e:
            print("error areaaaaaa 3 ", e)
    except Exception as e:
        print("Couldn't scroll for website", website, "and error is", e)



    filename = f"SS.png"
    ss_filepath = os.path.join(domain_dir, filename)

    # Take full-page screenshot of the webpage
    width = 1920 # HAVE TO SPECIFY WIDTH??
    try:
        height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight,document.documentElement.clientHeight,document.documentElement.scrollHeight,document.documentElement.offsetHeight);")
        driver.set_window_size(width, height)
        page_body = driver.find_element(By.TAG_NAME, "body")
        # screenshot_output_path = "SS" + str(websiteCounter) + ".png"
        page_body.screenshot(ss_filepath)
    except Exception as e:
        print("Screenshot did not take place for website", website, "and error is", e)

    try:
        with open(har_filepath, 'w') as fhar:
            json.dump(proxy.har, fhar, indent=4)
    except Exception as e:
        print("HAR file did not save for website", website, "and error is", e)
    
    try:
        fhar.close()
    except Exception as e:
        print("fhar did not close for website", website, "and error is", e)


    bid_collector.collectBids(driver)

        

if "__main__" == __name__:

    print("IT STARTS!")

    excelWebsites = pd.read_excel("FINAL_LIST.xlsx", sheet_name='Sheet3')
    selected_column = excelWebsites['Websites']
    selected_column = selected_column.head(18)
    websites = pd.DataFrame({'Websites': selected_column})


    excelBrands = pd.read_excel("BRANDSS.xlsx")
    selected_column = excelBrands['Company']
    selected_column = selected_column.head(3)
    brands = pd.DataFrame({'Brand': selected_column})
    
    websiteCounter = 0


    print(websites)
    print(brands)


    # Create a directory named 'Data Collected'
    data_collected_dir = os.path.join(os.getcwd(), 'Data Collected')
    os.makedirs(data_collected_dir, exist_ok=True)


    for index, row in brands.iterrows():

        brand = row['Brand']  # Access the value of the column
        print("\n\nBrand :", brand)

        # Create a folder for the brand
        brand_dir = os.path.join(data_collected_dir, brand)
        os.makedirs(brand_dir, exist_ok=True)


        for idx1 in range(PERSONAS):


            print("PERSONA NUMBER", idx1 + 1, "for BRAND", brand)

            server, proxy, chrome_options = configureProxy(8022)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.set_page_load_timeout(30)
            # Comment this for headless!!!
            driver.maximize_window()


            createPersona(brand, driver)


            driver.execute_script("window.open('');")   
            driver.switch_to.window(driver.window_handles[-1])
            driver.get('https://google.com')
            time.sleep(1)

            for idx2 in range(WEBSITES_PER_PERSONA):

                website = websites.iloc[websiteCounter]['Websites']
                
                # Create a folder for the domain
                domain_dir = os.path.join(brand_dir, website)
                os.makedirs(domain_dir, exist_ok=True)

                if not validators.url():
                    website = "http://" + website
                websiteCounter = websiteCounter + 1
                dataCollection(domain_dir, brand, website, websiteCounter, driver)

            
            proxy.close()
            server.stop()
            driver.quit()

    print("Entire crawl done done!")