from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Set up the Chrome WebDriver
driver = webdriver.Chrome()

# Open the target URL
driver.get('http://www.cashforgolfclubs.com/')  # Replace with the actual URL
time.sleep(3)  # Wait for the page to load

# Find the <ul> element by its class name
try:
    ul_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.dd_menu.dropdown-multicolumns.clearfix')  # Using CSS selector for multiple classes

    # Check if there is at least one <ul> element
    if len(ul_elements) > 0:
        # Get the first <ul> element
        first_ul = ul_elements[0]

        # Find only direct child <li> elements within the first <ul>
        li_elements = first_ul.find_elements(By.XPATH, "*")

        # Loop through each <li> element, starting at 1
        for i, _ in enumerate(li_elements, start=1):
            try:
                # Re-locate the <li> elements in case of DOM changes
                li_elements = first_ul.find_elements(By.XPATH, "*")
                li_element = first_ul.find_elements(By.XPATH, "./li")[i]
                a_element = li_element.find_element(By.TAG_NAME, 'a')
                href_value = a_element.get_attribute('href')
                driver.get(href_value)
                time.sleep(3)

                # On the new page, find the <h1> element with class "mainbox-title"
                h1_element = driver.find_element(By.CLASS_NAME, 'mainbox-title')

                # Find the <div> element with class "mainbox-body"
                div_element = driver.find_element(By.CLASS_NAME, 'mainbox-body')
                ul_element = div_element.find_element(By.TAG_NAME, 'ul')
                category_elements = ul_element.find_elements(By.TAG_NAME, 'li')

                # Store the category data (hrefs and texts) before navigation
                categories = []
                for j in range(len(category_elements)):
                    try:
                        category_a_element = category_elements[j].find_element(By.TAG_NAME, 'a')
                        category_span_element = category_a_element.find_element(By.TAG_NAME, 'span')
                        category_a_href_value = category_a_element.get_attribute('href')
                        categories.append({
                            'club_type': category_span_element.text,
                            'href': category_a_href_value
                        })
                    except Exception as e:
                        print("error while getting category info")

                # Now, navigate to each category
                for j, category in enumerate(categories):
                    try:
                        print(f"[{i}][{j}] Brand {h1_element.text}--club_type: {category['club_type']}--href_value: {category['href']}")
                        driver.get(category['href'])
                        time.sleep(3)
                        div_elements = driver.find_elements(By.CSS_SELECTOR, 'div.product-container.template-products.list.clearfix')
                        print(f"Number of products: {len(div_elements)}")
                    except Exception as e:
                        print("error while navigating to category")
                
                # After scraping, go back to the main page and re-locate the elements
                driver.back()
                time.sleep(3)  # Wait for the page to load again
                ul_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.dd_menu.dropdown-multicolumns.clearfix')
                first_ul = ul_elements[0]

            except Exception as e:
                print(f"Error scraping <li> element {i}: {e}")
                driver.back()  # Go back in case of failure
                time.sleep(2)

    else:
        print("No <ul> elements found.")

except Exception as e:
    print(f"Error finding the <ul> or <li> elements: {e}")

# Close the WebDriver
driver.quit()
