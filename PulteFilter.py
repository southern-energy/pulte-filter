import pandas as pd
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
import csv

"""
The Headless browsing option greatly reduces the amount of time it takes for the scraper to run.
"""
print("Headless Browser Running")
options = Options()
options.add_argument("--headless")  # Runs Chrome in headless mode.
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-gpu')  # applicable to windows os only
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
browser = webdriver.Chrome(
    options=options, executable_path=ChromeDriverManager().install())
print("Headless Browser has Launched")


def login_into_dash(json_target_file):
    """
    Takes the login information from JSON file and passes data to login form.

    Parameter json_target_file needs to be equal to the file's location.

    Contents of the file must be organized as follows [Note: don't forget the curly braces]:

    {
    "username": "please-put-your-username-here",
    "password": "please-put-your-password-here"
    }


    """
    browser.get("http://sem.myirate.com/")
    with open(json_target_file) as login_data:
        data = json.load(login_data)
    username = data['username']
    password = data['password']
    browser.find_element_by_name(
        "ctl00$ContentPlaceHolder1$Username").send_keys(username)
    browser.find_element_by_name(
        "ctl00$ContentPlaceHolder1$Password").send_keys(password)
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$btnLogin").click()


def read_and_filter_excel_report(report):
    df = pd.read_excel(report)
    global list_of_addresses
    list_of_addresses = df["Address"].to_list()
    print(list_of_addresses)


def check_address_in_dash():
    browser.get("https://sem.myirate.com/Reports/AdHoc_View.aspx?id=1374")
    address_exists = []
    address_does_not_exist = []

    for index, address in enumerate(list_of_addresses):
        print(f"We are on address " + str(address) + " number " +
              str(int(index)+1) + " of " + str(len(list_of_addresses)))
        try:
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable(
                (By.NAME, "ctl00$ContentPlaceHolder1$rfReport$ctl01$ctl08$ctl04")))
        finally:
            browser.find_element_by_name(
                "ctl00$ContentPlaceHolder1$rfReport$ctl01$ctl08$ctl04").click()
            browser.find_element_by_name("ctl00$ContentPlaceHolder1$rfReport$ctl01$ctl08$ctl04").send_keys(
                Keys.CONTROL, "a", Keys.BACKSPACE)
            browser.find_element_by_name(
                "ctl00$ContentPlaceHolder1$rfReport$ctl01$ctl08$ctl04").send_keys(str(address))
            browser.find_element_by_id(
                "ctl00_ContentPlaceHolder1_rfReport_ApplyButton").click()

        # We need a solution for if the table returns nothing--which is common.

        try:
            element = WebDriverWait(browser, 4).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_rgReport_ctl00"]/tbody/tr/td/div'))
            )
            print(f"Address " + str(address) + " Does Not Exist")
            address_does_not_exist.append(address)
        except TimeoutException:
            print(f"Address " + str(address) + " Exists")
            address_exists.append(address)

    print("\nWe have " + str(len(address_exists)) + " that exist!\n")
    print(address_exists)
    print("\n We have " + str(len(address_does_not_exist)) +
              " that will not be included!\n")
    print(address_does_not_exist)
    
    global addresses_for_scraping
    addresses_for_scraping = address_does_not_exist

    pd.DataFrame(addresses_for_scraping).to_excel("PulteExport_Trimmed.xlsx", header=False, index=False)


def logout_session():
    browser.get("http://sem.myirate.com/Dashboard_Company.aspx")
    browser.find_element_by_xpath('//*[@id="navProfile"]').click()
    try:
        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log Out"))).click()
    except:
        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log Out"))).click()


def main():
    read_and_filter_excel_report("PulteExport_2022_03_29.xlsx")
    login_into_dash("./DASHLoginInfo.json")
    check_address_in_dash()
    logout_session()

main()
browser.quit()
