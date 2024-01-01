import requests
from bs4 import BeautifulSoup
import adblockparser
from urllib.parse import urlparse
import pandas as pd

# Define the filter list paths
filter_list_paths = [
    r"C:\Users\ronit\OneDrive\Desktop\Automation\filterlists\easylist.txt",
    r"C:\Users\ronit\OneDrive\Desktop\Automation\filterlists\easyprivacy.txt",
    r"C:\Users\ronit\OneDrive\Desktop\Automation\filterlists\antiadblock.txt"
    # Add paths to additional filter lists as needed
]

output_file_path = r"C:\Users\ronit\OneDrive\Desktop\Automation\Functional Website\count.xlsx"  # Replace with your desired output file path

# Function to check for ads and remove social media links
def check_ads(url):
    ad_count = 0
    ad_details = []

    try:
        # Create AdblockRules object for each filter list
        filter_lists = [adblockparser.AdblockRules(path) for path in filter_list_paths]

        # Fetch webpage content
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse all tags
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all links
            links = [link.get('href') for link in soup.find_all('a')]

            # Filter out social media links
            filtered_links = [link for link in links if not is_social_media_link(link)]

            # Check ads for each remaining link against each filter list
            for source in filtered_links:
                try:
                    # Fetch content for each link
                    link_response = requests.get(source)
                    if link_response.status_code == 200:
                        link_soup = BeautifulSoup(link_response.content, 'html.parser')

                        # Batch check URLs against each filter list
                        for filter_list in filter_lists:
                            if any(filter_list.should_block(source, url) for filter_list in filter_lists):
                                ad_count += 1

                                # Extract ad details (title, URL)
                                ad_title = link_soup.title.text if link_soup.title else 'No Title'
                                ad_details.append({'Title': ad_title, 'URL': source})
                                break  # Move to the next link once an ad is found
                except requests.exceptions.RequestException:
                    pass  # Skip if there's an issue with the link

    except Exception as e:
        print(f"Error checking ads for {url}: {e}")

    return ad_count, ad_details

# Function to check if a link is a social media link
def is_social_media_link(link):
    social_media_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com']
    parsed_url = urlparse(link)
    return any(domain in parsed_url.netloc for domain in social_media_domains)

# Read URLs from input Excel file
input_file_path = r"C:\Users\ronit\OneDrive\Desktop\Automation\Functional Website\third_party.xlsx"  # Replace with your input file path

try:
    df = pd.read_excel(input_file_path)
    ad_data = df['URL'].apply(check_ads)
    df['Ad_Count'] = [data[0] for data in ad_data]
    df['Ad_Details'] = [data[1] for data in ad_data]

    # Save results to an output Excel file
    df.to_excel(output_file_path, index=False)
    print(f"Results saved to {output_file_path}")

except FileNotFoundError:
    print("Input file not found. Please provide the correct file path.")
