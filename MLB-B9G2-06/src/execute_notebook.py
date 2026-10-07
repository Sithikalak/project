"""Execute trusted project Python cells sequentially without a network Jupyter kernel.
Records real stdout, rich tables and PNG figures; no synthetic/precomputed outputs.
Each notebook is run in its own Python process by run_all.py.
"""
import sys,os,io,base64,contextlib,traceback
from pathlib import Path
import nbformat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import IPython.display
path=Path(sys.argv[1]).resolve();root=Path(__file__).resolve().parents[1];os.chdir(root)
nb=nbformat.read(path,4);ns={'__name__':'__main__'};active=[]
def display(*objects,**kwargs):
    for obj in objects:
        data={'text/plain':str(obj)}
        if hasattr(obj,'_repr_html_'):
            val=obj._repr_html_()
            if val:data['text/html']=val
        active.append(nbformat.v4.new_output('display_data',data=data,metadata={}))
def show(*args,**kwargs):
    for num in plt.get_fignums():
        buf=io.BytesIO();plt.figure(num).savefig(buf,format='png',dpi=120,bbox_inches='tight')
        active.append(nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode(buf.getvalue()).decode(),'text/plain':'<Executed matplotlib figure>'},metadata={}))
IPython.display.display=display;plt.show=show
counter=0
for i,cell in enumerate(nb.cells):
    if cell.cell_type!='code':continue
    counter+=1;active=[];stream=io.StringIO();cell.execution_count=counter
    print(' CELL',i,flush=True)
    try:
        with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):exec(compile(cell.source,f'{path.name}:cell{i}','exec'),ns)
    except Exception as exc:
        if stream.getvalue():active.insert(0,nbformat.v4.new_output('stream',name='stdout',text=stream.getvalue()))
        active.append(nbformat.v4.new_output('error',ename=type(exc).__name__,evalue=str(exc),traceback=traceback.format_exc().splitlines()))
        cell.outputs=active;nbformat.write(nb,path);raise
    if stream.getvalue():active.insert(0,nbformat.v4.new_output('stream',name='stdout',text=stream.getvalue()))
    cell.outputs=active;nbformat.write(nb,path)
nb.metadata['execution_method']='Sequential Python execution, one fresh process per notebook; real stdout, HTML tables and PNG capture. No Jupyter kernel sockets in build environment.'
nbformat.validate(nb);nbformat.write(nb,path)
