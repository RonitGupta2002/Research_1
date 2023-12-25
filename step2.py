import requests
from bs4 import BeautifulSoup, SoupStrainer
import adblockparser
from urllib.parse import urlparse

# Read filter list content from a file
filter_list_content = r"C:\Users\ronit\OneDrive\Desktop\Automation\filterlists\easylist.txt"  # Replace with your filter list file path

try:
    # Create AdblockRules object by parsing the filter list content
    filter_list = adblockparser.AdblockRules(filter_list_content)

    # Target webpage
    url = "https://timesofindia.indiatimes.com/"

    # Fetch webpage content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Use SoupStrainer to parse only 'a' tags
        parse_only_tags = SoupStrainer('a')
        soup = BeautifulSoup(response.content, "html.parser", parse_only=parse_only_tags)

        # Extract all links
        links = [link.get("href") for link in soup.find_all("a")]

        # Remove links having the domain name of the provided URL
        parsed_url = urlparse(url)
        domain_to_remove = parsed_url.netloc

        filtered_links = [link for link in links if urlparse(link).netloc != domain_to_remove]

        # Counter for ads found on each individual link
        ads_count_dict = {}

        # Check ads for each individual link
        for source in filtered_links:
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
