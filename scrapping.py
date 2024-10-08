from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import json

def scrape_website(url):
    # Setup Selenium WebDriver (make sure to download the appropriate driver for your browser)
    driver = webdriver.Chrome()  # You can use Firefox or other browsers as well
    driver.get(url)

    # Wait for the page to load
    time.sleep(2)

    # Function to scroll down the page
    def scroll_down():
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the page to load after scrolling

    # Function to click the "loadmore__button"
    def click_load_more(max_retries=5):
        for _ in range(max_retries):
            try:
                scroll_down()
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "loadmore__button"))
                )
                # Scroll the button into view
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1)
                # Try to click using JavaScript
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(2)  # Wait for the new content to load
                return True
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException):
                print(f"Attempt {_+1} failed. Retrying...")
                continue
        print("Max retries reached. Moving on...")
        return False

    # Click the "loadmore__button" until it no longer exists
    while click_load_more():
        pass

    # Get the page source after all content is loaded
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all elements with class "name-title"
    name_titles = soup.find_all(class_="name-title")

    # List to store the extracted data
    data = []

    # Extract h3 and p from each "name-title" element
    for title in name_titles:
        h3_text = title.find('h3').text.strip() if title.find('h3') else ''
        p_text = title.find('p').text.strip() if title.find('p') else ''
        data.append({
            "h3": h3_text,
            "p": p_text
        })

    # Close the browser
    driver.quit()

    # Save data to JSON file
    with open('name_titles.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Data saved to name_titles.json")

# Usage example
if __name__ == "__main__":
    target_url = "https://www.insper.edu.br/pt/docentes"  # Replace with the actual URL you want to scrape
    scrape_website(target_url)
