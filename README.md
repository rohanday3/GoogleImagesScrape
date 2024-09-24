# Google Image Scraper

A Python-based scraper that fetches images from Google based on a given search term. The scraper utilizes asynchronous programming for efficient image downloading and supports proxy usage to avoid rate limiting.

## Features

- Scrapes images from Google using a specified search term.
- Downloads images concurrently using asynchronous requests.
- Optionally uses proxies to prevent blocking.
- Customizable settings for the number of images to scrape and filename handling.

## Requirements

- Python 3.7 or higher
- Required Python packages can be installed using pip. 

```bash
pip install -r requirements.txt
```

## Getting Started
1. **Clone the repository:**

```bash
git clone https://github.com/rohanday3/GoogleImageScraper.git
cd GoogleImageScraper
```

2. **Obtain an API Key:**

- Go to Webshare.io and sign up for an account.
- Generate an API key from your account dashboard.

3. **Configure the Scraper:**

- Open main.py and set the api_key variable with your API key from Webshare.
- Modify other parameters as needed, such as search term, number of images, and whether to use proxies.

4. **Run the Scraper:**

You can run the scraper from the command line with the following command:

```bash
python main.py --search_keys "your+search+term" --num_images 5 --use_proxies True --keep_filenames False --api_key "your_api_key"
```
Replace "your search term" with your desired search keywords, and adjust the other parameters as necessary.

## Command Line Arguments
- `--search_keys`: List of search terms (e.g., "cat t-shirt").
- `--num_images`: Number of images to scrape (default is 5).
- `--use_proxies`: Use proxies (True/False, default is True).
- `--keep_filenames`: Keep original filenames (True/False, default is False).
- `--api_key`: Your API key for the proxy service (required if using proxies).

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please create an issue or submit a pull request.

## Acknowledgments
Thanks to the developers of the libraries used in this project, including aiohttp, BeautifulSoup, and Pillow.