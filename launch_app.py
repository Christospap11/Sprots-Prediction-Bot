#!/usr/bin/env python3
"""
Football Betting System Launcher
Easy launcher for GUI and monitoring system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import sys

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()
        
        # Process tracking
        self.monitor_process = None
        self.gui_process = None
    
    def setup_window(self):
        """Setup the launcher window."""
        self.root.title("⚽ Football Betting System Launcher")
        self.root.geometry("600x400")
        self.root.configure(bg='#1e1e1e')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Launcher.TLabel', 
                       background='#1e1e1e', 
                       foreground='#ffffff', 
                       font=('Arial', 14, 'bold'))
        
        style.configure('LauncherBtn.TButton',
                       background='#4fc3f7',
                       foreground='white',
                       font=('Arial', 12, 'bold'),
                       padding=(20, 10))
        
        style.configure('MonitorBtn.TButton',
                       background='#66bb6a',
                       foreground='white',
                       font=('Arial', 12, 'bold'),
                       padding=(20, 10))
        
        style.configure('StopBtn.TButton',
                       background='#f44336',
                       foreground='white',
                       font=('Arial', 12, 'bold'),
                       padding=(20, 10))
    
    def create_widgets(self):
        """Create launcher widgets."""
        
        # Title
        title_label = ttk.Label(self.root, 
                               text="⚽ FOOTBALL BETTING PREDICTION SYSTEM", 
                               style='Launcher.TLabel')
        title_label.pack(pady=30)
        
        # Subtitle
        subtitle_label = ttk.Label(self.root, 
                                  text="Choose what to launch:", 
                                  style='Launcher.TLabel')
        subtitle_label.pack(pady=10)
        
        # Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=30)
        
        # Launch GUI button
        gui_btn = ttk.Button(button_frame, 
                            text="🖥️ Launch GUI Interface", 
                            command=self.launch_gui,
                            style='LauncherBtn.TButton')
        gui_btn.pack(pady=10, fill='x')
        
        # Launch Monitor button
        monitor_btn = ttk.Button(button_frame, 
                               text="📊 Start Data Monitoring", 
                               command=self.launch_monitor,
                               style='MonitorBtn.TButton')
        monitor_btn.pack(pady=10, fill='x')
        
        # Launch Both button
        both_btn = ttk.Button(button_frame, 
                             text="🚀 Launch Both (Recommended)", 
                             command=self.launch_both,
                             style='LauncherBtn.TButton')
        both_btn.pack(pady=10, fill='x')
        
        # Stop All button
        stop_btn = ttk.Button(button_frame, 
                             text="⏹️ Stop All", 
                             command=self.stop_all,
                             style='StopBtn.TButton')
        stop_btn.pack(pady=10, fill='x')
        
        # Status frame
        status_frame = ttk.Frame(self.root)
        status_frame.pack(pady=20, fill='x', padx=50)
        
        self.status_label = ttk.Label(status_frame, 
                                     text="📊 Status: Ready to launch", 
                                     style='Launcher.TLabel')
        self.status_label.pack()
        
        # Instructions
        instructions = """
🔹 GUI Interface: Beautiful interface to view matches, odds, and predictions
🔹 Data Monitoring: Background system collecting live football data 24/7
🔹 Launch Both: Recommended for full functionality
        """
        
        info_label = ttk.Label(self.root, 
                              text=instructions,
                              style='Launcher.TLabel',
                              justify='left')
        info_label.pack(pady=20)
    
    def launch_gui(self):
        """Launch the GUI interface."""
        try:
            self.status_label.config(text="🖥️ Status: Launching GUI...")
            self.root.update()
            
            # Launch GUI in separate process
            if sys.platform.startswith('win'):
                self.gui_process = subprocess.Popen([sys.executable, 'football_betting_gui.py'])
            else:
                self.gui_process = subprocess.Popen(['python3', 'football_betting_gui.py'])
            
            self.status_label.config(text="✅ Status: GUI launched successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch GUI: {e}")
            self.status_label.config(text="❌ Status: GUI launch failed")
    
    def launch_monitor(self):
        """Launch the monitoring system."""
        try:
            self.status_label.config(text="📊 Status: Starting data monitoring...")
            self.root.update()
            
            # Launch monitor in separate process
            if sys.platform.startswith('win'):
                self.monitor_process = subprocess.Popen([sys.executable, 'monitor_with_database.py'])
            else:
                self.monitor_process = subprocess.Popen(['python3', 'monitor_with_database.py'])
            
            self.status_label.config(text="✅ Status: Monitoring system started!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
            self.status_label.config(text="❌ Status: Monitoring start failed")
    
    def launch_both(self):
        """Launch both GUI and monitoring system."""
        try:
            self.status_label.config(text="🚀 Status: Starting complete system...")
            self.root.update()
            
            # Start monitoring first
            if sys.platform.startswith('win'):
                self.monitor_process = subprocess.Popen([sys.executable, 'monitor_with_database.py'])
            else:
                self.monitor_process = subprocess.Popen(['python3', 'monitor_with_database.py'])
            
            # Small delay then start GUI
            self.root.after(2000, self._launch_gui_delayed)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch system: {e}")
            self.status_label.config(text="❌ Status: System launch failed")
    
    def _launch_gui_delayed(self):
        """Launch GUI with delay."""
        try:
            if sys.platform.startswith('win'):
                self.gui_process = subprocess.Popen([sys.executable, 'football_betting_gui.py'])
            else:
                self.gui_process = subprocess.Popen(['python3', 'football_betting_gui.py'])
            
            self.status_label.config(text="🎉 Status: Complete system running!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch GUI: {e}")
            self.status_label.config(text="⚠️ Status: Monitoring only (GUI failed)")
    
    def stop_all(self):
        """Stop all running processes."""
        try:
            stopped = []
            
            if self.monitor_process and self.monitor_process.poll() is None:
                self.monitor_process.terminate()
                stopped.append("Monitoring system")
            
            if self.gui_process and self.gui_process.poll() is None:
                self.gui_process.terminate()
                stopped.append("GUI interface")
            
            if stopped:
                self.status_label.config(text=f"⏹️ Status: Stopped {', '.join(stopped)}")
            else:
                self.status_label.config(text="ℹ️ Status: Nothing was running")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop processes: {e}")
    
    def on_closing(self):
        """Handle window closing."""
        self.stop_all()
        self.root.destroy()


def main():
    """Main launcher function."""
    
    # Check if required files exist
    required_files = ['football_betting_gui.py', 'monitor_with_database.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Missing Files", 
                           f"Required files not found:\n" + "\n".join(missing_files))
        return
    
    root = tk.Tk()
    app = LauncherGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.stop_all()


if __name__ == "__main__":
    main() 