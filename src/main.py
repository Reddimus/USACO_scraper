import scraper
import customtkinter, tkinter, os, json

class USACOProblemScraper(customtkinter.CTk):
    def __init__(self):
        """Initialize the USACO Problem Scraper GUI"""
        super().__init__()

        # Initialize the window
        self.title("USACO Problem Scraper")
        self.geometry("400x400")

        # Initialize directory
        self.font: tuple = ("Arial", 12)   # min font size: 12, max font size: 72
        # Max height for group frame should be 400

        # Create a frame to hold all the widgets and center them
        self.center_frame = customtkinter.CTkFrame(self)
        self.center_frame.pack(pady=30, padx=30, expand=True, fill=tkinter.BOTH)
        self.center_frame.bind("<Configure>", self._resize_font)

        # Initialize url entry
        self.url: str = ""
        self.url_entry = customtkinter.CTkEntry(
            self.center_frame, 
            placeholder_text="USACO Problem URL", 
            font=self.font
        )
        self.url_entry.pack(pady=3, padx=3, expand=True, fill=tkinter.BOTH)
        self.url_entry.bind("<KeyRelease>", self._check_entries)

        # Initialize file entry
        self.file: str = "README"
        self.file_entry = customtkinter.CTkEntry(
            self.center_frame, 
            placeholder_text="File", 
            font=self.font
        )
        self.file_entry.insert(tkinter.END, self.file)
        self.file_entry.pack(pady=3, padx=3, expand=True, fill=tkinter.BOTH)
        self.file_entry.bind("<KeyRelease>", self._check_entries)

        # Initialize the directory button
        self.directory_button = customtkinter.CTkButton(
            self.center_frame,
            text="Directory",
            command=self._choose_directory,
            font=self.font,
        )
        self.directory_button.pack(pady=3, padx=3, expand=True, fill=tkinter.BOTH)
        self.target_directory = os.path.expanduser('~\\Downloads')

        # Initialize the scrape button
        self.scrape_button = customtkinter.CTkButton(
            self.center_frame,
            text="Scrape",
            command=self._scrape_problem,
            font=self.font,
            state=tkinter.DISABLED
        )
        self.scrape_button.pack(pady=3, padx=3, expand=True, fill=tkinter.BOTH)

    def _resize_font(self, event):
        """Resize the font size of the widgets based on the window size

        Args:
            event (tkinter.Event): The event that triggered the font resize
        """
        new_font_size = min(max(int(event.width / 21), 12), 72)
        self.font = ("Arial", new_font_size)
        self.url_entry.configure(font=self.font)
        self.file_entry.configure(font=self.font)
        self.directory_button.configure(font=self.font)
        self.scrape_button.configure(font=self.font)

    def _choose_directory(self):
        """Choose the target directory to save the problem file when the directory button is clicked"""
        choosen_directory = tkinter.filedialog.askdirectory(initialdir=self.target_directory)
        if choosen_directory:
            self.target_directory = choosen_directory

    def _check_entries(self, event):
        """Check the url and file entries to enable the scrape button if they are valid.

        Args:
            event (tkinter.Event): The event that triggered the check
        """
        url: str = self.url_entry.get().strip()
        file: str = self.file_entry.get().strip()
        invalid_chars: list[str] = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if (url.startswith("https://usaco.org/index.php?page=viewproblem") and
        (not '.' in file or file.endswith('.md') and 
        not any(char in file for char in invalid_chars))):
            if self.scrape_button.cget('state') != tkinter.NORMAL:
                self.scrape_button.configure(state=tkinter.NORMAL)
        else:
            if self.scrape_button.cget('state') != tkinter.DISABLED:
                self.scrape_button.configure(state=tkinter.DISABLED)

    def _scrape_problem(self):
        """Scrape the USACO problem and write it to the target directory"""
        self.url = self.url_entry.get()
        self.file = self.file_entry.get()
        usaco_problem = scraper.USACOProblem(self.url, self.file, self.target_directory)
        usaco_problem.write_problem()

if __name__ == "__main__":
    app = USACOProblemScraper()
    app.mainloop()
