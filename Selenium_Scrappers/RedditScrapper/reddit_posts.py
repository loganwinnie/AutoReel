from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup # type: ignore
from dotenv import load_dotenv
from os import environ

load_dotenv() 




def reddit_login(driver):
    """
    login:
        driver - web driver used to navigate web

        Uses credentials from enviorment to sign into reddit. 
    """
    driver.get("https://www.reddit.com/login/")
    wait = WebDriverWait(driver, timeout=10, poll_frequency=.2)
    # wait.until(EC.visibility_of_element_located((By.ID, "login-button")))
    print(driver.page_source)
    # login_button = driver.find_element(By.ID, "login-button")

    # if login_button:
        # login_button.click()
    wait.until(EC.visibility_of_element_located((By.ID, "login-username")))
    driver.find_element(By.ID, "login-username").send_keys(environ.get("REDDIT_USER"))
    driver.find_element(By.ID, "login-password").send_keys(environ.get("REDDIT_PASSWORD"))
    driver.find_element(By.ID, "login-password").send_keys(Keys.RETURN)


def gather_posts(driver, amount):
    """
    gather_posts: 
        Browses Reddit feed and gathers set number of post.

        driver - web driver used to navigate web
        amount - int - amount of posts to be gathered

        Returns list of post objects 
        posts: {"title":str, "post_link":str, "feed_idx":int, "content":str}
    """
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


option = Options()
option.add_argument("--disable-extensions") 
option.add_argument("--disable-infobars") 
option.add_argument("--start-maximized") 
option.add_argument("--disable-notifications") 
option.add_argument('--headless') 
option.add_argument('--no-sandbox') 
option.add_argument('--disable-dev-shm-usage') 
# service = Service("/usr/bin/chromedriver")
browser = webdriver.Chrome(options=option)


reddit_login(driver=browser)
browser.get("https://www.reddit.com/r/AmItheAsshole/")

posts = gather_posts(driver=browser,amount=5)
print("POST LEN:", len(posts), "\n Posts", posts)

