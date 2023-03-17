'''
This script is half-done, future features to add: 
1. Each parameter will be drawn using a function so that the structure is cleaner and 
   the function can be more flexible 
2. All parameters should be saved in a .csv file
3. Hard-coded titles (e.g., h2, a, span, etc.) should be drawn from an external record
   and try to use strings (i.e., "h2" instead of h2)
4. Maybe make a checklist that records different scraping strategies for different 
   websites 
'''

# Get all the packages
from bs4 import BeautifulSoup
import requests
import csv
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Set the options so that this program will wait for the whole page to be loaded 
# However, this may mean only part of the Javascript have been executed 
options = Options()
options.page_load_strategy = 'normal'

# Open a browser 
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

# Set initial page index and index increment (because the current program cannot 
# scrape the whole page fully loaded) so that all pages will be scraped and only
# a certain amount of elements will be scraped each time 
box_index = 0
index_increment = 2

# Set home URL in case there are detail pages that need to be jumped to
# Set the original URL that will be the beginning of scraping work 
URL_home = "https://www.heritagetoyotaowingsmills.com"
URL_original = "https://www.heritagetoyotaowingsmills.com/used-inventory/index.htm?start="

# Go through each page and scrape elements 
while True: 

    ## Go to a certain page/box and get the raw html document 
    URL_specific = URL_original + str(box_index)
    driver.get(URL_specific)
    html_text = driver.page_source

    ## Process the raw file with BeautifulSoup() so as to make it easier to scrape
    soup = BeautifulSoup(html_text, "lxml")
    
    ## Get all the car-box on one page but only keep the first few that have the 
    ## full information  
    car_list = soup.find_all('div', class_ = 'vehicle-card-details-container')
    car_list = car_list[0:min(len(car_list), index_increment)]

    ## Go through each box/car on the list 
    for car in car_list:

        ### Get the mileage information that's on a separate page 
        try:
            detail_link = soup.find_all('a', class_ = 'more-details-link ml-auto text-link text-link-muted btn-small')[car_list.index(car)]['href']
            detail_link = URL_home + detail_link
            driver.get(detail_link)
            tmp_html_text = driver.page_source
            tmp_soup = BeautifulSoup(tmp_html_text, "lxml")

            #### different elements share the same feature as the mileage info, it's 
            #### better to go through each of them and filter out the mileage one 
            all_mileage = tmp_soup.find_all('span', class_ = 'mr-3')
            for i in range(0, len(all_mileage)):
                try: 
                    if i == len(all_mileage):
                        mileage = "N/A"
                    elif 'mile' in all_mileage[i].text:
                        mileage = all_mileage[i].text
                        break
                except: 
                    next
            driver.back()
        except:
            detail_link = "N/A"
            mileage = "N/A"

        ### Get the car name
        try:
            car_name = car.h2.a.text
        except: 
            car_name = "N/A"

        ### Get the retail price and discount if available 
        try:
            retail_price = car.find('dd', class_ = 'retailValue').span.text
            discount = car.find('dd', class_ = 'discount text-success').span.text
        except: 
            retail_price = "N/A"
            discount = "N/A"

        ### Get the current final price 
        try:
            final_price = car.find('span', class_ = 'text-right portal-price').text
        except:
            final_price = "N/A"

        ### For now, just print out the scraped info 
        print(car_name)
        print(retail_price)
        print(discount)
        print(final_price)
        print(detail_link)
        print(mileage)
    
    ## If there's no more car elements, don't need to go into the next page 
    if len(car_list) < index_increment:
        break
    else:
        box_index += index_increment

# Close the browser 
driver.quit()
