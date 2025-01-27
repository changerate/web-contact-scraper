import requests
from bs4 import BeautifulSoup # Parsing html
import re                   # Regular expression - used for finding phone numbers & emails
import pandas as pd         # Storing data as dataframes
from random import randint  # Used for choosing a random header from the gernerated list
import os                   # For saving files: accessing OS info from user.
from googlesearch import search

# allows us a list of headers to send.
# check your computer headers with: http://httpbin.org/headers
SCRAPEOPS_API_KEY = '59cfb68f-5843-432f-a4d3-81e93fa9a30e'


def get_random_header():
    # Use a Scrape Ops API to obtain a header list, only use one each time
    response = requests.get(
        'http://headers.scrapeops.io/v1/browser-headers?api_key=' +
        SCRAPEOPS_API_KEY)
    json_response = response.json()
    header_list = json_response.get('result', [])
    random_index = randint(0, len(header_list) - 1)
    return header_list[random_index]


def get_all_websites():
    searchTerm = input("\n\nEnter a Google search: ")
    search_results = list(search(searchTerm, num_results=50))
    print("\n\n")
    
    # Extract actual URLs from search results
    web_list = [result for result in search_results if result.startswith("http")]
    return web_list


def get_email_and_numbers(m, the_header):
    try:
        # requests website's html (from web_list)
        request = requests.get(m, headers=the_header)
        request.raise_for_status()  # Check for any errors in the response

        # Parses HTML with BeautifulSoup
        soup = BeautifulSoup(request.content, 'html.parser')
        emails = []
        phone_numbers = []

        email_pattern = re.compile(
            r'\b[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b')
        phone_pattern = re.compile(
            r'\b(?:(?:\+\d{1,2}[-.\s]*)?(?:(?:\(\d{3}\)|[2-9]\d{2})(?:[-.]|\s?-\s?|\s?\.\s?)\d{3}(?:[-.]|\s?-\s?|\s?\.\s?)\d{4}))\b')
        
        # Go through readable html elements
        for word in soup.find_all(['p', 'a', 'div', 'span'], recursive=True, limit=1000): # Has a limit to the amount of recursive HTML elements to go through
            word_text = word.get_text()

            # Check href attributes for mailto: links
            if word.name == 'a' and word.get('href'):
                href = word.get('href')
                if href.startswith('mailto:'):
                    emails.append(href[7:])  # Remove 'mailto:' prefix
                elif href.startswith('tel:'):
                    phone_numbers.append(href[4:])  # Remove 'tel:' prefix
            if word_text:
                emails.extend(email_pattern.findall(word_text))
                phone_numbers.extend(phone_pattern.findall(word_text))
        
        # Remove duplicates
        emails = list(dict.fromkeys(emails))
        phone_numbers = list(dict.fromkeys(phone_numbers))

        emails_and_nums = []
        if emails:
            emails_and_nums.append("EMAILS:")
            emails_and_nums.extend(emails)
        if phone_numbers:
            emails_and_nums.append("PHONE NUMBERS:")
            emails_and_nums.extend(phone_numbers)

        if emails_and_nums:
            return emails_and_nums
        else:
            return 0

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while processing {m}: {str(e)}")
        return []



# ------------------------------------------
# MAIN PROGRAM
if __name__ == "__main__":
    the_header = get_random_header()
    # print(the_header)
    web_list = get_all_websites()

    # Next two lines set's up the table
    d = []
    table = pd.DataFrame(d)

    # Iterates through each website (m) on the list (web_list) and performs necessary tasks
    for m in web_list:  
        found_emails_and_nums = get_email_and_numbers(m, the_header)  # PRIMARY VARIABLE
        if found_emails_and_nums:
            column_dataframe = pd.DataFrame({m: found_emails_and_nums})
            # concatenate current column to previous (side by side)
            table = pd.concat([table, column_dataframe], axis="columns")

    print("\n-------final table---------")
    print(table)
    user_home = os.path.expanduser("~")

    # Define the filename and folder in the documents directory
    filename = input("Enter a name for your file:\n")
    file_name = filename + ".csv"
    save_to_folder = "Documents"

    # Construct the full path to the CSV file
    csv_path = os.path.join(user_home, save_to_folder, file_name)

    # Use pandas to save the DataFrame to the CSV file
    table.to_csv(csv_path, index=False, header=True)
    print("\nDone!\nSaved to your " + save_to_folder + " folder.\n")
