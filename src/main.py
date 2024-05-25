import scraper
import customtkinter, tkinter, os, json

class USACOProblemScraper(customtkinter.CTk):
    def __init__(self):
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

        # Initialize file entry
        self.file: str = "README.md"
        self.file_entry = customtkinter.CTkEntry(
            self.center_frame, 
            placeholder_text="File", 
            font=self.font
        )
        self.file_entry.insert(tkinter.END, self.file)
        self.file_entry.pack(pady=3, padx=3, expand=True, fill=tkinter.BOTH)

        # Initialize the directory button
        self.directory_button = customtkinter.CTkButton(
            self.center_frame,
            text="Choose Directory",
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
        )
        self.scrape_button.pack(pady=3, padx=3, expand=True, fill=tkinter.BOTH)

    def _resize_font(self, event):
        new_font_size = min(max(int(event.width / 21), 12), 72)
        self.font = ("Arial", new_font_size)
        self.url_entry.configure(font=self.font)
        self.file_entry.configure(font=self.font)
        self.directory_button.configure(font=self.font)
        self.scrape_button.configure(font=self.font)

    def _choose_directory(self):
        choosen_directory = tkinter.filedialog.askdirectory(initialdir=self.target_directory)
        if choosen_directory:
            self.target_directory = choosen_directory

    def _scrape_problem(self):
        self.url = self.url_entry.get()
        self.file = self.file_entry.get()
        usaco_problem = scraper.USACOProblem(self.url, self.file, self.target_directory)
        usaco_problem.write_problem()

if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")
    app = USACOProblemScraper()
    app.mainloop()