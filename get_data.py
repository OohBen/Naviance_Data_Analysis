import concurrent.futures
import requests
import pandas as pd
import pickle
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Constants for URLs
LOGIN_URL = "https://student.naviance.com/stuyvesant"
GET_COLLEGES_URL = "https://blue-ridge-api.naviance.com/college/search"
URL_STATS_BASE = "https://blue-ridge-api.naviance.com/application-statistics/uuid/"


def login_to_naviance_and_get_token():
    driver = webdriver.Chrome()
    driver.get(LOGIN_URL)
    try:
        WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="main-container"]/article/div/div/div/div/div[2]/neon-0_12_0-card-standard/div[1]/h2'))
        )
        driver.minimize_window()
        token = driver.execute_script("return window.localStorage.getItem('deepLinkingAuthorizedToken');")
        return driver, token
    except Exception as e:
        print(f"An error occurred during login: {e}")
        driver.quit()


def fetch_college_data_and_urls(token):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    params = {"limit": 99999, "page": 1}
    response = requests.get(GET_COLLEGES_URL, headers=headers, params=params)
    college_data = response.json()

    college_urls = [
        (URL_STATS_BASE + college['coreMapping']['uuid'], college['name'])
        for college in college_data['data']
        if college.get('coreMapping') and college['coreMapping'].get('uuid')
    ]
    return college_urls


def process_data(data, school):
    records = []
    for test_type in ['act', 'sat']:
        if data.get(test_type):
            for appType in data[test_type]['apps']:
                for app in data[test_type]['apps'][appType]:
                    waitList = appType.startswith("waitlist")
                    waitList_result = "unknown"
                    if waitList:
                        if "Accepted" in appType:
                            waitList_result = "accepted"
                        elif "Denied" in appType:
                            waitList_result = "denied"
                        if waitList_result != "unknown":
                            record = {
                                "school": school,
                                "gpa": app['gpa'],
                                "act": app.get('actComposite'),
                                "sat": app.get('highestComboSat'),
                                "accepted": waitList_result == "accepted",
                                "appType": appType[-2:],
                            }
                            records.append(record)
                    else:
                        record = {
                            "school": school,
                            "gpa": app['gpa'],
                            "act": app.get('actComposite'),
                            "sat": app.get('highestComboSat'),
                            "accepted": appType.startswith("accepted"),
                            "appType": appType[-2:],
                        }
                        records.append(record)
    return records


def fetch_and_process_data(url, token, known_empties):
    if url[0] in known_empties:
        return []
    response = requests.get(url[0], headers={"Authorization": token})
    if response.status_code == 200:
        data = response.json().get('scattergrams', {}).get('gpa', {})
        if data.get('gpaCount', 0) == 0 or "DO NOT USE" in url[1]:
            known_empties.add(url[0])
            print("x", end="")
            return []
        return process_data(data, url[1])
    return []


def main():
    driver, token = login_to_naviance_and_get_token()
    driver.quit()
    refresh_data = input("Do you want to refresh the data? (y/n): ")
    refresh_data = refresh_data.lower() == "y"
    if refresh_data:
        if os.path.exists("college_urls.pkl"):
            os.remove("college_urls.pkl")
        if os.path.exists("known_empties.pkl"):
            os.remove("known_empties.pkl")
        known_empties = set()
        college_urls = fetch_college_data_and_urls(token)
        with open("college_urls.pkl", "wb") as file:
            pickle.dump(college_urls, file)

    else:
        known_empties = set()
        if os.path.exists("known_empties.pkl"):
            with open("known_empties.pkl", "rb") as file:
                known_empties = pickle.load(file)

        college_urls = fetch_college_data_and_urls(token)
    data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(fetch_and_process_data, url, token, known_empties): url for url in college_urls}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(f"\nProcessed {futures[future][1]}.")
                data.extend(result)

    if known_empties:
        with open("known_empties.pkl", "wb") as file:
            pickle.dump(known_empties, file)

    df = pd.DataFrame(data)
    df.to_pickle("college_data.pkl")
    print("Data saved to 'college_data.pkl'.")




if __name__ == "__main__":
    main()
