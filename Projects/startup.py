import os
import subprocess
import sys
import threading
import unittest
import webbrowser
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
from HtmlTestRunner.result import TestResult
import HtmlTestRunner
import glob
import time
import unittest
from selenium import webdriver

class BaseTest(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")  # if needed
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

        # pick URL from environment (set by GUI before test run)
        app_url = os.environ.get("APP_URL")
        if not app_url:
            raise RuntimeError("No APP_URL provided from GUI")
        self.driver.get(app_url)

    def tearDown(self):
        self.driver.quit()

# ---------------- Screenshot TestResult ----------------



class ScreenshotTestResult(HtmlTestRunner.result.TestResult):
    def startTest(self, test):
        self._start_time = time.time()
        test_name = getattr(test, "_testMethodName", str(test))
        print(f"[STARTED] {test_name}")
        super().startTest(test)

    def stopTest(self, test):
        duration = time.time() - getattr(self, "_start_time", time.time())
        test_name = getattr(test, "_testMethodName", str(test))
        print(f"[ENDED] {test_name} (Duration: {duration:.2f}s)")
        print("-" * 60)
        super().stopTest(test)

    def addSuccess(self, test):
        test_name = getattr(test, "_testMethodName", str(test))
        print(f"[PASSED] {test_name}")
        super().addSuccess(test)

    def addFailure(self, test, err):
        test_name = getattr(test, "_testMethodName", str(test))
        print(f"[FAILED] {test_name}")
        self._take_screenshot(test)
        super().addFailure(test, err)

    def addError(self, test, err):
        test_name = getattr(test, "_testMethodName", str(test))
        print(f"[ERROR] {test_name}")
        self._take_screenshot(test)
        super().addError(test, err)

    def addSkip(self, test, reason):
        test_name = getattr(test, "_testMethodName", str(test))
        print(f"[SKIPPED] {test_name} (Reason: {reason})")
        super().addSkip(test, reason)

    def _take_screenshot(self, test):
        driver = getattr(test, "driver", None)
        if driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_name = getattr(test, "_testMethodName", str(test))
            screenshot_name = f"{test_name}_{timestamp}.png"
            screenshot_path = os.path.join("reports", screenshot_name)
            try:
                driver.save_screenshot(screenshot_path)
                print(f"[FAILED] Screenshot saved: {screenshot_path}")
                if not hasattr(self, "screenshots"):
                    self.screenshots = []
                self.screenshots.append(screenshot_path)
            except Exception as e:
                print("Could not save screenshot:", e)


class ScreenshotTestRunner(HtmlTestRunner.HTMLTestRunner):
    resultclass = ScreenshotTestResult





# ---------------- Redirect console output ----------------
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        if text.strip() == "":
            self._write_to_widget(text)
            return

        # detect status keywords and map to console tags
        tag = None
        if text.startswith("[PASSED]"):
            tag = "ok"
        elif text.startswith("[FAILED]"):
            tag = "fail"
        elif text.startswith("[ERROR]"):
            tag = "error"
        elif text.startswith("[SKIPPED]"):
            tag = "skip"
        elif text.startswith("[STARTED]") or text.startswith("[ENDED]"):
            tag = "header"

        self._write_to_widget(text, tag)

    def _write_to_widget(self, text, tag=None):
        def append():
            self.widget.configure(state="normal")   # unlock
            if tag:
                self.widget.insert("end", text, tag)
            else:
                self.widget.insert("end", text)
            self.widget.see("end")
            self.widget.configure(state="disabled") # lock again
        self.widget.after(0, append)


    def flush(self):
        pass




# ---------------- Main App ----------------
class TestRunnerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Automation Test Runner")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Dark theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.running = False
        self.folder_path = tk.StringVar()
        self.report_file = None
        self.fullscreen = False
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widgets()

    def create_widgets(self):
        # ----------- Top Toolbar -----------
        top_frame = ctk.CTkFrame(self, corner_radius=10)
        top_frame.pack(side="top", fill="x", padx=12, pady=8)

        self.title_lbl = ctk.CTkLabel(top_frame, text="Automation Test Runner", font=("Segoe UI", 18, "bold"))
        self.title_lbl.pack(side="left", padx=10)

        self.url_entry = ctk.CTkEntry(top_frame, width=300, placeholder_text="Enter application URL (e.g. http://localhost:5082/)")
        self.url_entry.pack(side="left", padx=8)

        self.folder_entry = ctk.CTkEntry(top_frame, width=400, placeholder_text="Select test folder")
        self.folder_entry.pack(side="left", padx=10)

        browse_btn = ctk.CTkButton(top_frame, text="Browse", fg_color="#120EF0",hover=False,command=self.browse_folder,font=("Segoe UI", 14, "bold"))
        browse_btn.pack(side="left", padx=6)

        self.start_btn = ctk.CTkButton(top_frame, text="▶ Start Test", fg_color="green",hover=False, command=self.start_test,font=("Segoe UI", 14, "bold"))
        self.start_btn.pack(side="left", padx=10)

        clear_btn = ctk.CTkButton(top_frame, text="Clear Console", fg_color="gray",hover=False, command=self.clear_console,font=("Segoe UI", 14, "bold"))
        clear_btn.pack(side="left", padx=6)

        

        # ----------- Main Split Area -----------
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)

        # Left Summary
        left_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        self.lbl_total = self._make_summary_card(left_frame, "Total", row=0)
        self.lbl_passed = self._make_summary_card(left_frame, "Passed", row=1)
        self.lbl_fail = self._make_summary_card(left_frame, "Failures", row=2)
        self.lbl_error = self._make_summary_card(left_frame, "Errors", row=3)
        self.lbl_skipped = self._make_summary_card(left_frame, "Skipped", row=4)

        self.progress = ctk.CTkProgressBar(left_frame, orientation="horizontal", mode="indeterminate")
        self.progress.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        self.open_report_btn = ctk.CTkButton(left_frame, text="Open Report", fg_color="#4AECFF",
                                             state="disabled",text_color="black",hover=False,  command=self.open_report,font=("Segoe UI", 14, "bold"))
        self.open_report_btn.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        # Right Console
        right_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        self.console = ctk.CTkTextbox(right_frame, font=("Consolas", 11), wrap="word",state="disabled")
        self.console.pack(fill="both", expand=True, padx=10, pady=10)

        # Color tags
        self.console.tag_config("stdout", foreground="white")
        self.console.tag_config("stderr", foreground="red")
        self.console.tag_config("ok", foreground="#00ff00")
        self.console.tag_config("fail", foreground="red")
        self.console.tag_config("error", foreground="orange")
        self.console.tag_config("skip", foreground="cyan")
        self.console.tag_config("header", foreground="yellow")

        # Status bar
        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.status_label.pack(fill="x", side="bottom", padx=12, pady=6)

    # -------- Summary helper --------
    def _make_summary_card(self, parent, title, row):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=8)
        frame.grid_columnconfigure(1, weight=1)

        lbl_title = ctk.CTkLabel(frame, text=title, font=("Segoe UI", 12))
        lbl_title.grid(row=0, column=0, sticky="w", padx=8, pady=5)

        lbl_value = ctk.CTkLabel(frame, text="0", font=("Segoe UI", 20, "bold"))
        lbl_value.grid(row=0, column=1, sticky="e", padx=8, pady=5)

        return lbl_value

    # -------- Buttons --------
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def clear_console(self):
        self.console.configure(state="normal")
        # Clear the console output
        self.console.delete("1.0", "end")

        # Reset summary cards
        self.update_summary_cards(0, 0, 0, 0, 0)

        # Reset status bar
        self.status_label.configure(text="Ready")

        # Disable report button
        self.open_report_btn.configure(state="disabled")
        self.console.configure(state="disabled")


    # -------- Test Flow --------
    def start_test(self):
        if not self.folder_path.get():
            messagebox.showerror("Error", "Please select a test folder first!")
            return
        if not self.url_entry.get().strip():
            messagebox.showerror("Error", "Please enter the application URL!")
            return
    
        os.environ["APP_URL"] = self.url_entry.get().strip()

        self.clear_console()
        self.status_label.configure(text="Running tests...")
        self.start_btn.configure(state="disabled")
        self.open_report_btn.configure(state="disabled")

        self.progress.start()
        self.running = True

        threading.Thread(target=self.run_tests, daemon=True).start()
        #threading.Thread(target=self.run_tests_subprocess, daemon=True).start()


    def run_tests(self):
        try:
            sys.stdout = TextRedirector(self.console)
            sys.stderr = TextRedirector(self.console)

            loader = unittest.TestLoader()
            suite = loader.discover(self.folder_path.get())

            report_dir = os.path.join(self.folder_path.get(), "reports")
            os.makedirs(report_dir, exist_ok=True)

            print("\nRunning tests...\n" + "-" * 70 + "\n")
            suite_start = time.time()
            # single runner: console + HTML
            runner = ScreenshotTestRunner(
                output=report_dir,
                report_name="result",
                combine_reports=True,
                report_title="Automation Suite Report",
                descriptions="Execution report",
                verbosity=2
            )
            result = runner.run(suite)
            suite_end = time.time()
            total_duration = suite_end - suite_start
            # summary
            total = result.testsRun
            failures = len(result.failures)
            errors = len(result.errors)
            skipped = len(result.skipped) if hasattr(result, "skipped") else 0
            passed = total - failures - errors - skipped
            self.console.configure(state="normal")
            self.console.insert("end", f"\nTotal: {total}\n", "header")
            self.console.insert("end", f"Passed: {passed}\n", "ok")
            self.console.insert("end", f"Failures: {failures}\n", "fail")
            self.console.insert("end", f"Errors: {errors}\n", "error")
            self.console.insert("end", f"Skipped: {skipped}\n", "skip")
            self.console.insert("end", f"Total Duration: {total_duration:.2f}s\n", "header")
            self.console.configure(state="disabled")

            print("\nTest Complete...\n" + "-" * 70 + "\n")
            self.update_summary_cards(total, passed, failures, errors, skipped)
            self.status_label.configure(text="✅ Test Run Completed")
            self.open_report_btn.configure(state="normal")

        except Exception as e:
            self.console.insert("end", f"Error: {e}\n", "error")
            self.status_label.configure(text="❌ Test Run Failed")
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.start_btn.configure(state="normal")
            self.progress.stop()
            self.running = False




    def update_summary_cards(self, total, passed, failures, errors, skipped):
        self.lbl_total.configure(text=str(total))
        self.lbl_passed.configure(text=str(passed), text_color="#00ff00")
        self.lbl_fail.configure(text=str(failures), text_color="red")
        self.lbl_error.configure(text=str(errors), text_color="orange")
        self.lbl_skipped.configure(text=str(skipped), text_color="cyan")

    def open_report(self):
        if self.report_file and os.path.exists(self.report_file):
            webbrowser.open_new_tab(f"file:///{os.path.abspath(self.report_file)}")
        else:
            report_dir = os.path.join(self.folder_path.get(), "reports")
            html_reports = glob.glob(os.path.join(report_dir, "*.html"))
            if html_reports:
                latest = max(html_reports, key=os.path.getmtime)
                webbrowser.open_new_tab(f"file:///{os.path.abspath(latest)}")
            else:
                messagebox.showerror("Error", "Report not found!")

    def on_closing(self):
        if self.running:
            messagebox.showwarning("Warning", "Cannot close while tests are running!")
        else:
            self.destroy()


    


if __name__ == "__main__":
    app = TestRunnerApp()
    app.mainloop()
