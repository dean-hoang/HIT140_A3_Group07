"""Run the whole Objective 2 pipeline in order:  python run_all.py"""
import runpy, sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC))
for script in ["01_build_datasets.py",
               "02_regression_2_1_goal_difference.py",
               "03_regression_2_2_team_goals.py",
               "04_check_no_leakage.py"]:
    print(f"\n>>> running {script}")
    runpy.run_path(str(SRC / script), run_name="__main__")
