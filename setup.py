# from distutils.core import setup
# import py2exe
#
# setup(console=['dupsfinder.py'])

# Requires wxPython.  This sample demonstrates:
#
# - single file exe using wxPython as GUI.
import os
from distutils.core import setup
import py2exe
import sys

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "1.0.0"
        self.company_name = "Ohad Cohen"
        self.copyright = "no copyright"
        self.name = "DuplicateFinder"

################################################################
# A program using wxPython

# The manifest will be inserted as resource into dupsfinder.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store it in a file named
# dupsfinder.exe.manifest, and copy it with the data_files option into
# the dist-dir.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

DuplicateFinder = Target(
    # used for the versioninfo resource
    description = "A duplicate lines in text file finder",

    # what to build
    script = "DuplicateFinder.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="DuplicateFinder"))],
##    icon_resources = [(1, "icon.ico")],
    dest_base = "DuplicateFinder")

################################################################

setup(
    options = {"py2exe": {"compressed": 1,
                          "optimize": 2,
                          "ascii": 1,
                          "bundle_files": 1}},
    zipfile = None,
    data_files=[('.', [os.path.join(os.getcwd(), 'settings.ini')])],
    windows = [DuplicateFinder],
    )
