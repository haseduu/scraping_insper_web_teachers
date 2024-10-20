from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
import json
import time
from bs4 import BeautifulSoup

def get_email_photo_and_description_from_profile(driver, profile_url):
    driver.get(profile_url)
    time.sleep(2)  # Wait for the page to load

    email = None
    photo_url = None
    description = None

    try:
        # Look for the email
        email_li = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.teacher__links--email"))
        )
        email_element = email_li.find_element(By.TAG_NAME, "a")
        email = email_element.get_attribute('href').replace('mailto:', '')

        # Look for the profile picture using the new class
        photo_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.sc-vIzOl.cHsNCT"))
        )
        photo_url = photo_element.get_attribute('src')

        # Look for the description element
        description_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-yRUuS.iUnpfN"))
        )
        description = description_element.text.strip() if description_element else None

    except TimeoutException:
        print(f"Email, photo, or description not found for {profile_url}")
    except NoSuchElementException:
        print(f"Element structure not as expected for {profile_url}")

    return email, photo_url, description

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

    # Function to click the "loadmore__button" with threshold for attempts
    def click_load_more(driver, max_retries=3):
        """Attempts to click the 'Load More' button on the webpage."""
        retries = 0
        for _ in range (8):
            try:
                scroll_down()  # Scroll down to ensure the button is visible
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "loadmore__button"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1)  # Allow time for the scroll animation to complete
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(2)  # Wait for new content to load
                retries = 0  # Reset retries if clicking was successful
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException):
                retries += 1
                print(f"Retry {retries} out of {max_retries} failed.")
                if retries >= max_retries:
                    print("Max retries reached. Stopping 'Load More' attempts.")
                    break
        print("Finished attempting to click 'Load More'.")



    # Click the "loadmore__button" until it no longer exists or the retries are exhausted
    click_load_more(driver=driver)

    # Get the page source after all content is loaded
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all profile links
    profile_links = [a['href'] for a in soup.find_all('a', href=True) if '/pt/docentes/' in a['href']]
    profile_links = [link.split('.html')[0] for link in profile_links]
    print(profile_links)
    # List to store the extracted data
    data = []


    # Visit each profile page and extract information
    for profile_url in profile_links:
        try:
            full_profile_url = profile_url + '.html'
            email, photo_url, description = get_email_photo_and_description_from_profile(driver, full_profile_url)
            name = profile_url.split('/')[-1].replace('-', ' ').title()

            position = 'Unknown'  # Default value if position is not found
            # # Extract name and position from the main page information
            # profile_soup = soup.find('a', href=profile_url).parent
            # if profile_soup:
            #     name_element = profile_soup.find('h3')
            #     position_element = profile_soup.find('p')
            #     if name_element:
            #         name = name_element.text.strip()
            #     if position_element:
            #         position = position_element.text.strip()

            data.append({
                "name": name,
                "position": position,
                "profile_url": full_profile_url,
                "email": email,
                "photo_url": photo_url,
                "description": description
            })
        except Exception as e:
            print(f"Error processing {profile_url}: {e}")
            continue

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
