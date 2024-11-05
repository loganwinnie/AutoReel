import time
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup # type: ignore


def navigate_to_subreddit(driver, url):

    driver.get(url)



def login(driver):
    wait = WebDriverWait(driver, timeout=10, poll_frequency=.2)
    wait.until(EC.visibility_of_element_located((By.ID, "login-button")))
    login_button = driver.find_element(By.ID, "login-button")

    if login_button:
        login_button.click()
        wait.until(EC.visibility_of_element_located((By.ID, "login-username")))
        driver.find_element(By.ID, "login-username").send_keys("TuneFit341")
        driver.find_element(By.ID, "login-password").send_keys("jtp3ndm!FTP!yqg1egh")
        driver.find_element(By.ID, "login-password").send_keys(Keys.RETURN)


def gather_posts(driver, amount):
    post_list = []
    post_index = 0

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(post_list) < amount:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Wait to load page
        wait = WebDriverWait(driver, timeout=20, poll_frequency=.2)
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//shreddit-post[@feedindex='{post_index}']")))
        
        reddit_feed_html = BeautifulSoup(driver.page_source, 'html.parser')

        #Search for text posts
        posts = reddit_feed_html.select_one("shreddit-feed").find_all(attrs={"post-type":"text"})
        if len(post_list) + len(posts) >= amount: 
            posts = posts[:(len(post_list) + len(posts) - amount +2)]

        for post in posts:
            post_list.append({"title": post.get("post-title", "None"), "post_link": post.get("content-href", None), "feed_index": post.get("feedindex", None)})
        
        post_index = post_list[-1].get("feed_index", 0)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
    for post in post_list:
        driver.get(post["post_link"])
        post_page_html = BeautifulSoup(driver.page_source, 'html.parser')
        
        post_body = post_page_html.select_one("shreddit-post").find(attrs={"slot":"text-body"})
        content = post_body.select("p")
        formatted_contents = [item.contents[0].strip() for item in content]
        post["content"] = formatted_contents
    
    return post_list

def main():
    browser = webdriver.Chrome()

    navigate_to_subreddit(driver=browser, url="https://www.reddit.com/r/AmItheAsshole/")
    login(driver=browser)
    posts = gather_posts(driver=browser,amount=10)
    print("POST LEN:", len(posts), "\n Posts", posts)

main()
