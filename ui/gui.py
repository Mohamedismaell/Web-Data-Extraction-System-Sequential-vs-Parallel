import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from engines.sequential_engine import SequentialEngine
from engines.parallel_engine import ParallelEngine
import os

BACKGROUND = "#282828"
SURFACE = "#353535"
SURFACE_ALT = "#404040"
BORDER = "#4A4A4A"
ACCENT = "#FFFFFF"
ACCENT_HOVER = "#E0E0E0"
SECONDARY = "#3A3A3A"
SECONDARY_HOVER = "#4A4A4A"
TEXT = "#E8E8E8"
MUTED_TEXT = "#B0B0B0"
ACCENT_TEXT = "#000000"
SUCCESS = "#55FF55"
ERROR = "#FF5555"
CYAN = "#00DDDD"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Data Extractor Pipeline")
        self.root.geometry("1100x850") 
        self.root.configure(bg=BACKGROUND)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BACKGROUND)
        style.configure('Surface.TFrame', background=SURFACE)
        style.configure('TLabelframe', background=BACKGROUND, foreground=ACCENT, bordercolor=BORDER)
        style.configure('TLabelframe.Label', background=BACKGROUND, font=("Segoe UI", 11, "bold"), foreground=ACCENT)
        style.configure('TLabel', background=BACKGROUND, foreground=TEXT, font=("Segoe UI", 11))
        style.configure('Header.TLabel', font=("Segoe UI", 26, "bold"), foreground=TEXT, background=BACKGROUND)
        style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor=SURFACE_ALT, bordercolor=BACKGROUND)

        self.container = tk.Frame(self.root, bg=BACKGROUND)
        self.container.pack(fill="both", expand=True)

        self.urls = []
        self.is_running = False
        self.stop_flag = False
        
        self.create_main_screen()
        self.create_comparison_screen()
        self.show_main_screen()

    def create_main_screen(self):
        self.frame_main = tk.Frame(self.container, bg=BACKGROUND)
        lbl_title = ttk.Label(self.frame_main, text="Asynchronous Web Data Extractor", style="Header.TLabel")
        lbl_title.pack(pady=(200, 40))
        self.btn_start = tk.Button(self.frame_main, text="Initialize Architecture", bg=ACCENT, fg=ACCENT_TEXT, font=("Segoe UI", 16, "bold"), width=30, height=2, borderwidth=0, cursor="hand2", command=self.show_comp_screen)
        self.btn_start.pack()
        self.btn_start.bind("<Enter>", lambda e: self.btn_start.config(bg=ACCENT_HOVER))
        self.btn_start.bind("<Leave>", lambda e: self.btn_start.config(bg=ACCENT))
        
    def create_comparison_screen(self):
        self.frame_comp = tk.Frame(self.container, bg=BACKGROUND)
        
        top_bar = tk.Frame(self.frame_comp, bg=BACKGROUND)
        top_bar.pack(fill="x", pady=15, padx=15)
        
        btn_back = tk.Button(top_bar, text="← Return", bg=SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold"), borderwidth=0, cursor="hand2", command=self.show_main_screen)
        btn_back.pack(side="left")
        
        self.lbl_status = ttk.Label(top_bar, text="Status: Ready", font=("Segoe UI", 11, "italic"), foreground=MUTED_TEXT)
        self.lbl_status.pack(side="right")
        
        control_bar = tk.Frame(self.frame_comp, bg=SURFACE)
        control_bar.pack(fill="x", pady=10, padx=15)
        
        # Fixed the local function scope bug by moving the color logic to a simple variable
        btn_fg = "#FFFFFF" if BACKGROUND != "#FFFFFF" else "#000000"
        
        self.btn_upload = tk.Button(control_bar, text="Upload Your URLs (.txt)", bg="#4CAF50", fg=btn_fg, font=("Segoe UI", 10, "bold"), borderwidth=0, cursor="hand2", command=self.upload_custom_urls)
        self.btn_upload.pack(side="left", padx=10, pady=10)

        self.btn_test10 = tk.Button(control_bar, text="Wiki-10", bg=SECONDARY, fg=TEXT, borderwidth=0, font=("Segoe UI", 9, "bold"), cursor="hand2", command=lambda: self.load_preset("test_10.txt"))
        self.btn_test10.pack(side="left", padx=2)
        self.btn_test50 = tk.Button(control_bar, text="Wiki-50", bg=SECONDARY, fg=TEXT, borderwidth=0, font=("Segoe UI", 9, "bold"), cursor="hand2", command=lambda: self.load_preset("test_50.txt"))
        self.btn_test50.pack(side="left", padx=2)
        
        self.lbl_urls = ttk.Label(control_bar, text="0 URLs Staged")
        self.lbl_urls.pack(side="left", padx=15)
        
        self.btn_reset = tk.Button(control_bar, text="Reset", bg=SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold"), borderwidth=0, width=8, cursor="hand2", command=self.reset_all)
        self.btn_reset.pack(side="left", padx=5)

        self.btn_run = tk.Button(control_bar, text="Start Extraction", bg=ACCENT, fg=ACCENT_TEXT, font=("Segoe UI", 11, "bold"), borderwidth=0, width=15, cursor="hand2", command=self.run_comparisons)
        self.btn_run.pack(side="right", padx=10)
        
        content_frame = ttk.Frame(self.frame_comp)
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        frame_seq = ttk.Labelframe(content_frame, text="Sequential Pipeline (Requests)")
        frame_seq.grid(row=0, column=0, sticky="nsew", padx=10)
        frame_par = ttk.Labelframe(content_frame, text="Parallel Pipeline (aiohttp + asyncio)")
        frame_par.grid(row=0, column=1, sticky="nsew", padx=10)
        
        self.seq_fields = self.build_four_fields(frame_seq)
        self.par_fields = self.build_four_fields(frame_par)
        
        summary_frame = ttk.Labelframe(self.frame_comp, text="Data Performance Benchmark")
        summary_frame.pack(fill="x", padx=25, pady=20)
        
        self.lbl_speed_seq = ttk.Label(summary_frame, text="Sequential Time: --", font=("Segoe UI", 12))
        self.lbl_speed_seq.pack(side="left", padx=15, pady=10)
        self.lbl_speed_par = ttk.Label(summary_frame, text="Parallel Time: --", font=("Segoe UI", 12))
        self.lbl_speed_par.pack(side="left", padx=15, pady=10)
        self.lbl_diff = ttk.Label(summary_frame, text="Speedup Multiplier: --", font=("Segoe UI", 12, "bold"))
        self.lbl_diff.pack(side="left", padx=30, pady=10)
        
    def build_four_fields(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        fields = {}
        prog = ttk.Progressbar(parent, orient="horizontal", mode="determinate")
        prog.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        fields["prog"] = prog
        
        f1 = ttk.Labelframe(parent, text="Total Execution Time")
        f1.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        fields["time"] = ttk.Label(f1, text="0.0 sec", font=("Segoe UI", 20, "bold"), foreground=SUCCESS)
        fields["time"].pack(expand=True, pady=10)
        
        f2 = ttk.Labelframe(parent, text="Extraction Success / Failed")
        f2.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        fields["count"] = ttk.Label(f2, text="0 / 0", font=("Segoe UI", 20, "bold"), foreground=CYAN)
        fields["count"].pack(expand=True, pady=10)
        
        f3 = ttk.Labelframe(parent, text="Total Dataset Word Count")
        f3.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        fields["words"] = ttk.Label(f3, text="0", font=("Segoe UI", 20, "bold"), foreground=ACCENT)
        fields["words"].pack(expand=True, pady=10)
        
        f4 = ttk.Labelframe(parent, text="Top Global Keywords")
        f4.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        fields["common"] = tk.Text(f4, bg=SURFACE, fg=TEXT, borderwidth=0, font=("Consolas", 11), height=8)
        fields["common"].pack(fill="both", expand=True, padx=10, pady=10)
        return fields

    def upload_custom_urls(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as f:
                self.urls = [line.strip() for line in f if line.strip().startswith("http")]
            self.lbl_urls.config(text=f"{len(self.urls)} Custom URLs Staged")
            self.lbl_status.config(text=f"Status: Loaded custom list from {os.path.basename(file_path)}")

    def load_preset(self, filename):
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Could not find {filename}. Run generate_urls.py first.")
            return
        with open(filename, "r") as f:
            self.urls = [line.strip() for line in f if line.strip()]
        self.lbl_urls.config(text=f"{len(self.urls)} Wiki URLs Staged")

    def reset_all(self):
        self.urls = []
        self.lbl_urls.config(text="0 URLs Staged")
        self.lbl_status.config(text="Status: Ready", foreground=MUTED_TEXT)
        self.update_fields_blank(self.seq_fields)
        self.update_fields_blank(self.par_fields)
        self._set_progress(self.seq_fields["prog"], 0, 100)
        self._set_progress(self.par_fields["prog"], 0, 100)
        self.lbl_speed_seq.config(text="Sequential Time: --")
        self.lbl_speed_par.config(text="Parallel Time: --")
        self.lbl_diff.config(text="Speedup Multiplier: --")

    def run_comparisons(self):
        if not self.urls:
            messagebox.showwarning("No Data", "Please load or upload URLs first.")
            return
        self.is_running = True
        self.stop_flag = False
        self.lbl_status.config(text="Status: Operating Sequential Web Extraction...")
        self.btn_run.config(bg=SECONDARY, fg=MUTED_TEXT, state=tk.DISABLED)
        self.update_fields_blank(self.seq_fields)
        self.update_fields_blank(self.par_fields)
        self._set_progress(self.seq_fields["prog"], 0, len(self.urls))
        self._set_progress(self.par_fields["prog"], 0, len(self.urls))
        t = threading.Thread(target=self._process_data)
        t.daemon = True
        t.start()

    def show_main_screen(self):
        self.frame_comp.pack_forget()
        self.frame_main.pack(fill="both", expand=True)
    def show_comp_screen(self):
        self.frame_main.pack_forget()
        self.frame_comp.pack(fill="both", expand=True)
    def _set_progress(self, prog_widget, current, total):
        prog_widget["maximum"] = total
        prog_widget["value"] = current
    def update_fields_blank(self, field_dict):
        field_dict["time"].config(text="0.0 sec")
        field_dict["count"].config(text="0 / 0")
        field_dict["words"].config(text="0")
        field_dict["common"].delete("1.0", tk.END)
    def update_fields(self, field_dict, res):
        field_dict["time"].config(text=f"{res.time_taken} sec")
        field_dict["count"].config(text=f"{res.successful_urls} / {res.failed_urls}")
        field_dict["words"].config(text=str(res.total_words))
        field_dict["common"].delete("1.0", tk.END)
        for i, msg in enumerate(res.top_global_words):
            field_dict["common"].insert(tk.END, f"{i+1}. {msg}\n")

    def _process_data(self):
        def check_cancel(): return self.stop_flag
        def seq_progress(current, total): self.root.after(0, lambda: self._set_progress(self.seq_fields["prog"], current, total))
        def par_progress(current, total): self.root.after(0, lambda: self._set_progress(self.par_fields["prog"], current, total))
        try:
            seq_res = SequentialEngine.run(self.urls, check_cancel=check_cancel, progress_cb=seq_progress)
            self.root.after(0, lambda: self.update_fields(self.seq_fields, seq_res))
            self.root.after(0, lambda: self.lbl_status.config(text="Status: Operating Parallel Web Extraction..."))
            par_res = ParallelEngine.run(self.urls, check_cancel=check_cancel, progress_cb=par_progress)
            self.root.after(0, lambda: self.update_fields(self.par_fields, par_res))
            speedup = "N/A"
            if par_res.time_taken > 0: speedup = round(seq_res.time_taken / par_res.time_taken, 2)
            self.root.after(0, lambda: self.lbl_speed_seq.config(text=f"Sequential Time: {seq_res.time_taken} s"))
            self.root.after(0, lambda: self.lbl_speed_par.config(text=f"Parallel Time: {par_res.time_taken} s"))
            self.root.after(0, lambda: self.lbl_diff.config(text=f"Speedup Multiplier: {speedup}x 🚀", foreground=SUCCESS))
            self.root.after(0, lambda: self.lbl_status.config(text="Status: Global Scrape Complete!"))
            self.root.after(0, lambda: self.btn_run.config(bg=ACCENT, fg=ACCENT_TEXT, state=tk.NORMAL))
        except Exception as e:
            self.root.after(0, lambda: self.lbl_status.config(text=f"Error! {e}", foreground=ERROR))
            self.root.after(0, lambda: self.btn_run.config(bg=ACCENT, fg=ACCENT_TEXT, state=tk.NORMAL))
            print(f"Error during extraction thread -> {e}")
