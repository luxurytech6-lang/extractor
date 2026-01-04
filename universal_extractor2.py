import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
import concurrent.futures
import re
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
from validate_email import validate_email
import os
import time
from urllib.parse import urljoin, quote

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
]

PERSONAL_PROVIDERS = {
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com',
    'protonmail.com', 'aol.com', 'gmx.com', 'zoho.com', 'ymail.com',
    'live.com', 'msn.com', 'me.com', 'mac.com'
}

US_MOBILE_AREA_CODES = set([
    '201','202','203','205','206','207','208','209','210','212','213','214','215','216','217','218','219',
    '220','223','224','225','227','228','229','231','234','239','240','248','251','252','253','254','256',
    '260','262','267','269','270','272','274','276','279','281','283','301','302','303','304','305','307',
    '308','309','310','312','313','314','315','316','317','318','319','320','321','323','325','327','330',
    '331','332','334','336','337','339','346','347','351','352','360','361','364','380','385','386','401',
    '402','404','405','406','407','408','409','410','412','413','414','415','417','419','423','424','425',
    '430','432','434','435','440','442','443','445','447','448','458','463','469','470','475','478','479',
    '480','484','501','502','503','504','505','507','508','509','510','512','513','515','516','517','518',
    '520','530','531','534','539','540','541','551','559','561','562','563','564','567','570','571','573',
    '574','575','580','582','585','586','601','602','603','605','606','607','608','609','610','612','614',
    '615','616','617','618','619','620','623','626','628','629','630','631','636','640','641','646','650',
    '651','657','660','661','662','667','669','678','680','681','682','684','701','702','703','704','706',
    '707','708','710','712','713','714','715','716','717','718','719','720','724','725','727','730','731',
    '732','734','737','740','743','747','754','757','760','762','763','765','769','770','772','773','774',
    '775','779','781','785','786','802','803','804','805','806','808','810','812','813','814','815','816',
    '817','818','820','828','830','831','832','843','845','847','848','850','854','856','857','858','859',
    '860','862','863','864','865','870','872','878','901','903','904','906','908','909','910','912','913',
    '914','915','916','917','918','919','920','925','928','929','930','931','934','936','937','938','940',
    '941','947','949','951','952','954','956','959','970','971','972','973','975','978','979','980','984',
    '985','986','989'
])

PHONE_REGEX = re.compile(r'(\+?1[-.\s]?\(?(\d{3})\)?[-.\s]?\d{3}[-.\s]?\d{4})')

AREA_CODE_CARRIER = {
    '201': 'Verizon', '202': 'Verizon', '203': 'Verizon', '207': 'Verizon', '212': 'Verizon',
    '215': 'Verizon', '267': 'Verizon', '302': 'Verizon', '401': 'Verizon', '551': 'Verizon',
    '609': 'Verizon', '732': 'Verizon', '856': 'Verizon', '908': 'Verizon', '973': 'Verizon',
    '210': 'AT&T', '214': 'AT&T', '254': 'AT&T', '281': 'AT&T', '325': 'AT&T', '346': 'AT&T',
    '361': 'AT&T', '409': 'AT&T', '430': 'AT&T', '469': 'AT&T', '512': 'AT&T', '682': 'AT&T',
    '713': 'AT&T', '726': 'AT&T', '737': 'AT&T', '817': 'AT&T', '832': 'AT&T', '903': 'AT&T',
    '940': 'AT&T', '945': 'AT&T', '956': 'AT&T', '972': 'AT&T', '979': 'AT&T',
    '206': 'T-Mobile', '253': 'T-Mobile', '360': 'T-Mobile', '425': 'T-Mobile', '509': 'T-Mobile',
    '564': 'T-Mobile', '310': 'T-Mobile', '323': 'T-Mobile', '424': 'T-Mobile',
    '626': 'T-Mobile', '657': 'T-Mobile', '661': 'T-Mobile', '805': 'T-Mobile', '818': 'T-Mobile',
}

def get_carrier(area_code):
    return AREA_CODE_CARRIER.get(area_code, "Unknown / Other Carrier")

OBFUSCATED_EMAIL_REGEX = re.compile(
    r'[a-zA-Z0-9._%+-]+'
    r'(?:\s*(?:\[at\]|\[?at\]?|@|&#x40;|\(at\)|at|\{\s*at\s*\}))'
    r'\s*[a-zA-Z0-9.-]+'
    r'(?:\s*(?:\[dot\]|\.?|dot))\s*'
    r'[a-zA-Z]{2,}',
    re.IGNORECASE
)

def normalize_obfuscated_email(text):
    email = re.sub(r'\s*(?:\[at\]|\[?at\]?|&#x40;|\(at\)|at|\{\s*at\s*\})', '@', text, flags=re.IGNORECASE)
    email = re.sub(r'\s*(?:\[dot\]|dot)', '.', email, flags=re.IGNORECASE)
    email = re.sub(r'\s+', '', email)
    return email.lower()

class UniversalExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Universal Extractor & Validator Suite 2025")
        self.geometry("1000x750")
        self.minsize(800, 550)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.running = False
        self.stop_event = threading.Event()
        self.executor = None
        self.page_cache = {}
        self.cache_lock = threading.Lock()
        self.create_welcome_screen()

    def create_welcome_screen(self):
        self.clear_frame()
        title = ctk.CTkLabel(self.main_frame, text="Universal Extractor & Validator Suite",
                             font=ctk.CTkFont(size=30, weight="bold"))
        title.grid(row=0, column=0, pady=(40, 20))
        subtitle = ctk.CTkLabel(self.main_frame, text="Select a tool to begin", font=ctk.CTkFont(size=16))
        subtitle.grid(row=1, column=0, pady=(0, 30))
        options = [
            ("Email Only Extractor", self.email_only_setup),
            ("USA Mobile Phone Extractor", self.phone_setup),
            ("Email Pattern Generator", self.email_pattern_setup),
            ("Email Verification", self.email_verify_setup),
            ("USA Phone Verification (with Carrier)", self.phone_verify_setup),
        ]
        for i, (text, command) in enumerate(options):
            btn = ctk.CTkButton(self.main_frame, text=text, width=500, height=50,
                                font=ctk.CTkFont(size=14), command=command)
            btn.grid(row=i+2, column=0, pady=10)
        exit_btn = ctk.CTkButton(self.main_frame, text="Exit Application", width=200, height=40,
                                 fg_color="dark red", hover_color="red", command=self.destroy)
        exit_btn.grid(row=len(options)+3, column=0, pady=30)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def start_thread(self, func):
        if self.running:
            return
        self.running = True
        self.stop_event.clear()
        thread = threading.Thread(target=func, daemon=True)
        thread.start()

    def stop_extraction(self):
        self.stop_event.set()
        self.running = False
        if self.executor:
            self.executor.shutdown(wait=False, cancel_futures=True)
            self.executor = None
        self.update_buttons_after_stop()

    def update_buttons_after_stop(self):
        if hasattr(self, 'email_start_btn'):
            self.email_start_btn.configure(state="normal")
            self.email_stop_btn.configure(state="disabled")
            self.email_status.configure(text="Extraction stopped by user")
        if hasattr(self, 'phone_start_btn'):
            self.phone_start_btn.configure(state="normal")
            self.phone_stop_btn.configure(state="disabled")
            self.phone_status.configure(text="Extraction stopped by user")

    def email_only_setup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Email Only Extractor", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="Search Keyword:").grid(row=1, column=0, sticky="w", padx=30, pady=8)
        self.email_keyword = ctk.CTkEntry(self.main_frame, width=450)
        self.email_keyword.grid(row=1, column=1, pady=8, sticky="w")
        self.email_keyword.insert(0, "any keyword here")
        ctk.CTkLabel(self.main_frame, text="Email Type:").grid(row=2, column=0, sticky="w", padx=30, pady=8)
        self.email_type = ctk.StringVar(value="all")
        ctk.CTkRadioButton(self.main_frame, text="All Emails", variable=self.email_type, value="all").grid(row=2, column=1, sticky="w")
        ctk.CTkRadioButton(self.main_frame, text="Company Only", variable=self.email_type, value="company").grid(row=3, column=1, sticky="w")
        ctk.CTkRadioButton(self.main_frame, text="Personal Only", variable=self.email_type, value="personal").grid(row=4, column=1, sticky="w")
        ctk.CTkLabel(self.main_frame, text="Max Valid Emails (max 1000):").grid(row=5, column=0, sticky="w", padx=30, pady=15)
        self.email_count = ctk.CTkEntry(self.main_frame, width=150)
        self.email_count.grid(row=5, column=1, sticky="w")
        self.email_count.insert(0, "200")
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        self.email_start_btn = ctk.CTkButton(button_frame, text="Start Extraction", width=200, height=40,
                                             font=ctk.CTkFont(size=14),
                                             command=lambda: self.start_thread(self.extract_emails_only))
        self.email_start_btn.grid(row=0, column=0, padx=10)
        self.email_stop_btn = ctk.CTkButton(button_frame, text="Stop Extraction", width=200, height=40,
                                            fg_color="dark red", hover_color="red",
                                            command=self.stop_extraction, state="disabled")
        self.email_stop_btn.grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.main_frame, text="← Back to Menu", command=self.create_welcome_screen, width=150).grid(row=7, column=0, columnspan=2, pady=10)
        ctk.CTkButton(self.main_frame, text="Exit App", fg_color="dark red", hover_color="red", command=self.destroy, width=120).grid(row=8, column=0, columnspan=2, pady=10)
        results_label = ctk.CTkLabel(self.main_frame, text="Live Results:", font=ctk.CTkFont(size=16, weight="bold"))
        results_label.grid(row=9, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=30)
        self.email_results_text = scrolledtext.ScrolledText(self.main_frame, height=10, font=("Consolas", 10))
        self.email_results_text.grid(row=10, column=0, columnspan=2, padx=30, pady=5, sticky="nsew")
        self.main_frame.grid_rowconfigure(10, weight=1)
        self.email_progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate", length=600)
        self.email_progress.grid(row=11, column=0, columnspan=2, pady=15, padx=30)
        self.email_status = ctk.CTkLabel(self.main_frame, text="Ready")
        self.email_status.grid(row=12, column=0, columnspan=2)

    def extract_emails_only(self):
        keyword = self.email_keyword.get().strip()
        if not keyword:
            messagebox.showerror("Error", "Search keyword is required")
            self.running = False
            return
        try:
            target = int(self.email_count.get())
            if not 1 <= target <= 1000:
                raise ValueError
        except:
            messagebox.showerror("Error", "Enter a number between 1 and 1000")
            self.running = False
            return
        etype = self.email_type.get()
        self.email_start_btn.configure(state="disabled")
        self.email_stop_btn.configure(state="normal")
        self.email_status.configure(text="Searching multiple engines...")
        self.email_results_text.delete(1.0, tk.END)
        self.email_progress["value"] = 0
        self.update_idletasks()

        platform_variations = [
            f"{keyword} site:reddit.com",
            f"{keyword} site:quora.com",
            f"{keyword} site:answers.yahoo.com",
            f"{keyword} site:trustpilot.com",
            f"{keyword} site:bbb.org",
            f"{keyword} site:complaintsboard.com",
            f"{keyword} site:ripoffreport.com",
            f"{keyword} site:pissedconsumer.com",
            f"{keyword} site:sitejabber.com",
            f"{keyword} site:yelp.com",
            f"{keyword} site:glassdoor.com",
            f"{keyword} site:facebook.com",
            f"{keyword} site:nextdoor.com",
            f"{keyword} site:angi.com",
            f"{keyword} site:producthunt.com",
            f"{keyword} site:news.ycombinator.com",
            f"{keyword} site:indiehackers.com",
            f"{keyword} site:linkedin.com",
            f"{keyword} \"contact email\" OR \"reach me at\" OR \"my email is\"",
            f"{keyword} \"customer service\" OR \"support email\"",
        ]

        personal_extra = [
            f"{keyword} site:pastebin.com",
            f"{keyword} site:github.io OR site:gitlab.io",
            f"{keyword} site:about.me OR site:linktr.ee OR site:carrd.co",
            f'"{keyword}" "gmail.com" OR "yahoo.com" OR "hotmail.com" OR "outlook.com" OR "protonmail.com"',
            f'"{keyword}" ("my email" OR "email me at" OR "contact me at" OR "write to me")',
            f"{keyword} intext:@gmail.com OR intext:@yahoo.com OR intext:@outlook.com",
            f"{keyword} filetype:csv OR filetype:xlsx OR filetype:txt \"email\"",
            f"{keyword} site:stackoverflow.com",
            f"{keyword} site:medium.com",
            f"{keyword} site:dev.to",
            f"{keyword} site:tumblr.com",
            f"{keyword} site:blogger.com",
            f"{keyword} site:wordpress.com",
            f"{keyword} inurl:contact OR inurl:about OR inurl:profile",
        ]

        company_extra = [
            f'"{keyword}" ("contact@" OR "info@" OR "support@" OR "sales@" OR "hello@" OR "admin@")',
            f"{keyword} inurl:contact OR inurl:about OR inurl:team OR inurl:staff",
            f"{keyword} site:crunchbase.com OR site:angel.co OR site:linkedin.com/company",
        ]

        if etype == "personal":
            platform_variations.extend(personal_extra)
        elif etype == "company":
            platform_variations.extend(company_extra)
        else:
            platform_variations.extend(personal_extra + company_extra)

        urls = self.multi_engine_search(keyword, extra_variations=platform_variations)
        if not urls:
            self.email_status.configure(text="No search results found.")
            self.email_start_btn.configure(state="normal")
            self.email_stop_btn.configure(state="disabled")
            self.running = False
            return

        self.email_progress["maximum"] = len(urls)
        self.email_progress["value"] = 0

        emails = set()
        valid_emails = []
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=30)

        def fetch_and_extract(url, depth=0):
            if depth > 3 or self.stop_event.is_set():
                return set()

            with self.cache_lock:
                if url in self.page_cache:
                    html = self.page_cache[url]
                else:
                    html = self.fetch_page(url)
                    if html:
                        self.page_cache[url] = html
            if not html:
                return set()

            local_emails = set()

            for match in OBFUSCATED_EMAIL_REGEX.finditer(html):
                raw = match.group(0)
                email = normalize_obfuscated_email(raw)
                if validate_email(email, verify=False):
                    local_emails.add(email)

            standard = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
            for e in standard:
                e_lower = e.lower()
                if any(bad in e_lower for bad in ["example@", "sample@", "test@", "demo@", "placeholder@", "noreply@", "no-reply@", "do-not-reply@"]):
                    continue
                domain = e_lower.split('@')[-1]
                if etype == "company" and domain in PERSONAL_PROVIDERS:
                    continue
                if etype == "personal" and domain not in PERSONAL_PROVIDERS:
                    continue
                local_emails.add(e_lower)

            if depth < 3:
                soup = BeautifulSoup(html, 'html.parser')
                links = soup.find_all('a', href=True)
                raw_links = [l['href'] for l in links]
                full_links = [urljoin(url, l) for l in raw_links]
                full_links = [l for l in full_links if l.startswith('http') and 'logout' not in l.lower()]

                priority_keywords = ['contact', 'about', 'team', 'profile', 'bio', 'member', 'forum', 'thread', 'user', 'directory']
                priority = [l for l in full_links if any(k in l.lower() for k in priority_keywords)]
                others = [l for l in full_links if l not in priority]
                selected = priority + random.sample(others, min(30, len(others)))

                for link in selected[:40]:
                    if self.stop_event.is_set():
                        return local_emails
                    time.sleep(random.uniform(0.3, 0.9))
                    local_emails.update(fetch_and_extract(link, depth + 1))

            return local_emails

        future_to_url = {self.executor.submit(fetch_and_extract, url): url for url in urls}
        processed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            if self.stop_event.is_set():
                break
            processed += 1
            self.email_progress["value"] = processed
            self.update_idletasks()

            try:
                new_emails = future.result()
                for e in new_emails:
                    if e not in emails:
                        emails.add(e)
                        self.email_results_text.insert(tk.END, f"{e}\n")
                        self.email_results_text.see(tk.END)
                        self.update_idletasks()
            except Exception:
                pass

            if len(emails) >= target * 3:
                break

        self.executor.shutdown(wait=False, cancel_futures=True)
        self.executor = None

        self.email_status.configure(text="Validating syntax...")
        self.update_idletasks()

        for email in list(emails):
            if self.stop_event.is_set():
                break
            if validate_email(email, verify=False):
                valid_emails.append(email)
                self.email_results_text.insert(tk.END, f"[VALID] {email}\n")
                self.email_results_text.see(tk.END)
                self.update_idletasks()
                if len(valid_emails) >= target:
                    break

        final_emails = valid_emails[:target]

        if final_emails:
            save_path = filedialog.asksaveasfilename(
                title="Save Extracted Emails",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="extracted_emails"
            )
            if save_path:
                df = pd.DataFrame({"email": final_emails})
                if save_path.endswith(".csv"):
                    csv_path = save_path
                    txt_path = save_path.replace(".csv", ".txt")
                else:
                    csv_path = save_path.rsplit(".", 1)[0] + ".csv"
                    txt_path = save_path
                df.to_csv(csv_path, index=False)
                with open(txt_path, "w") as f:
                    for e in final_emails:
                        f.write(e + "\n")
                messagebox.showinfo("Success", f"Extracted {len(final_emails)} valid emails!\nSaved to:\n{csv_path}\n{txt_path}")
            else:
                messagebox.showinfo("Cancelled", "Save cancelled.")
        else:
            messagebox.showinfo("Complete", "No valid emails found.")

        self.email_status.configure(text="Complete")
        self.email_start_btn.configure(state="normal")
        self.email_stop_btn.configure(state="disabled")
        self.running = False

    def phone_setup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="USA Mobile Phone Extractor", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="Search Keyword:").grid(row=1, column=0, sticky="w", padx=30, pady=8)
        self.phone_keyword = ctk.CTkEntry(self.main_frame, width=450)
        self.phone_keyword.grid(row=1, column=1, pady=8, sticky="w")
        self.phone_keyword.insert(0, "contact phone customer service support")
        ctk.CTkLabel(self.main_frame, text="Max Numbers (max 1000):").grid(row=2, column=0, sticky="w", padx=30, pady=15)
        self.phone_count = ctk.CTkEntry(self.main_frame, width=150)
        self.phone_count.grid(row=2, column=1, sticky="w")
        self.phone_count.insert(0, "100")
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        self.phone_start_btn = ctk.CTkButton(button_frame, text="Start Extraction", width=200, height=40,
                                             font=ctk.CTkFont(size=14),
                                             command=lambda: self.start_thread(self.extract_usa_phones))
        self.phone_start_btn.grid(row=0, column=0, padx=10)
        self.phone_stop_btn = ctk.CTkButton(button_frame, text="Stop Extraction", width=200, height=40,
                                            fg_color="dark red", hover_color="red",
                                            command=self.stop_extraction, state="disabled")
        self.phone_stop_btn.grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.main_frame, text="← Back to Menu", command=self.create_welcome_screen, width=150).grid(row=4, column=0, columnspan=2, pady=10)
        ctk.CTkButton(self.main_frame, text="Exit App", fg_color="dark red", hover_color="red", command=self.destroy, width=120).grid(row=5, column=0, columnspan=2, pady=10)
        results_label = ctk.CTkLabel(self.main_frame, text="Live Results:", font=ctk.CTkFont(size=16, weight="bold"))
        results_label.grid(row=6, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=30)
        self.phone_results_text = scrolledtext.ScrolledText(self.main_frame, height=10, font=("Consolas", 10))
        self.phone_results_text.grid(row=7, column=0, columnspan=2, padx=30, pady=5, sticky="nsew")
        self.main_frame.grid_rowconfigure(7, weight=1)
        self.phone_progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate", length=600)
        self.phone_progress.grid(row=8, column=0, columnspan=2, pady=15, padx=30)
        self.phone_status = ctk.CTkLabel(self.main_frame, text="Ready")
        self.phone_status.grid(row=9, column=0, columnspan=2)

    def extract_usa_phones(self):
        keyword = self.phone_keyword.get().strip()
        if not keyword:
            messagebox.showerror("Error", "Search keyword is required")
            self.running = False
            return
        try:
            target = int(self.phone_count.get())
            if not 1 <= target <= 1000:
                raise ValueError
        except:
            messagebox.showerror("Error", "Enter a number between 1 and 1000")
            self.running = False
            return

        self.phone_start_btn.configure(state="disabled")
        self.phone_stop_btn.configure(state="normal")
        self.phone_status.configure(text="Searching web...")
        self.phone_results_text.delete(1.0, tk.END)
        self.update_idletasks()

        phone_variations = [
            keyword,
            f'"{keyword}"',
            f"{keyword} \"phone number\" OR \"contact number\" OR \"call me at\"",
            f"{keyword} site:facebook.com",
            f"{keyword} site:twitter.com",
            f"{keyword} site:linkedin.com",
            f"{keyword} filetype:pdf \"phone\"",
            f"{keyword} inurl:contact OR inurl:support",
        ]

        urls = self.multi_engine_search(keyword, extra_variations=phone_variations)
        if not urls:
            self.phone_status.configure(text="No results found.")
            self.phone_start_btn.configure(state="normal")
            self.phone_stop_btn.configure(state="disabled")
            self.running = False
            return

        results = []
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=30)

        def fetch_and_extract(url):
            html = self.fetch_page(url)
            if html:
                matches = PHONE_REGEX.findall(html)
                local_phones = []
                for match in matches:
                    full = match[0]
                    cleaned = re.sub(r'\D', '', full)
                    if cleaned.startswith('1'):
                        cleaned = cleaned[1:]
                    if len(cleaned) == 10 and cleaned[:3] in US_MOBILE_AREA_CODES:
                        carrier = get_carrier(cleaned[:3])
                        formatted = f"+1 {cleaned[:3]} {cleaned[3:6]} {cleaned[6:]}"
                        local_phones.append((formatted, carrier))
                return local_phones
            return []

        future_to_url = {self.executor.submit(fetch_and_extract, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            if self.stop_event.is_set():
                break
            try:
                local_phones = future.result()
                for formatted, carrier in local_phones:
                    if formatted not in [r['phone'] for r in results]:
                        results.append({"phone": formatted, "carrier": carrier})
                        self.phone_results_text.insert(tk.END, f"{formatted} | Carrier: {carrier}\n")
                        self.phone_results_text.see(tk.END)
                        self.update_idletasks()
                        if len(results) >= target:
                            self.executor.shutdown(wait=False, cancel_futures=True)
                            self.executor = None
                            break
            except:
                pass

        self.executor = None
        final_results = results[:target]

        if final_results:
            save_path = filedialog.asksaveasfilename(
                title="Save USA Mobile Phones with Carriers",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="usa_mobile_phones_with_carrier"
            )
            if save_path:
                df = pd.DataFrame(final_results)
                if save_path.endswith(".csv"):
                    csv_path = save_path
                    txt_path = save_path.replace(".csv", ".txt")
                else:
                    csv_path = save_path.rsplit(".", 1)[0] + ".csv"
                    txt_path = save_path
                df.to_csv(csv_path, index=False)
                with open(txt_path, "w") as f:
                    for _, row in df.iterrows():
                        f.write(f"{row['phone']} | Carrier: {row['carrier']}\n")
                messagebox.showinfo("Complete", f"Extracted {len(final_results)} phone numbers!\nSaved to:\n{csv_path}\n{txt_path}")
            else:
                messagebox.showinfo("Cancelled", "Save cancelled.")
        else:
            messagebox.showinfo("Complete", "No valid phone numbers found.")

        self.phone_status.configure(text="Complete")
        self.phone_start_btn.configure(state="normal")
        self.phone_stop_btn.configure(state="disabled")
        self.running = False

    def email_pattern_setup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Email Pattern Generator", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="First Name:").grid(row=1, column=0, sticky="w", padx=30, pady=8)
        self.pattern_first = ctk.CTkEntry(self.main_frame, width=300)
        self.pattern_first.grid(row=1, column=1, pady=8, sticky="w")
        ctk.CTkLabel(self.main_frame, text="Last Name:").grid(row=2, column=0, sticky="w", padx=30, pady=8)
        self.pattern_last = ctk.CTkEntry(self.main_frame, width=300)
        self.pattern_last.grid(row=2, column=1, pady=8, sticky="w")
        ctk.CTkLabel(self.main_frame, text="Company Domain:").grid(row=3, column=0, sticky="w", padx=30, pady=8)
        self.pattern_domain = ctk.CTkEntry(self.main_frame, width=300)
        self.pattern_domain.grid(row=3, column=1, pady=8, sticky="w")
        self.pattern_domain.insert(0, "company.com")
        ctk.CTkButton(self.main_frame, text="Generate Patterns", command=self.generate_email_patterns, width=200, height=40).grid(row=4, column=0, columnspan=2, pady=20)
        ctk.CTkButton(self.main_frame, text="← Back to Menu", command=self.create_welcome_screen, width=150).grid(row=5, column=0, columnspan=2, pady=10)
        results_label = ctk.CTkLabel(self.main_frame, text="Generated Emails:", font=ctk.CTkFont(size=16, weight="bold"))
        results_label.grid(row=6, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=30)
        self.pattern_results_text = scrolledtext.ScrolledText(self.main_frame, height=10, font=("Consolas", 10))
        self.pattern_results_text.grid(row=7, column=0, columnspan=2, padx=30, pady=5, sticky="nsew")
        self.main_frame.grid_rowconfigure(7, weight=1)

    def generate_email_patterns(self):
        first = self.pattern_first.get().strip().lower()
        last = self.pattern_last.get().strip().lower()
        domain = self.pattern_domain.get().strip().lower()
        if not first or not last or not domain:
            messagebox.showerror("Error", "All fields are required")
            return
        f = first[0]
        l = last[0]
        generated = set()
        patterns = [
            "{first}.{last}@{domain}",
            "{first}@{domain}",
            "{first}{last}@{domain}",
            "{f}{last}@{domain}",
            "{first}.{l}@{domain}",
            "{first}-{last}@{domain}",
            "{last}@{domain}",
            "{last}{first}@{domain}",
            "{f}{l}@{domain}",
            "{first}_{last}@{domain}",
            "{last}.{first}@{domain}",
            "{f}.{last}@{domain}",
        ]
        for pattern in patterns:
            try:
                email = pattern.format(first=first, last=last, f=f, l=l, domain=domain)
                generated.add(email)
            except:
                pass
        self.pattern_results_text.delete(1.0, tk.END)
        for email in generated:
            self.pattern_results_text.insert(tk.END, email + "\n")
        save_path = filedialog.asksaveasfilename(
            title="Save Generated Email Patterns",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="generated_email_patterns"
        )
        if save_path:
            df = pd.DataFrame({"email": list(generated)})
            if save_path.endswith(".csv"):
                csv_path = save_path
                txt_path = save_path.replace(".csv", ".txt")
            else:
                csv_path = save_path.rsplit(".", 1)[0] + ".csv"
                txt_path = save_path
            df.to_csv(csv_path, index=False)
            with open(txt_path, "w") as f:
                for e in generated:
                    f.write(e + "\n")
            messagebox.showinfo("Complete", f"Generated {len(generated)} patterns saved!")
        else:
            messagebox.showinfo("Cancelled", "Save cancelled.")

    def email_verify_setup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Email Verification Tool", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="Upload CSV or TXT file with emails").grid(row=1, column=0, columnspan=2, pady=20)
        ctk.CTkButton(self.main_frame, text="Choose File", command=self.load_file_for_verification, width=300, height=40).grid(row=2, column=0, columnspan=2, pady=30)
        self.verify_file_label = ctk.CTkLabel(self.main_frame, text="No file selected")
        self.verify_file_label.grid(row=3, column=0, columnspan=2, pady=10)
        ctk.CTkButton(self.main_frame, text="Start Verification", command=lambda: self.start_thread(self.verify_emails_from_file), width=300, height=40).grid(row=4, column=0, columnspan=2, pady=40)
        ctk.CTkButton(self.main_frame, text="← Back to Menu", command=self.create_welcome_screen, width=150).grid(row=5, column=0, columnspan=2, pady=10)

    def load_file_for_verification(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV/TXT", "*.csv *.txt")])
        if file_path:
            self.verify_file_path = file_path
            self.verify_file_label.configure(text=f"Selected: {os.path.basename(file_path)}")

    def verify_emails_from_file(self):
        if not hasattr(self, 'verify_file_path'):
            messagebox.showerror("Error", "Select a file first")
            return
        emails = []
        try:
            if self.verify_file_path.endswith('.csv'):
                df = pd.read_csv(self.verify_file_path)
                for col in df.columns:
                    emails.extend(df[col].dropna().astype(str).tolist())
            else:
                with open(self.verify_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    emails = [line.strip() for line in f if '@' in line]
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        emails = list(set([e.lower() for e in emails if e]))
        valid = [e for e in emails if validate_email(e, verify=False)]
        if valid:
            df = pd.DataFrame({"email": valid})
            df.to_csv("verified_emails.csv", index=False)
            with open("verified_emails.txt", "w") as f:
                for e in valid:
                    f.write(e + "\n")
            messagebox.showinfo("Complete", f"{len(valid)} valid emails saved!")
        else:
            messagebox.showinfo("Complete", "No valid emails found.")

    def phone_verify_setup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="USA Phone Verification + Carrier", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="Upload CSV or TXT file with phones").grid(row=1, column=0, columnspan=2, pady=20)
        ctk.CTkButton(self.main_frame, text="Choose File", command=self.load_phone_file, width=300, height=40).grid(row=2, column=0, columnspan=2, pady=30)
        self.phone_file_label = ctk.CTkLabel(self.main_frame, text="No file selected")
        self.phone_file_label.grid(row=3, column=0, columnspan=2, pady=10)
        ctk.CTkButton(self.main_frame, text="Validate & Show Carriers", command=lambda: self.start_thread(self.verify_phones_file), width=300, height=40).grid(row=4, column=0, columnspan=2, pady=40)
        ctk.CTkButton(self.main_frame, text="← Back to Menu", command=self.create_welcome_screen, width=150).grid(row=5, column=0, columnspan=2, pady=10)

    def load_phone_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV/TXT", "*.csv *.txt")])
        if file_path:
            self.phone_file_path = file_path
            self.phone_file_label.configure(text=f"Selected: {os.path.basename(file_path)}")

    def verify_phones_file(self):
        if not hasattr(self, 'phone_file_path'):
            messagebox.showerror("Error", "Select a file first")
            return
        phones = []
        try:
            if self.phone_file_path.endswith('.csv'):
                df = pd.read_csv(self.phone_file_path)
                for col in df.columns:
                    phones.extend(df[col].dropna().astype(str).tolist())
            else:
                with open(self.phone_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    phones = [line.strip() for line in f]
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        results = []
        for p in phones:
            digits = re.sub(r'\D', '', p)
            if digits.startswith('1'):
                digits = digits[1:]
            if len(digits) == 10 and digits[:3] in US_MOBILE_AREA_CODES:
                carrier = get_carrier(digits[:3])
                formatted = f"+1 {digits[:3]} {digits[3:6]} {digits[6:]}"
                results.append({"phone": formatted, "carrier": carrier})
        if results:
            df = pd.DataFrame(results)
            df.to_csv("verified_usa_phones_with_carrier.csv", index=False)
            with open("verified_usa_phones_with_carrier.txt", "w") as f:
                for _, row in df.iterrows():
                    f.write(f"{row['phone']} | Carrier: {row['carrier']}\n")
            messagebox.showinfo("Complete", f"{len(results)} valid phones saved!")
        else:
            messagebox.showinfo("Complete", "No valid phones found.")

    def multi_engine_search(self, query, extra_variations=None):
        urls = set()
        variations = [query, f'"{query}"']
        if extra_variations:
            variations.extend(extra_variations)

        for variation in variations:
            try:
                google_url = f"https://www.google.com/search?q={quote(variation)}&num=100"
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                r = requests.get(google_url, headers=headers, timeout=30)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('/url?q='):
                            clean_url = href.split('/url?q=')[1].split('&')[0]
                            if 'google.com' not in clean_url:
                                urls.add(clean_url)
            except Exception:
                pass

            try:
                bing_url = f"https://www.bing.com/search?q={quote(variation)}&count=50"
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                r = requests.get(bing_url, headers=headers, timeout=30)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('http') and 'bing.com' not in href:
                            urls.add(href)
            except Exception:
                pass

            try:
                yahoo_url = f"https://search.yahoo.com/search?p={quote(variation)}&n=100"
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                r = requests.get(yahoo_url, headers=headers, timeout=30)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('http') and 'yahoo.com' not in href and 'search.yahoo.com' not in href:
                            urls.add(href)
            except Exception:
                pass

            try:
                brave_url = f"https://search.brave.com/search?q={quote(variation)}"
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                r = requests.get(brave_url, headers=headers, timeout=30)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('http') and 'brave.com' not in href:
                            urls.add(href)
            except Exception:
                pass

        return list(set(urls))[:3000]

    def fetch_page(self, url):
        try:
            time.sleep(random.uniform(1.0, 2.5))
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code in (403, 429, 503):
                time.sleep(random.uniform(10, 20))
                return None
            r.raise_for_status()
            return r.text
        except Exception:
            return None

if __name__ == "__main__":
    app = UniversalExtractorApp()
    app.mainloop()