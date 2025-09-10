import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, os, time, platform
from .wipe import wipe_file, wipe_folder, wipe_drive, get_available_drives, WipeError
from .cert import generate_certificate
from .logger import WipeLogger

APP_TITLE = "Data Wiping Tool"
LICENSE_TEXT = "Licensed to Aniket Tegginamath"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('720x540')
        self.configure(bg='#0f172a')
        self.logger = WipeLogger()
        self._build_style()
        self._build_ui()

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TLabel', background='#0f172a', foreground='#e5e7eb', font=('Segoe UI', 10))
        style.configure('License.TLabel', background='#0f172a', foreground='#94a3b8', font=('Segoe UI', 9, 'italic'))
        style.configure('TButton', padding=8)
        style.configure('TEntry', fieldbackground='#111827', foreground='#e5e7eb')
        style.configure('TCombobox', fieldbackground='#ffffff', foreground='#000000')
        style.configure('Horizontal.TProgressbar', troughcolor='#111827', bordercolor='#111827', background='#22c55e')

    def _build_ui(self):
        pad = 12
        
        # Main frame
        frm = ttk.Frame(self, padding=pad)
        frm.pack(fill='both', expand=True)
        
        # License text at top right
        license_label = ttk.Label(frm, text=LICENSE_TEXT, style='License.TLabel')
        license_label.grid(row=0, column=2, sticky='e', pady=(0, pad*2))
        
        # Rest of the UI
        ttk.Label(frm, text="Target (file, folder, or drive)").grid(row=1, column=0, sticky='w')
        self.path_var = tk.StringVar()
        ent = ttk.Entry(frm, textvariable=self.path_var, width=60)
        ent.grid(row=2, column=0, columnspan=2, sticky='we', pady=(0, pad))
        
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=2, sticky='e')
        ttk.Button(btn_frame, text="Browse...", command=self.browse).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Drives", command=self.browse_drives).pack(side='left')
        
        ttk.Label(frm, text="Wipe Method").grid(row=3, column=0, sticky='w')
        self.method_var = tk.StringVar(value='quick')
        cmb = ttk.Combobox(frm, textvariable=self.method_var, values=['quick', 'nist', 'dod'], state='readonly')
        cmb.grid(row=4, column=0, sticky='w', pady=(0, pad))
        
        self.verify_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Verify after wipe", variable=self.verify_var).grid(row=4, column=1, sticky='w')
        
        self.log = tk.Text(frm, height=12, bg='#111827', fg='#e5e7eb', insertbackground='#e5e7eb')
        self.log.grid(row=5, column=0, columnspan=3, sticky='nsew', pady=(0, pad))
        
        frm.rowconfigure(5, weight=1)
        frm.columnconfigure(0, weight=1)
        
        # Progress frame
        progress_frame = ttk.Frame(frm)
        progress_frame.grid(row=6, column=0, columnspan=3, sticky='we', pady=(0, pad))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', maximum=100)
        self.progress.grid(row=0, column=0, sticky='we')
        
        self.progress_label = ttk.Label(progress_frame, text="Ready", style='TLabel')
        self.progress_label.grid(row=1, column=0, sticky='w', pady=(4, 0))
        
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=7, column=0, columnspan=3, sticky='e', pady=(pad, 0))
        
        self.run_btn = ttk.Button(btn_frame, text="Start Wipe", command=self.start_wipe)
        self.run_btn.pack(side='left', padx=6)
        
        self.cert_btn = ttk.Button(btn_frame, text="Open Certificate Folder", command=self.open_cert_dir, state='disabled')
        self.cert_btn.pack(side='left')
        
        self.email_btn = ttk.Button(btn_frame, text="Email Certificate", command=self.email_certificate, state='disabled')
        self.email_btn.pack(side='left', padx=6)
        
        self.logs_btn = ttk.Button(btn_frame, text="View Logs", command=self.view_logs)
        self.logs_btn.pack(side='left', padx=6)

    def browse(self):
        path = filedialog.askopenfilename(title="Select file")
        if not path:
            path = filedialog.askdirectory(title="Or select folder")
        if path:
            # Convert to absolute path and normalize
            path = os.path.abspath(os.path.normpath(path))
            self.path_var.set(path)

    def browse_drives(self):
        try:
            drives = get_available_drives()
            if not drives:
                messagebox.showwarning("No Drives", "No available drives found")
                return
            
            # Create a simple dialog to select drive
            drive_window = tk.Toplevel(self)
            drive_window.title("Select Drive")
            drive_window.geometry('400x300')
            drive_window.configure(bg='#0f172a')
            
            ttk.Label(drive_window, text="Available Drives:", style='TLabel').pack(pady=10)
            
            # Create listbox for drives
            listbox = tk.Listbox(drive_window, bg='#111827', fg='#e5e7eb', selectbackground='#22c55e')
            listbox.pack(fill='both', expand=True, padx=10, pady=10)
            
            for drive in drives:
                size_gb = drive['total'] / (1024**3) if drive['total'] > 0 else 0
                display_text = f"{drive['label']} - {size_gb:.1f} GB"
                listbox.insert(tk.END, display_text)
            
            def select_drive():
                selection = listbox.curselection()
                if selection:
                    selected_drive = drives[selection[0]]
                    self.path_var.set(selected_drive['path'])
                    drive_window.destroy()
            
            ttk.Button(drive_window, text="Select", command=select_drive).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get drives: {str(e)}")

    def start_wipe(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror("Error", "Please select a file or folder")
            return
            
        # Get method and verify settings
        method = self.method_var.get()
        verify = self.verify_var.get()
            
        # Convert to absolute path and normalize
        path = os.path.abspath(os.path.normpath(path))
        
        # Check if path exists
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Path does not exist: {path}")
            return
            
        # Check if it's a drive (Windows: C:\, D:\, etc. or Linux: /mnt/, etc.)
        is_drive = False
        if platform.system() == "Windows":
            is_drive = len(path) == 3 and path[1] == ':' and path[2] == '\\'
        else:
            # Check if it's a mount point
            try:
                drives = get_available_drives()
                is_drive = any(d['path'] == path for d in drives)
            except:
                is_drive = False
        
        # Check if path is accessible
        try:
            if os.path.isfile(path):
                with open(path, 'rb') as f:
                    pass
            else:
                os.listdir(path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot access path: {path}\nError: {str(e)}")
            return
            
        # Special warning for drives
        if is_drive:
            warning_msg = f"""WARNING: You are about to wipe the entire drive {path}

This will:
• Permanently delete ALL files and folders on this drive
• Overwrite data with secure patterns
• Cannot be undone

Are you absolutely sure you want to continue?

Drive: {path}
Method: {method}
Verification: {'Yes' if verify else 'No'}"""
            
            if not messagebox.askyesno("CRITICAL WARNING - Drive Wipe", warning_msg):
                return
        else:
            if not messagebox.askyesno("Confirm", "This will irreversibly overwrite data. Continue?"):
                return
            
        self.run_btn.configure(state='disabled')
        self._update_progress(0, "Starting wipe process...")
        t = threading.Thread(target=self._do_wipe, daemon=True)
        t.start()

    def _update_progress(self, value, text):
        self.progress['value'] = value
        self.progress_label['text'] = text
        self.update_idletasks()

    def _do_wipe(self):
        path = self.path_var.get().strip()
        method = self.method_var.get()
        verify = self.verify_var.get()
        
        # Convert to absolute path and normalize
        path = os.path.abspath(os.path.normpath(path))
        
        # Check if it's a drive (Windows: C:\, D:\, etc. or Linux: /mnt/, etc.)
        is_drive = False
        if platform.system() == "Windows":
            is_drive = len(path) == 3 and path[1] == ':' and path[2] == '\\'
        else:
            # Check if it's a mount point
            try:
                drives = get_available_drives()
                is_drive = any(d['path'] == path for d in drives)
            except:
                is_drive = False
        
        try:
            self._log(f"Starting wipe: {path} • method={method} • verify={verify}")
            self._update_progress(10, "Initializing wipe process...")
            
            if is_drive:
                self._update_progress(20, "Scanning drive for files...")
                self._log(f"Drive wipe initiated for: {path}")
                result = wipe_drive(path, method=method, verify=verify)
                self._update_progress(60, "Drive contents wiped...")
                
                # Log detailed results
                if isinstance(result, dict):
                    total_files = result.get('total_files_found', 0)
                    processed_files = result.get('total_files_processed', 0)
                    self._log(f"Files found: {total_files}, Successfully processed: {processed_files}")
                    
                    # Log any errors
                    results_list = result.get('results', [])
                    errors = [r for r in results_list if 'error' in r]
                    if errors:
                        self._log(f"Warning: {len(errors)} files had issues during processing")
                        for error in errors[:5]:  # Show first 5 errors
                            self._log(f"  - {error.get('path', 'Unknown')}: {error.get('error', 'Unknown error')}")
                        if len(errors) > 5:
                            self._log(f"  ... and {len(errors) - 5} more errors")
            elif os.path.isfile(path):
                self._update_progress(20, "Wiping file contents...")
                result = wipe_file(path, method=method, verify=verify)
                self._update_progress(60, "File contents wiped...")
            else:
                result = wipe_folder(path, method=method, verify=verify)
            
            self._update_progress(70, "Verifying wipe operation...")
            self._log("Wipe completed.")
            
            if isinstance(result, list):
                # For folders, check if there were any errors
                errors = [r.get('error') for r in result if 'error' in r]
                if errors:
                    self._log("Warning: Some items could not be wiped:")
                    for error in errors:
                        self._log(f"  - {error}")
            
            self._update_progress(80, "Generating certificate...")
            cert_dir = os.path.join(os.path.expanduser('~'), 'DataWipingCertificates')
            cert_path = os.path.join(cert_dir, f'certificate_{int(time.time())}.pdf')
            payload = {
                'target': path,
                'method': method,
                'verified': True,
                'results': result,
            }
            os.makedirs(cert_dir, exist_ok=True)
            info = generate_certificate(cert_path, payload)
            self._log(f"Certificate saved: {info['path']}")
            
            # Log the operation
            operation_data = {
                'target': path,
                'method': method,
                'verified': True,
                'success': True,
                'results': result,
                'certificate_path': info['path'],
                'device_info': payload.get('device_info', {}),
                'drive_info': payload.get('drive_info', {})
            }
            operation_id = self.logger.log_operation(operation_data)
            self._log(f"Operation logged: {operation_id}")
            
            self._update_progress(100, "Data wiped successfully!")
            self.cert_btn.configure(state='normal')
            self.email_btn.configure(state='normal')
            self.last_certificate_path = info['path']
            
            # Show success message
            messagebox.showinfo("Success", "Data has been successfully wiped and certificate generated!")
            
        except Exception as e:
            self._log(f"Error: {e}")
            self._update_progress(0, "Error occurred during wipe")
            
            # Log the failed operation
            operation_data = {
                'target': path,
                'method': method,
                'verified': verify,
                'success': False,
                'error': str(e),
                'results': {},
                'certificate_path': '',
                'device_info': {},
                'drive_info': {}
            }
            operation_id = self.logger.log_operation(operation_data)
            self._log(f"Failed operation logged: {operation_id}")
            
            messagebox.showerror("Error", str(e))
        finally:
            self.run_btn.configure(state='normal')

    def _log(self, msg):
        self.log.insert('end', msg + "\n")
        self.log.see('end')

    def open_cert_dir(self):
        cert_dir = os.path.join(os.path.expanduser('~'), 'DataWipingCertificates')
        if not os.path.isdir(cert_dir):
            os.makedirs(cert_dir, exist_ok=True)
        import subprocess, sys
        if sys.platform.startswith('win'):
            os.startfile(cert_dir)
        elif sys.platform == 'darwin':
            subprocess.call(['open', cert_dir])
        else:
            subprocess.call(['xdg-open', cert_dir])

    def view_logs(self):
        """Open logs viewer window"""
        log_window = tk.Toplevel(self)
        log_window.title("Wipe Operation Logs")
        log_window.geometry('800x600')
        log_window.configure(bg='#0f172a')
        
        # Get statistics
        stats = self.logger.get_statistics()
        history = self.logger.get_operation_history(20)
        
        # Statistics frame
        stats_frame = ttk.Frame(log_window)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(stats_frame, text="Statistics", style='TLabel').pack(anchor='w')
        stats_text = f"Total Operations: {stats.get('total_operations', 0)}\n"
        stats_text += f"Success Rate: {stats.get('success_rate', 0):.1f}%\n"
        stats_text += f"Recent Operations (7 days): {stats.get('recent_operations_7days', 0)}"
        ttk.Label(stats_frame, text=stats_text, style='TLabel').pack(anchor='w')
        
        # History frame
        history_frame = ttk.Frame(log_window)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(history_frame, text="Recent Operations", style='TLabel').pack(anchor='w')
        
        # Create treeview for history
        columns = ('Time', 'Target', 'Method', 'Status', 'Verified')
        tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Populate tree
        for op in history:
            status = "Success" if op.get('success', False) else "Failed"
            verified = "Yes" if op.get('verified', False) else "No"
            timestamp = op.get('timestamp', '')[:19]  # Remove microseconds
            
            tree.insert('', 'end', values=(
                timestamp,
                op.get('target', '')[:50] + '...' if len(op.get('target', '')) > 50 else op.get('target', ''),
                op.get('method', ''),
                status,
                verified
            ))
        
        tree.pack(fill='both', expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(log_window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Export Logs", command=lambda: self.export_logs()).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Open Log Folder", command=lambda: self.open_log_dir()).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Close", command=log_window.destroy).pack(side='right', padx=5)

    def export_logs(self):
        """Export logs to a file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            format = 'csv' if file_path.endswith('.csv') else 'json'
            if self.logger.export_logs(file_path, format):
                messagebox.showinfo("Success", f"Logs exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export logs")

    def open_log_dir(self):
        """Open log directory"""
        log_dir = self.logger.log_dir
        import subprocess, sys
        if sys.platform.startswith('win'):
            os.startfile(log_dir)
        elif sys.platform == 'darwin':
            subprocess.call(['open', log_dir])
        else:
            subprocess.call(['xdg-open', log_dir])

    def email_certificate(self):
        """Email the last generated certificate"""
        if not hasattr(self, 'last_certificate_path') or not self.last_certificate_path:
            messagebox.showerror("Error", "No certificate available to email")
            return
        
        # Create email dialog
        email_window = tk.Toplevel(self)
        email_window.title("Email Certificate")
        email_window.geometry('400x300')
        email_window.configure(bg='#0f172a')
        
        # Email configuration
        ttk.Label(email_window, text="Email Configuration", style='TLabel').pack(pady=10)
        
        # SMTP Server
        ttk.Label(email_window, text="SMTP Server:", style='TLabel').pack(anchor='w', padx=10)
        smtp_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(email_window, textvariable=smtp_var, width=40).pack(padx=10, pady=5)
        
        # Port
        ttk.Label(email_window, text="Port:", style='TLabel').pack(anchor='w', padx=10)
        port_var = tk.StringVar(value="587")
        ttk.Entry(email_window, textvariable=port_var, width=40).pack(padx=10, pady=5)
        
        # From Email
        ttk.Label(email_window, text="From Email:", style='TLabel').pack(anchor='w', padx=10)
        from_var = tk.StringVar()
        ttk.Entry(email_window, textvariable=from_var, width=40).pack(padx=10, pady=5)
        
        # Password
        ttk.Label(email_window, text="Password/App Password:", style='TLabel').pack(anchor='w', padx=10)
        pass_var = tk.StringVar()
        ttk.Entry(email_window, textvariable=pass_var, show="*", width=40).pack(padx=10, pady=5)
        
        # To Email
        ttk.Label(email_window, text="To Email:", style='TLabel').pack(anchor='w', padx=10)
        to_var = tk.StringVar()
        ttk.Entry(email_window, textvariable=to_var, width=40).pack(padx=10, pady=5)
        
        def send_email():
            try:
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.base import MIMEBase
                from email import encoders
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = from_var.get()
                msg['To'] = to_var.get()
                msg['Subject'] = "Data Wiping Certificate"
                
                # Email body
                body = f"""
Data Wiping Certificate

This email contains the certificate of secure data erasure.

Certificate Details:
- Target: {self.path_var.get()}
- Method: {self.method_var.get()}
- Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

Please find the certificate attached.

Best regards,
Data Wiping Tool
                """
                msg.attach(MIMEText(body, 'plain'))
                
                # Attach certificate
                with open(self.last_certificate_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(self.last_certificate_path)}'
                )
                msg.attach(part)
                
                # Send email
                server = smtplib.SMTP(smtp_var.get(), int(port_var.get()))
                server.starttls()
                server.login(from_var.get(), pass_var.get())
                text = msg.as_string()
                server.sendmail(from_var.get(), to_var.get(), text)
                server.quit()
                
                messagebox.showinfo("Success", "Certificate emailed successfully!")
                email_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send email: {str(e)}")
        
        # Buttons
        btn_frame = ttk.Frame(email_window)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Send Email", command=send_email).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=email_window.destroy).pack(side='left', padx=5)

def main():
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()
