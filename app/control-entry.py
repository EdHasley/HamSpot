# Root-owned entry point; isolated Python ignores environment and user site packages.
import runpy
import sys
sys.path.insert(0,'/opt/hamspot/app')
runpy.run_path('/opt/hamspot/app/control.py',run_name='__main__')
