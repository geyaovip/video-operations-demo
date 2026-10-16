#!/usr/bin/env python3
"""只读检查当前单HTML、素材、文档链接和交付包；不操作浏览器存储。"""
from pathlib import Path
from hashlib import sha256
from urllib.parse import quote, unquote, urlsplit
from urllib.request import urlopen
import argparse
import json
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / '交付/视频运营_交付包.zip'


def package_files():
    files = {'视频运营.html': ROOT / '视频运营.html',
             '打开说明.md': ROOT / '交付/使用说明.md',
             '第三方许可/Tabler-icons-LICENSE.txt': ROOT / '参考资料/许可/Tabler-icons-LICENSE.txt'}
    media = sorted((ROOT / '媒体/成片').glob('*.mp4')) + sorted((ROOT / '媒体/封面').glob('*.jpg'))
    if len(media) != 30:
        raise ValueError('运行媒体应为12条成片及18张封面；请核对清单后调整打包规则')
    files.update({p.relative_to(ROOT).as_posix(): p for p in media})
    return files


def check(url=None, include_package=True, runtime_only=False):
    source = (ROOT / '视频运营.html').read_bytes()
    html = source.decode('utf-8')
    node = shutil.which('node')
    if not node:
        raise RuntimeError('需要Node.js执行内联JavaScript语法检查')
    with tempfile.TemporaryDirectory(prefix='videoops-check-') as folder:
        script = Path(folder) / 'inline.js'
        script.write_text(html[html.index('<script>') + 8:html.rindex('</script>')])
        subprocess.run([node, '--check', str(script)], check=True, capture_output=True, text=True)
    manifest = json.loads((ROOT / '媒体/素材清单.json').read_text())['files']
    listed = set()
    for entry in manifest:
        if runtime_only and not entry['path'].startswith(('媒体/成片/', '媒体/封面/')):
            continue
        path = ROOT / entry['path']
        if ROOT not in path.resolve().parents:
            raise ValueError('媒体清单路径越界')
        data = path.read_bytes()
        if len(data) != entry['bytes'] or sha256(data).hexdigest() != entry['sha256']:
            raise ValueError('素材与清单不一致：' + entry['path'])
        listed.add(path.relative_to(ROOT).as_posix())
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / '媒体').rglob('*')
              if p.is_file() and p.name not in {'素材清单.json', '.DS_Store'}}
    if runtime_only:
        actual = {name for name in actual if name.startswith(('媒体/成片/', '媒体/封面/'))}
    if listed != actual:
        raise ValueError('素材文件与清单的路径集合不一致')
    docs = [ROOT / 'README.md', ROOT / 'AGENTS.md', *(ROOT / '文档').rglob('*.md'),
            *(ROOT / '交付').glob('*.md'), *(ROOT / '参考资料').rglob('*.md'), *(ROOT / '品牌').rglob('*.md')]
    broken = []
    for doc in docs:
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', doc.read_text()):
            target = target.strip().strip('<>')
            if urlsplit(target).scheme or target.startswith('#'):
                continue
            target = unquote(target.split('#', 1)[0])
            if target and (doc.parent / target).resolve() == PACKAGE and not include_package:
                continue
            if target and not (doc.parent / target).exists():
                broken.append(str(doc.relative_to(ROOT)) + ' -> ' + target)
    if broken:
        raise ValueError('文档存在失效链接：' + '; '.join(broken))
    if include_package:
        expected = package_files()
        with zipfile.ZipFile(PACKAGE) as archive:
            if len(archive.namelist()) != len(set(archive.namelist())):
                raise ValueError('交付ZIP中有重复路径')
            if archive.testzip() is not None or set(archive.namelist()) != set(expected):
                raise ValueError('交付ZIP损坏或文件集合不一致')
            for name, path in expected.items():
                if archive.read(name) != path.read_bytes():
                    raise ValueError('交付ZIP与正式文件不一致：' + name)
    if url:
        base = url.rstrip('/') + '/'
        if urlopen(base + quote('视频运营.html'), timeout=15).read() != source:
            raise ValueError('HTTP服务返回的HTML与正式源码不一致')
        sample = '媒体/封面/MAT-02.jpg'
        if urlopen(base + quote(sample), timeout=15).read() != (ROOT / sample).read_bytes():
            raise ValueError('HTTP媒体路径不可用或内容不一致')
    return {'html_sha256': sha256(source).hexdigest(), 'javascript_syntax': 'passed',
            'media_files_verified': len(listed), 'document_links': 'passed',
            'package_files_verified': len(package_files()) if include_package else None,
            'http': 'passed' if url else 'not requested'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', help='项目根目录静态服务地址，例如http://127.0.0.1:8797')
    parser.add_argument('--runtime-only', action='store_true', help='只核验30个运行媒体，供无本地原片的Git克隆及部署使用')
    parser.add_argument('--source-only', action='store_true', help='跳过交付包检查')
    args = parser.parse_args()
    print(json.dumps(check(args.url, not args.source_only, args.runtime_only), ensure_ascii=False, indent=2))
