import bs4, requests, time, os, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from datetime import date, timedelta
import inquirer
import threading
load_dotenv()


def get_updates(day_offset, hour):
    url = 'https://northwestbadmintonacademy.sites.zenplanner.com/calendar.cfm?DATE='

    today = (date.today() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    url+=today+'&VIEW=LIST'
    x = requests.get(url)

    soup = bs4.BeautifulSoup(x.text, features="html.parser")
    calendar = soup.find(class_ = "list calendar")

    if(calendar.find('tr') == None):
       return False

    day = calendar.find('tr').find('td').text
    for tr in calendar.find_all('tr', class_="item"):
        if(tr.find_all('td')[0].text == hour):
            return True
    return False

def sign_up(day_offset, hour):
    print("Task assigned to thread: {}".format(threading.current_thread().name))
    while(True):
        if(get_updates(day_offset, hour) == True):
            break
        time.sleep(5)

    browser = webdriver.Chrome(executable_path="./chromedriver.exe")
    url = 'https://northwestbadmintonacademy.sites.zenplanner.com/calendar.cfm?DATE='

    today = (date.today() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    url+=today+'&VIEW=LIST'

    browser.get(url)
    time.sleep(1)
    calendar = browser.find_element(By.XPATH, "/html/body/div/table/tbody/tr/td[2]/table[2]")
    
    for tr in calendar.find_elements(By.CLASS_NAME, "item"):
        if(tr.find_elements(By.TAG_NAME, 'td')[0].text == hour):
            toClick = tr

    toClick.click()
    time.sleep(1)

    user = browser.find_element(By.XPATH, "/html/body/div/table/tbody/tr/td[2]/div[2]/table/tbody/tr/td/form/table/tbody/tr[2]/td/input")
    user.send_keys(os.getenv('USER'))
    password = browser.find_element(By.XPATH, "/html/body/div/table/tbody/tr/td[2]/div[2]/table/tbody/tr/td/form/table/tbody/tr[5]/td/input")
    password.send_keys(os.getenv('PASS'))
    browser.find_element(By.XPATH, "/html/body/div/table/tbody/tr/td[2]/div[2]/table/tbody/tr/td/form/table/tbody/tr[7]/td/input").click()

    browser.find_element(By.XPATH, "/html/body/div/table/tbody/tr/td[2]/div/div[3]/div[2]/table/tbody/tr/td[3]/a").click()


if __name__ == '__main__':
    choices = []
    for i in range(2,7):
        day = date.today() + timedelta(days=i)
        for j in range(4,11):
            choices.append(str(i)+"-"+day.strftime("%A : %Y-%m-%d") + " &" + str(j) + ":00 PM - " + str(j+1) + ":00 PM")

    questions = [
    inquirer.Checkbox('Timeslots',
                    message="Select timeslots",
                    choices=choices,
                    ),
    ]
    answers = inquirer.prompt(questions)

    threads = []
    for ans in answers['Timeslots']:
        thread = threading.Thread(target=sign_up, args=(int(ans[:ans.index('-')]), ans[ans.index('&')+1:ans.index('PM')+2]), name=ans, daemon=True)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()