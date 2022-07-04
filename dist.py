#!/usr/bin/env python
# encoding: utf-8
"""
dist.py

Bundle up the libraries into individual zips and an omnibus collection

Created by Christian Swinehart on 2014/04/21.
Copyright (c) 2014 Samizdat Drafting Co All rights reserved.
"""


import sys
import os
from glob import glob
from os.path import dirname, basename, join
py_root = os.path.dirname(os.path.abspath(__file__))
_mkdir = lambda pth: os.path.exists(pth) or os.makedirs(pth)

dist_root = join(py_root,'dist')

def main():
  _mkdir(dist_root)
  libs = [dirname(p) for p in glob('%s/*/__init__.py'%py_root)]
  for lib in libs:
    print(lib)
    LIBDIR = basename(lib)
    ZIP = "%s/%s.zip"%(dist_root, LIBDIR)
    os.system('ditto -ck --keepParent "%s" "%s"' % (LIBDIR, ZIP))

  print("plotdevice-libs")
  os.system('zip -r -q "%s/plotdevice-libs.zip" %s'%(dist_root, ' '.join(basename(l) for l in libs)))

if __name__ == "__main__":
  main()
