// ExEngineCore.cpp : 定义控制台应用程序的入口点。
//
#include "Python.h"
#include <locale.h>
#include "stdafx.h"

int
wmain(int argc, wchar_t **argv)
{
	extern int Py_OptimizeFlag;
	extern int Py_NoSiteFlag;
	Py_OptimizeFlag = 2; //1 for -O, and 2 for -OO
	Py_NoSiteFlag = 1; //why need site module?
	Py_SetProgramName(L"PyRun");
	/*Get the absolute path of the libcore.zip*/
	wchar_t *path = Py_GetProgramFullPath();
	wchar_t libpath[500];
	wcscpy(libpath, path);
	wchar_t *pos = libpath + wcslen(path);
	wcscpy(pos, L"/../libcore.zip;");
	//printf("%ls", libpath);
	Py_SetPath(libpath); // absolute path of libcore.zip is need when debug
	Py_Initialize(); 
	PyRun_SimpleString("import os\n"
		"import sys\n"
		"if not os.path.exists('packages') or os.path.isfile('packages'):\n"
		"    os.mkdir('packages')\n"
		"sys.path.append('packages')\n"
		"for name in os.listdir('packages'):\n"
		"    path = os.path.join('packages', name)\n"
		"    if(os.path.isfile(path) and name.endswith('.zip')):\n"
		"        sys.path.append(path)\n");
	char script[500];
	sprintf_s(script, 500,
		"try:\n"
		"    import %ls\n"
		"except Exception as ex:\n"
		"    print('>>>>>>>>')\n"
		"    print(ex)\n"
		"    print('<<<<<<<<')\n"
		"    print('Press any key to exit...')\n"
		"    sys.stdin.read(1)\n", argv[0]);
	printf("%s", script);
	PyRun_SimpleString(script);
	Py_Finalize();
	return 0;
}

