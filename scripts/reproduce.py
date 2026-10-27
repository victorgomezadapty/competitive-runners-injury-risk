"""One entry point; authored code only. Network is needed only for acquisition."""
from pathlib import Path
import subprocess,sys,argparse
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--notebooks',action='store_true',help='Also execute all 11 authored result notebooks')
    parser.add_argument('--complementary',action='store_true',help='Acquire/profile separate complementary cohorts')
    args=parser.parse_args()
    scripts=['download_data.py','run_milestone_01.py','run_phase_02.py','write_phase_02_report.py','run_final_analysis.py']
    if args.complementary:
        scripts+=['acquire_soccermon_subjective.py','profile_complementary.py','acquire_wu_supplement.py','profile_wu_supplement.py']
    scripts+=['build_release.py']
    for script in scripts:
        subprocess.run([sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,check=True)
    if args.notebooks:
        subprocess.run([sys.executable,'scripts/execute_notebooks.py','--start','1','--end','11'],cwd=ROOT,check=True)
    print('Numerical reproduction complete. Web build: cd web && npm run build. Publishing requires your own platform accounts.')

if __name__=='__main__': main()
