# Getting Started with Unimpeded Jupyter Notebook

This guide helps you set up a Python virtual environment and launch the unimpeded tutorial Jupyter notebook.

## Prerequisites

- Python 3.8 or higher
- Git

## Step-by-Step Setup

### 1. Navigate to your working directory

```zsh
cd /path/to/your/workspace
```

### 2. Clone the unimpeded repository

**Option A: HTTPS (Recommended for most users)**
```zsh
git clone https://github.com/handley-lab/unimpeded.git
```

**Option B: SSH (For contributors with write access)**
```zsh
git clone git@github.com:handley-lab/unimpeded.git
```

**Which should you use?**
- **HTTPS**: Simple, works immediately, no setup required. Best for users who just want to use the package.
- **SSH**: Requires SSH key setup but more convenient for developers who frequently push code. Only needed if you're a repository contributor.

### 3. Create a virtual environment

**Important:** Create the virtual environment in your workspace directory, NOT inside the cloned repository.

```zsh
python -m venv venv_unimpeded
```

**Windows:**
```powershell
python -m venv venv_unimpeded
```

Your directory structure should look like:
```
workspace/
├── venv_unimpeded/    # Virtual environment
└── unimpeded/         # Cloned repository
```

### 4. Activate the virtual environment

**macOS/Linux:**
```zsh
source venv_unimpeded/bin/activate
```

**Windows (PowerShell):**
```powershell
venv_unimpeded\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv_unimpeded\Scripts\activate.bat
```

### 5. Navigate into the repository

```zsh
cd unimpeded
```

### 6. Install unimpeded in editable mode

This installs unimpeded along with all dependencies:

```zsh
pip install -e .
```

### 7. Install Jupyter

```zsh
pip install jupyter
```

### 8. Launch Jupyter Notebook

```zsh
jupyter notebook unimpeded_tutorial.ipynb
```

## Deactivating the Environment

When you're done:

```zsh
deactivate
```

## Troubleshooting

### Issue: `jupyter: command not found`
**Solution:** Make sure you've activated the virtual environment and installed jupyter:
```zsh
source venv_unimpeded/bin/activate
pip install jupyter
```

### Issue: `ModuleNotFoundError: No module named 'unimpeded'`
**Solution:** Install unimpeded in the virtual environment:
```zsh
pip install -e .
```

### Issue: `No such file or directory: unimpeded_tutorial.ipynb`
**Solution:** Make sure you're in the unimpeded repository directory and that you've pulled the latest version from GitHub.

### Issue: Old pip version causing installation errors
**Solution:** Upgrade pip first:
```zsh
python -m pip install --upgrade pip
```

### Issue (Windows): Cannot run scripts (PowerShell execution policy)
**Solution:** Enable script execution temporarily:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

## Complete Installation Summary

**macOS/Linux:**
```zsh
# 1. Setup
cd /your/workspace
git clone https://github.com/handley-lab/unimpeded.git

# 2. Virtual environment (in workspace, not inside repo)
python -m venv venv_unimpeded
source venv_unimpeded/bin/activate

# 3. Install
cd unimpeded
pip install -e .
pip install jupyter

# 4. Launch notebook
jupyter notebook unimpeded_tutorial.ipynb
```

**Windows (PowerShell):**
```powershell
# 1. Setup
cd C:\your\workspace
git clone https://github.com/handley-lab/unimpeded.git

# 2. Virtual environment (in workspace, not inside repo)
python -m venv venv_unimpeded
venv_unimpeded\Scripts\Activate.ps1

# 3. Install
cd unimpeded
pip install -e .
pip install jupyter

# 4. Launch notebook
jupyter notebook unimpeded_tutorial.ipynb
```

## Checking Your Installation

Run this to verify everything is installed correctly:

**macOS/Linux:**
```zsh
pip list | grep -E "(unimpeded|jupyter|anesthetic)"
```

**Windows (PowerShell):**
```powershell
pip list | Select-String -Pattern "(unimpeded|jupyter|anesthetic)"
```

You should see:
- `unimpeded` (with editable project location)
- `jupyter`
- `anesthetic`
- Related jupyter packages

---

**Note:** This setup uses an **editable install** (`pip install -e .`), which means changes to the source code will be reflected immediately without reinstalling. If you just want to use unimpeded without modifying it, you can use `pip install unimpeded` instead.
