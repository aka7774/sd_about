import os
import sys
import platform
import shutil
import datetime
import torch

import gradio as gr

from launch import run
from modules import script_callbacks, sd_models, shared, extensions

def on_ui_tabs():
    with gr.Blocks() as about:
        with gr.Row():
            about_basic = gr.Textbox(label="Basic",lines=20,value=print_about_basic(),Interactive=False)
            about_detail = gr.Textbox(label="Detail",lines=20,value=print_about_detail(),Interactive=False)

    return (about, "About", "about"),

script_callbacks.on_ui_tabs(on_ui_tabs)

def print_about_basic():
    rs = []

    try:
        rs.append(f"Reported at {datetime.datetime.now()} by github.com/aka7774/sd_about")
    except:
        rs.append(f"Reported by github.com/aka7774/sd_about")

    try:
        rs.append(f"Python {sys.version}")
    except:
        rs.append(f"Python: unknown")

    try:
        free, total = torch.cuda.mem_get_info()
        rs.append(f"GPU {torch.cuda.get_device_name()}, VRAM: {gib(total)} GiB")
    except:
        rs.append(f"GPU: unknown")

    rs.append(f'argv: {" ".join(sys.argv[1:])}')

    try:
        git = os.environ.get('GIT', "git")
        commithash = run(f"{git} rev-parse HEAD").strip()
        rs.append('stable-diffusion-webui: ' + commithash)
    except:
        pass

    try:
        import diffusers
        rs.append(f"diffusers: {diffusers.__version__}")
    except:
        rs.append('diffusers: unknown')

    try:
        rs.append(f"torch: {torch.__version__}")
    except:
        rs.append('torch: unknown')

    try:
        import torchvision
        rs.append(f"torchvision: {torchvision.__version__}")
    except:
        rs.append('torchvision: unknown')

    try:
        import transformers
        rs.append(f"transformers: {transformers.__version__}")
    except:
        rs.append('transformers: unknown')

    try:
        # Dreambooth流
        from diffusers.utils.import_utils import is_xformers_available
        if is_xformers_available():
            import xformers
            import xformers.ops
            rs.append(f"xformers: {transformers.__version__}")
        else:
            rs.append('xformers: none')
    except:
        try:
            # だめならpipで見る
            python = sys.executable
            xformers = run(f"{python} -m pip show xformers")
            for line in xformers.split("\n"):
                values = line.split(':')
                if values[0] == 'Version' and values[1]:
                    rs.append(f"xformers: {values[1]}")
                    break
        except:
            rs.append('xformers: unknown')

    return "\n".join(rs)

def print_about_detail():
    rs = []

    try:
        rs.append(f"Reported at {datetime.datetime.now()} by github.com/aka7774/sd_about")
    except:
        rs.append(f"Reported by github.com/aka7774/sd_about")

    try:
        rs.append(f"{platform.system()} ({platform.platform()})")
    except:
        rs.append(f"platform: unknown")

    try:
        rs.append(f"{platform.machine()} ({platform.processor()})")
    except:
        rs.append(f"processor: unknown")

    try:
        # Windowsでは取れない
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        rs.append(f'Memory total: {gib(mem_bytes)} GiB')
    except:
        try:
            import psutil
            mem = psutil.virtual_memory()
            rs.append(f'Memory: {gib(mem.total)} GiB')
        except:
            rs.append('Memory: unknown')

    try:
        total, used, free = shutil.disk_usage(os.path.abspath('.'))
        rs.append(f"Disk: {gib(total - free)} / {gib(total)} GiB")
    except:
        rs.append('Disk: unknown')

    rs.append('')

    try:
        git = os.environ.get('GIT', "git")
        for ext in extensions.extensions:
            if ext.is_builtin or not ext.enabled:
                continue
            commithash = run(f"{git} -C {os.path.abspath(ext.path)} rev-parse HEAD").strip()
            rs.append(f"{ext.name}: {commithash}")
    except:
        rs.append('Extensions: unknown')

    return "\n".join(rs)

def get_commithash(url):
    try:
        import requests
        commits = requests.get(url).json()
        return commits['commit']['sha']
    except Exception as e:
        return 'failed'

def gib(bytes):
    return round(bytes / (2**30), 2)
