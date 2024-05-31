import requests, bs4, time, os, argparse

class USACOProblem:
	def __init__(self, url: str) -> None:
		"""Scrapes a USACO problem from the given URL and formats it for markdown.

		Args:
			url (str): URL of the USACO problem.
		"""
		self.USACO_WEBSITE: str = "https://usaco.org/"
		problem_subwebsite: str = "index.php?page=viewproblem"
		if not url or not url.startswith(self.USACO_WEBSITE) or problem_subwebsite not in url:
			raise ValueError(f"URL must start with: {self.USACO_WEBSITE} and contain {problem_subwebsite}.")
		self.URL: str = url

		response = None
		attempts, max_attempts = 0, 3
		while response is None and attempts < max_attempts:
			try:
				response = requests.get(url)
			except requests.exceptions.ConnectionError:
				print(f"Connection error. Retrying {max_attempts - attempts} more times.")
				time.sleep(attempts)
				attempts += 1
		if response is None:
			raise requests.exceptions.ConnectionError("Connection error. Please check your internet connection or the URL.")
		self._soup = bs4.BeautifulSoup(response.content, 'html.parser')

		self.CONTEST_URL = self.USACO_WEBSITE + self._soup.find('button')['onclick'].split('\'')[1]
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

	def write_problem(self, save_as: str = "README", overwrite: bool = False) -> None:
		"""Writes the problem to a markdown file.

		Args:
			save_as (str, optional): File name to save the problem as. Defaults to "README".
			overwrite (bool, optional): Overwrite the file if it already exists. Defaults to False.
		"""

		# Check & get the directory and file name to save the problem as
		file_name: str = ""
		directory: str = ""
		# If the save_as file has invalid characters
		if any(char in save_as for char in ['*', '?', '"', '<', '>', '|']):
			raise ValueError("File name contains invalid characters.")
		# Else if the save_as file is invalid file type format
		elif '.' in save_as and (not save_as.endswith('.md') and not save_as.endswith('.txt')):
			raise ValueError("File must be a markdown file or a text file.")
		# Else if the save_as file is located at a directory that does not exist
		elif ('\\' in save_as or '/' in save_as) and not os.path.exists(os.path.dirname(save_as)):
			raise ValueError("Directory does not exist.")
		# Else if the save_as file is located at a valid directory
		elif os.path.exists(os.path.dirname(save_as)):
			directory = os.path.dirname(save_as)
			file_name = os.path.basename(save_as)
		# Else if the save_as file is just a string and not a directory
		else:
			default_directory = os.getcwd()
			directory = default_directory if not default_directory.endswith('src') else default_directory[:-4]
			file_name = save_as

		# Create a valid file path
		base_name, extension = os.path.splitext(file_name)
		if not extension:
			extension = '.md'
		
		existing_files = os.listdir(directory)

		if file_name not in existing_files or overwrite:
			save_as = os.path.join(directory, file_name)
		else:
			num = 1
			while f"{base_name} ({num}){extension}" in existing_files:
				num += 1

			save_as = os.path.join(directory, f"{base_name} ({num}){extension}")

		# Create a new file with the formatted problem
		with open(save_as, 'w') as fin:
			fin.write(self.text)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'url', 
		type=str, 
		help='URL of the USACO problem'
	)
	parser.add_argument(
		'--save', 
		type=str, 
		help='File name to save the problem as', 
		default='README'
	)
	parser.add_argument(
		'--overwrite', 
		action='store_true', 
		help='Overwrite the file if it already exists', 
		default=False
	)
	args = parser.parse_args()

	usaco_problem = USACOProblem(url=args.url)
	usaco_problem.write_problem(save_as=args.save, overwrite=args.overwrite)
