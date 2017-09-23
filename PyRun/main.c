// ExEngineCore.cpp : 定义控制台应用程序的入口点。
//
#include "Python.h"
#include <stdio.h>

int
wmain(int argc, wchar_t **argv)
{
	extern int Py_OptimizeFlag;
	extern int Py_NoSiteFlag;
	Py_OptimizeFlag = 2; //1 for -O, and 2 for -OO
	Py_NoSiteFlag = 1; //why need site module?
	Py_SetProgramName(L"PyRun");
	/*Get the absolute path of the libcore.zip*/
	//wchar_t *path = Py_GetProgramFullPath();
	wchar_t *path = argv[0];
	wchar_t libpath[1024];
	wcscpy(libpath, path);
	wchar_t *pos = libpath + wcslen(path);
	wcscpy(pos, L"/../libcore.zip;");
	//add packages
	pos = libpath + wcslen(libpath);
	wcscpy(pos, path);
	pos = libpath + wcslen(libpath);
	wcscpy(pos, L"/../packages;");
	//printf("%ls", libpath);
	Py_SetPath(libpath); // absolute path of libcore.zip is need when debug
	Py_Initialize();
	PySys_SetArgv(argc, argv); //Set sys.argv
	PyRun_SimpleString("import os\n"
		"import sys\n"
		"if not os.path.exists('packages') or os.path.isfile('packages'):\n"
		"    os.mkdir('packages')\n"
		"sys.path.append('packages')\n"
		"for name in os.listdir('packages'):\n"
		"    path = os.path.join('packages', name)\n"
		"    if(os.path.isfile(path) and name.endswith('.zip')):\n"
		"        sys.path.append(path)\n");
	PyRun_SimpleString("try:\n"
		"    __import__(os.path.splitext(os.path.basename(sys.argv[0]))[0])\n"
		"except Exception as ex:\n"
		"    print('>>>>>>>>')\n"
		"    print(ex)\n"
		"    print('<<<<<<<<')\n"
		"    print('Press any key to exit...')\n"
		"    sys.stdin.read(1)\n");
	Py_Finalize();
	return 0;
}

