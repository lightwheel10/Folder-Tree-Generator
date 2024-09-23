import os
import json
import threading
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# ------------------------------ Configuration ------------------------------ #

# Default Exclusions
DEFAULT_EXCLUSIONS = ['node_modules', '.git', '.next', 'dist', '__pycache__', '.venv']

# Tree Symbols
TREE_SYMBOLS = {
    'Classic': {'branch': '├── ', 'last': '└── ', 'indent': '│   '},
    'Simple': {'branch': '|-- ', 'last': '\\-- ', 'indent': '|   '},
    'ASCII': {'branch': '+-- ', 'last': '+-- ', 'indent': '    '},
}

# Settings File
SETTINGS_FILE = "settings.json"

# ------------------------------ Tree Generation ------------------------------ #

def generate_tree(folder_path, exclusions=None, include_hidden=False,
                 max_depth=None, show_metadata=False, symbols=None, visited=None):
    """
    Generates a tree-like string representation of the folder structure.

    Parameters:
        folder_path (str): The root folder path.
        exclusions (list): List of folder/file names to exclude.
        include_hidden (bool): Whether to include hidden files and folders.
        max_depth (int): Maximum depth to traverse.
        show_metadata (bool): Whether to show file size and modification date.
        symbols (dict): Symbols used for tree representation.
        visited (set): Set of visited paths to handle symlinks.

    Returns:
        str: The generated tree structure as a string.
    """
    if symbols is None:
        symbols = TREE_SYMBOLS['Classic']
    branch = symbols['branch']
    last = symbols['last']
    indent = symbols['indent']

    if exclusions is None:
        exclusions = []
    exclusions = set(exclusions)
    tree_lines = []
    prefix = ""

    if visited is None:
        visited = set()

    def walk_dir(current_path, prefix, current_depth):
        if max_depth is not None and current_depth > max_depth:
            tree_lines.append(prefix + last + "...")
            return
        try:
            items = sorted(os.listdir(current_path), key=lambda s: s.lower())
        except PermissionError:
            tree_lines.append(prefix + last + "[Permission Denied]")
            return
        except Exception as e:
            tree_lines.append(prefix + last + f"[Error: {e}]")
            return

        if not include_hidden:
            items = [item for item in items if not item.startswith('.')]
        else:
            # Optionally handle inclusion of hidden files
            pass

        items = [item for item in items if item not in exclusions]
        for index, item in enumerate(items):
            item_path = os.path.join(current_path, item)
            is_last = index == len(items) - 1

            connector = last if is_last else branch
            display_prefix = prefix + connector

            # Handle symlinks
            if os.path.islink(item_path):
                try:
                    target_path = os.readlink(item_path)
                    display_name = f"{item} -> {target_path}"
                except Exception:
                    display_name = f"{item} -> [Invalid Symlink]"
                tree_lines.append(display_prefix + display_name)
                continue  # Do not traverse into symlinked directories
            else:
                display_name = item

            # Append metadata if required
            if show_metadata and os.path.isfile(item_path):
                try:
                    size = os.path.getsize(item_path)
                    mtime = os.path.getmtime(item_path)
                    mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    display_name += f" [Size: {size} bytes, Modified: {mtime_str}]"
                except Exception:
                    pass

            tree_lines.append(display_prefix + display_name)

            # Traverse into directories
            if os.path.isdir(item_path):
                real_path = os.path.realpath(item_path)
                if real_path in visited:
                    tree_lines.append(prefix + indent + "[Circular Link]")
                    continue
                visited.add(real_path)
                extension = indent if not is_last else "    "
                walk_dir(item_path, prefix + extension, current_depth + 1)

    tree_lines.append(folder_path)
    walk_dir(folder_path, "", 1)
    return "\n".join(tree_lines)

def tree_to_json(tree_str):
    """
    Converts a tree string into a JSON-like dictionary structure.

    Parameters:
        tree_str (str): The tree structure as a string.

    Returns:
        dict: The tree structure as a nested dictionary.
    """
    lines = tree_str.split('\n')
    root = {"name": lines[0], "children": []}
    stack = [(root, 0)]
    for line in lines[1:]:
        stripped = line.lstrip(' │└├──+--\\')
        depth = (len(line) - len(stripped)) // 4
        node = {"name": stripped, "children": []}
        while stack and stack[-1][1] >= depth:
            stack.pop()
        if stack:
            stack[-1][0]["children"].append(node)
        stack.append((node, depth))
    return root

def tree_to_html(tree_str):
    """
    Converts a tree string into an HTML unordered list.

    Parameters:
        tree_str (str): The tree structure as a string.

    Returns:
        str: The tree structure as HTML.
    """
    lines = tree_str.split('\n')
    html = "<ul>\n"
    stack = [0]
    for line in lines:
        stripped = line.lstrip(' │└├──+--\\')
        depth = (len(line) - len(stripped)) // 4
        while depth < stack[-1]:
            html += "</ul></li>\n"
            stack.pop()
        if depth > stack[-1]:
            html += "<ul>\n"
            stack.append(depth)
        html += f"<li>{stripped}</li>\n"
    while len(stack) > 1:
        html += "</ul></li>\n"
        stack.pop()
    html += "</ul>"
    return html

# ------------------------------ GUI Components ------------------------------ #

class FolderTreeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Folder Tree Generator")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)

        # Initialize variables
        self.folder_path_var = tk.StringVar()
        self.exclusion_vars = {}
        self.search_var = tk.StringVar()

        # Setup GUI
        self.setup_gui()

    def setup_gui(self):
        # Create PanedWindow to divide the window into two panels
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # ----------------- Left Panel (Configuration) ----------------- #
        left_panel = ttk.Frame(paned_window, width=400, relief=tk.SUNKEN)
        paned_window.add(left_panel, weight=1)

        # Make the left panel scrollable
        canvas = tk.Canvas(left_panel, borderwidth=0)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
        self.config_frame = ttk.Frame(canvas)

        self.config_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.config_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ----------------- Right Panel (Preview and Output) ----------------- #
        right_panel = ttk.Frame(paned_window, relief=tk.SUNKEN)
        paned_window.add(right_panel, weight=3)

        # ----------------- Configuration Components in Left Panel ----------------- #

        # --- Folder Selection Frame ---
        selection_frame = ttk.LabelFrame(self.config_frame, text="Folder Selection")
        selection_frame.pack(pady=10, padx=10, fill='x')

        folder_label = ttk.Label(selection_frame, text="Selected Folder:")
        folder_label.pack(anchor='w', padx=5, pady=5)

        folder_entry = ttk.Entry(selection_frame, textvariable=self.folder_path_var, state='readonly')
        folder_entry.pack(fill='x', padx=5, pady=5)

        browse_button = ttk.Button(selection_frame, text="Browse", command=self.select_folder)
        browse_button.pack(pady=5)

        # --- Exclusions Frame ---
        exclusion_frame = ttk.LabelFrame(self.config_frame, text="Exclusions")
        exclusion_frame.pack(pady=10, padx=10, fill='x')

        # Default Exclusions Checkboxes
        for excl in DEFAULT_EXCLUSIONS:
            var = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(exclusion_frame, text=excl, variable=var, command=self.update_preview)
            chk.pack(anchor='w', padx=5, pady=2)
            self.exclusion_vars[excl] = var

        # Additional Exclusions Entry
        additional_excl_label = ttk.Label(exclusion_frame, text="Additional Exclusions (comma-separated):")
        additional_excl_label.pack(anchor='w', padx=5, pady=(10, 2))

        self.additional_excl_entry = ttk.Entry(exclusion_frame)
        self.additional_excl_entry.pack(fill='x', padx=5, pady=2)
        self.additional_excl_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        # --- Depth Configuration Frame ---
        depth_frame = ttk.LabelFrame(self.config_frame, text="Depth Configuration")
        depth_frame.pack(pady=10, padx=10, fill='x')

        depth_label = ttk.Label(depth_frame, text="Maximum Depth (Leave empty for no limit):")
        depth_label.pack(anchor='w', padx=5, pady=5)

        self.depth_spinbox = ttk.Spinbox(depth_frame, from_=1, to=50, width=5, command=self.update_preview)
        self.depth_spinbox.pack(anchor='w', padx=5, pady=5)
        self.depth_spinbox.bind("<KeyRelease>", lambda e: self.update_preview())

        # --- Metadata Options Frame ---
        metadata_frame = ttk.LabelFrame(self.config_frame, text="Metadata Options")
        metadata_frame.pack(pady=10, padx=10, fill='x')

        self.metadata_var = tk.BooleanVar()
        metadata_chk = ttk.Checkbutton(metadata_frame, text="Show File Size and Modification Date",
                                       variable=self.metadata_var, command=self.update_preview)
        metadata_chk.pack(anchor='w', padx=5, pady=5)

        # --- Tree Symbols Frame ---
        symbols_frame = ttk.LabelFrame(self.config_frame, text="Tree Symbols")
        symbols_frame.pack(pady=10, padx=10, fill='x')

        symbols_label = ttk.Label(symbols_frame, text="Select Tree Symbol Style:")
        symbols_label.pack(anchor='w', padx=5, pady=5)

        self.symbols_var = tk.StringVar(value='Classic')
        symbols_dropdown = ttk.Combobox(symbols_frame, textvariable=self.symbols_var,
                                        values=list(TREE_SYMBOLS.keys()), state='readonly')
        symbols_dropdown.pack(anchor='w', padx=5, pady=5)
        symbols_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # --- Save and Load Settings Frame ---
        settings_frame = ttk.Frame(self.config_frame)
        settings_frame.pack(pady=10, padx=10, fill='x')

        save_settings_btn = ttk.Button(settings_frame, text="Save Settings", command=self.save_settings)
        save_settings_btn.pack(side='left', padx=5, pady=5)

        load_settings_btn = ttk.Button(settings_frame, text="Load Settings", command=self.load_settings)
        load_settings_btn.pack(side='left', padx=5, pady=5)

        # --- Export Buttons Frame ---
        export_frame = ttk.LabelFrame(self.config_frame, text="Export Options")
        export_frame.pack(pady=10, padx=10, fill='x')

        export_txt_btn = ttk.Button(export_frame, text="Export as TXT", command=lambda: self.export_file('txt'))
        export_txt_btn.pack(fill='x', padx=5, pady=2)

        export_json_btn = ttk.Button(export_frame, text="Export as JSON", command=lambda: self.export_file('json'))
        export_json_btn.pack(fill='x', padx=5, pady=2)

        export_html_btn = ttk.Button(export_frame, text="Export as HTML", command=lambda: self.export_file('html'))
        export_html_btn.pack(fill='x', padx=5, pady=2)

        export_md_btn = ttk.Button(export_frame, text="Export as Markdown", command=lambda: self.export_file('md'))
        export_md_btn.pack(fill='x', padx=5, pady=2)

        # ----------------- Preview and Output Components in Right Panel ----------------- #

        # --- Preview Frame ---
        preview_frame = ttk.LabelFrame(right_panel, text="Folder Structure Preview")
        preview_frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap='none', state='disabled', font=("Courier", 10))
        self.preview_text.pack(fill='both', expand=True)

        # --- Search Frame ---
        search_frame = ttk.LabelFrame(right_panel, text="Search in Preview")
        search_frame.pack(pady=10, padx=10, fill='x')

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=5, pady=5, fill='x', expand=True)
        search_entry.bind("<Return>", lambda e: self.search_tree())

        search_button = ttk.Button(search_frame, text="Search", command=self.search_tree)
        search_button.pack(side='left', padx=5, pady=5)

        # --- Progress Bar ---
        self.progress_bar = ttk.Progressbar(right_panel, mode='indeterminate')

        # --- Tag Configuration for Search Highlighting ---
        self.preview_text.tag_config('highlight', background='yellow')

    # ----------------- Folder Selection and Tree Generation ----------------- #

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)
            self.update_preview()

    def update_preview(self):
        # Only proceed if a folder is selected
        folder_selected = self.folder_path_var.get()
        if not folder_selected:
            return

        try:
            # Gather exclusions
            exclusions = [excl for excl, var in self.exclusion_vars.items() if var.get()]
            additional_exclusions = self.additional_excl_entry.get().split(',')
            additional_exclusions = [excl.strip() for excl in additional_exclusions if excl.strip()]
            exclusions.extend(additional_exclusions)

            # Gather file type filters - Removed as per user request
            # include_exts = self.include_entry.get().split(',')
            # include_exts = [ext.strip() if ext.strip().startswith('.') else '.' + ext.strip()
            #                for ext in include_exts if ext.strip()]
            # exclude_exts = self.exclude_entry.get().split(',')
            # exclude_exts = [ext.strip() if ext.strip().startswith('.') else '.' + ext.strip()
            #                for ext in exclude_exts if ext.strip()]

            # Get max depth
            depth = self.depth_spinbox.get()
            max_depth = int(depth) if depth.isdigit() else None

            # Get metadata option
            show_metadata = self.metadata_var.get()

            # Get symbols
            symbols = self.symbols_var.get()
            symbols_set = TREE_SYMBOLS.get(symbols, TREE_SYMBOLS['Classic'])

            # Show progress bar
            self.progress_bar.pack(pady=10, padx=10, fill='x')
            self.progress_bar.start()

            # Clear previous preview
            self.preview_text.configure(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.configure(state='disabled')

            # Start thread for tree generation
            threading.Thread(target=self.generate_tree_thread,
                             args=(folder_selected, exclusions, False,  # include_hidden=False by default
                                   max_depth, show_metadata, symbols_set),
                             daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while preparing to generate the tree:\n{e}")

    def generate_tree_thread(self, folder_selected, exclusions, include_hidden,
                             max_depth, show_metadata, symbols_set):
        try:
            tree_str = generate_tree(folder_selected, exclusions=exclusions, include_hidden=include_hidden,
                                     max_depth=max_depth, show_metadata=show_metadata, symbols=symbols_set)
            self.preview_text.configure(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, tree_str)
            self.preview_text.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the tree:\n{e}")
        finally:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    # ----------------- Export Functionality ----------------- #

    def export_file(self, file_format):
        tree_content = self.preview_text.get(1.0, tk.END).strip()
        if not tree_content:
            messagebox.showwarning("No Content", "There is no tree structure to export. Please generate the tree first.")
            return

        filetypes = []
        default_ext = ".txt"
        if file_format == 'txt':
            filetypes = [("Text Files", "*.txt"), ("All Files", "*.*")]
            default_ext = ".txt"
        elif file_format == 'json':
            filetypes = [("JSON Files", "*.json"), ("All Files", "*.*")]
            default_ext = ".json"
        elif file_format == 'html':
            filetypes = [("HTML Files", "*.html"), ("All Files", "*.*")]
            default_ext = ".html"
        elif file_format == 'md':
            filetypes = [("Markdown Files", "*.md"), ("All Files", "*.*")]
            default_ext = ".md"

        save_path = filedialog.asksaveasfilename(defaultextension=default_ext,
                                                 filetypes=filetypes,
                                                 title=f"Export as {file_format.upper()}")

        if save_path:
            try:
                ext = os.path.splitext(save_path)[1].lower()
                if ext == '.json':
                    json_structure = tree_to_json(tree_content)
                    with open(save_path, 'w', encoding='utf-8') as file:
                        json.dump(json_structure, file, indent=4)
                elif ext == '.html':
                    html_content = tree_to_html(tree_content)
                    with open(save_path, 'w', encoding='utf-8') as file:
                        file.write(html_content)
                elif ext == '.md':
                    with open(save_path, 'w', encoding='utf-8') as file:
                        file.write("```\n" + tree_content + "\n```")
                else:
                    with open(save_path, 'w', encoding='utf-8') as file:
                        file.write(tree_content)
                messagebox.showinfo("Success", f"Tree structure exported successfully at:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while exporting the file:\n{e}")

    # ----------------- Search Functionality ----------------- #

    def search_tree(self):
        search_term = self.search_var.get().lower()
        self.preview_text.tag_remove('highlight', '1.0', tk.END)
        if search_term:
            start = '1.0'
            while True:
                pos = self.preview_text.search(search_term, start, nocase=1, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(search_term)}c"
                self.preview_text.tag_add('highlight', pos, end)
                start = end
            self.preview_text.tag_config('highlight', background='yellow')

    # ----------------- Save and Load Settings ----------------- #

    def save_settings(self):
        settings = {
            'exclusions': [excl for excl, var in self.exclusion_vars.items() if var.get()],
            'additional_exclusions': self.additional_excl_entry.get(),
            'max_depth': self.depth_spinbox.get(),
            'show_metadata': self.metadata_var.get(),
            'symbols': self.symbols_var.get(),
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            messagebox.showwarning("No Settings", "No saved settings found.")
            return
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            # Apply exclusions
            for excl in DEFAULT_EXCLUSIONS:
                self.exclusion_vars[excl].set(excl in settings.get('exclusions', []))
            self.additional_excl_entry.delete(0, tk.END)
            self.additional_excl_entry.insert(0, settings.get('additional_exclusions', ''))
            # Apply depth
            self.depth_spinbox.delete(0, tk.END)
            self.depth_spinbox.insert(0, settings.get('max_depth', ''))
            # Apply metadata
            self.metadata_var.set(settings.get('show_metadata', False))
            # Apply symbols
            self.symbols_var.set(settings.get('symbols', 'Classic'))
            messagebox.showinfo("Success", "Settings loaded successfully.")
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings:\n{e}")

# ------------------------------ Main Execution ------------------------------ #

def main():
    root = tk.Tk()
    app = FolderTreeGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
