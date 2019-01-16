#include "Python.h"
#include <stdio.h>
#include <stdlib.h>

wchar_t* wcs_append(wchar_t* pos, const wchar_t* content)
{
	wcscpy(pos, content);
	pos = pos + wcslen(content);
	return pos;
}

int
wmain(int argc, wchar_t **argv)
{
	extern int Py_OptimizeFlag;
	extern int Py_NoSiteFlag;
	Py_OptimizeFlag = 2; //1 for -O, and 2 for -OO
	Py_NoSiteFlag = 1; //why need site module?
	Py_SetProgramName(argv[0]); //full path of the programe, needed by multiprocessing
	                            // need combine with cwd to get full path

	/*Get the absolute path of the program*/
	//wchar_t *path = Py_GetProgramFullPath();
	wchar_t *path = argv[0];

	/*Set PATH for dll search, It cannot be used for pythonXX.dll, 
	  because this dll is needed before the wmain executed*/
	const wchar_t *os_path = _wgetenv(L"PATH");
	const char *os_path1 = getenv("PATH");
	wchar_t* path_env = malloc((wcslen(os_path) + 1024) * 2);
	wchar_t* pos = path_env;
	pos = wcs_append(pos, L"PATH=");
	pos = wcs_append(pos, path);
	pos = wcs_append(pos, L"/../DLLs;");
	//pos = wcs_append(pos, L"C:/Anaconda3/Library/bin;"); //for dll debug
	pos = wcs_append(pos, os_path); //comment this, and import sqlite3 to test dll finder
	int iRet = _wputenv(path_env);
	free(path_env);
	if (iRet < 0)
	{
		printf("set PATH error\n");
		return 1;
	}

	/*Get the absolute path of the python.zip*/
	wchar_t libpath[1024];
	pos = libpath;
	pos = wcs_append(pos, path);
	pos = wcs_append(pos, L"/../packages/;");
	pos = wcs_append(pos, path);
	pos = wcs_append(pos, L"/../scripts/;");
	pos = wcs_append(pos, path);
	pos = wcs_append(pos, L"/../packages/python.zip;");
	//printf("%ls", libpath);
	Py_SetPath(libpath); // Cannot be removed
	Py_Initialize();
	PySys_SetArgv(argc, argv); //Set sys.argv
	PyRun_SimpleString("import hook\n"
		"hook.register()\n"
	);
	PyRun_SimpleString("import sys\n"
		"if sys.platform == 'win32': sys.frozen = True\n"
	);
	PyRun_SimpleString("try:\n"
		"    import os, sys, runpy\n"
		"    import traceback\n"
		"    module = '__main__' + os.path.splitext(os.path.basename(sys.argv[0]))[0]\n"
		"    runpy._run_module_as_main(module)\n"
		"except Exception as ex:\n"
		"    print('>>>>>>>>')\n"
		"    print(ex)\n"
		"    traceback.print_exc()\n"
		"    print('<<<<<<<<')\n"
		"    print('Press any key to exit...')\n"
		"    sys.stdin.read(1)\n");
	Py_Finalize();
	return 0;
}
