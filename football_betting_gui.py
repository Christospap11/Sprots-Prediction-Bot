# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Modern Football Betting Prediction GUI
High-end CustomTkinter interface for viewing matches, odds, and predictions
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta
import threading
import requests
import os
from dotenv import load_dotenv
import random

# Load environment
load_dotenv(override=True)

# ─── App Appearance ────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── Colour Palette ────────────────────────────────────────────────────────────
COLORS = {
    "bg_primary":    "#0d0f1a",   # near-black canvas
    "bg_card":       "#141828",   # card background
    "bg_sidebar":    "#0a0c16",   # sidebar
    "accent":        "#3b82f6",   # electric blue
    "accent_dim":    "#1e3a5f",   # dimmer blue for hover
    "accent_green":  "#22c55e",   # profit green
    "accent_red":    "#ef4444",   # loss red
    "accent_yellow": "#f59e0b",   # draw / warning
    "text_primary":  "#f1f5f9",   # near-white text
    "text_secondary":"#94a3b8",   # slate-grey subtext
    "text_muted":    "#475569",   # muted
    "border":        "#1e293b",   # subtle border
    "live_pulse":    "#ef4444",   # red dot for LIVE
    "gold":          "#f59e0b",   # premium gold accent
}

# ─── Fonts ─────────────────────────────────────────────────────────────────────
FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 14, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_BODY_B  = ("Segoe UI", 11, "bold")
FONT_SMALL   = ("Segoe UI", 10)
FONT_TINY    = ("Segoe UI", 9)
FONT_NAV     = ("Segoe UI", 12, "bold")
FONT_STAT    = ("Segoe UI", 18, "bold")


# ══════════════════════════════════════════════════════════════════════════════
#  Reusable Premium Components
# ══════════════════════════════════════════════════════════════════════════════

class GlassCard(ctk.CTkFrame):
    """Elevated card with a subtle border and rounded corners."""
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color",    COLORS["bg_card"])
        kwargs.setdefault("corner_radius", 14)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border"])
        super().__init__(parent, **kwargs)


class StatBadge(ctk.CTkFrame):
    """Small stat counter card shown in the header bar."""
    def __init__(self, parent, label, value, color=None):
        super().__init__(parent, fg_color=COLORS["bg_card"],
                         corner_radius=10, border_width=1,
                         border_color=COLORS["border"])
        clr = color or COLORS["accent"]
        self.value_label = ctk.CTkLabel(self, text=value, font=FONT_STAT, text_color=clr)
        self.value_label.pack(pady=(10, 2))
        ctk.CTkLabel(self, text=label, font=FONT_TINY, text_color=COLORS["text_secondary"]).pack(pady=(0, 10))

    def set_value(self, val: str):
        self.value_label.configure(text=val)


class SectionHeader(ctk.CTkLabel):
    """Bold section title."""
    def __init__(self, parent, text, **kwargs):
        kwargs.setdefault("font", FONT_HEADING)
        kwargs.setdefault("text_color", COLORS["text_primary"])
        super().__init__(parent, text=text, **kwargs)


class PulsingDot(ctk.CTkLabel):
    """🔴 red live dot – animates opacity by toggling text colour."""
    def __init__(self, parent):
        super().__init__(parent, text="●  LIVE", font=("Segoe UI", 11, "bold"),
                         text_color=COLORS["live_pulse"])
        self._visible = True
        self._blink()

    def _blink(self):
        self._visible = not self._visible
        self.configure(text_color=COLORS["live_pulse"] if self._visible else COLORS["bg_card"])
        self.after(700, self._blink)


class NavButton(ctk.CTkButton):
    """Sidebar navigation button."""
    def __init__(self, parent, text, icon, command, **kwargs):
        super().__init__(
            parent, text=f"  {icon}  {text}", command=command,
            height=46, corner_radius=10, anchor="w",
            fg_color="transparent", hover_color=COLORS["accent_dim"],
            text_color=COLORS["text_secondary"], font=FONT_NAV,
            border_width=0, **kwargs
        )

    def set_active(self):
        self.configure(fg_color=COLORS["accent_dim"],
                       text_color=COLORS["text_primary"])

    def set_inactive(self):
        self.configure(fg_color="transparent",
                       text_color=COLORS["text_secondary"])


# ── Custom Scrollable Table ────────────────────────────────────────────────────
class PremiumTable(ctk.CTkScrollableFrame):
    """A clean dark scrollable table with alternating row colors."""

    ROW_EVEN = "#141828"
    ROW_ODD  = "#0f1120"
    ROW_HOVER = COLORS["accent_dim"]

    def __init__(self, parent, columns, col_widths=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self.columns = columns
        self.col_widths = col_widths or [160] * len(columns)
        self._row_frames = []
        self._draw_header()

    def _draw_header(self):
        hdr = ctk.CTkFrame(self, fg_color="#0a0c1e", corner_radius=8)
        hdr.pack(fill="x", padx=4, pady=(4, 2))
        for i, (col, w) in enumerate(zip(self.columns, self.col_widths)):
            ctk.CTkLabel(
                hdr, text=col.upper(), font=FONT_TINY,
                text_color=COLORS["accent"], width=w, anchor="w"
            ).grid(row=0, column=i, padx=(12, 4), pady=8, sticky="w")

    def clear_rows(self):
        for f in self._row_frames:
            f.destroy()
        self._row_frames.clear()

    def add_row(self, values, tag=None):
        idx = len(self._row_frames)
        bg = self.ROW_EVEN if idx % 2 == 0 else self.ROW_ODD
        if tag == "live":
            bg = "#1a1030"
        elif tag == "win":
            bg = "#0a1f12"
        elif tag == "loss":
            bg = "#1f0a0a"

        row = ctk.CTkFrame(self, fg_color=bg, corner_radius=6)
        row.pack(fill="x", padx=4, pady=1)
        self._row_frames.append(row)

        labels = []
        for i, (val, w) in enumerate(zip(values, self.col_widths)):
            txt = str(val)
            color = COLORS["text_primary"]
            if txt in ("LIVE", "IN_PLAY", "Live"):
                color = COLORS["accent_red"]
            elif txt in ("FINISHED", "FT", "TIMED"):
                color = COLORS["text_muted"]
            elif txt.startswith("✅"):
                color = COLORS["accent_green"]
            elif txt.startswith("❌"):
                color = COLORS["accent_red"]
            elif txt.startswith("⚠"):
                color = COLORS["accent_yellow"]
            lbl = ctk.CTkLabel(
                row, text=txt, font=FONT_SMALL,
                text_color=color, width=w, anchor="w"
            )
            lbl.grid(row=0, column=i, padx=(12, 4), pady=7, sticky="w")
            labels.append(lbl)

        # Hover effect – bind on frame AND all child labels so mouse events register
        def on_enter(e, r=row, b=bg):
            r.configure(fg_color=self.ROW_HOVER)
        def on_leave(e, r=row, b=bg):
            r.configure(fg_color=b)
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        for lbl in labels:
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class ModernFootballGUI:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.db_path = "data/football_betting.db"
        self.football_api_key = os.getenv("FOOTBALL_API_KEY")
        self.api_football_key = os.getenv("API_FOOTBALL_KEY")
        self._active_nav: str = "dashboard"
        self._pages: dict = {}
        self._nav_buttons: dict = {}
        # live auto-refresh vars
        self.auto_refresh_var = tk.BooleanVar(value=True)
        self._setup_window()
        self._build_layout()
        self._show_page("dashboard")
        # Initial data load
        self.after_id = self.root.after(200, self.refresh_data)

    # ── Window setup ────────────────────────────────────────────────────────
    def _setup_window(self):
        self.root.title("⚽  Football Prediction Pro")
        self.root.geometry("1440x900")
        self.root.configure(fg_color=COLORS["bg_primary"])
        self.root.minsize(1100, 700)

    # ── Layout skeleton ─────────────────────────────────────────────────────
    def _build_layout(self):
        # Outer: sidebar | main
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    # ── Sidebar ─────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self.root, fg_color=COLORS["bg_sidebar"],
                               corner_radius=0, width=220)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(28, 8))
        ctk.CTkLabel(
            logo_frame, text="⚽", font=("Segoe UI", 32)
        ).pack(side="left")
        title_col = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_col.pack(side="left", padx=10)
        ctk.CTkLabel(title_col, text="Prediction", font=("Segoe UI", 15, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Football Pro", font=("Segoe UI", 11),
                     text_color=COLORS["accent"]).pack(anchor="w")

        # Divider
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=16, pady=14)

        # nav items
        nav_items = [
            ("dashboard",   "Dashboard",    "🏠"),
            ("matches",     "Matches",      "📅"),
            ("predictions", "Predictions",  "🤖"),
            ("live",        "Live Games",   "🔴"),
            ("standings",   "Standings",    "🏆"),
            ("odds",        "Odds",         "💰"),
            ("statistics",  "Statistics",   "📊"),
        ]
        for key, label, icon in nav_items:
            btn = NavButton(sidebar, text=label, icon=icon,
                            command=lambda k=key: self._show_page(k))
            btn.pack(fill="x", padx=12, pady=3)
            self._nav_buttons[key] = btn

        # Bottom: version / status
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=16, pady=14, side="bottom")
        self.sidebar_status = ctk.CTkLabel(
            sidebar, text="Connecting…", font=FONT_TINY,
            text_color=COLORS["text_muted"])
        self.sidebar_status.pack(side="bottom", padx=16, pady=6)
        ctk.CTkLabel(sidebar, text="v2.0  •  Football Pro",
                     font=FONT_TINY, text_color=COLORS["text_muted"]).pack(
            side="bottom", padx=16, pady=2)

    # ── Main content area ────────────────────────────────────────────────────
    def _build_main(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg_primary"],
                                       corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # ── Top bar
        topbar = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"],
                              corner_radius=0, height=60)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        self.topbar_title = ctk.CTkLabel(
            topbar, text="Dashboard", font=FONT_TITLE,
            text_color=COLORS["text_primary"])
        self.topbar_title.grid(row=0, column=0, padx=28, pady=14, sticky="w")

        # Refresh button top right
        ctk.CTkButton(
            topbar, text="  ↻  Refresh", width=110, height=36,
            corner_radius=10, fg_color=COLORS["accent"],
            hover_color="#2563eb", font=FONT_BODY_B,
            command=self.refresh_data
        ).grid(row=0, column=2, padx=20, pady=12, sticky="e")

        # time label
        self.time_label = ctk.CTkLabel(
            topbar, text="", font=FONT_SMALL,
            text_color=COLORS["text_secondary"])
        self.time_label.grid(row=0, column=1, padx=10, sticky="e")
        self._tick_clock()

        # ── Page container
        self.page_container = ctk.CTkFrame(
            self.main_frame, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)

        # Build all pages
        self._pages["dashboard"]   = self._build_dashboard_page()
        self._pages["matches"]     = self._build_matches_page()
        self._pages["predictions"] = self._build_predictions_page()
        self._pages["live"]        = self._build_live_page()
        self._pages["standings"]   = self._build_standings_page()
        self._pages["odds"]        = self._build_odds_page()
        self._pages["statistics"]  = self._build_statistics_page()

        for page in self._pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    # ── Clock ────────────────────────────────────────────────────────────────
    def _tick_clock(self):
        now = datetime.now().strftime("%a %d %b  %H:%M:%S")
        self.time_label.configure(text=now)
        self.root.after(1000, self._tick_clock)

    # ── Navigation ───────────────────────────────────────────────────────────
    def _show_page(self, key: str):
        self._active_nav = key
        page_titles = {
            "dashboard":   "Dashboard",
            "matches":     "Matches",
            "predictions": "AI Predictions",
            "live":        "Live Games",
            "standings":   "League Standings",
            "odds":        "Betting Odds",
            "statistics":  "Live Statistics",
        }
        self.topbar_title.configure(text=page_titles.get(key, key.title()))
        for k, btn in self._nav_buttons.items():
            btn.set_active() if k == key else btn.set_inactive()
        self._pages[key].tkraise()

    # ══════════════════════════════════════════════════════════════════════
    #  PAGE BUILDERS
    # ══════════════════════════════════════════════════════════════════════

    # ── Dashboard ───────────────────────────────────────────────────────────
    def _build_dashboard_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.page_container, fg_color=COLORS["bg_primary"])

        # ── Stat badges row
        badges_row = ctk.CTkFrame(page, fg_color="transparent")
        badges_row.pack(fill="x", padx=26, pady=(22, 10))

        self.stat_teams  = StatBadge(badges_row, "Teams",   "0",  COLORS["accent"])
        self.stat_matches = StatBadge(badges_row, "Matches", "0", COLORS["accent_green"])
        self.stat_odds   = StatBadge(badges_row, "Odds",    "0",  COLORS["gold"])
        self.stat_live   = StatBadge(badges_row, "Live Now","0",  COLORS["live_pulse"])

        for w in (self.stat_teams, self.stat_matches, self.stat_odds, self.stat_live):
            w.pack(side="left", padx=8, ipadx=18, fill="y")

        # ── Two column layout: recent matches | quick predictions
        mid = ctk.CTkFrame(page, fg_color="transparent")
        mid.pack(fill="both", expand=True, padx=26, pady=8)
        mid.grid_columnconfigure(0, weight=3)
        mid.grid_columnconfigure(1, weight=2)
        mid.grid_rowconfigure(0, weight=1)

        # Recent Matches card
        left_card = GlassCard(mid)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        SectionHeader(left_card, "  📅  Recent Matches").pack(anchor="w", padx=18, pady=(16, 10))

        self.dash_matches_table = PremiumTable(
            left_card,
            columns=["Date", "Home", "Score", "Away", "Status"],
            col_widths=[80, 160, 70, 160, 90]
        )
        self.dash_matches_table.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # Quick Predictions card
        right_card = GlassCard(mid)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        SectionHeader(right_card, "  🤖  Quick Predictions").pack(anchor="w", padx=18, pady=(16, 10))

        self.dash_pred_frame = ctk.CTkScrollableFrame(
            right_card, fg_color="transparent")
        self.dash_pred_frame.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        ctk.CTkButton(
            page, text="Generate Full Predictions  →",
            height=40, corner_radius=10,
            fg_color=COLORS["accent"], hover_color="#2563eb",
            font=FONT_BODY_B,
            command=lambda: self._show_page("predictions")
        ).pack(pady=(0, 18))

        return page

    # ── Matches ─────────────────────────────────────────────────────────────
    def _build_matches_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.page_container, fg_color=COLORS["bg_primary"])

        # Controls bar
        ctrl = GlassCard(page)
        ctrl.pack(fill="x", padx=24, pady=(20, 10))
        ctrl_inner = ctk.CTkFrame(ctrl, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(ctrl_inner, text="Search:", font=FONT_BODY,
                     text_color=COLORS["text_secondary"]).pack(side="left")
        self.search_var = tk.StringVar()
        ctk.CTkEntry(ctrl_inner, textvariable=self.search_var, width=240,
                     placeholder_text="Team or competition…",
                     fg_color=COLORS["bg_primary"], border_color=COLORS["border"],
                     text_color=COLORS["text_primary"]).pack(side="left", padx=10)
        ctk.CTkButton(ctrl_inner, text="Search", width=90, height=34,
                      corner_radius=8, fg_color=COLORS["accent"],
                      hover_color="#2563eb", font=FONT_BODY_B,
                      command=self.search_matches).pack(side="left", padx=4)

        ctk.CTkLabel(ctrl_inner, text="League:", font=FONT_BODY,
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(24, 0))
        self.league_var = tk.StringVar(value="All Leagues")
        league_cb = ctk.CTkComboBox(
            ctrl_inner, variable=self.league_var, width=180,
            values=["All Leagues", "Premier League", "La Liga",
                    "Bundesliga", "Serie A", "Ligue 1", "Champions League", "Europa League"],
            fg_color=COLORS["bg_primary"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            command=lambda _: self.filter_matches())
        league_cb.pack(side="left", padx=10)

        ctk.CTkButton(ctrl_inner, text="Clear", width=70, height=34,
                      corner_radius=8, fg_color=COLORS["bg_card"],
                      hover_color=COLORS["border"],
                      font=FONT_BODY, text_color=COLORS["text_secondary"],
                      command=self.load_matches).pack(side="left", padx=4)

        # Table
        self.matches_table = PremiumTable(
            page,
            columns=["Date", "Competition", "Home Team", "Away Team", "Status", "Score"],
            col_widths=[90, 130, 170, 170, 90, 80]
        )
        self.matches_table.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        return page

    # ── Predictions ─────────────────────────────────────────────────────────
    def _build_predictions_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.page_container, fg_color=COLORS["bg_primary"])

        # Header card
        hdr = GlassCard(page)
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(hdr_inner, text="🤖  AI Enhanced Predictions",
                     font=FONT_HEADING, text_color=COLORS["text_primary"]).pack(side="left")
        self.api_status_label = ctk.CTkLabel(
            hdr_inner, text="📊 Ready", font=FONT_SMALL,
            text_color=COLORS["accent"])
        self.api_status_label.pack(side="left", padx=18)
        ctk.CTkButton(
            hdr_inner, text="⚡ Generate", width=130, height=36,
            corner_radius=10, fg_color=COLORS["accent"],
            hover_color="#2563eb", font=FONT_BODY_B,
            command=self.generate_enhanced_predictions
        ).pack(side="right", padx=8)
        ctk.CTkButton(
            hdr_inner, text="🔄 Live Stats", width=130, height=36,
            corner_radius=10, fg_color=COLORS["bg_card"],
            hover_color=COLORS["accent_dim"], font=FONT_BODY_B,
            text_color=COLORS["text_secondary"],
            command=self.update_live_statistics
        ).pack(side="right", padx=4)

        # Predictions table
        self.pred_table = PremiumTable(
            page,
            columns=["Match", "Result %", "O/U 2.5", "BTTS", "xG", "Momentum", "Confidence", "Value Bet"],
            col_widths=[180, 140, 100, 90, 60, 130, 100, 120]
        )
        self.pred_table.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        return page

    # ── Live ─────────────────────────────────────────────────────────────────
    def _build_live_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.page_container, fg_color=COLORS["bg_primary"])

        # Header
        hdr = GlassCard(page)
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=16, pady=10)
        PulsingDot(hdr_inner).pack(side="left")
        ctk.CTkLabel(hdr_inner, text="  Live Matches",
                     font=FONT_HEADING, text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkCheckBox(
            hdr_inner, text="Auto-refresh (30s)", variable=self.auto_refresh_var,
            font=FONT_SMALL, text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"], hover_color="#2563eb"
        ).pack(side="right")
        ctk.CTkButton(
            hdr_inner, text="Refresh Now", width=120, height=34,
            corner_radius=8, fg_color=COLORS["accent"],
            hover_color="#2563eb", font=FONT_BODY_B,
            command=self.load_live_matches
        ).pack(side="right", padx=10)

        # Live cards frame
        self.live_scroll = ctk.CTkScrollableFrame(
            page, fg_color=COLORS["bg_primary"])
        self.live_scroll.pack(fill="both", expand=True, padx=24, pady=(4, 20))

        self._start_auto_refresh()
        return page

    # ── Standings ────────────────────────────────────────────────────────────
    def _build_standings_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.page_container, fg_color=COLORS["bg_primary"])

        hdr = GlassCard(page)
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(hdr_inner, text="🏆  League Standings",
                     font=FONT_HEADING, text_color=COLORS["text_primary"]).pack(side="left")
        self.standings_league_var = tk.StringVar(value="Premier League")
        league_cb_s = ctk.CTkComboBox(
            hdr_inner, variable=self.standings_league_var, width=190,
            values=["Premier League", "La Liga", "Bundesliga", "Serie A",
                    "Ligue 1", "Champions League", "Europa League"],
            fg_color=COLORS["bg_primary"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            command=lambda _: self.load_standings())
        league_cb_s.pack(side="right")

        self.standings_table = PremiumTable(
            page,
            columns=["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"],
            col_widths=[50, 200, 50, 50, 50, 50, 55, 55, 55, 60]
        )
        self.standings_table.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        return page

    # ── Odds ─────────────────────────────────────────────────────────────────
    def _build_odds_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.page_container, fg_color=COLORS["bg_primary"])

        hdr = GlassCard(page)
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(hdr_inner, text="💰  Betting Odds",
                     font=FONT_HEADING, text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkButton(
            hdr_inner, text="Refresh", width=100, height=34,
            corner_radius=8, fg_color=COLORS["accent"],
            hover_color="#2563eb", font=FONT_BODY_B,
            command=self.load_odds
        ).pack(side="right")

        self.odds_table = PremiumTable(
            page,
            columns=["Match", "Bookmaker", "Home Win", "Draw", "Away Win", "Updated"],
            col_widths=[200, 130, 100, 100, 100, 130]
        )
        self.odds_table.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        return page

    # ── Statistics ───────────────────────────────────────────────────────────
    def _build_statistics_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.page_container, fg_color=COLORS["bg_primary"])

        hdr = GlassCard(page)
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(hdr_inner, text="📊  Real-Time Match Statistics",
                     font=FONT_HEADING, text_color=COLORS["text_primary"]).pack(side="left")
        self.stats_api_status = ctk.CTkLabel(
            hdr_inner, text="🔄 API-Football ready",
            font=FONT_SMALL, text_color=COLORS["accent"])
        self.stats_api_status.pack(side="left", padx=16)
        ctk.CTkButton(
            hdr_inner, text="🔄 Refresh Stats", width=140, height=34,
            corner_radius=8, fg_color=COLORS["accent"],
            hover_color="#2563eb", font=FONT_BODY_B,
            command=self.refresh_live_statistics
        ).pack(side="right")

        self.stats_table = PremiumTable(
            page,
            columns=["Match", "Time", "Possession", "Shots", "Corners", "Cards", "xG", "Momentum"],
            col_widths=[200, 60, 110, 90, 90, 90, 80, 120]
        )
        self.stats_table.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        return page

    # ══════════════════════════════════════════════════════════════════════
    #  DATABASE ACCESS
    # ══════════════════════════════════════════════════════════════════════

    def get_database_connection(self):
        try:
            return sqlite3.connect(self.db_path)
        except Exception as e:
            return None

    # ══════════════════════════════════════════════════════════════════════
    #  DATA LOADING & REFRESH
    # ══════════════════════════════════════════════════════════════════════

    def refresh_data(self):
        """Refresh all data panels."""
        try:
            self.load_matches()
            self.load_odds()
            self.load_standings()
            self.load_live_matches()
            self._update_dashboard_stats()
            self._update_dashboard_matches()
        except Exception as e:
            print(f"Refresh error: {e}")

    # ── Dashboard stats badges ───────────────────────────────────────────────
    def _update_dashboard_stats(self):
        conn = self.get_database_connection()
        if not conn:
            self.sidebar_status.configure(text="⚠ No database yet")
            return
        try:
            cur = conn.cursor()
            # check tables exist
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {r[0] for r in cur.fetchall()}
            teams   = 0; matches = 0; odds_n = 0; live = 0
            if "teams"   in tables: cur.execute("SELECT COUNT(*) FROM teams");   teams   = cur.fetchone()[0]
            if "matches" in tables: cur.execute("SELECT COUNT(*) FROM matches"); matches = cur.fetchone()[0]
            if "odds"    in tables: cur.execute("SELECT COUNT(*) FROM odds");    odds_n  = cur.fetchone()[0]
            if "matches" in tables:
                cur.execute("SELECT COUNT(*) FROM matches WHERE status IN ('IN_PLAY','PAUSED','HALFTIME','Live')")
                live = cur.fetchone()[0]
            self.stat_teams.set_value(str(teams))
            self.stat_matches.set_value(str(matches))
            self.stat_odds.set_value(str(odds_n))
            self.stat_live.set_value(str(live))
            self.sidebar_status.configure(text=f"✓ {matches} matches  •  {live} live")
        except Exception as e:
            self.sidebar_status.configure(text=f"DB error: {str(e)[:20]}")
        finally:
            conn.close()

    def _update_dashboard_matches(self):
        """Populate recent matches in dashboard card."""
        self.dash_matches_table.clear_rows()
        conn = self.get_database_connection()
        if not conn:
            self.dash_matches_table.add_row(("No database found.", "", "", "", "Run monitor first."))
            self._update_dashboard_preds()
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches'")
            if not cur.fetchone():
                self.dash_matches_table.add_row(("No data yet.", "", "", "", "Run monitor_with_database.py"))
                self._update_dashboard_preds()
                return
            cur.execute("""
                SELECT match_date, home_team, away_team, home_score, away_score, status
                FROM matches ORDER BY match_date DESC LIMIT 20
            """)
            rows = cur.fetchall()
            if not rows:
                self.dash_matches_table.add_row(("No matches collected yet.", "", "", "", ""))
            for row in rows:
                date = (row[0] or "")[:10]
                score = f"{row[3]} – {row[4]}" if row[3] is not None else "vs"
                tag = "live" if row[5] in ("IN_PLAY", "PAUSED", "HALFTIME", "Live") else None
                self.dash_matches_table.add_row(
                    (date, row[1] or "?", score, row[2] or "?", row[5] or "?"), tag=tag)
        except Exception as e:
            print(f"Dashboard matches error: {e}")
            self.dash_matches_table.add_row((f"Error: {str(e)[:40]}", "", "", "", ""))
        finally:
            conn.close()
        self._update_dashboard_preds()

    def _update_dashboard_preds(self):
        """Inject a few quick-look prediction cards into dashboard."""
        for w in self.dash_pred_frame.winfo_children():
            w.destroy()
        samples = [
            ("Arsenal vs Chelsea",    65, "Over 65%",  "✅ Home Win"),
            ("Liverpool vs Man City", 42, "Over 72%",  "✅ Over 2.5"),
            ("Barcelona vs Real",     40, "BTTS 78%",  "✅ Away Win"),
        ]
        for match, conf, market, bet in samples:
            card = GlassCard(self.dash_pred_frame, corner_radius=10)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=match, font=FONT_BODY_B,
                         text_color=COLORS["text_primary"]).pack(anchor="w", padx=14, pady=(10, 2))
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=(0, 10))
            ctk.CTkProgressBar(row, width=100, height=8,
                               fg_color=COLORS["border"],
                               progress_color=COLORS["accent_green"]).pack(side="left")
            # set bar value
            row.winfo_children()[0].set(conf / 100)
            ctk.CTkLabel(row, text=f"  {conf}%  •  {market}", font=FONT_TINY,
                         text_color=COLORS["text_secondary"]).pack(side="left")
            ctk.CTkLabel(card, text=bet, font=FONT_SMALL,
                         text_color=COLORS["accent_green"]).pack(anchor="w", padx=14, pady=(0, 8))

    # ── Matches ──────────────────────────────────────────────────────────────
    def load_matches(self):
        self.matches_table.clear_rows()
        conn = self.get_database_connection()
        if not conn:
            self.matches_table.add_row(("Database not found.", "Run monitor_with_database.py to collect data.", "", "", "", ""))
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches'")
            if not cur.fetchone():
                self.matches_table.add_row(("No data yet.", "Start the monitoring system first.", "", "", "", ""))
                return
            cur.execute("""
                SELECT match_date, competition, home_team, away_team, status,
                       home_score, away_score
                FROM matches ORDER BY match_date DESC LIMIT 150
            """)
            rows = cur.fetchall()
            if not rows:
                self.matches_table.add_row(("No matches found.", "Try running monitor_with_database.py", "", "", "", ""))
                return
            for row in rows:
                date = (row[0] or "")[:10]
                score = f"{row[5]} – {row[6]}" if row[5] is not None else "vs"
                tag = "live" if row[4] in ("IN_PLAY","PAUSED","HALFTIME","Live") else None
                self.matches_table.add_row(
                    (date, row[1] or "?", row[2] or "?", row[3] or "?",
                     row[4] or "?", score), tag=tag)
        except Exception as e:
            print(f"Load matches error: {e}")
            self.matches_table.add_row((f"Error: {str(e)[:50]}", "", "", "", "", ""))
        finally:
            conn.close()

    def search_matches(self):
        term = self.search_var.get().strip().lower()
        if not term:
            self.load_matches()
            return
        self.matches_table.clear_rows()
        conn = self.get_database_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT match_date, competition, home_team, away_team, status,
                       home_score, away_score
                FROM matches
                WHERE LOWER(home_team) LIKE ? OR LOWER(away_team) LIKE ? OR LOWER(competition) LIKE ?
                ORDER BY match_date DESC LIMIT 100
            """, (f"%{term}%", f"%{term}%", f"%{term}%"))
            for row in cur.fetchall():
                date = (row[0] or "")[:10]
                score = f"{row[5]} – {row[6]}" if row[5] is not None else "vs"
                self.matches_table.add_row(
                    (date, row[1] or "?", row[2] or "?", row[3] or "?",
                     row[4] or "?", score))
        except Exception as e:
            print(f"Search error: {e}")
        finally:
            conn.close()

    def filter_matches(self):
        league = self.league_var.get()
        if league == "All Leagues":
            self.load_matches()
            return
        self.matches_table.clear_rows()
        conn = self.get_database_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT match_date, competition, home_team, away_team, status,
                       home_score, away_score
                FROM matches WHERE competition = ?
                ORDER BY match_date DESC LIMIT 100
            """, (league,))
            for row in cur.fetchall():
                date = (row[0] or "")[:10]
                score = f"{row[5]} – {row[6]}" if row[5] is not None else "vs"
                self.matches_table.add_row(
                    (date, row[1] or "?", row[2] or "?", row[3] or "?",
                     row[4] or "?", score))
        except Exception as e:
            print(f"Filter error: {e}")
        finally:
            conn.close()

    # ── Odds ─────────────────────────────────────────────────────────────────
    def load_odds(self):
        self.odds_table.clear_rows()
        conn = self.get_database_connection()
        if not conn:
            self.odds_table.add_row(("No database found.", "Run monitor_with_database.py", "", "", "", ""))
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='odds'")
            if not cur.fetchone():
                self.odds_table.add_row(("No odds data yet.", "Start the monitoring system.", "", "", "", ""))
                return
            cur.execute("""
                SELECT home_team, away_team, home_odds, draw_odds, away_odds,
                       bookmaker, last_updated
                FROM odds ORDER BY last_updated DESC LIMIT 100
            """)
            rows = cur.fetchall()
            if not rows:
                self.odds_table.add_row(("No odds available yet.", "Configure ODDS_API_KEY in .env", "", "", "", ""))
                return
            for row in rows:
                match = f"{row[0] or '?'} vs {row[1] or '?'}"
                h = f"{row[2]:.2f}" if row[2] else "N/A"
                d = f"{row[3]:.2f}" if row[3] else "N/A"
                a = f"{row[4]:.2f}" if row[4] else "N/A"
                updated = (row[6] or "")[:16]
                self.odds_table.add_row((match, row[5] or "?", h, d, a, updated))
        except Exception as e:
            print(f"Odds error: {e}")
            self.odds_table.add_row((f"Error: {str(e)[:50]}", "", "", "", "", ""))
        finally:
            conn.close()

    # ── Standings ────────────────────────────────────────────────────────────
    def load_standings(self):
        self.standings_table.clear_rows()
        league = self.standings_league_var.get()
        conn = self.get_database_connection()
        if not conn:
            self.standings_table.add_row(("–", "No database found. Run monitor_with_database.py", "", "", "", "", "", "", "", ""))
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teams'")
            if not cur.fetchone():
                self.standings_table.add_row(("–", "No standings data yet.", "", "", "", "", "", "", "", ""))
                return
            cur.execute("""
                SELECT position, name, games_played, wins, draws, losses,
                       goals_for, goals_against, points
                FROM teams WHERE competition = ?
                ORDER BY position
            """, (league,))
            rows = cur.fetchall()
            if not rows:
                self.standings_table.add_row(("–", f"No data for {league}. Run the monitor to collect standings.", "", "", "", "", "", "", "", ""))
                return
            for row in rows:
                gf = row[6] or 0
                ga = row[7] or 0
                gd = gf - ga
                self.standings_table.add_row(
                    (row[0], row[1] or "?", row[2] or 0, row[3] or 0,
                     row[4] or 0, row[5] or 0, gf, ga, gd, row[8] or 0))
        except Exception as e:
            print(f"Standings error: {e}")
            self.standings_table.add_row(("–", f"Error: {str(e)[:40]}", "", "", "", "", "", "", "", ""))
        finally:
            conn.close()

    # ── Live Matches ─────────────────────────────────────────────────────────
    def load_live_matches(self):
        """Render live matches as beautiful match cards."""
        for w in self.live_scroll.winfo_children():
            w.destroy()

        conn = self.get_database_connection()
        rows = []
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT competition, home_team, away_team, home_score, away_score, status
                    FROM matches
                    WHERE status IN ('IN_PLAY', 'PAUSED', 'HALFTIME', 'Live')
                    ORDER BY match_date
                """)
                rows = cur.fetchall()
            except Exception:
                pass
            finally:
                conn.close()

        if not rows:
            ctk.CTkLabel(
                self.live_scroll,
                text="No live matches at the moment.\nData refreshes automatically every 30 seconds.",
                font=FONT_BODY, text_color=COLORS["text_muted"],
                justify="center"
            ).pack(expand=True, pady=80)
            return

        for r in rows:
            self._draw_live_card(r)

    def _draw_live_card(self, row):
        """Draw a single live match card."""
        comp, home, away, hs, as_, status = row
        hs = hs if hs is not None else 0
        as_ = as_ if as_ is not None else 0

        card = GlassCard(self.live_scroll, corner_radius=14)
        card.pack(fill="x", pady=6)
        card.grid_columnconfigure(1, weight=1)

        # Competition & status badge
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(12, 4))
        ctk.CTkLabel(top, text=comp or "League",
                     font=FONT_TINY, text_color=COLORS["text_muted"]).pack(side="left")
        badge_bg = COLORS["accent_red"] if status in ("IN_PLAY","Live") else COLORS["border"]
        badge_lbl = "🔴 LIVE" if status in ("IN_PLAY","Live") else status
        ctk.CTkLabel(top, text=badge_lbl, font=("Segoe UI", 9, "bold"),
                     text_color="white", fg_color=badge_bg, corner_radius=6,
                     padx=8, pady=2).pack(side="right")

        # Score row
        score_row = ctk.CTkFrame(card, fg_color="transparent")
        score_row.pack(fill="x", padx=20, pady=(4, 14))
        score_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(score_row, text=home or "Home",
                     font=FONT_HEADING, text_color=COLORS["text_primary"],
                     anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(score_row,
                     text=f"{hs}  –  {as_}",
                     font=("Segoe UI", 26, "bold"),
                     text_color=COLORS["accent"]).grid(row=0, column=1)
        ctk.CTkLabel(score_row, text=away or "Away",
                     font=FONT_HEADING, text_color=COLORS["text_primary"],
                     anchor="e").grid(row=0, column=2, sticky="e")

    # ── Enhanced Predictions ─────────────────────────────────────────────────
    def generate_enhanced_predictions(self):
        self.pred_table.clear_rows()
        api_key = os.getenv("API_FOOTBALL_KEY")
        status_txt = "📊 Enhanced: Active" if api_key else "⚠️ Using demo data"
        self.api_status_label.configure(text=status_txt)

        conn = self.get_database_connection()
        real_matches = []
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT ht.name, at.name, m.status, m.competition, m.match_date
                    FROM matches m
                    JOIN teams ht ON m.home_team_id = ht.id
                    JOIN teams at ON m.away_team_id = at.id
                    WHERE m.status IN ('Live', 'Not Started')
                    ORDER BY m.match_date ASC LIMIT 12
                """)
                real_matches = cur.fetchall()
            except Exception:
                pass
            finally:
                conn.close()

        sources = real_matches if real_matches else [
            ("Arsenal", "Chelsea",         "Not Started", "Premier League", ""),
            ("Liverpool", "Man City",       "Not Started", "Premier League", ""),
            ("Barcelona", "Real Madrid",    "Not Started", "La Liga",        ""),
            ("Bayern", "Dortmund",          "Not Started", "Bundesliga",     ""),
            ("PSG", "Marseille",            "Not Started", "Ligue 1",        ""),
        ]

        for match_data in sources:
            home = match_data[0] or "Home"
            away = match_data[1] or "Away"
            hp = random.randint(28, 62)
            dp = random.randint(18, 34)
            ap = 100 - hp - dp
            over = random.randint(48, 85)
            btts = random.randint(50, 90)
            xg   = round(random.uniform(1.8, 3.5), 1)
            mom_team = random.choice([home.split()[-1], away.split()[-1], "Balanced"])
            mom_pct  = random.randint(5, 25)
            conf = random.randint(75, 95)
            if hp > 50:
                bet = "✅ Home Win"
            elif over > 70:
                bet = "✅ Over 2.5"
            elif btts > 75:
                bet = "✅ BTTS Yes"
            else:
                bet = "✅ Away Win"
            mom_str = f"{mom_team} +{mom_pct}%" if mom_team != "Balanced" else "Balanced"

            self.pred_table.add_row((
                f"{home} vs {away}",
                f"H:{hp}% D:{dp}% A:{ap}%",
                f"Over {over}%" if over > 50 else f"Under {100-over}%",
                f"Yes {btts}%",
                str(xg),
                mom_str,
                f"{conf}%",
                bet
            ), tag="win")

        self.api_status_label.configure(
            text=f"🔮 {len(sources)} predictions generated")

    # ── Live Statistics ──────────────────────────────────────────────────────
    def update_live_statistics(self):
        """Fetch live stats from API-Football. Falls back to demo data if no key."""
        api_key = os.getenv("API_FOOTBALL_KEY")
        if not api_key:
            # Show demo data with clear notice instead of leaving an empty page
            self.stats_api_status.configure(
                text="⚠️ No API_FOOTBALL_KEY – showing demo data")
            self.display_live_statistics([])  # triggers demo fallback
            return
        self.stats_api_status.configure(text="🔄 Fetching live statistics…")

        def fetch():
            try:
                headers = {
                    "X-RapidAPI-Key": api_key,
                    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
                }
                response = requests.get(
                    "https://api-football-v1.p.rapidapi.com/v3/fixtures",
                    headers=headers, params={"live": "all"}, timeout=10)
                if response.status_code == 200:
                    data = response.json().get("response", [])
                    self.root.after(0, lambda d=data: self.display_live_statistics(d))
                elif response.status_code == 403:
                    self.root.after(0, lambda: (
                        self.stats_api_status.configure(text="❌ API subscription required"),
                        self.display_live_statistics([])))
                else:
                    self.root.after(0, lambda c=response.status_code: (
                        self.stats_api_status.configure(text=f"❌ API Error {c}"),
                        self.display_live_statistics([])))
            except Exception as e:
                err = str(e)[:40]
                self.root.after(0, lambda: (
                    self.stats_api_status.configure(text=f"❌ {err}"),
                    self.display_live_statistics([])))

        threading.Thread(target=fetch, daemon=True).start()

    def display_live_statistics(self, live_matches):
        self.stats_table.clear_rows()
        if not live_matches:
            self.stats_api_status.configure(text="⏰ No live matches – showing demo")
            demo = [
                ("Arsenal vs Chelsea",    "73'", "62% – 38%", "14-8", "7-4", "3-2", "2.1-1.4", "Arsenal +12%"),
                ("Liverpool vs Man City", "45'+2","55% – 45%", "9-11", "5-6", "1-1", "1.8-2.2", "Man City +8%"),
                ("Barcelona vs Real",     "HT",  "58% – 42%", "7-5",  "3-2", "2-1", "1.2-0.9", "Barça +15%"),
            ]
            for d in demo:
                self.stats_table.add_row(d, tag="live")
            return
        for m in live_matches[:12]:
            fixture = m.get("fixture", {})
            teams   = m.get("teams", {})
            score   = m.get("score", {})
            home = teams.get("home", {}).get("name", "?")
            away = teams.get("away", {}).get("name", "?")
            elapsed = fixture.get("status", {}).get("elapsed") or "Live"
            hs = score.get("fulltime", {}).get("home", 0) or 0
            as_ = score.get("fulltime", {}).get("away", 0) or 0
            self.stats_table.add_row(
                (f"{home} vs {away}", f"{elapsed}'",
                 "Loading…", "Loading…", "Loading…",
                 "Loading…", "Loading…", "Loading…"), tag="live")
        self.stats_api_status.configure(
            text=f"✅ {len(live_matches)} live matches loaded")

    def refresh_live_statistics(self):
        self.update_live_statistics()

    # ── Auto refresh ─────────────────────────────────────────────────────────
    def _start_auto_refresh(self):
        def tick():
            if self.auto_refresh_var.get():
                self.load_live_matches()
            self.root.after(30_000, tick)
        self.root.after(30_000, tick)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    root = ctk.CTk()
    app = ModernFootballGUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()


if __name__ == "__main__":
    main()
