import time
import pandas as pd
from urllib.parse import urlparse
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Function to extract domain name from a URL
def get_domain_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Create an empty DataFrame to store links
links_data = pd.DataFrame(columns=['Webpage_Link', 'Actual_Link'])

# Assign file path of the Excel sheet containing URLs
excel_file_path = r"C:\Users\ronit\OneDrive\Desktop\Automation\Functional Website\final_1.xlsx"

# Get URLs from the Excel sheet
urls_to_scrape = pd.read_excel(excel_file_path, usecols=[0]).iloc[:, 0].tolist()

# Initialize Selenium WebDriver (assuming Chrome)
driver_path = 'PATH_TO_CHROMEDRIVER'  # Replace 'PATH_TO_CHROMEDRIVER' with the actual path
options = ChromeOptions()
options.add_argument("--headless") # Run Chrome in headless mode
driver = webdriver.Chrome(options = options)

# Loop through each URL and extract the actual URLs using Selenium
for url_to_scrape in urls_to_scrape:
    try:
        driver.get(url_to_scrape)
        time.sleep(5)  # Give time for the page to load (adjust as needed)

        # Get all anchor elements with href attribute starting with "https://"
        elements = driver.find_elements("xpath","//a[starts-with(@href, 'https://')]")

        found_links = False  # Flag to determine if subpage links are found

        # Extract actual links
        for element in elements:
            actual_link = element.get_attribute("href")

            # Compare domain names of the webpage link and actual link
            if get_domain_name(url_to_scrape) == get_domain_name(actual_link):
                # Append the links to the DataFrame
                links_data = links_data._append({'Webpage_Link': url_to_scrape, 'Actual_Link': actual_link}, ignore_index=True)
                found_links = True  # Set flag to True if links are found

        # If no subpage links are found, set Actual_Link value as 0
        if not found_links:
            links_data = links_data._append({'Webpage_Link': url_to_scrape, 'Actual_Link': 0}, ignore_index=True)

    except WebDriverException as e:
        print(f"Error occurred while processing {url_to_scrape}: {e}")

# Quit the Selenium WebDriver
driver.quit()

# Save the extracted links to a new Excel file
output_file_path = r"C:\Users\ronit\OneDrive\Desktop\Automation\Functional Website\sublinks.xlsx"
links_data.to_excel(output_file_path, index=False)



# import time
# from bs4 import BeautifulSoup
# import requests
# import re
# import pandas as pd
# from urllib.parse import urlparse

# # Function to extract HTML document from a given URL with a specified timeout
# def getHTMLdocument(url, timeout=10):
#     try:
#         response = requests.get(url, timeout=timeout)
#         return response.text
#     except requests.RequestException as e:
#         print(f"Error occurred: {e}")
#         return None

# # Read URLs from an Excel file using pandas
# def get_urls_from_excel(file_path):
#     data = pd.read_excel(file_path)  # Assuming the URLs are in the first column
#     urls = data.iloc[:, 0].tolist()
#     return urls

# # Function to extract domain name from a URL
# def get_domain_name(url):
#     parsed_url = urlparse(url)
#     return parsed_url.netloc

# # Create an empty DataFrame to store links
# links_data = pd.DataFrame(columns=['Webpage_Link', 'Actual_Link'])

# # Assign file path of the Excel sheet containing URLs
# excel_file_path = r"C:\Users\ronit\OneDrive\Desktop\Automation\Functional Website\final_1.xlsx"

# # Get URLs from the Excel sheet
# urls_to_scrape = get_urls_from_excel(excel_file_path)

# # Loop through each URL and extract the actual URLs
# for url_to_scrape in urls_to_scrape:
#     # Create document with a timeout of 10 seconds
#     html_document = getHTMLdocument(url_to_scrape, timeout=10)
#     if html_document is None:
#         # Append status code to the DataFrame indicating failure to load
#         links_data = links_data._append({'Webpage_Link': url_to_scrape, 'Actual_Link': 'Failed to Load'}, ignore_index=True)
#         continue  # Skip this website and proceed to the next one
#     # Create soup object
#     soup = BeautifulSoup(html_document, 'html.parser')

#     found_links = False  # Flag to determine if subpage links are found

#     # Find all the anchor tags with "href" attribute starting with "https://"
#     for link in soup.find_all('a', attrs={'href': re.compile("^https://")}):
#         # Get the actual URLs
#         actual_link = link.get('href')

#         # Compare domain names of the webpage link and actual link
#         if get_domain_name(url_to_scrape) == get_domain_name(actual_link):
#             # Append the links to the DataFrame
#             links_data = links_data._append({'Webpage_Link': url_to_scrape, 'Actual_Link': actual_link},ignore_index=True)
#             found_links = True  # Set flag to True if links are found

#     # If no subpage links are found, set Actual_Link value as 0
#     if not found_links:
#         links_data = links_data._append({'Webpage_Link': url_to_scrape, 'Actual_Link': 0},ignore_index=True)

# # Save the extracted links to a new Excel file
# output_file_path = r"C:\Users\ronit\OneDrive\Desktop\Automation\Functional Website\sublinks.xlsx"
# links_data.to_excel(output_file_path, index=False)


