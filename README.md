# USA Computing Olympiad problem scraper

This is a simple program that scrapes problems from the USA Computing Olympiad website and saves them to a local directory. The program is written in Python and uses the BeautifulSoup library to parse the HTML of the website.

## Requirements

1. Python3 preferably 3.11 or higher.
2. Install third party Python libraries (`beautifulsoup4`, `requests`, `customtkinter`) using the text file from the repository.

    ```bash
    pip install -r requirements.txt
    ```

## Using the scraper python script

1. Locate the file `scraper.py` in `src` folder of the repository.

2. Run the file using the following command:

    ```bash
    python3 scraper.py <usaco-website-url> --save <file-and-or-directory-path> --overwrite
    ```

    > **Note:** that `--save` and `overwrite` are optional arguments. If `--save` is not provided, the problems will be saved to a file called `README.md` in the repository folder. While `--overwrite` is a flag that will overwrite the file if it already exists.

    Example 1:

    ```bash
    python3 scraper.py "https://usaco.org/index.php?page=viewproblem2&cpid=810" --save "Test"
    ```

    Example 2:

    ```bash
    python3 scraper.py "https://usaco.org/index.php?page=viewproblem2&cpid=1422" --save "C:\\Program Files\\Test.md" --overwrite
    ```

## Using the USACO scraper file with the GUI

1. Locate the file `main.py` in the `src` folder of the repository.

2. Run the file using the following command:

    ```bash
    python main.py
    ```

3. A GUI window will open up. Enter the USACO website URL and click on the "Scrape" button. Optionally, select the directory where you want to save the problems; by default, the problems will be saved to a file called `README.md` in the `downloads` directory.
