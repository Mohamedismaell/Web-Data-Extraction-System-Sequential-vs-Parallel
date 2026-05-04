import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from engines.sequential_engine import SequentialEngine
from engines.parallel_engine import ParallelEngine
import os

BG, SURF, ACCENT, TEXT, MUTED, SUCC, ERR, CYAN = "#282828", "#353535", "#FFFFFF", "#E8E8E8", "#B0B0B0", "#55FF55", "#FF5555", "#00DDDD"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Data Extractor Pipeline")
        self.root.geometry("1100x800") 
        self.root.configure(bg=BG)

        style = ttk.Style()
        style.theme_use('clam')
        for e, bg, fg in [('TFrame', BG, TEXT), ('Surface.TFrame', SURF, TEXT), 
                          ('TLabelframe', BG, ACCENT), ('TLabelframe.Label', BG, ACCENT)]:
            style.configure(e, background=bg, foreground=fg)
        style.configure('TLabel', background=BG, foreground=TEXT, font=("Segoe UI", 11))
        style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor=SURF)

        self.urls, self.stop_flag = [], False
        self.build_ui()

    def build_ui(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header Tools bar
        bar = tk.Frame(main, bg=SURF)
        bar.pack(fill="x", pady=5)
        
        tk.Button(bar, text="Upload URLs (.txt)", bg="#4CAF50", fg=TEXT, font=("Segoe UI", 10, "bold"), cursor="hand2", command=self.load_urls).pack(side="left", padx=10, pady=10)
        self.lbl_status = ttk.Label(bar, text="0 URLs Staged | Ready", font=("Segoe UI", 10, "italic"), foreground=MUTED)
        self.lbl_status.pack(side="left", padx=15)
        
        tk.Button(bar, text="Reset", bg=SURF, fg=TEXT, font=("Segoe UI", 10, "bold"), cursor="hand2", command=self.reset).pack(side="left")
        self.btn_run = tk.Button(bar, text="Start Extraction", bg=ACCENT, fg="black", font=("Segoe UI", 11, "bold"), cursor="hand2", command=self.run)
        self.btn_run.pack(side="right", padx=10)
        
        # Dual System Quadrants
        content = ttk.Frame(main)
        content.pack(fill="both", expand=True, pady=5)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        
        self.seq_f = self.make_panel(content, "Sequential Pipeline (Requests)", 0)
        self.par_f = self.make_panel(content, "Parallel Pipeline (aiohttp + asyncio)", 1)
        
        # Benchmark Footer
        sum_f = ttk.Labelframe(main, text="Data Performance")
        sum_f.pack(fill="x", pady=10)
        self.lbl_seq_bm = ttk.Label(sum_f, text="Sequential: -- | -- Req/s", font=("Segoe UI", 12))
        self.lbl_seq_bm.pack(side="left", padx=15, pady=10)
        self.lbl_par_bm = ttk.Label(sum_f, text="Parallel: -- | -- Req/s", font=("Segoe UI", 12))
        self.lbl_par_bm.pack(side="left", padx=15)
        self.lbl_diff = ttk.Label(sum_f, text="Speedup Multiplier: --", font=("Segoe UI", 12, "bold"), foreground=SUCC)
        self.lbl_diff.pack(side="left", padx=30)
        
    def make_panel(self, parent, title, col):
        f = ttk.Labelframe(parent, text=title)
        f.grid(row=0, column=col, sticky="nsew", padx=10)
        f.columnconfigure(0, weight=1); f.columnconfigure(1, weight=1)
        
        prog = ttk.Progressbar(f, orient="horizontal", mode="determinate")
        prog.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        lbl_c = ttk.Label(f, text="Ready", font=("Segoe UI", 9), foreground=CYAN)
        lbl_c.grid(row=1, column=0, columnspan=2)
        
        p = {"prog": prog, "c": lbl_c}
        p["time"] = self._box(f, "Total Execution Time", 2, 0, SUCC)
        
        sf = ttk.Labelframe(f, text="Success ✓ / Failed ✕")
        sf.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        hf = tk.Frame(sf, bg=BG)
        hf.pack(expand=True)
        p["S"], p["F"] = ttk.Label(hf, text="0", font=("Segoe UI", 20, "bold"), foreground=SUCC), ttk.Label(hf, text="0", font=("Segoe UI", 20, "bold"), foreground=ERR)
        p["S"].pack(side="left"); ttk.Label(hf, text=" / ", font=("Segoe UI", 20)).pack(side="left"); p["F"].pack(side="left")
        
        p["w"] = self._box(f, "Total Dataset Word Count", 3, 0, ACCENT)
        p["top"] = tk.Text(ttk.Labelframe(f, text="Top Dataset Keywords"), bg=SURF, fg=TEXT, height=7, borderwidth=0)
        p["top"].master.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)
        p["top"].pack(fill="both", expand=True, padx=5, pady=5)
        return p

    def _box(self, pr, txt, r, c, color):
        fr = ttk.Labelframe(pr, text=txt)
        fr.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
        lbl = ttk.Label(fr, text="0.0 sec" if "Time" in txt else "0", font=("Segoe UI", 20, "bold"), foreground=color)
        lbl.pack(expand=True, pady=10)
        return lbl

    def load_urls(self):
        if path := filedialog.askopenfilename(filetypes=[("Text", "*.txt")]):
            with open(path, "r") as f: self.urls = [r.strip() for r in f if r.strip().startswith("http")]
            self.lbl_status.config(text=f"{len(self.urls)} URLs Staged | File: {os.path.basename(path)}")
            
    def reset(self):
        self.urls, self.stop_flag = [], False
        self.lbl_status.config(text="0 URLs Staged | Ready", foreground=MUTED)
        self.load_res(self.seq_f, None); self.load_res(self.par_f, None)
        self.lbl_seq_bm.config(text="Sequential: -- | -- Req/s")
        self.lbl_par_bm.config(text="Parallel: -- | -- Req/s")
        self.lbl_diff.config(text="Speedup Multiplier: --")

    def load_res(self, p, res):
        p["time"].config(text=f"{res.time_taken}s" if res else "0.0 sec")
        p["S"].config(text=str(res.successful_urls) if res else "0")
        p["F"].config(text=str(res.failed_urls) if res else "0")
        p["w"].config(text=str(res.total_words) if res else "0")
        p["top"].delete("1.0", tk.END)
        if res: p["top"].insert(tk.END, "\n".join(f"{i+1}. {m}" for i, m in enumerate(res.top_global_words)))
        else: p["prog"]["value"] = 0; p["c"].config(text="Ready")

    def run(self):
        if not self.urls: return messagebox.showwarning("No Data", "Upload URLs first.")
        self.stop_flag, self.btn_run['state'] = False, tk.DISABLED
        self.load_res(self.seq_f, None); self.load_res(self.par_f, None)
        threading.Thread(target=self._proc, daemon=True).start()

    def _upd_prog(self, p, c, t, url, is_err=False):
        p["prog"]["maximum"], p["prog"]["value"] = t, c
        if url: p["c"].config(text=f"Process {c}/{t}: {url[:38]}...", foreground=ERR if is_err else CYAN)

    def _proc(self):
        post = lambda fn: self.root.after(0, fn)
        try:
            post(lambda: self.lbl_status.config(text="Operating Sequential Tracker..."))
            s_res = SequentialEngine.run(self.urls, lambda: self.stop_flag, lambda c, t, u="": post(lambda: self._upd_prog(self.seq_f, c, t, u)))
            post(lambda: [self.load_res(self.seq_f, s_res), self.seq_f["c"].config(text="Sequential Complete.", foreground=SUCC)])

            post(lambda: self.lbl_status.config(text="Operating Parallel Burst Engine..."))
            p_res = ParallelEngine.run(self.urls, lambda: self.stop_flag, lambda c, t, u="": post(lambda: self._upd_prog(self.par_f, c, t, u, "FAILED" in u.upper())))
            post(lambda: [self.load_res(self.par_f, p_res), self.par_f["c"].config(text="Parallel Complete.", foreground=SUCC)])

            if p_res.time_taken > 0:
                s_tps = round(len(self.urls)/s_res.time_taken, 2) if s_res.time_taken else 0
                p_tps = round(len(self.urls)/p_res.time_taken, 2)
                post(lambda: [
                    self.lbl_seq_bm.config(text=f"Sequential: {s_res.time_taken}s | {s_tps} Req/s"),
                    self.lbl_par_bm.config(text=f"Parallel: {p_res.time_taken}s | {p_tps} Req/s"),
                    self.lbl_diff.config(text=f"Speedup Multiplier: {round(s_res.time_taken/p_res.time_taken, 2)}x 🚀"),
                    self.lbl_status.config(text="Global Scrape Complete! ✓")
                ])
        except Exception as e:
            post(lambda: self.lbl_status.config(text=f"Error: {e}"))
        finally:
            post(lambda: self.btn_run.config(state=tk.NORMAL))
