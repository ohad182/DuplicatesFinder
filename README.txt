This application is built on python 2.4 and py2exe

dupsfinder.py - Console Application
DuplicateFinder.py - TkInter Application

Required python 2.4 changes:
- go to: C:\Python24\Lib\site-packages\py2exe\build_exe.py : (1276_
    change:
        self.dlls_in_exedir = [python_dll,
                                   "w9xpopen%s.exe" % (is_debug_build and "_d" or ""),
                                   "msvcr71%s.dll" % (is_debug_build and "d" or "")]
        self.dlls_in_exedir = [python_dll,
                                       "w9xpopen%s.exe" % (is_debug_build and "_d" or ""),
                                       "msvcr71%s.dll" % (is_debug_build and "d" or ""),
                                       "tcl84.dll",
                                       "tk84.dll"]