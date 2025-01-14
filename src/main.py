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

        # Group configuration related attributes
        self.config = {
            'settings_directory': os.path.join(os.path.dirname(os.getcwd()), "settings.json"),
            'save_directory': None,
            'usaco_problem': None
        }
        self._load_settings()

        # Initialize the window
        self.title("USACO Problem Scraper")
        self.geometry(f"{self.window_size[0]}x{self.window_size[1]}")
        self.attributes("-fullscreen", self.is_fullscreen)

        # Group UI components
        self.components = {
            'top_frame': None,
            'url_entry': None,
            'save_button': None,
            'scrape_button': None,
            'text_area': None
        }
        self._setup_ui()

    def _load_settings(self):
        """Load settings from the settings file."""
        with open(self.config['settings_directory'], "r", encoding="utf-8") as file:
            settings = json.load(file)

        self.window_size = settings["resolution"]
        self.is_fullscreen = settings["fullscreen"]
        self.config['save_directory'] = (
            os.path.expanduser(settings["save_directory"])
            if settings["save_directory"] == "~\\Downloads"
            else settings["save_directory"]
        )

    def _setup_ui(self):
        """Setup UI components."""
        # Top Frame setup
        self.components['top_frame'] = customtkinter.CTkFrame(self)
        self.components['top_frame'].pack(pady=20, padx=20, side=tkinter.TOP, fill=tkinter.X)

        # URL Entry setup
        self.components['url_entry'] = customtkinter.CTkEntry(
            self.components['top_frame'],
            placeholder_text="Enter USACO Problem URL"
        )
        self.components['url_entry'].pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)
        self.components['url_entry'].bind("<KeyRelease>", self._validate_url)
        self.components['url_entry'].bind("<Return>", self._scrape_problem)
        self.components['url_entry'].bind("<Return>", self._validate_save)

        # Save Button setup
        self.components['save_button'] = customtkinter.CTkButton(
            self.components['top_frame'],
            text="Save",
            command=self._save_problem,
            state=tkinter.DISABLED,
            width=30
        )
        self.components['save_button'].pack(side=tkinter.RIGHT)

        # Scrape Button setup
        self.components['scrape_button'] = customtkinter.CTkButton(
            self.components['top_frame'],
            text="Scrape",
            command=self._scrape_problem,
            state=tkinter.DISABLED,
            width=150
        )
        self.components['scrape_button'].pack(side=tkinter.RIGHT)
        self.components['scrape_button'].bind("<Button-1>", self._validate_save)

        # Text Area setup
        self.components['text_area'] = customtkinter.CTkTextbox(self)
        self.components['text_area'].pack(padx=20, pady=20, expand=True, fill=tkinter.BOTH)
        self.components['text_area'].bind("<KeyRelease>", self._update_text)

    def _validate_url(self, _):
        """Validate the URL in the URL entry"""
        url = self.components['url_entry'].get().strip()
        if url.startswith("https://usaco.org/") and "index.php?page=viewproblem" in url:
            self.components['scrape_button'].configure(state=tkinter.NORMAL)
        else:
            self.components['scrape_button'].configure(state=tkinter.DISABLED)

    def _validate_save(self, _):
        """Validate the save button"""
        if self.config['usaco_problem'] is None:
            self.components['save_button'].configure(state=tkinter.DISABLED)
        else:
            self.components['save_button'].configure(state=tkinter.NORMAL)

    def _scrape_problem(self, _=None):
        """Scrape the USACO problem and display it"""
        if self.components['scrape_button'].cget("state") == tkinter.DISABLED:
            return

        self.config['usaco_problem'] = scraper.USACOProblem(self.components['url_entry'].get().strip())
        self.components['text_area'].delete("1.0", tkinter.END)
        self.components['text_area'].insert(tkinter.END, self.config['usaco_problem'].text)

    def _save_problem(self):
        """Save the USACO problem to a file"""
        file_directory = tkinter.filedialog.asksaveasfilename(
            initialdir=self.config['save_directory'],
            title="Save USACO Problem",
            defaultextension=".md",
            filetypes=(("Markdown files", "*.md"), ("Text files", "*.txt"))
        )
        if file_directory:
            # Get directory
            self.config['save_directory'] = os.path.dirname(file_directory)
            self.config['usaco_problem'].write_problem(save_as=file_directory, overwrite=True)

    def _update_text(self, _):
        """Update the text area with the new text"""
        if self.config['usaco_problem'] is not None:
            self.config['usaco_problem'].text = self.components['text_area'].get("1.0", tkinter.END)

    def close_window(self):
        """Save settings and close the application window."""
        settings = {
            "fullscreen": self.attributes("-fullscreen"), 
            "resolution": self.window_size, 
            "save_directory": self.config['save_directory']
        }
        # Write settings.json file back one directory
        with open(self.config['settings_directory'], "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4, sort_keys=True)

        self.destroy()

if __name__ == "__main__":
    app = USACOProblemScraper()
    app.protocol("WM_DELETE_WINDOW", app.close_window)
    app.mainloop()
