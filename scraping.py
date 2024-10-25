import requests
from bs4 import BeautifulSoup
import os
import csv
import re

# File setup
image_folder = "product_images"
csv_filename = "products_data.csv"

# Remove the CSV file if it already exists
if os.path.exists(csv_filename):
    os.remove(csv_filename)

# Create the folder if it doesn't exist
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Base URL of the website
base_url = 'http://www.cashforgolfclubs.com/'

# Initialize CSV file with headers
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["brand", "club_type", "product_name", "price", "attributes", "image"])

# Send a GET request to the main page
response = requests.get(base_url)
if response.status_code == 200:
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the <ul> element by its class
    ul_element = soup.find_all('ul', {"class": "dd_menu dropdown-multicolumns clearfix"})

    # Check if the <ul> element is found
    if ul_element:
        # Find all direct <li> children of the <ul>
        li_elements = ul_element[0].find_all('li', recursive=False)
        
        # Loop through each <li> element
        # for i in range(1, len(li_elements)):
        for i in range(17, len(li_elements)):
            try:
                brand_element = li_elements[i].find('a', recursive=False)
                brand_name = brand_element.text.strip()
                div_element = li_elements[i].find('div', {"class": "col-1 firstcolumn lastcolumn"})
                
                if div_element:
                    a_elements = div_element.select('ul > li > a')
                else:
                    if i == 36:
                        a_elements = li_elements[i].select('div > div > ul > li > a')
                    else:
                        continue
                
                for j in range(0, len(a_elements)):
                    href_value = a_elements[j]['href']
                    club_type_name = a_elements[j].text.strip()
                    category_page = requests.get(href_value)
                    category_soup = BeautifulSoup(category_page.text, 'html.parser')
                    product_listing_element = category_soup.find('div', {"class": "pagination-container cm-pagination-container"})
                    parent_spans = product_listing_element.find_all('span', {"class": "button-action button-wrap-right"})
                    
                    for span_element in parent_spans:
                        child_a_element = span_element.find('a', recursive=False)
                        product_url = child_a_element['href']
                        product_page = requests.get(product_url)
                        product_soup = BeautifulSoup(product_page.text, 'html.parser')
                        options_list = []
                        
                        option_div_elements = product_soup.find_all('div', {"class": "control-group product-list-field clearfix"})
                        for k in range(0, len(option_div_elements)):
                            select_element = option_div_elements[k].find('select', recursive=False)
                            child_option_elements = select_element.find_all('option', recursive=False)
                            for option_element in child_option_elements:
                                option_element_text = option_element.text.strip()
                                options_list.append(option_element_text)
                        
                        # Collect image, name, and price data
                        image_a_element = product_soup.find('a', {"class": "cm-image-previewer"})
                        product_image_url = image_a_element['href']
                        product_name_div = product_soup.find('div', {"class": "breadcrumbs clearfix"})
                        product_name_span = product_name_div.find('span', recursive=False)
                        product_name = product_name_span.text.strip()
                        actual_price_p_element = product_soup.find('p', {"class": "actual-price"})
                        price_span_element = actual_price_p_element.find('span', {"class": "price-num", "id": True})
                        price_text = price_span_element.text.strip()
                        
                        # Remove non-numeric characters from price_text
                        price_numeric = re.sub(r'[^\d.]', '', price_text)  # Keeps digits and decimal point
                        price_value = float(price_numeric)  # Convert to float for numeric representation
                        
                        # Download image and save path
                        image_response = requests.get(product_image_url, stream=True)
                        image_filename = ""
                        if image_response.status_code == 200:
                            image_filename = os.path.join(image_folder, f"{product_name.replace(' ', '_')}.jpg").replace('\\', '/')
                            with open(image_filename, 'wb') as image_file:
                                for chunk in image_response.iter_content(1024):
                                    image_file.write(chunk)
                        
                        # Save product data to CSV
                        with open(csv_filename, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([
                                brand_name,
                                club_type_name,
                                product_name,
                                price_value,
                                options_list,
                                image_filename
                            ])
                            
                        print(f"Saved: {brand_name}::{club_type_name}: {product_name} - Price: {price_text} - Attributes: {options_list} - Image: {image_filename}")

            except Exception as e:
                print(f"Error processing category {i}: {e}")
    else:
        print("No <ul> elements found.")
else:
    print(f"Error loading page: {response.status_code}")
print("==========The scraping is done successfully!==========")