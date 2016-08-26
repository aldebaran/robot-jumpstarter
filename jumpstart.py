#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK
"""
jumpstart.py

A script for generating a NAOqi project from a tamplate folder.
"""

__version__ = "0.1.1"

__copyright__ = "Copyright 2015-2016, SBRE"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'

import os
import shutil
import re

import distutils.dir_util

argcomplete = None
try:
    import argcomplete
except Exception as e:
    pass

TEMPLATES = "templates"
OUTPUT = "output"

FILETYPES_TO_REPROCESS = [".xar", ".pml", ".manifest", ".py", ".js", ".json",
                          ".xml", ".html", ".top", ".dlg"]
                          

def rename_in_file(filepath, sourceword, destword):
    sourcere = re.compile(r"\b" + sourceword + r"\b")
    # Does this pattern even occur in this file? (most of the time, it won't)
    with open(filepath) as f:
        if not any(sourcere.search(line) for line in f):
            return False# We're done here.
    # pattern is in the file, so perform replace operation.

    with open(filepath) as f:
        temp_filepath = filepath + ".tmp"
        out = open(temp_filepath, "w")
        for line in f:
            out.write(sourcere.sub(destword, line))
        f.close()
        out.close()
        os.unlink(filepath)
        os.rename(temp_filepath, filepath)
    return True

def rename_in_folder(folder, sourceword, destword):
    files = list(os.listdir(folder))
    for filename in files:
        if filename.startswith("."):
            continue
        filepath = os.path.join(folder, filename)
        # 1) replace everything inside
        if os.path.isdir(filepath):
            rename_in_folder(filepath, sourceword, destword)
        else:
            extension = os.path.splitext(filename)[-1].lower()
            if extension in FILETYPES_TO_REPROCESS:
                if rename_in_file(filepath, sourceword, destword):
                    print "Renamed inside", filename
        # 2) rename if needed
        if sourceword in filename:
            newfilename = filename.replace(sourceword, destword)
            os.rename(filepath, os.path.join(folder, newfilename))
            print "Renamed", filename

def generate(sourcename, destname, servicename=None):
    "Generate a folder based on a template, or add to an existing one."
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)
    sourcepath = os.path.join(TEMPLATES, sourcename)
    destpath = os.path.join(OUTPUT, destname)
    if not os.path.exists(sourcepath):
        raise Exception, "Template not found: " + repr(sourcename)
    project_exists = os.path.exists(destpath)
    if project_exists:
        shutil.move(destpath, destpath + "_TEMP")
        print "Project already exists, only adding new files to it"
    shutil.copytree(sourcepath, destpath)
    rename_in_folder(destpath, sourcename, destname)

    if servicename:
        # script name (used by ALServiceManager) should be underscore
        scriptname = servicename.lower()
        # service name (used in ServiceDirectory) should be capitalized
        if not servicename[0].isupper():
            servicename = servicename.capitalize()
        rename_in_folder(destpath, "ALMyService", servicename)
        rename_in_folder(destpath, "myservice", scriptname)

    if project_exists:
        distutils.dir_util.copy_tree(destpath + "_TEMP", destpath)
        shutil.rmtree(destpath + "_TEMP")
        print "Done adding to", destname, "from", sourcename, 
    else:
        print "Done generating", destname, "from", sourcename, 
    
    
def test_run():
    #generate("pythonapp", "mytestapp")
    generate("service-tabletpage", "servicetestapp", "ALSuperDuperService")

# Used for argcomplete
class TemplateCompleter(object):
    def __init__(self):
        self.choices = os.listdir("templates")

    def __call__(self, prefix, **kwargs):
        return (c for c in self.choices if c.startswith(prefix))


def run_with_sysargs():
    import argparse
    parser = argparse.ArgumentParser(description='Generates a project.')
    parser.add_argument('sourcename', type=str,
                       help='name of source recipe/template').completer = TemplateCompleter()
    parser.add_argument('destname', type=str,
                       help='name of new project to create')
    parser.add_argument('servicename', type=str,
                       help='optional, name of service to create',
                       nargs='?')
    if argcomplete:
        argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if (args.servicename):
        generate(args.sourcename, args.destname, args.servicename)
    else:
        generate(args.sourcename, args.destname)

if __name__ == "__main__":
    #test_run()
    #rename_in_folder("./output/basicparams/", "basicparams", "volumeslider")
    run_with_sysargs()

