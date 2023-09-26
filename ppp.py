import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
from faker import Faker
from playwright.async_api import async_playwright
import nest_asyncio

nest_asyncio.apply()
fake = Faker('en_IN')
MUTEX = threading.Lock()

def sync_print(text):
    with MUTEX:
        print(text)

async def start(name, user, wait_time, meetingcode, passcode):
    sync_print(f"{name} started!")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'])
        context = await browser.new_context(permissions=['microphone'])
        page = await context.new_page()
        await page.goto(f'https://zoom.us/wc/join/{meetingcode}', timeout=200000)

        try:
            await page.click('//button[@id="onetrust-accept-btn-handler"]', timeout=5000)
        except:
            pass
        try:
            await page.click('//button[@id="wc_agree1"]', timeout=50000)
        except:
            pass

        await page.wait_for_selector('input[type="text"]', timeout=200000)
        await page.fill('input[type="text"]', user)
        await page.fill('input[type="password"]', passcode)
        join_button = await page.wait_for_selector('button.preview-join-button')
        await join_button.click()

        try:
            # Increase timeout if still mic missing on some users
            query = '//button[text()="Join Audio by Computer"]'
            mic_button_locator = await page.wait_for_selector(query, timeout=200000)
            await mic_button_locator.wait_for_element_state('stable', timeout=200000)
            await mic_button_locator.evaluate_handle('node => node.click()')
            sync_print(f"{name} mic aayenge.")

        except Exception as e:
            print(e)
            sync_print(f"{name} mic nhi aayenge.")

        sync_print(f"{name} sleep for {wait_time} seconds ...")
        await asyncio.sleep(wait_time)
        sync_print(f"{name} ended!")

        await browser.close()

async def main():
    number = int(input("Enter number of Users: "))
    meetingcode = input("Enter meeting code (No Space): ")
    passcode = input("Enter Password (No Space): ")

    sec = 60
    wait_time = sec * 60

    with ThreadPoolExecutor(max_workers=number) as executor:
        loop = asyncio.get_event_loop()
        tasks = []
        for i in range(number):
            try:
                user = fake.name()
            except IndexError:
                break
            task = loop.create_task(start(f'[Thread{i}]', user, wait_time, meetingcode, passcode))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    # Add your custom message below
    custom_message = "Google Colab has updated itself from LTS 18.0 to 20.0, so please update the code accordingly, in order to support Playwright on this platform."
    
    print(custom_message)
