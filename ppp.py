import threading
import time
import warnings
from playwright.sync_api import sync_playwright
import getindianname as name  # Import the getindianname library
import asyncio
from concurrent.futures import ThreadPoolExecutor
import nest_asyncio

nest_asyncio.apply()

# Flag to indicate whether the script is running
running = True

MUTEX = threading.Lock()


def sync_print(text):
    with MUTEX:
        print(text)


async def start(name, wait_time, meetingcode, passcode):
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
        user = name.get_name()  # Use getindianname library to generate a random Indian name
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
        while running and wait_time > 0:
            await asyncio.sleep(1)
            wait_time -= 1
        sync_print(f"{name} ended!")

        browser.close()


async def main():
    global running
    number = int(input("Enter number of Users: "))
    meetingcode = input("Enter meeting code (No Space): ")
    passcode = input("Enter Password (No Space): ")

    sec = 90
    wait_time = sec * 60

    with ThreadPoolExecutor(max_workers=number) as executor:
        loop = asyncio.get_running_loop()
        tasks = []
        for i in range(number):
            try:
                # Generate a random Indian name using getindianname
                user = name.get_name()
            except IndexError:
                break
            task = loop.create_task(start(f'[Thread{i}]', wait_time, meetingcode, passcode))
            tasks.append(task)
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            running = False
            # Wait for tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
