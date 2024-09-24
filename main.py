# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 23:32:06 2024

@author: Rohan
"""

import asyncio
import re
import aiohttp
import random
import os
import io
import requests
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urlparse
import autonomous_proxy
import argparse
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn

class GoogleImageScraper:
    def __init__(self, api_key, image_path=None, search_key="cat", number_of_images=1, concurrency=30, use_proxies=True, keep_filenames=False):
        self.api_key = api_key
        self.proxy_service = autonomous_proxy.AutonomousProxy(api_key) if use_proxies else None
        self.image_path = image_path if image_path else os.path.join(os.getcwd(), search_key)
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.semaphore = asyncio.Semaphore(concurrency)  # Limit concurrent requests
        self.working_proxies = []
        self.use_proxies = use_proxies
        self.keep_filenames = keep_filenames
        self.console = Console()
        self.image_queue = asyncio.Queue()  # Queue for image URLs

        # Create directory if it does not exist
        if not os.path.exists(self.image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(self.image_path)

    # Test if a proxy works
    async def test_proxy(self, session, proxy, test_url='https://www.google.com'):
        try:
            async with session.get(test_url, proxy=proxy, timeout=5) as response:
                return response.status == 200
        except Exception as e:
            return False

    async def fetch_working_proxies(self):
        if not self.use_proxies:
            return  # Skip fetching proxies if not using them
        
        top_proxies = self.proxy_service.ReturnTOP10Proxies()
        async with aiohttp.ClientSession() as session:
            tasks = [self.test_proxy(session, proxy) for proxy in top_proxies]
            results = await asyncio.gather(*tasks)
            self.working_proxies = [proxy for proxy, result in zip(top_proxies, results) if result]

    async def save_image(self, image_url):
        try:
            print(f"[INFO] Downloading image from URL: {image_url}")
            search_string = ''.join(e for e in self.search_key if e.isalnum())
            image = requests.get(image_url, timeout=5)
            if image.status_code == 200:
                with Image.open(io.BytesIO(image.content)) as image_from_web:
                    if self.keep_filenames:
                        o = urlparse(image_url)
                        name = os.path.splitext(os.path.basename(o.path))[0]
                        filename = f"{name}.{image_from_web.format.lower()}"
                    else:
                        filename = f"{search_string}_{random.randint(0, 10000)}.{image_from_web.format.lower()}"

                    image_path = os.path.join(self.image_path, filename)
                    print(f"[INFO] Saving image at: {image_path}")
                    image_from_web.save(image_path)
            else:
                print(f"[ERROR] Failed to download image with status code: {image.status_code}")
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")

    async def download_images(self):
        while True:
            image_url = await self.image_queue.get()
            if image_url is None:  # Stop signal
                break
            await self.save_image(image_url)
            self.image_queue.task_done()

    async def scrape_google_images(self):
        search_url = f"https://www.google.com/search?q={self.search_key}&tbm=isch"
        async with aiohttp.ClientSession() as session:
            with Progress(BarColumn(), TextColumn("[progress.description]{task.description}"),
                          TextColumn("[bold green]Images Scraped: {task.completed}/{task.total}")) as progress:
                task = progress.add_task("Scraping images...", total=self.number_of_images)
                for _ in range(self.number_of_images):
                    proxy = random.choice(self.working_proxies) if self.working_proxies else None
                    try:
                        async with self.semaphore:
                            async with session.get(search_url, proxy=proxy, timeout=5) as response:
                                if response.status == 200:
                                    soup = BeautifulSoup(await response.text(), 'html.parser')
                                    imgs = soup.find_all('img')
                                    for img in imgs:
                                        img_url = img.get('src')
                                        if img_url and len(img_url) > 0 and re.match(r'^https?://', img_url):
                                            await self.image_queue.put(img_url)  # Add image URL to the queue
                                            progress.update(task, advance=1)
                                            break  # Exit after finding the first valid image URL
                                else:
                                    print(f"Failed to fetch images with status {response.status} using proxy {proxy}")
                    except Exception as e:
                        print(f"Error while scraping images: {e}")
                    await asyncio.sleep(1)  # Delay between requests

    async def scrape(self):
        if self.use_proxies and not self.working_proxies:
            print("No working proxies available. Fetching new proxies...")
            await self.fetch_working_proxies()

        if self.use_proxies and not self.working_proxies:
            print("Failed to find any working proxies.")
            return []

        # Start image downloading in the background
        download_task = asyncio.create_task(self.download_images())

        await self.scrape_google_images()

        # Stop the downloader
        await self.image_queue.put(None)  # Send stop signal
        await download_task  # Wait for the downloader to finish

async def main(search_key, number_of_images, api_key, use_proxies, keep_filenames):
    if not api_key:
        print("[WARNING] No API key provided. Proxies will not be used.")
        use_proxies = False

    scraper = GoogleImageScraper(
        search_key=search_key,
        number_of_images=number_of_images,
        api_key=api_key,
        use_proxies=use_proxies,
        keep_filenames=keep_filenames
    )
    await scraper.scrape()

# Run the main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Image Scraper script with configurable parameters.")
    
    parser.add_argument('--search_keys', type=str, nargs='+', help="List of search keys (e.g., 'cat t-shirt')", required=True)
    parser.add_argument('--num_images', type=int, help="Number of images to scrape", default=5)
    parser.add_argument('--use_proxies', type=bool, help="Use proxies (True/False)", default=True)
    parser.add_argument('--keep_filenames', type=bool, help="Keep original filenames (True/False)", default=False)
    parser.add_argument('--api_key', type=str, help="API key for proxy service", required=False)

    args = parser.parse_args()

    # Remove duplicate search keys
    search_keys = list(set(args.search_keys))

    asyncio.run(main(search_keys[0], args.num_images, args.api_key, args.use_proxies, args.keep_filenames))