
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def write_comment(username,password,postid,comment):

    chrome_options = Options()
    browser = webdriver.Chrome()

    # Login
    browser.get("https://www.linkedin.com/login")
    elementID = browser.find_element(By.ID, "username")
    elementID.send_keys(username)
    elementID = browser.find_element(By.ID, "password")
    elementID.send_keys(password)
    elementID.submit()
    time.sleep(10)

    # Go to Post
    url = 'https://www.linkedin.com/feed/update/' + postid
    browser.get(url)
    time.sleep(4)

    # Scroll to the element
    action_tab = browser.find_element(By.XPATH, "//div[contains(@class, 'update-v2-social-activity')]")
    browser.execute_script("arguments[0].scrollIntoView();", action_tab)
    browser.execute_script("window.scrollBy(0, -300);")

    # Like the Post
    time.sleep(4)
    like = browser.find_element(By.XPATH, "//button[@aria-label = 'React Like']")
    like.click()

    # Comment on post
    time.sleep(4)
    comment_box = browser.find_element(By.XPATH,"//div[@class = 'ql-editor ql-blank']" )
    comment_box.click()
    comment_box.send_keys(comment)
    time.sleep(4)
    post = browser.find_element(By.XPATH, "//button[contains(@class, 'comments-comment-box__submit-button')]").click()

