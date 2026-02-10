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

---

### 9. Architecture & Internals (Technical)

- **UI framework**: `PyQt6` (`QMainWindow`, `QTabWidget`, `QTableWidget`, `QTextEdit`, dialogs, custom `QWidget` for Matrix rain)
- **Threads**:
  - `ScanWorker` (`QThread`): enumerates apps, Homebrew, pip, and system packages
  - `ProcessWorker` (`QThread`): runs `ps aux` and parses processes
  - `DiskWorker` (`QThread`): reads disk usage via `shutil.disk_usage("/")`
  - `UninstallWorker` (`QThread`): executes uninstall shell commands and streams logs
- **Main tabs**:
  - `[PACKAGES]` → package inventory, filters, stats, uninstall/export actions
  - `[PROCESSES]` → live process list + kill actions
  - `[TERMINAL]` → log console (boot sequence + runtime logs)

#### 9.1. Scanning logic

- **Applications**
  - Folders scanned:
    - `/Applications`
    - `~/Applications`
  - For each `*.app` bundle:
    - Reads `Contents/Info.plist` with `plistlib` to get `CFBundleShortVersionString` / `CFBundleVersion`
    - Recursively walks the bundle to compute size in MB
  - Each app is represented as:
    - `name`, `version`, `size_mb`, `kind` (`Application` or `User App`), `path`, `uninstall_cmd`

- **Homebrew formulae**
  - Runs:
    - `brew list --formula --versions`
    - `brew --cellar`
  - Calculates size of each formula directory under the Cellar
  - Builds uninstall command: `brew uninstall --formula NAME`

- **Homebrew casks**
  - Runs: `brew list --cask --versions`
  - No size calculation (shown as `-`)
  - Builds uninstall command: `brew uninstall --cask NAME`

- **pip packages**
  - Runs: `pip3 list --format=json`
  - For each package:
    - Stores name + version
    - Builds uninstall command: `pip3 uninstall -y --break-system-packages NAME`

- **System packages**
  - Runs:
    - `pkgutil --pkgs`
    - For each pkg ID: `pkgutil --pkg-info PKG_ID` to read version
  - Builds uninstall command: `pkgutil --forget PKG_ID`

All of these results are merged into a single `all_items` list and displayed in the `[PACKAGES]` table with color-coded rows by type.

#### 9.2. Uninstall pipeline

1. User selects rows (checkboxes in the first column).
2. Clicks **`[UNINSTALL]`**.
3. `HackerConfirmDialog` shows a summary of selected targets.
4. `HackerPasswordDialog` prompts for the macOS account password.
5. `UninstallWorker`:
   - For each item, takes `uninstall_cmd` (e.g. `rm -rf "App.app"`).
   - If the command is `rm -rf` or `pkgutil ...`, it prefixes with:
     ```bash
     echo 'PASSWORD' | sudo -S <uninstall_cmd>
     ```
   - For other commands (brew / pip), it runs them directly.
   - Captures stdout/stderr and emits log lines to the `[TERMINAL]` tab.
6. When done, it shows a summary: `N removed, M failed`, and automatically triggers a rescan.

#### 9.3. Process manager

- Executes `ps aux` once per scan, parses the output into:
  - `user`, `pid`, `%CPU`, `%MEM`, `command`
- Displays in a sortable `QTableWidget`:
  - Numeric sorting for PID / CPU / MEM using `UserRole` data
  - Color highlights:
    - High CPU / MEM in **orange** or **red**
- Kills:
  - On `[KILL -9]`, sends `kill -9 PID`, then rescans processes.

#### 9.4. Disk usage panel

- Uses `shutil.disk_usage("/")`:
  - `total_gb`, `used_gb`, `free_gb`, `% used`
- Color‑codes usage:
  - `< 70%` → green
  - `70–90%` → orange
  - `> 90%` → red

---

### 10. Development Notes

- **Python version**: target is modern Python 3 on macOS.
- **Style**:
  - Heavy use of PyQt stylesheets for the **Matrix / hacker** aesthetic.
  - Monospace fonts (`Menlo`, `Monaco`, `Courier New`) everywhere.
- **Platform assumptions**:
  - macOS only (uses `platform.mac_ver()`, `pkgutil`, `.app` bundles, Homebrew).
  - Not intended for Linux/Windows without changes.

#### 10.1. Running from source (dev mode)

```bash
git clone https://github.com/RhelSenseiZamiq/macos_package_checker.git
cd macos_package_checker
python3 xp_app_manager.py
```

You can also modify `xp_app_manager.py` directly and rerun to experiment with the UI or logic.

---

### 11. Known Limitations / Ideas

- Does not track or undo changes (no “recycle bin”).
- System package removal via `pkgutil --forget` only forgets receipts; it does not fully uninstall underlying files.
- No sandboxing of commands; assumes a trusted user on a personal macOS workstation.
- Possible future enhancements:
  - Dry‑run mode (show commands without executing).
  - Per‑type safety levels (e.g. block some system packages by default).
  - Live process auto‑refresh.


