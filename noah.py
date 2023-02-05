import time
import requests

from re import findall
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from pyuseragents import random as random_useragent

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def create_email():
    try:
        response = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
        email = response.json()[0]
        return email
    except Exception:
        logger.error('Failed to create email')
        time.sleep(1)
        return(create_email())


def check_email(login: str, domain: str, count: int):
    try:
        response = requests.get('https://www.1secmail.com/api/v1/?action=getMessages&'
                                f'login={login}&domain={domain}')
        email_id = response.json()[0]['id']
        return(email_id)
    except:
        while count < 30:
            count += 1
            time.sleep(1)
            return(check_email(login, domain, count))
        logger.error('Emails not found')
        raise Exception()


def get_link(login: str, domain: str, email_id):
    try:
        response = requests.get('https://www.1secmail.com/api/v1/?action=readMessage&'
                                f'login={login}&domain={domain}&id={email_id}')
        data = response.json()['body']
        link = findall(
            r'"(https:\/\/auth.noah.com\/u\/email-verification.+)"', data)[0]
        return(link)
    except:
        logger.error('Failed to get link')
        raise Exception()


def main(ref):
    while True:
        try:
            logger.info('Get email')
            email = create_email()

            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={random_useragent()}')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-gpu')
            options.add_argument('--mute-audio')
            options.headless = True

            driver = webdriver.Chrome(options=options)
            actions = ActionChains(driver)
            wait = WebDriverWait(driver, 15)

            driver.get(f"https://app.noah.com/?referralCode={ref}")

            logger.info('Create an account')
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create an account')]"))).click()
            wait.until(EC.element_to_be_clickable((By.ID, 'email'))).send_keys(email)
            wait.until(EC.element_to_be_clickable((By.ID, 'password'))).send_keys(email)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Account')]"))).click()

            logger.info('Check email')
            email_id = check_email(email.split('@')[0], email.split('@')[1], 0)

            logger.info('Get link')
            link = get_link(email.split('@')[0], email.split('@')[1], email_id)

            logger.info('Confirm email')
            driver.get(link)

            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Continue')]"))).click()
            time.sleep(5)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))).click()
            time.sleep(2)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save & Enter NOAH')]"))).click()

        except:
            logger.error('Error')

        else:
            with open('registered.txt', 'a', encoding='utf-8') as f:
                f.write(f'{email}\n')
            logger.success('Successfully\n')


if __name__ == '__main__':
    print('Bot Noah @flamingoat\n')

    ref = input('Referral code: ')
    threads = int(input('Threads: '))
    ref_list = [ref] * threads

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(main, ref_list)