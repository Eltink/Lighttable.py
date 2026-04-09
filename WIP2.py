import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class DirectorySorterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Directory Sorter")
        self.resizable(False, False)

        # Variables
        self.source_dir = tk.StringVar()
        self.combine_jpg = tk.BooleanVar(value=True)
        self.combine_xls = tk.BooleanVar(value=False)
        self.combine_html = tk.BooleanVar(value=False)
        self.keep_structure = tk.BooleanVar(value=True)
        self.custom_combine = tk.StringVar()

        # Build GUI
        self._build_widgets()

    def _build_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=0, sticky="ew")

        # Source Directory
        ttk.Label(frame, text="Source Directory:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.source_dir, width=40)
        entry.grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Browse...", command=self._browse_source).grid(row=0, column=2)

        # Combine Options
        grp = ttk.LabelFrame(frame, text="Combine file types")
        grp.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        ttk.Checkbutton(grp, text="jpg + JPG", variable=self.combine_jpg).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(grp, text="xls + xlsx", variable=self.combine_xls).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(grp, text="html + lrf + srt", variable=self.combine_html).grid(row=0, column=2, sticky="w", padx=5, pady=2)
        ttk.Label(grp, text="Custom groups (semicolon-separated, comma for exts):").grid(row=1, column=0, columnspan=3, sticky="w", padx=5)
        ttk.Entry(grp, textvariable=self.custom_combine, width=60).grid(row=2, column=0, columnspan=3, padx=5, pady=2)
        ttk.Label(grp, text="e.g. jpg,JPG; mp4,mkv; doc,docx,xlsx").grid(row=3, column=0, columnspan=3, sticky="w", padx=5)

        # Structure Option
        struct = ttk.LabelFrame(frame, text="Directory structure")
        struct.grid(row=2, column=0, columnspan=3, sticky="ew")
        ttk.Radiobutton(struct, text="Keep subdirectories", variable=self.keep_structure, value=True).grid(row=0, column=0, padx=5, pady=2)
        ttk.Radiobutton(struct, text="Flatten all files", variable=self.keep_structure, value=False).grid(row=0, column=1, padx=5, pady=2)

        # Progress Bars
        self.scan_pb = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
        self.scan_pb.grid(row=3, column=0, columnspan=3, pady=5)
        self.copy_pb = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
        self.copy_pb.grid(row=4, column=0, columnspan=3, pady=5)
        self.status_label = ttk.Label(frame, text="Ready")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=(0,10))

        # Start Button
        ttk.Button(frame, text="Start Sorting", command=self._start_sort).grid(row=6, column=0, columnspan=3)

    def _browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_dir.set(path)

    def _parse_custom_groups(self):
        # Returns dict mapping ext to group key
        groups = {}
        raw = self.custom_combine.get().strip()
        if raw:
            for grp in raw.split(';'):
                exts = [e.strip().lower() for e in grp.split(',') if e.strip()]
                if exts:
                    key = '_'.join(exts)
                    for ext in exts:
                        groups[ext] = key
        return groups

    def _start_sort(self):
        src = self.source_dir.get()
        if not src or not os.path.isdir(src):
            messagebox.showerror("Error", "Please select a valid source directory.")
            return
        # Disable UI
        for child in self.winfo_children():
            child.configure(state="disabled")
        threading.Thread(target=self._run_sort, daemon=True).start()

    def _run_sort(self):
        src = self.source_dir.get()
        parent, name = os.path.split(src.rstrip(os.sep))
        dest = os.path.join(parent, name + '_sorted')
        os.makedirs(dest, exist_ok=True)

        # Gather files
        all_files = []
        for root, dirs, files in os.walk(src):
            for f in files:
                all_files.append(os.path.join(root, f))
        total_files = len(all_files)
        self.scan_pb['maximum'] = total_files

        # Build mapping by extension
        mapping = {}
        scan_count = 0
        custom_map = self._parse_custom_groups()
        for fpath in all_files:
            ext = os.path.splitext(fpath)[1].lstrip('.')
            low = ext.lower()
            # Determine group key
            if low in custom_map:
                ext_key = custom_map[low]
            elif not ext:
                ext_key = 'no_ext'
            elif self.combine_jpg.get() and low == 'jpg':
                ext_key = 'jpg'
            elif self.combine_xls.get() and low in ('xls','xlsx'):
                ext_key = 'xls'
            elif self.combine_html.get() and low in ('html','lrf','srt'):
                ext_key = 'html_lrf_srt'
            else:
                ext_key = ext
            mapping.setdefault(ext_key, []).append(fpath)
            scan_count += 1
            self.scan_pb['value'] = scan_count
            self.status_label.config(text=f"Scanning: {scan_count}/{total_files}")
            self.update_idletasks()

        # Copy files
        copy_count = 0
        self.copy_pb['maximum'] = total_files
        for ext_key, flist in mapping.items():
            folder = os.path.join(dest, ext_key)
            os.makedirs(folder, exist_ok=True)
            for fpath in flist:
                rel = os.path.relpath(fpath, src)
                if self.keep_structure.get():
                    target = os.path.join(folder, rel)
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                else:
                    target = os.path.join(folder, os.path.basename(fpath))
                try:
                    shutil.copy2(fpath, target)
                except Exception as e:
                    print(f"Error copying {fpath}: {e}")
                copy_count += 1
                self.copy_pb['value'] = copy_count
                self.status_label.config(text=f"Copying: {copy_count}/{total_files}")
                self.update_idletasks()

        self.status_label.config(text="Completed!")
        messagebox.showinfo("Done", f"Sorted {total_files} files into '{dest}'")
        self.destroy()

if __name__ == '__main__':
    app = DirectorySorterApp()
    app.mainloop()
