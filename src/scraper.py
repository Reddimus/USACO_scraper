"""Module for scraping and formatting USACO problems from their website."""

import argparse
import os
import time

import bs4
import requests

class USACOProblem:
    """Class to scrape, format and save USACO problems from their website."""

    def __init__(self, url: str) -> None:
        """Initialize USACOProblem with given URL."""
        self.usaco_base_url: str = "https://usaco.org/"
        problem_subwebsite: str = "index.php?page=viewproblem"
        if (
            not url
            or not url.startswith(self.usaco_base_url)
            or problem_subwebsite not in url
        ):
            raise ValueError(
                f"URL must start with: {self.usaco_base_url} and contain {problem_subwebsite}."
            )
        self.url: str = url

        response = None
        attempts, max_attempts = 0, 3
        while response is None and attempts < max_attempts:
            try:
                response = requests.get(url, timeout=30)
            except requests.exceptions.ConnectionError:
                print(
                    f"Connection error. Retrying {max_attempts - attempts} more times."
                )
                time.sleep(attempts)
                attempts += 1
        if response is None:
            raise requests.exceptions.ConnectionError(
                "Connection error. Please check your internet connection or the URL."
            )
        self._soup = bs4.BeautifulSoup(response.content, "html.parser")

        self.contest_url = (
            self.usaco_base_url + self._soup.find("button")["onclick"].split("'")[1]
        )
        self.contest_title: str = self._soup.find("h2").text.strip()
        self.problem_title: str = self._soup.find_all("h2")[1].text.strip()
        self.division: str = self.contest_title.split(" ")[-1]
        self.abreviated_title: str = self._format_abreviated_title()
        self.problem_statement: str = self._format_problem_statement()
        self.text: str = self._format_problem()

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
        year: str = self.contest_title.split(" ")[1]

        problem_number: str = self.problem_title.split(" ")[1].split(".")[0]
        problem_name: str = "_".join(self.problem_title.split(" ")[2::])
        return f"P{problem_number}_{year}-{problem_name}"

    def _format_problem(self) -> str:
        """Formats the problem for markdown.

        Returns:
                str: Formatted problem.
        """
        contest_title: str = f"# [{self.contest_title}]({self.contest_url})"
        problem_title: str = f"## [{self.problem_title}]({self.url})"
        return f"{contest_title}\n{problem_title}\n\n{self.problem_statement}"

    def write_problem(self, save_as: str = "README", overwrite: bool = False) -> None:
        """Write the problem to a markdown file."""
        # Check & get the directory and file name to save the problem as
        file_name: str = ""
        directory: str = ""
        # If the save_as file has invalid characters
        if any(char in save_as for char in ["*", "?", '"', "<", ">", "|"]):
            raise ValueError("File name contains invalid characters.")
        # Else if the save_as file is invalid file type format
        elif "." in save_as and (
            not save_as.endswith(".md") and not save_as.endswith(".txt")
        ):
            raise ValueError("File must be a markdown file or a text file.")
        # Else if the save_as file is located at a directory that does not exist
        elif ("\\" in save_as or "/" in save_as) and not os.path.exists(
            os.path.dirname(save_as)
        ):
            raise ValueError("Directory does not exist.")
        # Else if the save_as file is located at a valid directory
        elif os.path.exists(os.path.dirname(save_as)):
            directory = os.path.dirname(save_as)
            file_name = os.path.basename(save_as)
        # Else if the save_as file is just a string and not a directory
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
