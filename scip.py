import os
import click
import json
from pathlib import Path
import subprocess

index_dir = Path('index_dir') / 'scip'

@click.command()
@click.argument('workspace_path', type=click.Path(exists=True, dir_okay=True))
@click.argument('target', type=click.Path(exists=True, dir_okay=True))
@click.option('--print', is_flag=True, help='Print SCIP index data in json format')
def scip(workspace_path:str, target:str, print):
    index_dir.mkdir(exist_ok=True, parents=True)

    abs_wspath = Path(workspace_path).absolute()
    abs_target = Path(workspace_path).absolute() / target
    ws_name = os.path.basename(abs_wspath)

    index_wspath = index_dir / ws_name
    index_wspath.mkdir(exist_ok=True, parents=True)

    if abs_wspath == abs_target:
        rel_target = abs_target.relative_to(abs_wspath)
        scip_index_path = 'index.scip'
        scip_index_path = os.path.join(index_wspath, scip_index_path)

        click.echo(f'workspace name : {ws_name}')
        click.echo(f'rel target : {rel_target}')
        click.echo(f'rel scip path : {scip_index_path}')
    elif abs_target.is_dir():
        rel_target = abs_target.relative_to(abs_wspath)

        scip_index_path = rel_target.as_posix() + '.scip'
        scip_index_path = os.path.join(index_wspath, scip_index_path)

        click.echo(f'workspace name : {ws_name}')
        click.echo(f'rel target is a directory')
        click.echo(f'rel target : {rel_target}')
        click.echo(f'rel scip path : {scip_index_path}')
    else:
        rel_target = abs_target.relative_to(abs_wspath)
        name = rel_target.stem
        dirpath = os.path.dirname(rel_target)

        scip_index_path = os.path.join(dirpath, name + '.scip')
        scip_index_path = scip_index_path.replace(os.path.sep, '.')
        scip_index_path = os.path.join(index_wspath, scip_index_path)

        click.echo(f'workspace name : {ws_name}')
        click.echo(f'rel target is a file')
        click.echo(f'rel target : {rel_target}')
        click.echo(f'rel target stem  : {name}')
        click.echo(f'rel target dirpath : {dirpath}')
        click.echo(f'rel scip path : {scip_index_path}')

    
    subproc = subprocess.Popen([
                'scip-python',
                'index',
                '--target-only',
                abs_target,
                '--output',
                scip_index_path
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    for line in iter(subproc.stdout.readline, b''):
        click.echo(line.decode().rstrip())

    subproc.wait()

    click.echo(f'return code : {subproc.returncode}')

    if print:
        scip = Path('~/workspace/scip/scip').expanduser()
        
        subproc = subprocess.Popen([
                scip,
                'print',
                '--color=false',
                '--json',
                scip_index_path
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        out, err = subproc.communicate()

        out = out.decode('utf8')

        with open(scip_index_path + '.json', 'w') as f:
            f.write(json.dumps(json.loads(out), indent=2))

if __name__ == '__main__':
    scip()