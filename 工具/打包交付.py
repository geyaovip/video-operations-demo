#!/usr/bin/env python3
"""生成唯一当前交付包；不打入原片、草稿、文档历史或检查输出。"""
from pathlib import Path
import importlib.util
import json
import os
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('videoops_delivery_check', ROOT / '工具/检查交付.py')
check_module = importlib.util.module_from_spec(spec)
# 不产生__pycache__；将该检查模块作为源码执行。
exec(compile((ROOT / '工具/检查交付.py').read_text(), str(ROOT / '工具/检查交付.py'), 'exec'), check_module.__dict__)


def main():
    check_module.check(include_package=False, runtime_only=True)
    target = check_module.PACKAGE
    target.parent.mkdir(exist_ok=True)
    payloads = {name: path.read_bytes() for name, path in check_module.package_files().items()}
    handle, filename = tempfile.mkstemp(prefix='videoops-package-', suffix='.zip', dir=target.parent)
    os.close(handle)
    temporary = Path(filename)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, data in payloads.items():
                archive.writestr(name, data)
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError('交付包CRC检查失败')
            for name, data in payloads.items():
                if archive.read(name) != data:
                    raise ValueError('打包内容不一致：' + name)
        for name, path in check_module.package_files().items():
            if path.read_bytes() != payloads[name]:
                raise ValueError('打包期间正式文件变化，请重新执行')
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(json.dumps(check_module.check(runtime_only=True), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
