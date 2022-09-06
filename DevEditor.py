
import configparser
import idlelib.colorizer as ic
import idlelib.percolator as ip
import tkinter as tk

from tkinter import filedialog

class TextEditor:

    # root window
    root = tk.Tk()
    root.title("Text Editor v0.4")

    # root toolbar
    toolbar = tk.Menu(root)

    # add menus to toolbar
    file_menu = tk.Menu(toolbar, tearoff=False)
    tools_menu = tk.Menu(toolbar, tearoff=False)
    editor_menu = tk.Menu(toolbar, tearoff=False)
    about_menu = tk.Menu(toolbar, tearoff=False)
    toolbar.add_cascade(label="File", menu= file_menu)
    toolbar.add_cascade(label="Tools", menu= tools_menu)
    toolbar.add_cascade(label="Editor", menu= editor_menu)
    toolbar.add_cascade(label="About", menu= about_menu)

    # text area frame
    textarea_frame = tk.Frame(root)

    # text area
    text_area = tk.Text(textarea_frame, wrap="none", state="normal")

	# vertical scroll bar
    v_scroll = tk.Scrollbar(textarea_frame, command=text_area.yview)

	# horizontal scroll bar
    h_scroll = tk.Scrollbar(textarea_frame, orient="horizontal", command=text_area.xview)

    # line count
    linecount_lbl = tk.Label(root, text="Lines: ")

    # status label
    status_label = tk.Label(root, text="Status: ")

    # config settings
    config = ""

    # theme highlighting, probably better ways
    perc = ip.Percolator(text_area)
    old_cdg = ""
    curr_cdg = ""

    # default don't show console
    console_toggle=False

    def __init__(self):

        # read config
        config_parser = configparser.ConfigParser()
        config_parser.optionxform = str
        config_parser.read("./config.ini")
        self.config = config_parser

        # apply window config
        width = self.config["settings"]["winx"]
        height = self.config["settings"]["winy"]
        posx = self.config["settings"]["posx"]
        posy = self.config["settings"]["posy"]
        self.root.geometry(f"{width}x{height}+{posx}+{posy}")

        # apply linter settings# text highlighting
        theme_parser = configparser.ConfigParser()
        theme_parser.optionxform = str
        theme = self.config['settings']['theme']
        theme_parser.read(f"./themes/{theme}.ini")

        self.curr_cdg = ic.ColorDelegator()
        self.curr_cdg.tagdefs["COMMENT"] = {"foreground": str(theme_parser[theme]["comment"]), "background" : str(theme_parser[theme]["comment_bg"])}
        self.curr_cdg.tagdefs["KEYWORD"] = {"foreground": str(theme_parser[theme]["keyword"]), "background" : str(theme_parser[theme]["keyword_bg"])}
        self.curr_cdg.tagdefs["BUILTIN"] = {"foreground": str(theme_parser[theme]["built_in"]), "background" : str(theme_parser[theme]["built_in_bg"])}
        self.curr_cdg.tagdefs["STRING"] = {"foreground": str(theme_parser[theme]["string"]), "background" : str(theme_parser[theme]["string_bg"])}
        self.curr_cdg.tagdefs["DEFINITION"] = {"foreground": str(theme_parser[theme]["definition"]), "background" : str(theme_parser[theme]["definition_bg"])}
		
        # apply theme
        self.root["bg"] = theme_parser[theme]["editor_bg"]
        self.text_area["bg"] = theme_parser[theme]["text_bg"]
        self.text_area["fg"] = theme_parser[theme]["text_color"]
        self.text_area["insertbackground"] = theme_parser[theme]["cursor_color"]
        self.linecount_lbl["bg"] = theme_parser[theme]["editor_bg"]
        self.status_label["bg"] = theme_parser[theme]["editor_bg"]

        self.perc.insertfilter(self.curr_cdg)

        self.root.update()

        # populate tool bar menus
        self.root.config(menu=self.toolbar)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Exit", command=self.exit)

        # set up scrollbars
        self.text_area.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        ################################
        # Packing
        ################################
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.textarea_frame.pack(padx=20, pady=20, expand=True,fill=tk.BOTH)
        self.linecount_lbl.pack(side=tk.BOTTOM, anchor="w")
        self.status_label.pack(side=tk.BOTTOM, anchor="w")

        # start application
        self.root.mainloop()

    def new_file(self):
        self.text_area.delete("1.0", tk.END)
    def open_file(self):
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
        self.root.title(f"Text Editor v0.3 - {f}")
    def save_file(self):
        filetypes = []
        for key in self.config["opentypes"]:
            filetypes.append((key, self.config["opentypes"][key]))
        initial_dir = "D:/Github"
        f = filedialog.asksaveasfile(defaultextension=".txt",filetypes=filetypes, mode="w")
        if f is None:
            return
        text_to_save = self.text_area.get(1.0,tk.END)
        text_to_save2 = text_to_save.replace("\t", "    ")
        f.write(text_to_save)
        f.close()
    def exit(self):
        self.root.quit()
    def update_line_count(self, event):
        num_lines = int(self.text_area.index('end-1c').split('.')[0])
        self.linecount_lbl["text"] = f"Lines: {num_lines}"
        self.linecount_lbl.update()

def main():
    te = TextEditor()

if __name__ == '__main__':
    main()