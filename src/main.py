"""GUI application for scraping USACO problems from their website and saving them locally."""

import json
import os
import tkinter

import customtkinter

import scraper

class USACOProblemScraper(customtkinter.CTk):
    """GUI application that provides an interface for scraping and saving USACO problems."""

    def __init__(self):
        """Initialize the USACO Problem Scraper GUI"""
        super().__init__()

        self.settings_directory: str = os.path.join(os.path.dirname(os.getcwd()), "settings.json")
        with open(self.settings_directory, "r", encoding="utf-8") as file:
            settings = json.load(file)

        # Initialize the window
        self.title("USACO Problem Scraper")

        width, height = settings["resolution"]
        self.geometry(f"{width}x{height}")

        if settings["fullscreen"]:
            self.attributes("-fullscreen", True)
        else:
            self.attributes("-fullscreen", False)

        self.usaco_problem = None
        if settings["save_directory"] == "~\\Downloads":
            self.save_directory = os.path.expanduser(settings["save_directory"])
        else:
            self.save_directory = settings["save_directory"]

        # Top Frame for URL entry and Scrape button
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.pack(pady=20, padx=20, side=tkinter.TOP, fill=tkinter.X)

        self.url_entry = customtkinter.CTkEntry(
            self.top_frame,
            placeholder_text="Enter USACO Problem URL"
        )
        self.url_entry.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)
        self.url_entry.bind("<KeyRelease>", self._validate_url)
        self.url_entry.bind("<Return>", self._scrape_problem)
        self.url_entry.bind("<Return>", self._validate_save)

        self.save_button = customtkinter.CTkButton(
            self.top_frame,
            text="Save",
            command=self._save_problem,
            state=tkinter.DISABLED,
            width=30
        )
        self.save_button.pack(side=tkinter.RIGHT)

        self.scrape_button = customtkinter.CTkButton(
            self.top_frame,
            text="Scrape",
            command=self._scrape_problem,
            state=tkinter.DISABLED,
            width=150
        )
        self.scrape_button.pack(side=tkinter.RIGHT)
        self.scrape_button.bind("<Button-1>", self._validate_save)

        # Text Area for displaying scraped problem text
        self.text_area = customtkinter.CTkTextbox(self)
        self.text_area.pack(padx=20, pady=20, expand=True, fill=tkinter.BOTH)
        self.text_area.bind("<KeyRelease>", self._update_text)

    def _validate_url(self, _):
        """Validate the URL in the URL entry"""
        url = self.url_entry.get().strip()
        if url.startswith("https://usaco.org/") and "index.php?page=viewproblem" in url:
            self.scrape_button.configure(state=tkinter.NORMAL)
        else:
            self.scrape_button.configure(state=tkinter.DISABLED)

    def _validate_save(self, _):
        """Validate the save button"""
        if self.usaco_problem is None:
            self.save_button.configure(state=tkinter.DISABLED)
        else:
            self.save_button.configure(state=tkinter.NORMAL)

    def _scrape_problem(self, _=None):
        """Scrape the USACO problem and display it"""
        if self.scrape_button.cget("state") == tkinter.DISABLED:
            return

        self.usaco_problem = scraper.USACOProblem(self.url_entry.get().strip())
        self.text_area.delete("1.0", tkinter.END)
        self.text_area.insert(tkinter.END, self.usaco_problem.text)

    def _save_problem(self):
        """Save the USACO problem to a file"""
        file_directory = tkinter.filedialog.asksaveasfilename(
            initialdir=self.save_directory,
            title="Save USACO Problem",
            defaultextension=".md",
            filetypes=(("Markdown files", "*.md"), ("Text files", "*.txt"))
        )
        if file_directory:
            # Get directory
            self.save_directory = os.path.dirname(file_directory)
            self.usaco_problem.write_problem(save_as=file_directory, overwrite=True)

    def _update_text(self, _):
        """Update the text area with the new text"""
        if self.usaco_problem is not None:
            self.usaco_problem.text = self.text_area.get("1.0", tkinter.END)

    def close_window(self):
        """Save settings and close the application window."""
        settings = {
            "fullscreen": self.attributes("-fullscreen"), 
            "resolution": (self.winfo_width(), self.winfo_height()), 
            "save_directory": self.save_directory
        }
        # Write settings.json file back one directory
        with open(self.settings_directory, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4, sort_keys=True)

        self.destroy()

if __name__ == "__main__":
    app = USACOProblemScraper()
    app.protocol("WM_DELETE_WINDOW", app.close_window)
    app.mainloop()
