import threading
import time
import warnings
from playwright.sync_api import sync_playwright
import getindianname as name  # Import the getindianname library

warnings.filterwarnings('ignore')
MUTEX = threading.Lock()


def sync_print(text):
    with MUTEX:
        print(text)


def start(name, wait_time, meetingcode, passcode):
    sync_print(f"{name} started!")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'])
        context = browser.new_context(permissions=['microphone'])
        page = context.new_page()
        page.goto(f'https://zoom.us/wc/join/{meetingcode}', timeout=200000)

        try:
            page.click('//button[@id="onetrust-accept-btn-handler"]')
        except:
            page
        try:
            page.click('//button[@id="wc_agree1"]')
        except:
            pass

        page.wait_for_selector('input[type="text"]', timeout=200000)
        user = name.randname()  # Use getindianname library to generate a random Indian name
        page.fill('input[type="text"]', user)
        page.fill('input[type="password"]', passcode)
        join_button = page.wait_for_selector('button.preview-join-button')
        join_button.click()

        try:
            # Increase timeout if still mic missing on some users
            query = '//button[text()="Join Audio by Computer"]'
            mic_button_locator = page.wait_for_selector(query, timeout=200000)
            mic_button_locator.wait_for_element_state('stable', timeout=200000)
            mic_button_locator.evaluate_handle('node => node.click()')
            sync_print(f"{name} mic aayenge.")

        except Exception as e:
            print(e)
            sync_print(f"{name} mic nhi aayenge.")

        sync_print(f"{name} sleep for {wait_time} seconds ...")
        time.sleep(wait_time)
        sync_print(f"{name} ended!")

        browser.close()


def main():
    sec = 90
    wait_time = sec * 60
    workers = []
    for i in range(number):
        try:
            user = name.randname()  # Use getindianname library to generate a random Indian name
        except IndexError:
            break
        wk = threading.Thread(target=start, args=(
            f'[Thread{i}]', wait_time, meetingcode, passcode))
        workers.append(wk)
    for wk in workers:
        wk.start()
    for wk in workers:
        wk.join()


if __name__ == '__main__':
    number = int(input("Enter the number of Users: "))
    meetingcode = input("Enter the meeting code (No Space): ")
    passcode = input("Enter the Password (No Space): ")

    main()
