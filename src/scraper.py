"""Module for scraping and formatting USACO problems from their website."""

import argparse
import os
import time

import bs4
import requests

class USACOProblem:
    """Class to scrape, format and save USACO problems from their website."""

    USACO_BASE_URL: str = "https://usaco.org/"
    PROBLEM_SUBWEBSITE: str = "index.php?page=viewproblem"

    def __init__(self, url: str) -> None:
        """Initialize USACOProblem with given URL."""
        if not self.is_valid_url(url):
            raise ValueError(
                f"URL must start with: {self.USACO_BASE_URL} and contain {self.PROBLEM_SUBWEBSITE}."
            )

        # Group related attributes into a dictionary
        self.problem_info = {
            'url': url,
            'contest_url': None,
            'contest_title': None,
            'problem_title': None,
            'division': None,
            'abbreviated_title': None,
            'text': None
        }

        self._soup = self._fetch_problem_page(url)
        self._parse_problem_data()

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """Validate if the given URL is a valid USACO problem URL.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        return bool(
            url and
            url.startswith(cls.USACO_BASE_URL) and
            cls.PROBLEM_SUBWEBSITE in url
        )

    def _fetch_problem_page(self, url: str) -> bs4.BeautifulSoup:
        """Fetch and parse the problem page.
        
        Args:
            url (str): URL to fetch
            
        Returns:
            bs4.BeautifulSoup: Parsed HTML content
            
        Raises:
            requests.exceptions.ConnectionError: If connection fails
        """
        response = None
        attempts, max_attempts = 0, 3
        while response is None and attempts < max_attempts:
            try:
                response = requests.get(url, timeout=30)
            except requests.exceptions.ConnectionError:
                print(f"Connection error. Retrying {max_attempts - attempts} more times.")
                time.sleep(attempts)
                attempts += 1

        if response is None:
            raise requests.exceptions.ConnectionError(
                "Connection error. Please check your internet connection or the URL."
            )

        return bs4.BeautifulSoup(response.content, "html.parser")

    def _parse_problem_data(self) -> None:
        """Parse problem data from the fetched page."""
        # Parse contest and problem information
        self.problem_info['contest_url'] = (
            self.USACO_BASE_URL + self._soup.find("button")["onclick"].split("'")[1]
        )
        self.problem_info['contest_title'] = self._soup.find("h2").text.strip()
        self.problem_info['problem_title'] = self._soup.find_all("h2")[1].text.strip()
        self.problem_info['division'] = self.problem_info['contest_title'].split(" ")[-1]
        self.problem_info['abbreviated_title'] = self._format_abreviated_title()

        # Generate formatted problem text
        problem_statement = self._format_problem_statement()
        self.problem_info['text'] = self._format_problem(problem_statement)

    def _format_problem_statement(self) -> str:
        """Extracts the problem statement from the USACO problem page and formats it for markdown.

        Returns:
                str: Formatted problem statement.
        """
        problem_text_div = self._soup.find("div", class_="problem-text")
        if not problem_text_div:
            return "Problem text not found."

        # Extract text that will be formatted for markdown
        subheaders: set[str] = {
            subheader.text.strip() for subheader in problem_text_div.find_all("h4")
        }
        sample_inputs: list[str] = [
            sample_input.text.strip()
            for sample_input in problem_text_div.find_all("pre", class_="in")
        ]
        sample_outputs: list[str] = [
            sample_output.text.strip()
            for sample_output in problem_text_div.find_all("pre", class_="out")
        ]
        bolded_texts: set[str] = {
            bolded.text.strip() for bolded in problem_text_div.find_all("strong")
        }

        problem_text: str = problem_text_div.text

        # Format for markdown

        # Format subheaders to be titles
        for subheader in subheaders:
            problem_text = problem_text.replace(subheader, f"**{subheader}**  ")

        # Format sample input to be a code block
        sample_start: int = 0
        target: str = "**SAMPLE INPUT:**"
        for sample_input in sample_inputs:
            # Find the the current sample input index based off previous start index
            sample_start = problem_text.find(target, sample_start)
            if sample_start == -1:
                break
            sample_end = sample_start + len(target)

            # Gather other characters & spaces
            while problem_text[sample_end] != "\n":
                sample_end += 1

            sample_title: str = problem_text[sample_start : sample_end + 1]
            problem_text = problem_text.replace(
                f"{sample_title}{sample_input}",
                f"{sample_title}```\n{sample_input}\n```plaintext",
            )

            sample_start = (
                sample_end  # Update the start index for the next sample input
            )

        # Format sample output to be a code block
        sample_start = 0
        target = "**SAMPLE OUTPUT:**"
        for sample_output in sample_outputs:
            # Find the the current sample output index based off previous start index
            sample_start = problem_text.find(target, sample_start)
            if sample_start == -1:
                break
            sample_end = sample_start + len(target)

            # Gather other characters & spaces
            while problem_text[sample_end] != "\n":
                sample_end += 1

            sample_title = problem_text[sample_start : sample_end + 1]
            problem_text = problem_text.replace(
                f"{sample_title}{sample_output}",
                f"{sample_title}``\n{sample_output}\n```plaintext",
            )

            sample_start = sample_end

        # Format bolded text
        for bolded_text in bolded_texts:
            problem_text = problem_text.replace(bolded_text, f"**{bolded_text}**")

        return problem_text

    def _format_abreviated_title(self) -> str:
        """Formats the problem title to be used as the file name.

        Returns:
                str: Formatted problem title.
        """
        year = self.problem_info['contest_title'].split(" ")[1]
        problem_number = self.problem_info['problem_title'].split(" ")[1].split(".")[0]
        problem_name = "_".join(self.problem_info['problem_title'].split(" ")[2::])
        return f"P{problem_number}_{year}-{problem_name}"

    def _format_problem(self, problem_statement: str) -> str:
        """Format the complete problem for markdown."""
        contest_title = f"# [{self.problem_info['contest_title']}]({self.problem_info['contest_url']})"
        problem_title = f"## [{self.problem_info['problem_title']}]({self.problem_info['url']})"
        return f"{contest_title}\n{problem_title}\n\n{problem_statement}"

    def write_problem(self, save_as: str = "README", overwrite: bool = False) -> None:
        """Write the problem to a markdown file."""
        # Check & get the directory and file name to save the problem as
        file_name: str = ""
        directory: str = ""

        if any(char in save_as for char in ["*", "?", '"', "<", ">", "|"]):
            raise ValueError("File name contains invalid characters.")

        if "." in save_as and (not save_as.endswith(".md") and not save_as.endswith(".txt")):
            raise ValueError("File must be a markdown file or a text file.")

        if ("\\" in save_as or "/" in save_as) and not os.path.exists(os.path.dirname(save_as)):
            raise ValueError("Directory does not exist.")

        if os.path.exists(os.path.dirname(save_as)):
            directory = os.path.dirname(save_as)
            file_name = os.path.basename(save_as)
        else:
            default_directory = os.getcwd()
            directory = (
                default_directory
                if not default_directory.endswith("src")
                else default_directory[:-4]
            )
            file_name = save_as

        # Create a valid file path
        base_name, extension = os.path.splitext(file_name)
        if not extension:
            extension = ".md"

        existing_files = os.listdir(directory)

        if file_name not in existing_files or overwrite:
            save_as = os.path.join(directory, file_name)
        else:
            num = 1
            while f"{base_name} ({num}){extension}" in existing_files:
                num += 1

            save_as = os.path.join(directory, f"{base_name} ({num}){extension}")

        # Create a new file with the formatted problem
        with open(save_as, "w", encoding="utf-8") as fin:
            fin.write(self.text)

    @property
    def text(self) -> str:
        """Get the formatted problem text."""
        return self.problem_info['text']

    @text.setter
    def text(self, value: str) -> None:
        """Set the formatted problem text."""
        self.problem_info['text'] = value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="URL of the USACO problem")
    parser.add_argument(
        "--save", type=str, help="File name to save the problem as", default="README"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the file if it already exists",
        default=False,
    )
    args = parser.parse_args()

    usaco_problem = USACOProblem(url=args.url)
    usaco_problem.write_problem(save_as=args.save, overwrite=args.overwrite)
