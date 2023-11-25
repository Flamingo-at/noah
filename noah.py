import time
import requests

from re import findall
from loguru import logger
from random import choice
from string import ascii_letters
from concurrent.futures import ThreadPoolExecutor
from pyuseragents import random as random_useragent
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_email():
    try:
        response = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
        email = response.json()[0]
        if email.split('@')[1] not in ['laafd.com', 'vjuum.com', 'txcct.com']:
            return create_email()
        return email
    except Exception:
        logger.error('Failed to create email')
        time.sleep(5)
        return create_email()


@retry(retry=retry_if_exception(Exception), stop=stop_after_attempt(60), wait=wait_fixed(1), reraise=True)
def check_email(login: str, domain: str, count: int):
    try:
        response = requests.get('https://www.1secmail.com/api/v1/?action=getMessages&'
                                f'login={login}&domain={domain}')
        email_id = response.json()[0]['id']
        return email_id
    except:
        raise Exception('Emails not found')


def get_code(login: str, domain: str, email_id: int):
    try:
        response = requests.get('https://www.1secmail.com/api/v1/?action=readMessage&'
                                f'login={login}&domain={domain}&id={email_id}')
        data = response.json()['htmlBody']
        link = findall(r'code=(\d{6})', data)[0]
        return link
    except:
        raise Exception('Failed to get link')


def main():
    while True:
        try:
            logger.info('Get email')
            email = create_email()

            options = webdriver.ChromeOptions()

            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={random_useragent()}')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-gpu')
            options.add_argument('--mute-audio')
            options.add_argument('--headless')

            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 30)
            driver.get(f'https://app.noah.com/?referralCode={REF_CODE}')

            logger.info('Create an account')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign up")]'))).click()
            wait.until(EC.element_to_be_clickable((By.ID, 'email'))).send_keys(email)
            password = ''.join(choice(ascii_letters) for _ in range(10))
            wait.until(EC.element_to_be_clickable((By.ID, 'password'))).send_keys(password)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign up")]'))).click()

            logger.info('Check email')
            email_id = check_email(email.split('@')[0], email.split('@')[1], 0)

            logger.info('Get code')
            verification_сode = get_code(email.split('@')[0], email.split('@')[1], email_id)

            logger.info('Confirm email')
            wait.until(EC.element_to_be_clickable((By.ID, 'verificationCode'))).send_keys(verification_сode)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Continue")]'))).click()

            logger.info('Set nickname')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Next")]'))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Continue")]'))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not now")]'))).click()
            time.sleep(2)

        except Exception as error:
            logger.error(error)

        else:
            with open('registered.txt', 'a', encoding='utf-8') as f:
                f.write(f'{email}:{password}\n')
            logger.success('Successfully\n')

        finally:
            driver.quit()


if __name__ == '__main__':
    print('Bot Noah @flamingoat\n')

    REF_CODE = input('Referral code: ')
    THREADS = int(input('Threads: '))

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.submit(main)
