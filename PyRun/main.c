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
	Py_NoSiteFlag = 1; //需要导入site，依赖很多包？？
	Py_SetProgramName("CExEngine");
	wchar_t *path = Py_GetProgramFullPath();
	Py_SetPath(L"libcore.zip;packages;");
	Py_Initialize();
	PyRun_SimpleString("import sys"); //
	char script[200];
	sprintf_s(script, 200, "try:\n"
		"    import %s\n"
		"except Exception as ex:\n"
		"    print('>>>>>>>>')\n"
		"    print(ex)\n"
		"    print('<<<<<<<<')\n"
		"    print('Press any key to exit...')\n"
		"    sys.stdin.read(1)\n", argv[0]);
	PyRun_SimpleString(script);
	Py_Finalize();
	return 0;
}

