# 🧹 Data Wiping Tool  

A **cross-platform secure data erasure utility** with both **CLI ⚡** and **GUI 🖥️** support.  
Ensures files, folders, and drives are **permanently wiped** using industry-standard methods like **NIST** and **DoD**.  
Every operation generates a **Certificate of Secure Data Erasure 📜** for compliance and auditing.  

---

## ✨ Features  

- 🔒 **Secure Wiping Methods**  
  - `quick` → Single-pass random overwrite  
  - `nist` → NIST SP 800-88 Rev.1 compliant  
  - `dod` → DoD 5220.22-M three-pass method  

- 📁 **Target Support**  
  - Individual files  
  - Entire folders  
  - Complete drives (⚠️ with safety checks)  

- 📜 **Certificate Generation**  
  - PDF certificates with metadata  
  - QR code support for quick verification  

- 🖥️ **User Interfaces**  
  - **CLI (Command-Line)**: lightweight & scriptable  
  - **GUI (Tkinter)**: modern design with progress bar & logs  

- 📝 **Logging System**  
  - Tracks all operations  
  - Export logs to JSON/CSV  
  - View success rate & history  

- 📧 **Extras**  
  - Email certificates directly from GUI  
  - Open log and certificate directories with one click  

---

## 🚀 Installation  

```bash
git clone https://github.com/yourusername/data-wiping-tool.git
cd data-wiping-tool
pip install -r requirements.txt
```

## ⚡ Usage

CLI Mode
```bash
python -m data_wiping_tool.cli target_path --method nist --cert-out cert.pdf
```

Example:
```bash
python -m data_wiping_tool.cli ~/Documents/secret.txt --method dod --cert-out wipe_cert.pdf
```

GUI Mode
```bash
python -m data_wiping_tool.main
```

⚠️ Warnings

❌ Irreversible: Data wiped cannot be recovered.

🖥️ Do NOT use on system partitions (e.g., C:\ or /).

🔑 Admin/root privileges required for full drive wipes.

📦 Requirements

* Python 3.8+

* Dependencies:

* reportlab

* qrcode

* pillow

* psutil

* Install via:
```bash
pip install -r requirements.txt
```

🛡️ License

Licensed to Aniket Tegginamath.


