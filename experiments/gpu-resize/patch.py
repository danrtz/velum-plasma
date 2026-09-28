"""Apply to a clean KWin 6.7.5 source tree only."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
with (root/'gpu-resize.patch').open() as patch:
 subprocess.run(['patch','-p1','--forward'],cwd=root/'kwin-6.7.5',stdin=patch,check=True)
