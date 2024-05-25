import requests, bs4, time, os, argparse

class USACOProblem:
	def __init__(self, url: str, file: str = "README.md", directory: str = os.getcwd()):
		"""Scrapes a USACO problem and writes it to a markdown file.

		Args:
			url (str): URL of the USACO problem.
			file (str, optional): File name to write the problem to. Defaults to "README.md".
			directory (str, optional): Directory to write the file to. Defaults to workspace directory.
		"""
		self.URL: str = url
		self.FILE: str = file
		if directory == os.getcwd() and directory.endswith('src'):
			directory = os.getcwd()[:-4]	# Remove the 'src' part of the directory
		self.DIRECTORY: str = directory

		response = None
		attempts, max_attempts = 0, 3
		while response is None and attempts < max_attempts:
			try:
				response = requests.get(url)
			except requests.exceptions.ConnectionError:
				print(f"Connection error. Retrying {max_attempts - attempts} more times.")
				time.sleep(attempts)
				attempts += 1
		self._soup = bs4.BeautifulSoup(response.content, 'html.parser')

		self.CONTEST_URL = "https://usaco.org/" + self._soup.find('button')['onclick'].split('\'')[1]
		self.CONTEST_TITLE: str = self._soup.find('h2').text.strip()
		self.PROBLEM_TITLE: str = self._soup.find_all('h2')[1].text.strip()
		self.division: str = self.CONTEST_TITLE.split(' ')[-1]
		self.abreviated_title: str = self._format_abreviated_title()
		self.PROBLEM_STATEMENT: str = self._format_problem_statement()
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
		subheaders: list[str] = [
			subheader.text.strip() 
			for subheader in problem_text_div.find_all("h4")
		]
		sample_input: str = problem_text_div.find("pre", class_="in").text.strip()
		sample_output: str = problem_text_div.find('pre', class_='out').text.strip()
		bolded_texts: list[str] = [
			bolded.text.strip() 
			for bolded in problem_text_div.find_all("strong")
		]

		problem_text: str = problem_text_div.text.strip()

		# Format for markdown
		for subheader in subheaders:
			problem_text = problem_text.replace(subheader, f"### {subheader}  ")
		sample_start = problem_text.find("### SAMPLE INPUT:")
		sample_end = sample_start + len("### SAMPLE INPUT:")
		while problem_text[sample_end] != '\n':
			sample_end += 1
		sample_title = problem_text[sample_start:sample_end+1]
		problem_text = problem_text.replace(
			f"{sample_title}{sample_input}", 
			f"{sample_title}```\n{sample_input}\n```"
		)
		sample_start = problem_text.find("### SAMPLE OUTPUT:")
		sample_end = sample_start + len("### SAMPLE OUTPUT:")
		while problem_text[sample_end] != '\n':
			sample_end += 1
		sample_title = problem_text[sample_start:sample_end+1]
		problem_text = problem_text.replace(
			f"{sample_title}{sample_output}",
			f"{sample_title}```\n{sample_output}\n```"
		)
		for bolded_text in bolded_texts:
			problem_text = problem_text.replace(bolded_text, f"**{bolded_text}**")
		
		return problem_text

	def _format_abreviated_title(self) -> str:
		"""Formats the problem title to be used as the file name.

		Returns:
			str: Formatted problem title.
		"""
		year: str = self.CONTEST_TITLE.split(' ')[1]

		problem_number: str = self.PROBLEM_TITLE.split(' ')[1].split('.')[0]
		problem_name: str = '_'.join(self.PROBLEM_TITLE.split(' ')[2::])
		return f'P{problem_number}_{year}-{problem_name}'
	
	def _format_problem(self) -> str:
		"""Formats the problem for markdown.

		Returns:
			str: Formatted problem.
		"""
		contest_title: str = f'# [{self.CONTEST_TITLE}]({self.CONTEST_URL})'
		problem_title: str = f'## [{self.PROBLEM_TITLE}]({self.URL})'
		problem_statement: str = self._format_problem_statement()
		return f'{contest_title}\n{problem_title}\n\n{problem_statement}'

	def write_problem(self) -> None:
		"""Writes the problem to a markdown file."""
		file: str = self.FILE
		num: int = 1
		while os.path.exists(os.path.join(self.DIRECTORY, file)):
			file = f"{self.FILE.split('.')[0]} ({num}).md"
			num += 1

		with open(os.path.join(self.DIRECTORY, file), 'w') as fin:
			fin.write(self.text)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('url', type=str, help='URL of the USACO problem')
	parser.add_argument('--file', type=str, help='File to write the problem to', default='README.md')
	parser.add_argument('--directory', type=str, help='Directory to write the file to', default=os.getcwd())
	args = parser.parse_args()

	usaco_problem = USACOProblem(url=args.url, file=args.file)
	usaco_problem.write_problem()