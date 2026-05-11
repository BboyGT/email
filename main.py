"""Main CLI application for EmailGen."""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import time
from colorama import init
init(autoreset=True)

from config import Colors, APP_NAME, APP_VERSION
from storage import Storage
from email_generator import EmailGenerator
from inbox_reader import InboxReader
from phone_provider import PhoneProvider
from auto_signup import EnhancedAutoSignup
from email_monitor import EmailMonitor


class EmailGenApp:
    def __init__(self):
        self.storage = Storage()
        self.generator = EmailGenerator()
        self.reader = InboxReader()
        self.phone_provider = PhoneProvider()
        self.auto_signup = EnhancedAutoSignup()
        self.monitor = EmailMonitor(self.storage, self.reader)
    
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def banner(self):
        print("="*60)
        print("  %s - Email & OTP Automation Tool" % APP_NAME)
        print("  Version %s" % APP_VERSION)
        print("="*60)
        print("  Generate Emails | Auto Signup | Monitor Codes")
        print("="*60)
    
    def menu(self):
        e = self.storage.get_email_count()
        p = self.storage.get_phone_count()
        
        print("\n[ MAIN MENU ] (Emails: %d | Phones: %d)" % (e, p))
        print("-"*60)
        print(" [1] Generate Emails")
        print(" [2] Generate Phone Numbers")
        print(" [3] Check Email Inbox")
        print(" [4] Auto Signup (Bulk)")
        print(" [5] Monitor for Codes")
        print(" [6] View All Emails")
        print(" [7] View All Phones")
        print(" [8] Delete Entry")
        print(" [9] Delete All")
        print(" [0] Exit")
        print("-"*60)
    
    def ok(self, msg): print("[OK] %s" % msg)
    def err(self, msg): print("[ERROR] %s" % msg)
    def warn(self, msg): print("[WARN] %s" % msg)
    def info(self, msg): print("[INFO] %s" % msg)
    
    def gen_emails(self):
        self.clear(); self.banner()
        try:
            n = int(input("\nHow many emails? [1-1000]: "))
            n = max(1, min(1000, n))
        except: n = 1
        
        for i in range(n):
            email = self.generator.generate_single()
            self.storage.add_email(email.email, email.password, email.provider)
            print("  [%d/%d] %s" % (i+1, n, email.email))
        
        print("\nGenerated %d emails!" % n)
    
    def gen_phones(self):
        self.clear(); self.banner()
        countries = ["USA", "UK", "Canada", "Australia"]
        for i,c in enumerate(countries,1): print("  [%d] %s" % (i,c))
        
        try:
            c = int(input("\nCountry [1]: ") or "1")
            country = countries[max(0, min(c-1, len(countries)))]
        except: country = "USA"
        
        phones = self.phone_provider.get_phone_numbers(country)
        if phones:
            for p in phones[:5]:
                self.storage.add_phone(self.phone_provider.get_phone_info(p), country, p.get('service','unknown'))
            print("Added %d phones" % len(phones[:5]))
        else:
            print("No phones available")
    
    def check_inbox(self):
        emails = self.storage.get_all_emails()
        if not emails: print("No emails"); return
        
        for email in emails: print("  [%d] %s" % (email.id, email.email))
        try:
            eid = int(input("\nEmail ID: "))
            entry = self.storage.get_email_by_id(eid)
            if not entry: print("Not found"); return
            
            print("Checking %s..." % entry.email)
            msgs = self.reader.check_inbox(entry.email)
            
            if not msgs: print("No emails in inbox")
            else:
                for m in msgs:
                    print("\nFrom: %s" % m.from_addr)
                    print("Subject: %s" % m.subject)
        except: pass
    
    def auto_signup(self):
        emails = self.storage.get_all_emails()
        if not emails: print("No emails"); return
        
        url = input("Signup URL: ").strip()
        if not url.startswith('http'): url = 'https://' + url
        
        try:
            n = int(input("How many emails? [all]: ") or str(len(emails)))
            elist = [e.email for e in emails[:n]]
        except: elist = [emails[0].email]
        
        print("Signing up with %d emails..." % len(elist))
        results = self.auto_signup.bulk_signup(url, elist, 2)
        
        ok = sum(1 for r in results if r['success'])
        print("\nResults: %d/%d successful" % (ok, len(results)))
    
    def monitor(self):
        print("\n[ MONITOR ]")
        print("-"*40)
        print(" [1] Add website to monitor")
        print(" [2] View monitored websites")
        print(" [3] Start monitoring")
        print(" [4] View detected codes")
        print(" [0] Back")
        print("-"*40)
        
        ch = input("Choice: ").strip()
        
        if ch == '1':
            url = input("URL: ").strip()
            if not url.startswith('http'): url = 'https://' + url
            s = self.monitor.add_site(url, None)
            print("Added: %s" % s.name)
        elif ch == '2':
            for s in self.monitor.get_monitored_sites():
                print("  [%d] %s (%s)" % (s.id, s.name, s.domain))
        elif ch == '3':
            try:
                d = int(input("Duration (sec) [60]: ") or "60")
                print("Monitoring... (Ctrl+C to stop)")
                r = self.monitor.monitor_all(max_duration=d)
                if r:
                    print("Found %d codes!" % len(r))
                    self.monitor.display_results()
                else:
                    print("No codes found")
            except: pass
        elif ch == '4':
            self.monitor.display_results()
    
    def view_emails(self):
        emails = self.storage.get_all_emails()
        if not emails: print("No emails"); return
        
        print("\n[ ALL EMAILS ]")
        print("-"*60)
        for e in emails:
            print(" [%d] %-35s %s" % (e.id, e.email, e.password[:8]))
        print("-"*60)
        print("Total: %d" % len(emails))
    
    def view_phones(self):
        phones = self.storage.get_all_phones()
        if not phones: print("No phones"); return
        
        print("\n[ ALL PHONES ]")
        print("-"*50)
        for p in phones:
            print(" [%d] %-25s %s" % (p.id, p.phone, p.country))
        print("-"*50)
        print("Total: %d" % len(phones))
    
    def delete(self):
        print("\n[ DELETE ]")
        print("-"*40)
        print(" [1] Delete email by ID")
        print(" [2] Delete phone by ID")
        print(" [3] Delete all emails")
        print(" [4] Delete all phones")
        print(" [5] Delete everything")
        print(" [0] Back")
        print("-"*40)
        
        ch = input("Choice: ").strip()
        
        if ch == '1':
            emails = self.storage.get_all_emails()
            for e in emails: print("  [%d] %s" % (e.id, e.email))
            try:
                eid = int(input("Email ID: "))
                if self.storage.delete_email_by_id(eid): print("Deleted")
                else: print("Not found")
            except: pass
        elif ch == '2':
            phones = self.storage.get_all_phones()
            for p in phones: print("  [%d] %s" % (p.id, p.phone))
            try:
                pid = int(input("Phone ID: "))
                if self.storage.delete_phone_by_id(pid): print("Deleted")
                else: print("Not found")
            except: pass
        elif ch == '3':
            if input("Delete all emails? [y/N]: ").lower()=='y':
                self.storage.delete_all_emails()
                print("Done")
        elif ch == '4':
            if input("Delete all phones? [y/N]: ").lower()=='y':
                self.storage.delete_all_phones()
                print("Done")
        elif ch == '5':
            if input("Delete EVERYTHING? [y/N]: ").lower()=='y':
                self.storage.clear_all()
                print("Done")
    
    def run(self):
        while True:
            self.clear()
            self.banner()
            self.menu()
            
            ch = input("\n> ").strip()
            
            try:
                if ch == '1': self.gen_emails()
                elif ch == '2': self.gen_phones()
                elif ch == '3': self.check_inbox()
                elif ch == '4': self.auto_signup()
                elif ch == '5': self.monitor()
                elif ch == '6': self.view_emails()
                elif ch == '7': self.view_phones()
                elif ch == '8': self.delete()
                elif ch == '9': self.delete()
                elif ch == '0': break
                else: print("Invalid choice")
            except Exception as e:
                print("Error: %s" % str(e)[:50])
            
            if ch != '0':
                input("\nPress Enter...")


if __name__ == "__main__":
    EmailGenApp().run()
