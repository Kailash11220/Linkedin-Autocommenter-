from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import time
import json

def linkedin_search(username,password,keyword):

    # Set LinkedIn page URL for scraping
    def search_posts(keyword):
        keyword = keyword.replace(' ', '%20')
        page = 'https://www.linkedin.com/search/results/content/?keywords='
        return page + keyword

    chrome_options = Options()


    # Initialize WebDriver for Chrome
    browser = webdriver.Chrome()

    # Open LinkedIn login page
    browser.get('https://www.linkedin.com/login')

    # Enter login credentials and submit
    elementID = browser.find_element(By.ID, "username")
    elementID.send_keys(username)
    elementID = browser.find_element(By.ID, "password")
    elementID.send_keys(password)
    elementID.submit()

    #Intentional time gap , for any captcha verification
    time.sleep(10)

    # Navigate to the posts page of the company
    browser.get(search_posts(keyword))



    # Set parameters for scrolling through the page
    SCROLL_PAUSE_TIME = 1.5
    MAX_SCROLLS = 10
    last_height = browser.execute_script("return document.body.scrollHeight")
    scrolls = 0
    no_change_count = 0

    # Scroll through the page until no new content is loaded
    while scrolls < MAX_SCROLLS:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = browser.execute_script("return document.body.scrollHeight")
        no_change_count = no_change_count + 1 if new_height == last_height else 0
        if no_change_count >= 3 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
            break
        last_height = new_height
        scrolls += 1

    # Parse the page source with BeautifulSoup
    company_page = browser.page_source
    linkedin_soup = bs(company_page.encode("utf-8"), "html.parser")

    # Save the parsed HTML to a file
    with open(f"posts_html.txt", "w+",encoding='utf-8') as t:
        t.write(linkedin_soup.prettify())

    # Extract post containers from the HTML
    containers = [container for container in linkedin_soup.find_all("div",{"class":"feed-shared-update-v2"}) if 'activity' in container.get('data-urn', '')]



    # Define a data structure to hold all the post information
    posts_data = []


    # Function to extract text from a container
    def get_text(container, selector, attributes):
        try:
            element = container.find(selector, attributes)
            if element:
                return element.text.strip()
        except Exception as e:
            print(e)
        return ""


    # Function to extract media information
    def get_media_info(container):
        media_info = [("div", {"class": "update-components-video"}, "Video"),
                    ("div", {"class": "update-components-linkedin-video"}, "Video"),
                    ("div", {"class": "update-components-image"}, "Image"),
                    ("article", {"class": "update-components-article"}, "Article"),
                    ("div", {"class": "feed-shared-external-video__meta"}, "Youtube Video"),
                    ("div", {"class": "feed-shared-mini-update-v2 feed-shared-update-v2__update-content-wrapper artdeco-card"}, "Shared Post"),
                    ("div", {"class": "feed-shared-poll ember-view"}, "Other: Poll, Shared Post, etc")]
        
        for selector, attrs, media_type in media_info:
            element = container.find(selector, attrs)
            if element:
                link = element.find('a', href=True)
                return link['href'] if link else "None", media_type
        return "None", "Unknown"


    # Main loop to process each container
    for container in containers:
        post_text = get_text(container, "div", {"class": "feed-shared-update-v2__description-wrapper"})
        media_link, media_type = get_media_info(container)

        # Reactions (likes)
        try:
            post_reactions_list = container.find(class_="social-details-social-counts__reactions-count").text.split()
            post_reactions = post_reactions_list[0]
        except:
            post_reactions = "0"

        # Comments
        comment_element = container.find_all(lambda tag: tag.name == 'button' and 'aria-label' in tag.attrs and 'comments' in tag['aria-label'].lower())
        comment_idx = 1 if len(comment_element) > 1 else 0
        post_comments = comment_element[comment_idx].text.strip() if comment_element and comment_element[comment_idx].text.strip() != '' else 0

        # Shares OK
        shares_element = container.find_all(lambda tag: tag.name == 'button' and 'aria-label' in tag.attrs and 'repost' in tag['aria-label'].lower())
        shares_idx = 1 if len(shares_element) > 1 else 0
        post_shares = shares_element[shares_idx].text.strip() if shares_element and shares_element[shares_idx].text.strip() != '' else 0
        
        # Post ID
        postid = container.get('data-urn','')

        # Append the collected data to the posts_data list
        content_data = {
            "Post ID": postid,
            "Post Text": post_text,
            "Media Link": media_link,
            "Likes": post_reactions,
            "Comments": post_comments,
            "Shares": post_shares
        }
        posts_data.append({
            "Keyword": keyword,
            "Content": content_data
            })

    # Print the number of posts
    print(len(posts_data))

    # Write the list to a JSON file
    with open("posts_data_temporary.json", "w") as json_file:
        json.dump(posts_data, json_file, indent=4)

    with open("post_history.json", "a") as j:
        json.dump(posts_data, j , indent=4)

    