#!/usr/bin/env python3
"""使用现有Wrangler登录发布到本项目Pages，不创建令牌或保存云凭据。"""
from pathlib import Path
import argparse
import importlib.util
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = 'weibot-video-operations-demo'
VERSION = '4.149.0'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wrangler-js', help='可选，现有Wrangler CLI的完整路径')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('videoops_site', ROOT / '工具/构建静态站.py')
    builder = importlib.util.module_from_spec(spec)
    exec(compile((ROOT / '工具/构建静态站.py').read_text(), str(ROOT / '工具/构建静态站.py'), 'exec'), builder.__dict__)
    with tempfile.TemporaryDirectory(prefix='videoops-pages-') as folder:
        builder.build(folder)
        command = [shutil.which('node'), args.wrangler_js] if args.wrangler_js else ['npx', '--yes', 'wrangler@' + VERSION]
        command += ['pages', 'deploy', folder, '--project-name', PROJECT, '--branch', 'main']
        revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
        if revision.returncode == 0:
            command += ['--commit-hash', revision.stdout.strip()]
        subprocess.run(command, cwd=ROOT, check=True)
