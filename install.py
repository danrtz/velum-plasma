#!/usr/bin/env python3
"""Install the full Velum KDE shell locally; no publishing."""
import os,sys
from pathlib import Path
os.execv(sys.executable,[sys.executable,str(Path(__file__).parent/'shell/kde/install.py'),*sys.argv[1:]])
