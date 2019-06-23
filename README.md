DuplicatesFinder
=============



**This application is built on python 2.4 and py2exe**


### Files ###
* dupsfinder.py - Console Application
* DuplicateFinder.py - TkInter Application
* setup.py - The setup file required by py2exe
    
### Build ###
* c:\Python24\python.exe setup.py py2exe

### Run ###
Run using python 2.4 - <python.exe> DuplicateFinder.py
<code>c:\Python24\python.exe DuplicateFinder.py</code>


#### Prerequisites on python 2.4 changes ####
* Install py2exe
* Go to: C:\Python24\Lib\site-packages\py2exe\build_exe.py : (1276)
<pre>
    Change:
        self.dlls_in_exedir = [python_dll,
                                   "w9xpopen%s.exe" % (is_debug_build and "_d" or ""),
                                   "msvcr71%s.dll" % (is_debug_build and "d" or "")]
        self.dlls_in_exedir = [python_dll,
                                       "w9xpopen%s.exe" % (is_debug_build and "_d" or ""),
                                       "msvcr71%s.dll" % (is_debug_build and "d" or ""),
                                       "tcl84.dll",
                                       "tk84.dll"]
  </pre>
