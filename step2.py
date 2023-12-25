# import os
# import requests
# from bs4 import BeautifulSoup, SoupStrainer
# import adblockparser

# # Path to the folder containing filter lists
# filter_lists_folder = r"C:\Users\ronit\OneDrive\Desktop\Automation\filterlists"

# # Function to load filter lists from files in a folder
# def load_filter_lists(folder_path):
#     filter_lists = []
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
#         with open(file_path, "r") as file:
#             content = file.read()
#             filter_list = adblockparser.AdblockRules(content)
#             filter_lists.append(filter_list)
#     return filter_lists

# # Function to check URLs against multiple filter lists
# def check_urls_against_filter_lists(urls, filter_lists):
#     blocked_urls = []
#     for url in urls:
#         for filter_list in filter_lists:
#             for blocked_url, referring_url in url:
#                 if filter_list.should_block(blocked_url, referring_url):
#                     blocked_urls.append((blocked_url, referring_url))
#     return blocked_urls

# # Target webpage
# url = "https://luogocomune.net/21-medicina-salute/5774-covid-le-cure-proibite-video-completo"  # Replace with the URL you want to analyze

# # Social media domains to filter out
# social_media_domains = [
#     "facebook.com",
#     "twitter.com",
#     "instagram.com",
#     "youtube.com"
#     # Add other social media domains as needed
# ]

# try:
#     # Fetch webpage content
#     response = requests.get(url)

#     # Check if the request was successful
#     if response.status_code == 200:
#         # Use SoupStrainer to parse only 'a' tags
#         parse_only_links = SoupStrainer("a")
#         soup = BeautifulSoup(response.content, "html.parser", parse_only=parse_only_links)

#         # Extract all links
#         links = [link.get("href") for link in soup.find_all("a")]

#         # Remove links related to social media domains
#         links_without_social_media = [link for link in links if not any(domain in link for domain in social_media_domains)]

#         # Create a list of tuples with URLs and referring URL
#         urls_to_check = [(link, url) for link in links_without_social_media if link]

#         # Load filter lists from the folder
#         filter_lists = load_filter_lists(filter_lists_folder)

#         # Check URLs against loaded filter lists
#         blocked_urls = check_urls_against_filter_lists(urls_to_check, filter_lists)

#         # Categorize blocked URLs
#         for blocked_url, referring_url in blocked_urls:
#             print(f"Ad detected: {blocked_url}")

#             # Perform additional actions based on categorization (if needed)

#     else:
#         print(f"Failed to fetch webpage. Status code: {response.status_code}")

# except requests.exceptions.RequestException as e:
#     print("Error fetching webpage:", e)


import requests
from bs4 import BeautifulSoup, SoupStrainer
import adblockparser

# Read filter list content from a file
filter_list_content = r"C:\Users\ronit\OneDrive\Desktop\Automation\filterlists\easylist.txt"  # Replace with your filter list file path

try:
    # Create AdblockRules object by parsing the filter list content
    filter_list = adblockparser.AdblockRules(filter_list_content)

    # Target webpage
    url = "https://timesofindia.indiatimes.com/"

    # Social media domains to filter out
    social_media_domains = [
        "facebook.com",
        "twitter.com",
        "instagram.com",
        "youtube.com"
        # Add other social media domains as needed
    ]

    # Fetch webpage content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Use SoupStrainer to parse only 'a' and 'iframe' tags
        parse_only_tags = SoupStrainer(['a', 'iframe'])
        soup = BeautifulSoup(response.content, "html.parser", parse_only=parse_only_tags)

        # Extract all links and iframe sources
        links = [link.get("href") for link in soup.find_all("a")]
        iframes = [iframe.get("src") for iframe in soup.find_all("iframe")]

        # Combine links and iframe sources
        all_sources = links + iframes

        # Remove links related to social media domains
        filtered_sources = [source for source in all_sources if not any(domain in source for domain in social_media_domains)]

        # Counter for ads found on each individual link
        ads_count_dict = {}

        # Check ads for each individual link
        for source in filtered_sources:
            try:
                # Fetch content for each link
                link_response = requests.get(source)
                if link_response.status_code == 200:
                    link_soup = BeautifulSoup(link_response.content, "html.parser")
                    # Batch check URLs against filter list rules for each link
                    if filter_list.should_block(source, url):
                        ads_count_dict[source] = ads_count_dict.get(source, {"count": 0, "details": ""})
                        ads_count_dict[source]["count"] += 1

                        # Extract some identifiable feature for the ad (e.g., title, class, id)
                        ad_title = link_soup.title.text if link_soup.title else "No Title"
                        ad_details = f"Title: {ad_title}"  # You can extract more details here if available
                        ads_count_dict[source]["details"] = ad_details
            except requests.exceptions.RequestException:
                pass  # Skip if there's an issue with the link

        # Print the count of ads found on each individual link along with details
        print("Ads count on each individual link:")
        for link, ad_info in ads_count_dict.items():
            print(f"{link}: Ads count - {ad_info['count']} - Details: {ad_info['details']}")

    else:
        print(f"Failed to fetch webpage. Status code: {response.status_code}")

except FileNotFoundError:
    print("Filter list file not found. Please provide the correct file path.")
except requests.exceptions.RequestException as e:
    print("Error fetching webpage:", e)
