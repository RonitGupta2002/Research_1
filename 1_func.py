from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
import pandas as pd

excel_file_path = r"C:\Users\ronit\OneDrive\Desktop\Automation\Functional Website\curated.xlsx"
df = pd.read_excel(excel_file_path)


options = ChromeOptions()
options.add_argument("--headless")

def functionOrNot(url):
    flag = True
    if (url[:7] != r"http://" and url[:8] != r"https://"):
        urlnew = "http://" + url
    try:
        driver = webdriver.Chrome(options = options)
        driver.get(urlnew)
        titlePage = driver.title
        titlePage = titlePage.lower()

        if (titlePage == ""):
            flag = False
        elif ("404" in titlePage or "sale" in titlePage or "wordpress" in titlePage or "moved" in titlePage or "connection timed out" in titlePage 
              or "coming soon" in titlePage or "contact" in titlePage or "domain owner" in titlePage or "youtube" in titlePage or "prank" in titlePage 
              or "usercheck" in titlePage or url in titlePage or "server" in titlePage or "bluehost.com" in titlePage or "hostinger" in titlePage 
              or "just a moment" in titlePage or "forbidden!" in titlePage):
            flag = False
        else:
            print("Url is ", urlnew," and Page title:", titlePage)
            print()
    except Exception as e:
        print("Website is not functional ", urlnew)
        flag = False
    
    driver.quit()
    
    if (flag):
        return "Yes"
    else:
        return "No"


df["ProcessedColumn"] = df["Websites"].apply(functionOrNot)

df.to_excel("./final.xlsx", index = False)