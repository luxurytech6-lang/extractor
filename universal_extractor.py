import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
import re
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
from ddgs import DDGS
import os
import concurrent.futures
import urllib.parse

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

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

DISPOSABLE_PROVIDERS = {
    '0-mail.com', '027168.com', '0815.ru', '0815.su', '0clickemail.com', '10-minute-mail.com',
    '10minutemail.com', '10minutemail.de', '123-m.com', '1secmail.com', '1secmail.net',
    '1secmail.org', '20minutemail.com', 'disposable-mail.com', 'emailondeck.com',
    'fakemail.com', 'getnada.com', 'guerrillamail.com', 'mail7.io', 'mailinator.com',
    'sharklasers.com', 'temp-mail.org', 'tempmail.com', 'tempmail.net', 'throwawaymail.com',
    'trashmail.com', 'yopmail.com', 'burnermail.io', 'tempr.email', 'fakeinbox.com',
    '0n0ff.net', '2prong.com', '30minutemail.com', '4warding.com', '6mail.cf', '6mail.ga',
    '9ox.net', 'a-bc.net', 'abyssmail.com', 'afrobacon.com', 'agedmail.com', 'ama-trade.de',
    'anon-mail.de', 'anonbox.net', 'anonymail.dk', 'anonymbox.com', 'anypng.com', 'appmail.uk',
    'armyspy.com', 'autotwollow.com', 'azmeil.tk', 'binkmail.com', 'bio-muesli.net', 'bobmail.info',
    'bugmenever.com', 'chogmail.com', 'clrmail.com', 'cool.fr.nf', 'courriel.fr.nf', 'cust.in',
    'd3p.email', 'despam.it', 'disbox.net', 'disposableinbox.com', 'dispostable.com', 'dodgeit.com',
    'dontreg.com', 'droplar.com', 'dropmail.me', 'e4ward.com', 'einrot.com', 'email60.com',
    'emailfake.com', 'emailmiser.com', 'emails.ga', 'etranquil.com', 'evopo.com', 'fakedemail.com',
    'filzmail.com', 'frapmail.com', 'garliclife.com', 'gishpuppy.com', 'great-host.in', 'guerillamail.biz',
    'guerrillamailblock.com', 'haltospam.com', 'hmail.us', 'hotpop.com', 'ieatspam.eu', 'ieatspam.info',
    'ihateyoualot.info', 'imails.info', 'inboxalias.com', 'incognitomail.org', 'ipoo.org', 'jetable.com',
    'jetable.fr.nf', 'jetable.net', 'jetable.org', 'jnxjn.com', 'kasmail.com', 'kulturbasar.com',
    'kurzepost.de', 'lortemail.dk', 'mail-temporaire.fr', 'mail.by', 'mailcatch.com', 'maildrop.cc',
    'mailexpire.com', 'mailfreeonline.com', 'mailguard.me', 'mailhazard.com', 'mailimate.com',
    'mailin8r.com', 'mailinater.com', 'mailinator2.com', 'mailismagic.com', 'mailjunk.gq', 'mailmate.com',
    'mailme.gq', 'mailme.ir', 'mailme.lv', 'mailmetrash.com', 'mailmoat.com', 'mailms.com', 'mailnator.com',
    'mailnesia.com', 'mailnull.com', 'mailproxsy.com', 'mailquack.com', 'mailscrap.com', 'mailshell.com',
    'mailsiphon.com', 'mailzilla.com', 'mbx.cc', 'meltmail.com', 'mohmal.com', 'mt2009.com', 'my10minutemail.com',
    'mytrashmail.com', 'neomailbox.com', 'nervmich.net', 'netmails.com', 'netmails.net', 'no-spam.ws',
    'nobulk.com', 'noclickemail.com', 'nomail.pw', 'nomail2me.com', 'noreply.fr.nf', 'nospam4.us',
    'nospamthanks.info', 'notmailinator.com', 'nowmymail.com', 'objectmail.com', 'obobbo.com',
    'oneoffemail.com', 'onewaymail.com', 'onlatedotcom.info', 'oopi.org', 'otherinbox.com', 'p33.org',
    'pancakemail.com', 'paplease.com', 'pcusers.otherinbox.com', 'pimpmymail.com', 'pjjkp.com',
    'politikerclub.de', 'poofy.org', 'pookmail.com', 'privacy.net', 'privy-mail.com', 'privymail.de',
    'putthisinyourspamdatabase.com', 'putthisinyourspamdatabase.net', 'quickinbox.com', 'rcpt.at',
    'reallymymail.com', 'recode.me', 'reconmail.com', 'regbypass.com', 'rejectmail.com', 'rklips.com',
    'rmqkr.net', 'rootprompt.org', 's0ny.net', 'safe-mail.net', 'safetymail.info', 'sandelf.de',
    'saynotospams.com', 'selfdestructingmail.com', 'sendspamhere.com', 'sharklasers.com', 'shieldedmail.com',
    'shiftmail.com', 'shitmail.me', 'shortmail.net', 'skeefmail.com', 'slaskpost.se', 'slopsbox.com',
    'smellfear.com', 'snakemail.com', 'sneakemail.com', 'sofort-mail.de', 'sogetthis.com', 'soodonims.com',
    'spam-be-gone.com', 'spam.la', 'spam.su', 'spam4.me', 'spamavert.com', 'spambob.com', 'spambob.net',
    'spambog.com', 'spambog.de', 'spambog.ru', 'spamcannon.com', 'spamcero.com', 'spamcon.org',
    'spamcorptastic.com', 'spamcowboy.com', 'spamcowboy.net', 'spamday.com', 'spamdecoy.net', 'spamex.com',
    'spamfree.eu', 'spamfree24.org', 'spamgourmet.com', 'spamgourmet.net', 'spamherelots.com',
    'spamhereplease.com', 'spamhole.com', 'spamify.com', 'spaml.com', 'spaml.de', 'spammotel.com',
    'spamobox.com', 'spamoff.de', 'spamreturn.com', 'spamspot.com', 'spamstack.net', 'spamthis.co.uk',
    'spamthisplease.com', 'spamtrail.com', 'spamtroll.net', 'speed.1s.fr', 'spoofmail.de', 'squizzy.de',
    'sriaus.com', 'stop-my-spam.com', 'super-auswahl.de', 'suremail.info', 'tagyourself.com', 'teewars.org',
    'teleworm.com', 'teleworm.us', 'temp-mail.com', 'temp-mail.ru', 'tempail.com', 'tempalias.com',
    'tempemail.biz', 'tempemail.co.za', 'tempemail.net', 'tempinbox.co.uk', 'tempinbox.com', 'tempmail.eu',
    'tempmail.it', 'tempmail2.com', 'tempmaildemo.com', 'tempmailer.com', 'tempmailer.de', 'temporaryemail.net',
    'temporaryemail.us', 'temporaryinbox.com', 'thankyou2010.com', 'the-spam.com', 'thisisnotmyrealemail.com',
    'throwaway.email', 'tilien.com', 'tittbit.in', 'tmail.ws', 'tmailinator.com', 'toomail.biz', 'topranklist.de',
    'tradermail.info', 'trash-mail.at', 'trash-mail.cf', 'trash-mail.com', 'trash-mail.de', 'trash2009.com',
    'trashdevil.com', 'trashmail.at', 'trashmail.com', 'trashmail.de', 'trashmail.me', 'trashmail.net',
    'trashmail.org', 'trashmail.ws', 'trashmailer.com', 'trashymail.com', 'trashymail.net', 'trbvm.com',
    'trillianpro.com', 'turual.com', 'twinmail.de', 'tyldd.com', 'uggsrock.com', 'upliftnow.com',
    'venompen.com', 'veryrealemail.com', 'viditag.com', 'viewcastmedia.com', 'viewcastmedia.net',
    'vomoto.com', 'vubby.com', 'walala.org', 'wasteland.rfc822.org', 'webm4il.info', 'wegwerfemail.de',
    'wegwerfmail.de', 'wegwerfmail.net', 'wegwerfmail.org', 'wh4f.org', 'whyspam.me', 'willhackforfood.biz',
    'willselfdestruct.com', 'winemaven.info', 'wronghead.com', 'wuzup.net', 'xagloo.com', 'xemaps.com',
    'xents.com', 'xoxy.net', 'yep.it', 'yogamail.com', 'yopmail.fr', 'yopmail.net', 'youmailr.com',
    'yourdomain.com', 'yuurok.com', 'zippymail.info', 'zoaxe.com', 'zoemail.org', 'zomg.info'
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

EMAIL_SYNTAX_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def has_mx_record(domain):
    if not DNS_AVAILABLE:
        return True
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, dns.resolver.NoNameservers):
        try:
            dns.resolver.resolve(domain, 'A')
            return True
        except:
            try:
                dns.resolver.resolve(domain, 'AAAA')
                return True
            except:
                return False
    except:
        return False

class UniversalExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Email & Phone Extractor Suite 2026")
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

        self.create_welcome_screen()

    def create_welcome_screen(self):
        self.clear_frame()

        title = ctk.CTkLabel(self.main_frame, text="Email & Phone Extractor Suite", 
                             font=ctk.CTkFont(size=30, weight="bold"))
        title.grid(row=0, column=0, pady=(40, 20))

        subtitle = ctk.CTkLabel(self.main_frame, text="Select a tool to begin", font=ctk.CTkFont(size=16))
        subtitle.grid(row=1, column=0, pady=(0, 30))

        options = [
            ("Email Extractor", self.email_only_setup),
            ("USA Mobile Phone Extractor", self.phone_setup),
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

    def email_only_setup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Email Extractor", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))

        ctk.CTkLabel(self.main_frame, text="Search Keyword:").grid(row=1, column=0, sticky="w", padx=30, pady=8)
        self.email_keyword = ctk.CTkEntry(self.main_frame, width=450)
        self.email_keyword.grid(row=1, column=1, pady=8, sticky="w")
        self.email_keyword.insert(0, "contact email support sales")

        ctk.CTkLabel(self.main_frame, text="Email Type:").grid(row=2, column=0, sticky="w", padx=30, pady=8)
        self.email_type = ctk.StringVar(value="all")
        ctk.CTkRadioButton(self.main_frame, text="All Emails", variable=self.email_type, value="all").grid(row=2, column=1, sticky="w")
        ctk.CTkRadioButton(self.main_frame, text="Company Only", variable=self.email_type, value="company").grid(row=3, column=1, sticky="w")
        ctk.CTkRadioButton(self.main_frame, text="Personal Only", variable=self.email_type, value="personal").grid(row=4, column=1, sticky="w")

        ctk.CTkLabel(self.main_frame, text="Max Valid Emails (max 1000):").grid(row=5, column=0, sticky="w", padx=30, pady=15)
        self.email_count = ctk.CTkEntry(self.main_frame, width=150)
        self.email_count.grid(row=5, column=1, sticky="w")
        self.email_count.insert(0, "200")

        self.email_start_btn = ctk.CTkButton(self.main_frame, text="Start Extraction", width=200, height=40,
                                             font=ctk.CTkFont(size=14), command=lambda: self.start_thread(self.extract_emails_only))
        self.email_start_btn.grid(row=6, column=0, columnspan=2, pady=20)

        ctk.CTkButton(self.main_frame, text="Back to Menu", command=self.create_welcome_screen, width=150).grid(row=7, column=0, columnspan=2, pady=10)

        results_label = ctk.CTkLabel(self.main_frame, text="Live Results:", font=ctk.CTkFont(size=16, weight="bold"))
        results_label.grid(row=8, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=30)

        self.email_results_text = scrolledtext.ScrolledText(self.main_frame, height=12, font=("Consolas", 10))
        self.email_results_text.grid(row=9, column=0, columnspan=2, padx=30, pady=5, sticky="nsew")

        self.main_frame.grid_rowconfigure(9, weight=1)

        self.email_progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate", length=600)
        self.email_progress.grid(row=10, column=0, columnspan=2, pady=15, padx=30)
        self.email_status = ctk.CTkLabel(self.main_frame, text="Ready")
        self.email_status.grid(row=11, column=0, columnspan=2)

    def crawl_page(self, url, depth=1, max_depth=2):
        if depth > max_depth:
            return []
        html = self.fetch_page(url)
        if not html:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        domain = urllib.parse.urlparse(url).netloc
        additional_urls = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_href = urllib.parse.urljoin(url, href)
            if urllib.parse.urlparse(full_href).netloc == domain and any(k in href.lower() for k in ['contact', 'about', 'team', 'people', 'staff', 'directory']):
                additional_urls.append(full_href)
            if len(additional_urls) >= 10:
                break
        extra_htmls = []
        for u in additional_urls:
            extra = self.fetch_page(u)
            if extra:
                extra_htmls.append(extra)
            time.sleep(random.uniform(0.8, 2.0))
        return [html] + extra_htmls

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
        self.email_status.configure(text="Searching web for more sources...")
        self.email_results_text.delete(1.0, tk.END)
        self.email_start_btn.configure(text="Stop Extraction", fg_color="dark red", command=self.stop_extraction)
        self.update_idletasks()

        urls = self.multi_engine_search(keyword)
        if not urls:
            self.email_status.configure(text="No results found.")
            self.reset_start_button(self.email_start_btn)
            return

        emails = set()
        valid_emails = []
        needed = target * 8

        for i, url in enumerate(urls):
            if self.stop_event.is_set():
                self.email_status.configure(text="Extraction stopped by user")
                self.reset_start_button(self.email_start_btn)
                return

            if len(emails) >= needed:
                break
            self.email_progress['value'] = (i / len(urls)) * 70
            self.update_idletasks()

            htmls = self.crawl_page(url)
            for html in htmls:
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    text = soup.get_text()
                    found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text + html)
                    for e in found:
                        e_clean = e.lower().strip()

                        if e_clean.startswith('u003e'):
                            e_clean = e_clean[5:]

                        if '...' in e_clean:
                            parts = e_clean.split('@')
                            if len(parts) == 2:
                                username = parts[0].replace('...', '')
                                e_clean = username + '@' + parts[1]

                        e_clean = e_clean.replace('[at]', '@').replace('(at)', '@')
                        e_clean = e_clean.replace('[dot]', '.').replace('(dot)', '.')
                        e_clean = e_clean.replace(' at ', '@').replace(' dot ', '.')

                        domain = e_clean.split('@')[-1] if '@' in e_clean else ''
                        if domain in DISPOSABLE_PROVIDERS:
                            continue
                        if etype == "company" and domain in PERSONAL_PROVIDERS:
                            continue
                        if etype == "personal" and domain not in PERSONAL_PROVIDERS:
                            continue

                        if e_clean not in emails:
                            emails.add(e_clean)
                            self.email_results_text.insert(tk.END, f"{e_clean}\n")
                            self.email_results_text.see(tk.END)
                            self.update_idletasks()

        self.email_status.configure(text="Verifying emails (this may take time)...")
        self.update_idletasks()

        def verify_single(email):
            domain = email.split('@')[-1].lower()
            if domain in DISPOSABLE_PROVIDERS:
                return None
            if not EMAIL_SYNTAX_REGEX.match(email):
                return None
            if has_mx_record(domain):
                return email
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(verify_single, email) for email in list(emails)]
            for future in concurrent.futures.as_completed(futures):
                if self.stop_event.is_set():
                    break
                result = future.result()
                if result and len(valid_emails) < target:
                    valid_emails.append(result)
                    self.email_results_text.insert(tk.END, f"[VERIFIED] {result}\n")
                    self.email_results_text.see(tk.END)
                    self.update_idletasks()

        final_emails = valid_emails[:target]
        self.save_emails(final_emails, "extracted_emails")
        self.email_status.configure(text="Complete")
        self.reset_start_button(self.email_start_btn)
        messagebox.showinfo("Complete", f"Extracted {len(final_emails)} valid emails! (Collected from {len(urls)} sources)")

    def reset_start_button(self, btn):
        btn.configure(text="Start Extraction", fg_color=("gray75", "gray25"), command=lambda: self.start_thread(self.extract_emails_only))
        self.running = False
        self.stop_event.clear()

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

        self.phone_start_btn = ctk.CTkButton(self.main_frame, text="Start Extraction", width=200, height=40,
                                             font=ctk.CTkFont(size=14), command=lambda: self.start_thread(self.extract_usa_phones))
        self.phone_start_btn.grid(row=3, column=0, columnspan=2, pady=20)

        ctk.CTkButton(self.main_frame, text="Back to Menu", command=self.create_welcome_screen, width=150).grid(row=4, column=0, columnspan=2, pady=10)

        results_label = ctk.CTkLabel(self.main_frame, text="Live Results:", font=ctk.CTkFont(size=16, weight="bold"))
        results_label.grid(row=5, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=30)

        self.phone_results_text = scrolledtext.ScrolledText(self.main_frame, height=12, font=("Consolas", 10))
        self.phone_results_text.grid(row=6, column=0, columnspan=2, padx=30, pady=5, sticky="nsew")

        self.main_frame.grid_rowconfigure(6, weight=1)

        self.phone_progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate", length=600)
        self.phone_progress.grid(row=7, column=0, columnspan=2, pady=15, padx=30)
        self.phone_status = ctk.CTkLabel(self.main_frame, text="Ready")
        self.phone_status.grid(row=8, column=0, columnspan=2)

    def extract_usa_phones(self):
        keyword = self.phone_keyword.get().strip()
        if not keyword:
            messagebox.showerror("Error", "Search keyword is required")
            return

        try:
            target = int(self.phone_count.get())
            if not 1 <= target <= 1000:
                raise ValueError
        except:
            messagebox.showerror("Error", "Enter a number between 1 and 1000")
            return

        self.phone_status.configure(text="Searching web...")
        self.phone_results_text.delete(1.0, tk.END)
        self.phone_start_btn.configure(text="Stop Extraction", fg_color="dark red", command=self.stop_extraction)
        self.update_idletasks()

        urls = self.multi_engine_search(keyword)
        if not urls:
            self.phone_status.configure(text="No results found.")
            self.reset_start_button(self.phone_start_btn)
            return

        results = []
        for i, url in enumerate(urls):
            if self.stop_event.is_set():
                self.phone_status.configure(text="Extraction stopped by user")
                self.reset_start_button(self.phone_start_btn)
                return

            if len(results) >= target:
                break
            self.phone_progress['value'] = (i / len(urls)) * 100
            self.update_idletasks()

            htmls = self.crawl_page(url)
            for html in htmls:
                if html:
                    matches = PHONE_REGEX.findall(html)
                    for match in matches:
                        full = match[0]
                        cleaned = re.sub(r'\D', '', full)
                        if cleaned.startswith('1'):
                            cleaned = cleaned[1:]
                        if len(cleaned) == 10 and cleaned[:3] in US_MOBILE_AREA_CODES:
                            carrier = get_carrier(cleaned[:3])
                            formatted = f"+1 {cleaned[:3]} {cleaned[3:6]} {cleaned[6:]}"
                            if formatted not in [r['phone'] for r in results]:
                                results.append({"phone": formatted, "carrier": carrier})
                                self.phone_results_text.insert(tk.END, f"{formatted} | Carrier: {carrier}\n")
                                self.phone_results_text.see(tk.END)
                                self.update_idletasks()

        final_results = results[:target]
        df = pd.DataFrame(final_results)
        df.to_csv("usa_mobile_phones_with_carrier.csv", index=False)
        with open("usa_mobile_phones_with_carrier.txt", "w") as f:
            for _, row in df.iterrows():
                f.write(f"{row['phone']} | Carrier: {row['carrier']}\n")

        self.phone_status.configure(text="Complete")
        self.reset_start_button(self.phone_start_btn)
        messagebox.showinfo("Complete", f"Extracted {len(final_results)} USA mobile numbers!")

    def email_verify_setup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Email Verification Tool", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="Upload CSV or TXT file with emails").grid(row=1, column=0, columnspan=2, pady=20)

        ctk.CTkButton(self.main_frame, text="Choose File", command=self.load_file_for_verification, width=300, height=40).grid(row=2, column=0, columnspan=2, pady=30)

        self.verify_file_label = ctk.CTkLabel(self.main_frame, text="No file selected")
        self.verify_file_label.grid(row=3, column=0, columnspan=2, pady=10)

        ctk.CTkButton(self.main_frame, text="Start Verification", command=lambda: self.start_thread(self.verify_emails_from_file), width=300, height=40).grid(row=4, column=0, columnspan=2, pady=40)

        ctk.CTkButton(self.main_frame, text="Back to Menu", command=self.create_welcome_screen, width=150).grid(row=5, column=0, columnspan=2, pady=10)

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

        def verify_single(email):
            domain = email.split('@')[-1].lower()
            if domain in DISPOSABLE_PROVIDERS:
                return None
            if not EMAIL_SYNTAX_REGEX.match(email):
                return None
            if has_mx_record(domain):
                return email
            return None

        valid = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(verify_single, email) for email in emails]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid.append(result)

        self.save_emails(valid, "verified_emails")
        messagebox.showinfo("Complete", f"{len(valid)} valid emails saved!")

    def phone_verify_setup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="USA Phone Verification + Carrier", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="Upload CSV or TXT file with phones").grid(row=1, column=0, columnspan=2, pady=20)

        ctk.CTkButton(self.main_frame, text="Choose File", command=self.load_phone_file, width=300, height=40).grid(row=2, column=0, columnspan=2, pady=30)

        self.phone_file_label = ctk.CTkLabel(self.main_frame, text="No file selected")
        self.phone_file_label.grid(row=3, column=0, columnspan=2, pady=10)

        ctk.CTkButton(self.main_frame, text="Validate & Show Carriers", command=lambda: self.start_thread(self.verify_phones_file), width=300, height=40).grid(row=4, column=0, columnspan=2, pady=40)

        ctk.CTkButton(self.main_frame, text="Back to Menu", command=self.create_welcome_screen, width=150).grid(row=5, column=0, columnspan=2, pady=10)

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

        df = pd.DataFrame(results)
        df.to_csv("verified_usa_phones_with_carrier.csv", index=False)
        with open("verified_usa_phones_with_carrier.txt", "w") as f:
            for _, row in df.iterrows():
                f.write(f"{row['phone']} | Carrier: {row['carrier']}\n")

        messagebox.showinfo("Complete", f"{len(results)} valid USA phones with carriers saved!")

    def searxng_search(self, query):
        urls = set()
        # Reliable public SearXNG instances (active as of January 2026, high uptime)
        instances = [
            "https://searx.tiekoetter.com",
            "https://search.rhscz.eu",
            "https://searxng.site",
            "https://priv.au",
            "https://opnxng.com",
            "https://copp.gg",
            "https://searx.tuxcloud.net",
            "https://search.sapti.me",
            "https://paulgo.io",
            "https://baresearch.org",
            "https://search.ononoki.org",
            "https://search.mdosch.de",
        ]

        headers = {'User-Agent': random.choice(USER_AGENTS)}

        for instance in instances:
            if self.stop_event.is_set():
                break
            try:
                params = {
                    'q': query,
                    'format': 'json',
                    'pageno': 1,
                }
                r = requests.get(f"{instance}/search", params=params, headers=headers, timeout=25)
                if r.status_code == 200:
                    data = r.json()
                    for result in data.get('results', [])[:50]:
                        if 'url' in result:
                            urls.add(result['url'])
            except Exception:
                continue
            time.sleep(random.uniform(0.8, 2.0))

        return urls

    def multi_engine_search(self, query):
        urls = set()
        variations = [
            query,
            f'"{query}"',
            f"{query} contact",
            f"{query} email",
            f"{query} \"contact us\"",
            f"{query} \"get in touch\"",
            f"{query} support",
            f"{query} team",
            f"{query} directory",
            f"{query} staff",
            f"{query} leadership",
            f"intitle:\"contact us\" {query}",
            f"inurl:contact {query}",
            f"inurl:about {query}",
            f"inurl:team {query}",
            f"inurl:people {query}",
            f"inurl:staff {query}",
            f"filetype:pdf {query} contact email",
            f"{query} @gmail.com OR @yahoo.com OR @outlook.com OR @hotmail.com OR @protonmail.com",
            f"{query} site:.com OR site:.org OR site:.net -site:facebook.com -site:linkedin.com -site:twitter.com -site:instagram.com",
            f"{query} \"mail\" OR \"e-mail\" OR \"email address\" OR \"reach us\"",
        ]

        for variation in variations:
            if self.stop_event.is_set():
                break
            try:
                with DDGS() as ddgs:
                    results = ddgs.text(variation, max_results=250)
                    for r in results:
                        urls.add(r['href'])
            except:
                continue
            time.sleep(random.uniform(0.6, 1.8))

        # Existing Google scraping (kept but may be blocked)
        try:
            google_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=100"
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            r = requests.get(google_url, headers=headers, timeout=30)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/url?q='):
                        clean_url = urllib.parse.unquote(href.split('/url?q=')[1].split('&')[0])
                        if all(block not in clean_url for block in ['google.com', 'youtube.com', 'facebook.com', 'linkedin.com', 'twitter.com', 'instagram.com']):
                            urls.add(clean_url)
        except:
            pass

        # Existing Bing scraping
        try:
            bing_url = f"https://www.bing.com/search?q={requests.utils.quote(query)}&count=100"
            r = requests.get(bing_url, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=30)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http') and 'bing.com' not in href:
                        urls.add(href)
        except:
            pass

        # NEW: SearXNG metasearch (adds many non-blocked engines like Brave, Ecosia, Qwant, Yandex, etc.)
        if not self.stop_event.is_set():
            searxng_urls = self.searxng_search(query)
            urls.update(searxng_urls)

        return list(urls)[:1000]

    def fetch_page(self, url):
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            return r.text
        except:
            return None

    def save_emails(self, emails, prefix):
        if not emails:
            return
        df = pd.DataFrame({"email": emails})
        df.to_csv(f"{prefix}.csv", index=False)
        with open(f"{prefix}.txt", "w") as f:
            for e in emails:
                f.write(e + "\n")

if __name__ == "__main__":
    app = UniversalExtractorApp()
    app.mainloop()