
import configparser
import ctypes
import idlelib.colorizer as ic
import idlelib.percolator as ip
import pathlib
import time
import tkinter as tk
import tkinter.font as tkfont

from tkinter import colorchooser
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog

class TextEditor:
	# root window
	root = tk.Tk()

	# main toolbar
	toolbar = tk.Menu(root)

	# tool bar options
	file_menu = tk.Menu(toolbar, tearoff=0)
	tools_menu = tk.Menu(toolbar, tearoff=0)
	editor_menu = tk.Menu(toolbar, tearoff=0)
	about_menu = tk.Menu(toolbar, tearoff=0)

	# text area
	text_area = tk.Text(root, wrap="none", state="normal")

	# table
	table = tk.Frame(root)

	# vertical scroll bar
	v_scroll = tk.Scrollbar(root, command=text_area.yview)

	# horizontal scroll bar
	h_scroll = tk.Scrollbar(root, orient="horizontal", command=text_area.xview)

	# line count label
	line_cnt_lbl = tk.Label(root, text="Lines: ")

	# status label
	status_lbl = tk.Label(root, text="Status: ")

	# config files
	config = ""
	theme_config = ""

	# theme highlighting, probably better ways
	perc = ip.Percolator(text_area)
	old_cdg = ""
	curr_cdg = ""

	# default don't show console
	console_toggle=False

	# configuration and start main loop
	def __init__(self, config, theme_config):
		self.toggle_console()
		self.config = config
		self.theme_config = theme_config

		# root related stuff
		print("Initializing root...")
		self.root.title("Text Editor v0.3")
		width = self.config["settings"]["winx"]
		height = self.config["settings"]["winy"]
		posx = self.config["settings"]["posx"]
		posy = self.config["settings"]["posy"]
		self.root.geometry(f"{width}x{height}+{posx}+{posy}")
		# self.root.state("zoomed")   # start maximized, figure out how to save state to eventually
		self.root.protocol("WM_DELETE_WINDOW",self.exit)    # overwrite exit behaviour to save ini file before exiting

		########################################################################
		# TOOL BAR STUFF
		########################################################################
		print("Intializing toolbar...")
		# link root to toolbar
		self.root.config(menu=self.toolbar)

		# add command(s) to file option
		self.file_menu.add_command(label="New", command=self.new_file)
		self.file_menu.add_command(label="Open", command=self.open_file)
		self.file_menu.add_command(label="Save", command=self.save_file)
		self.file_menu.add_command(label="Exit", command=self.exit)

		# add theme menu dynamically
		self.load_theme_menu()

		# tools menu
		self.tools_menu.add_command(label="Show text", command=self.show_text)
		self.tools_menu.add_command(label="Show table", command=self.show_table)
		self.tools_menu.add_command(label="Convert to table", command=self.convert_to_table)
		self.tools_menu.add_command(label="Convert to text", command=self.convert_to_text)
		self.tools_menu.add_command(label="Toggle console", command=self.toggle_console)

		# about menu
		self.about_menu.add_command(label="About", command=self.about_msg_box)

		# add options to tool bar
		self.toolbar.add_cascade(label="File", menu=self.file_menu)
		self.toolbar.add_cascade(label="Tools", menu=self.tools_menu)
		self.toolbar.add_cascade(label="Editor", menu=self.editor_menu)
		self.toolbar.add_cascade(label="About", menu=self.about_menu)

		# link text area to scroll bars
		self.text_area.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

		########################################################################
		# CONFIGURE TEXT AREA STUFF
		########################################################################
		print("Intializing text area...")
		# set up tab width
		font = tkfont.Font(font=self.text_area['font'])
		tab_width = font.measure("	")
		self.text_area.config(tabs=(tab_width,))

		# create bindings for text area
		self.text_area.bind("<Key>", self.update_line_count)
		self.text_area.bind("<Control-n>", self.new_file)
		self.text_area.bind("<Control-o>", self.open_file)
		self.text_area.bind("<Control-s>", self.save_file)

		########################################################################
		# PACKING
		########################################################################
		print("Packing...")
		self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
		self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.text_area.pack(padx=20, pady=20, side=tk.LEFT, expand=True, fill=tk.BOTH)
		self.line_cnt_lbl.pack(side=tk.BOTTOM, anchor="w")
		self.status_lbl.pack(side=tk.BOTTOM, anchor="w")
		self.table.pack_forget()

		# set up start up theme
		theme = self.config["settings"]["theme"]
		self.change_theme(theme)

		# start application
		self.root.mainloop()

	def toggle_console(self):
		if self.console_toggle:
			ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
			self.console_toggle = not self.console_toggle
		else:
			ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
			self.console_toggle = not self.console_toggle

	def show_text(self):
		self.table.pack_forget()
		self.text_area.pack(padx=20, pady=20, side=tk.LEFT, expand=True, fill=tk.BOTH)

	def show_table(self):
		self.text_area.pack_forget()
		self.table.pack(padx=20, pady=20, side=tk.LEFT, expand=True, fill=tk.BOTH)

	def about_msg_box(self):
		messagebox.showinfo("About TextEditor", "Basic file editor built on Python that is built to be modular so you can build your own extensions in Python with ease!")

	# Converts the text area text to a table
	# Offers user to choose a delimiter, if nothing is picked, semi colon is used
	# Automatically removes blank entries (this may need to be changed in case
	#   there is a need for blank entries in the table)
	def convert_to_table(self):
		print("Converting text to table")
		table = tk.Frame(self.root)
		for child in self.table.winfo_children():
			child.destroy()
		delimiter = simpledialog.askstring(title="",prompt="Delimiter			")
		self.text_area.pack_forget()
		text_lines = self.text_area.get(1.0,tk.END).splitlines()
		max = self.get_longest_line(text_lines, delimiter)

		while "" in text_lines:
			text_lines.remove("")

		for line in text_lines:
			if delimiter == "":
				delimiter = "\n"
			text_split = line.strip(";").split(delimiter)
			row = tk.Frame(self.table)
			for i in range(max):
				try:
					var = tk.StringVar()
					var.set(text_split[i])
					e = tk.Entry(row, textvariable=var, highlightthickness=2)
					e.configure(highlightbackground="black", highlightcolor="blue")
					e.pack(side=tk.LEFT)
				except IndexError as e:
					var = tk.StringVar()
					var.set("")
					e = tk.Entry(row, textvariable=var, highlightthickness=2)
					e["fg"] = "black"
					e.pack(side=tk.LEFT)
			row.pack(side=tk.TOP, anchor=tk.NW)

		self.table.pack(padx=20, pady=20, side=tk.LEFT, expand=True, fill=tk.BOTH)

	# "Creates" new file, just clears text area without saving
	def new_file(self, *args):
		print("Creating new file")
		self.text_area.delete("1.0", tk.END)

	# Converts the table to plain text
	# Offers user to choose a delimiter, if nothing is picked space is used
	# Empty entries are skipped which like above may need to be changed
	def convert_to_text(self):
		print("Converting table to text")
		delimiter = simpledialog.askstring(title="",prompt="Delimiter			")
		self.table.pack_forget()
		self.text_area.delete("1.0", tk.END)
		rows = self.table.winfo_children()
		for row in rows:
			cols = row.winfo_children()
			line = ""
			for entry in cols:
				text = entry.get()
				if text == "":
					continue
				line = f"{line}{delimiter}{text}"
			if line[0] == delimiter:
				self.text_area.insert(tk.END, f"{line[1:]}\n")
			else:
				self.text_area.insert(tk.END, f"{line}\n")

		for child in self.table.winfo_children():
			child.destroy()
		self.text_area.pack(padx=20, pady=20, side=tk.LEFT, expand=True, fill=tk.BOTH)

	# gets the length of the longest list
	def get_longest_line(self, list, delim):
		max = 0
		for line in list:
			cols = len(line.strip(delim).split(delim))
			if cols > max:
				max = cols
		return max

	# updates line label with the number of lines file has
	def update_line_count(self, event):
		num_lines = int(self.text_area.index('end-1c').split('.')[0])
		self.line_cnt_lbl["text"] = f"Lines: {num_lines}"
		self.line_cnt_lbl.update()

	# saves file to disk
	# need to change initial directory
	def save_file(self, *args):
		print("Saving file")
		filetypes = []
		for key in self.config["opentypes"]:
			filetypes.append((key, self.config["opentypes"][key]))
		initial_dir = "C:/Users/brownjo/Documents/Workspaces/Git/utilities/Python/Text Editor"
		f = filedialog.asksaveasfile(defaultextension=".txt",filetypes=filetypes, mode="w")
		if f is None:
			return
		text_to_save = self.text_area.get(1.0,tk.END)
		text_to_save2 = text_to_save.replace("\t", "    ")
		f.write(text_to_save)
		f.close()

	# opens file
	# clears (no save) text area
	def open_file(self, *args):
		print("Opening file")
		filetypes = []
		for key in self.config["opentypes"]:
			filetypes.append((key, self.config["opentypes"][key]))
		f = filedialog.askopenfilename(title="Open...",filetypes=filetypes)
		if f is None:
			return
		file = open(f, "r")
		self.text_area.delete("1.0", tk.END)
		for line in file:
			self.text_area.insert(tk.END, line)
		file.close()
		self.update_line_count("a")
		self.root.title(f"Text Editor v0.1 - {f}")

	# handle program exit stuff here
	def exit(self):
		print("Saving configuration before exit")

		# save window settings
		winx = self.root.winfo_width()
		winy = self.root.winfo_height()
		posx = self.root.winfo_x()
		posy = self.root.winfo_y()
		self.config.set("settings", "winx", str(winx))
		self.config.set("settings", "winy", str(winy))
		self.config.set("settings", "posx", str(posx))
		self.config.set("settings", "posy", str(posy))

		# save config file
		with open("config.ini", "w") as configfile:
			self.config.write(configfile)
		print("Goodbye")
		self.root.destroy()

	# gets list of theme names, will be redesigned to read from individual theme files
	def get_theme_configs(self):
		config = configparser.ConfigParser()
		config.optionxform = str
		config.read("themes.ini")
		return config.sections()

	# dynamically creates menu options to change the theme with a reload themes
	# option to make changes to theme live without restarting
	def load_theme_menu(self):
		print("Loading themes")
		# add command(s) to editor option
		last = self.editor_menu.index(tk.END)
		self.editor_menu.delete(0,last)
		self.editor_menu.add_command(label="Reload themes", command=self.load_theme_menu)
		self.editor_menu.add_command(label="Color picker", command=self.color_picker)
		themes = self.get_theme_configs()
		for theme in themes:
			self.editor_menu.add_command(label=f"{theme}", command=lambda btheme=theme: self.change_theme(btheme))

	def color_picker(self):
		color_code = colorchooser.askcolor(parent=self.root, title="Color picker")

	# reloads config file
	def reload_config(self):
		self.config = configparser.ConfigParser()
		self.config.optionxform = str
		self.config.read("config.ini")

	# changes theme
	def change_theme(self, theme):
		print(f"Changing to theme: {theme}")

		# update settings config
		self.config.set("settings", "theme", theme)

		# apply theme
		self.root["bg"] = self.theme_config[theme]["editor_bg"]
		self.table["bg"] = self.theme_config[theme]["table_bg"]
		self.text_area["bg"] = self.theme_config[theme]["text_bg"]
		self.text_area["fg"] = self.theme_config[theme]["text_color"]
		self.text_area["insertbackground"] = self.theme_config[theme]["cursor_color"]

		# text highlighting
		self.curr_cdg = ic.ColorDelegator()
		self.curr_cdg.tagdefs["COMMENT"] = {"foreground": str(self.theme_config[theme]["comment"]), "background" : str(self.theme_config[theme]["comment_bg"])}
		self.curr_cdg.tagdefs["KEYWORD"] = {"foreground": str(self.theme_config[theme]["keyword"]), "background" : str(self.theme_config[theme]["keyword_bg"])}
		self.curr_cdg.tagdefs["BUILTIN"] = {"foreground": str(self.theme_config[theme]["built_in"]), "background" : str(self.theme_config[theme]["built_in_bg"])}
		self.curr_cdg.tagdefs["STRING"] = {"foreground": str(self.theme_config[theme]["string"]), "background" : str(self.theme_config[theme]["string_bg"])}
		self.curr_cdg.tagdefs["DEFINITION"] = {"foreground": str(self.theme_config[theme]["definition"]), "background" : str(self.theme_config[theme]["definition_bg"])}

		self.perc.insertfilter(self.curr_cdg)
		if self.old_cdg != "":
			test.removefilter(self.old_cdg)

		# save and load new configuration
		self.root.update()

def main():
	print("Reading config")
	config = configparser.ConfigParser()
	config.optionxform = str
	fn = pathlib.Path(__file__).parent/"config.ini"
	config.read(fn)

	theme_config = configparser.ConfigParser()
	theme_config.optionxform = str
	tfn = pathlib.Path(__file__).parent/"themes.ini"
	theme_config.read(tfn)

	print("Starting application")
	texteditor = TextEditor(config, theme_config)

if __name__ == '__main__':
	main()


