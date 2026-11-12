import logging
import os
import sys
import threading
from pathlib import Path

import customtkinter as ctk

import config
from .dcl_parser import select_and_parse
from .errors import AppError, ArchiveError
from .job_locator import locate_dcl_folder, locate_job, validate_job_number
from .shortcut_manager import create_or_update_shortcut


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / relative


class JobArchiveApp:
    RED = "#c8102e"
    DARK = "#202124"

    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title(config.APP_NAME)
        icon = resource_path("assets/branding/qualitrol-q.ico")
        if icon.exists():
            self.root.iconbitmap(str(icon))
        self.root.geometry(config.WINDOW_SIZE)
        self.root.minsize(720, 520)
        self.root.configure(fg_color="#f8f9fa")
        self._configure_logging()
        self._build()
        self._centre()
        self.root.after(150, self.entry.focus_set)

    def _configure_logging(self):
        try:
            config.LOG_DIR.mkdir(parents=True, exist_ok=True)
            logging.basicConfig(filename=config.LOG_DIR / "app.log", level=logging.INFO,
                                format="%(asctime)s %(levelname)s %(message)s")
        except OSError:
            logging.basicConfig(level=logging.INFO)

    def _build(self):
        header = ctk.CTkFrame(self.root, height=130, corner_radius=0, fg_color="white")
        header.pack(fill="x")
        header.pack_propagate(False)
        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.pack(fill="both", expand=True, padx=40)
        ctk.CTkLabel(brand, text="QUALI", font=ctk.CTkFont("Segoe UI", 34, "bold"), text_color="#202124").pack(side="left")
        ctk.CTkLabel(brand, text="TROL", font=ctk.CTkFont("Segoe UI", 34, "bold"), text_color=self.RED).pack(side="left")
        ctk.CTkFrame(brand, width=2, height=45, fg_color="#8b8d91").pack(side="left", padx=28)
        ctk.CTkLabel(brand, text="Job Archive", font=ctk.CTkFont("Segoe UI", 29, "bold"), text_color=self.DARK).pack(side="left")
        ctk.CTkFrame(self.root, height=4, corner_radius=0, fg_color=self.RED).pack(fill="x")

        content = ctk.CTkFrame(self.root, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=75, pady=(45, 38))
        self.entry = ctk.CTkEntry(content, height=64, corner_radius=12, border_width=2,
                                  border_color="#c8cbd0", fg_color="white", text_color=self.DARK,
                                  placeholder_text="Enter job number", font=ctk.CTkFont("Segoe UI", 26, "bold"))
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", lambda _event: self.submit())
        self.button = ctk.CTkButton(content, height=62, corner_radius=12, fg_color=self.RED,
                                    hover_color="#a90d27", text="🔗  Create Shortcut",
                                    font=ctk.CTkFont("Segoe UI", 23, "bold"), command=self.submit)
        self.button.pack(fill="x", pady=(22, 0))
        self.result = ctk.CTkFrame(content, corner_radius=12, border_width=1)
        self.result_title = ctk.CTkLabel(self.result, anchor="w", font=ctk.CTkFont("Segoe UI", 20, "bold"))
        self.result_title.pack(fill="x", padx=26, pady=(20, 4))
        self.result_detail = ctk.CTkLabel(self.result, anchor="w", justify="left", wraplength=600,
                                          font=ctk.CTkFont("Segoe UI", 16, "bold"))
        self.result_detail.pack(fill="x", padx=26, pady=(0, 8))
        self.open_button = ctk.CTkButton(self.result, text="↗  Open archive", width=145, height=30,
                                         fg_color="transparent", hover_color="#e6f0fb", text_color="#0969b5",
                                         font=ctk.CTkFont("Segoe UI", 15, "bold"), command=self.open_archive)
        self.open_button.pack(anchor="w", padx=18, pady=(0, 16))

    def _centre(self):
        self.root.update_idletasks()
        width, height = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def submit(self):
        if str(self.button.cget("state")) == "disabled":
            return
        self.result.pack_forget()
        try:
            job_number = validate_job_number(self.entry.get())
        except ValueError as exc:
            self._show_error(str(exc))
            return
        self.button.configure(state="disabled", text="Processing...")
        self.entry.configure(state="disabled")
        threading.Thread(target=self._process, args=(job_number,), daemon=True).start()

    def _process(self, job_number: str):
        try:
            job = locate_job(config.NETWORK_ROOT, job_number)
            dcl = select_and_parse(locate_dcl_folder(job), job_number)
            outcome = create_or_update_shortcut(
                job, config.ARCHIVE_DIR, job_number, dcl.customer_name, config.CREATE_JOB_SUBFOLDER
            )
            titles = {"created": "✓  Shortcut created", "updated": "✓  Shortcut updated", "exists": "✓  Shortcut already exists"}
            self.root.after(0, self._show_success, titles[outcome.status], f"{job_number} - {dcl.customer_name}")
        except AppError as exc:
            logging.exception("Job %s failed", job_number)
            self.root.after(0, self._show_error, str(exc))
        except Exception:
            logging.exception("Unexpected failure for job %s", job_number)
            self.root.after(0, self._show_error, "Something went wrong. Please try again.")
        finally:
            self.root.after(0, self._finish)

    def _show_success(self, title: str, detail: str):
        self.result.configure(fg_color="#f1f8f0", border_color="#cde3c7")
        self.result_title.configure(text=title, text_color="#174c2d")
        self.result_detail.configure(text="📁  " + detail, text_color=self.DARK)
        self.open_button.pack(anchor="w", padx=18, pady=(0, 16))
        self.result.pack(fill="x", pady=(36, 0))

    def _show_error(self, message: str):
        self.result.configure(fg_color="#fff3f3", border_color="#efc4c7")
        self.result_title.configure(text="!  Unable to create shortcut", text_color="#9e1b32")
        self.result_detail.configure(text=message, text_color="#5b2029")
        self.open_button.pack_forget()
        self.result.pack(fill="x", pady=(36, 0))

    def _finish(self):
        self.button.configure(state="normal", text="🔗  Create Shortcut")
        self.entry.configure(state="normal")
        self.entry.focus_set()

    def open_archive(self):
        try:
            Path(config.ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)
            os.startfile(config.ARCHIVE_DIR)
        except OSError:
            self._show_error("Unable to open archive folder.")

    def run(self):
        self.root.mainloop()

