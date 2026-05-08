"""Bare Repo Scanner — v0.14.0 嵌入式裸仓库检测器。"""
from __future__ import annotations
import os

class BareRepoScanner:
    def scan_directory(self, root_path:str)->list[str]:
        found=[]
        if not os.path.exists(root_path):return found
        for root,dirs,_ in os.walk(root_path):
            for d in dirs:
                if d==".git":
                    full=os.path.join(root,d)
                    head_path=os.path.join(full,"HEAD")
                    config_path=os.path.join(full,"config")
                    if not os.path.exists(head_path) and os.path.exists(config_path):
                        found.append(root)
        return found
