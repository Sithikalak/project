from pathlib import Path
import subprocess,sys,time,os
root=Path(__file__).resolve().parent
paths=[root/'group_pipeline.ipynb']+sorted((root/'notebooks').glob('*_Model_*.ipynb'))+sorted(p for p in (root/'notebooks').glob('*.ipynb') if '_Model_' not in p.name)+[root/'implementation_pipeline.ipynb']
for path in paths:
    print('RUN',path.name,flush=True);start=time.time()
    subprocess.run([sys.executable,str(root/'src/execute_notebook.py'),str(path)],check=True,cwd=root,
                   env={**os.environ,'OPENBLAS_NUM_THREADS':'2','OMP_NUM_THREADS':'2'})
    print('DONE',path.name,round(time.time()-start,1),'seconds',flush=True)
print('All notebooks executed successfully.',flush=True)
