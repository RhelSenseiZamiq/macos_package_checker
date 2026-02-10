## H4CK3R / XP App Manager

Cyberpunk-style **macOS app & package manager** with a Matrix GUI.  
Scans your system for applications, packages and processes, then lets you **uninstall** or **kill** them from one dashboard.

---

### 1. Features

- **Visual inventory of your system**
  - `/Applications` and `~/Applications` (`.app` bundles)
  - Homebrew **formulae** and **casks**
  - `pip3` Python packages
  - System packages from `pkgutil`
- **Fast search & filters**
  - Filter by type (Applications, Brew Formula, Brew Cask, pip Package, System Pkg)
  - Text search (similar to `grep -i`)
- **Bulk uninstall**
  - Select multiple targets and execute uninstall in one shot
  - Uses appropriate commands:
    - Apps: `rm -rf "App.app"`
    - Brew formulae: `brew uninstall --formula NAME`
    - Brew casks: `brew uninstall --cask NAME`
    - pip: `pip3 uninstall -y --break-system-packages NAME`
    - System pkgs: `pkgutil --forget PKG_ID`
- **Process manager**
  - `ps aux` style process list
  - Sort by CPU / MEM / PID
  - Kill selected process with **SIGKILL (`kill -9`)**
- **Disk usage overview**
  - Shows total, used, free space and % usage for `/`
- **Export inventory**
  - Save a snapshot of all detected apps/packages to `~/Desktop/h4ck3r_export.txt`

> **WARNING**: This tool can remove apps and system packages.  
> Use it only if you understand what you’re deleting.

---

### 2. Requirements

- **Operating system**: macOS (designed for modern macOS with Homebrew)
- **Python**: `python3` (3.x) installed and available on `PATH`
- **Qt**: `PyQt6`
- **Homebrew (optional but recommended)** for brew scanning:
  - `brew list --formula --versions`
  - `brew list --cask --versions`

#### 2.1. Install Python & PyQt6 (if needed)

```bash
brew install python
python3 -m pip install --upgrade pip
python3 -m pip install PyQt6
```

---

### 3. Project Files

```text
XP_App_Manager/
├── xp_app_manager.py   # Main GUI application
├── run.sh              # Launcher script (double-click / CLI)
└── __pycache__/        # Python bytecode cache (auto-created)
```

- **`xp_app_manager.py`**: All logic and GUI (Matrix header, tables, dialogs).
- **`run.sh`**: Convenience wrapper so you can run the app without typing Python commands.

---

### 4. How to Run

From Terminal:

```bash
cd /Users/administrator/Desktop/XP_App_Manager
./run.sh
```

If `run.sh` is not executable:

```bash
cd /Users/administrator/Desktop/XP_App_Manager
chmod +x run.sh
./run.sh
```

Or run directly with Python:

```bash
cd /Users/administrator/Desktop/XP_App_Manager
python3 xp_app_manager.py
```

---

### 5. Using the App

#### 5.1. Packages tab (`[PACKAGES]`)

- Click **`[SCAN ALL]`** to:
  - Scan `/Applications` and `~/Applications`
  - Enumerate Homebrew formulae & casks
  - List `pip3` packages
  - List system packages from `pkgutil`
- Use **TYPE** dropdown to filter:
  - `All`, `Application`, `User App`, `Brew Formula`, `Brew Cask`, `pip Package`, `System Pkg`
- Use **FIND** box to search by name (case-insensitive).
- Use **`[ALL]` / `[NONE]`** to mark rows.
- Click **`[EXPORT]`** to write a text report to `~/Desktop/h4ck3r_export.txt`.
- Click **`[UNINSTALL]`** to remove selected items:
  1. Review the confirmation dialog and list of targets.
  2. Enter your **macOS account password** for `sudo` when asked.
  3. Watch the log in the **`[TERMINAL]`** tab for progress.

> **Note**: Uninstalling system packages (`pkgutil --forget`) and `rm -rf` on apps can be destructive.  
> Double‑check before you confirm.

#### 5.2. Processes tab (`[PROCESSES]`)

- Click **`[SCAN PROCESSES]`** to run `ps aux` and display all processes.
- Filter by user or command using the search box.
- Select a row and click **`[KILL -9]`** to send `SIGKILL` to that PID.
- High‑CPU / high‑memory processes are highlighted in orange/red.

#### 5.3. Terminal tab (`[TERMINAL]`)

- Shows a **boot banner**, status messages, scan logs, and uninstall logs.
- When you export or uninstall, all commands and results are printed here.

---

### 6. Security & Safety Notes

- The app executes shell commands like:
  - `rm -rf "path"`
  - `brew uninstall ...`
  - `pip3 uninstall ...`
  - `pkgutil --forget ...`
  - `kill -9 PID`
- For operations requiring root, it builds:

  ```bash
  echo 'PASSWORD' | sudo -S <command>
  ```

- **Use on your own machine only.**  
- Do **not** run it on systems you don’t fully control.
- Always review selected targets before confirming uninstall.

---

### 7. Troubleshooting

- **Window does not open / crash on start**
  - Ensure `PyQt6` is installed:
    ```bash
    python3 -c "from PyQt6 import QtWidgets; print('OK')"
    ```
  - If this fails, reinstall:
    ```bash
    python3 -m pip install --upgrade --force-reinstall PyQt6
    ```

- **Brew sections empty**
  - Check Homebrew is installed and on `PATH`:
    ```bash
    brew --version
    ```

- **Uninstall fails with permission errors**
  - Make sure the password is correct.
  - Some system packages may not be removable via `pkgutil --forget`.

- **Fonts / colors look strange**
  - App prefers `"Menlo"` / `"Monaco"`. On non-standard setups, macOS may substitute another font, but functionality is unaffected.

---

### 8. License / Usage

Created by **Aykhan** as a hacker‑style utility and portfolio project.  
Use responsibly on personal systems; no warranty is provided.

