#!/usr/bin/env python3
"""Yayındaki sitenin adresini Git uzak deposundan türetir (https://<sahip>.github.io/<depo>/). Adres koda yazılmaz."""
import re, subprocess, sys

try:
    url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True).stdout.strip()
except Exception:
    sys.exit("origin uzak deposu yok")
m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", url)
if not m:
    sys.exit("origin bir GitHub deposu değil")
print("https://%s.github.io/%s/" % (m.group(1).lower(), m.group(2)))
