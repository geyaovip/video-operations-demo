#!/usr/bin/env python3
"""从唯一HTML生成Cloudflare Pages静态目录，不发布文档、原片或本机数据。"""
from pathlib import Path
import argparse
import base64
import hashlib
import re
import importlib.util
import json
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def build(output):
    target = Path(output).resolve()
    if target == ROOT or ROOT in target.parents:
        raise ValueError('静态输出请使用项目外临时目录，避免混入源码目录')
    if target.exists() and any(target.iterdir()):
        raise ValueError('输出目录必须为空，避免覆盖已有文件')
    spec = importlib.util.spec_from_file_location('videoops_check', ROOT / '工具/检查交付.py')
    checker = importlib.util.module_from_spec(spec)
    exec(compile((ROOT / '工具/检查交付.py').read_text(), str(ROOT / '工具/检查交付.py'), 'exec'), checker.__dict__)
    checker.check(include_package=False, runtime_only=True)
    target.mkdir(parents=True, exist_ok=True)
    source_html = (ROOT / '视频运营.html').read_text()
    extracted = {}
    original_urls = {}
    extensions = {'image/png': 'png', 'image/jpeg': 'jpg', 'video/mp4': 'mp4', 'audio/mp4': 'm4a'}
    def separate_media(match):
        mime, encoded = match.groups()
        data = base64.b64decode(encoded, validate=True)
        digest = hashlib.sha256(data).hexdigest()
        name = '媒体/内嵌/' + digest[:24] + '.' + extensions[mime]
        extracted[name] = data
        original_urls['/' + name] = match.group(0)
        return '/' + name
    html = re.sub(r'data:((?:image/png|image/jpeg|video/mp4|audio/mp4));base64,([A-Za-z0-9+/=]+)', separate_media, source_html).encode('utf-8')
    restored = html.decode('utf-8')
    for url, original in original_urls.items():
        restored = restored.replace(url, original)
    if restored != source_html:
        raise ValueError('媒体提取改变了非媒体内容，已停止发布')
    for name, data in extracted.items():
        asset = target / name
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_bytes(data)
    (target / 'index.html').write_bytes(html)
    (target / '视频运营.html').write_bytes(html)
    for name, source in checker.package_files().items():
        if not name.startswith(('媒体/', '第三方许可/')):
            continue
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
    (target / '_headers').write_text('''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
/
  Cache-Control: no-cache
/*.html
  Cache-Control: no-cache
''')
    # 明确不存在的资源返回404，避免把文档／原片请求伪装成SPA成功页面。
    (target / '404.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>页面不存在</title><h1>页面不存在</h1><a href="/">返回视频运营</a></html>')
    return {'output': str(target), 'files': sum(p.is_file() for p in target.rglob('*')), 'html_bytes': len(html), 'source_bytes': len(source_html.encode('utf-8')), 'extracted_media_files': len(extracted)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=None, help='项目外的空目录，默认创建系统临时目录')
    args = parser.parse_args()
    destination = args.output or tempfile.mkdtemp(prefix='videoops-pages-')
    print(json.dumps(build(destination), ensure_ascii=False, indent=2))
