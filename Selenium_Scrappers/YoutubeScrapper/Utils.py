def navigate_to_url(driver, url):
    driver.get(url)

def read_file_and_select(path):
    file = open(path)
    lines = file.readlines()
    file.close() 
    return choice(lines)
