#include "Python.h"
#include <stdio.h>
#include <stdlib.h>
#ifdef WINDOWS
#include <direct.h>
#else
#endif

wchar_t* wcs_append(wchar_t* pos, const wchar_t* content)
{
	wcscpy(pos, content);
	pos = pos + wcslen(content);
	return pos;
}

void c_getcwd(wchar_t *buffer,
	int maxlen)
{
#ifdef WINDOWS
	_wgetcwd(
		buffer,
		maxlen
	);
#else
#endif
}

wchar_t* GetProgramAbsPath(wchar_t *cwd,
	int maxlen, wchar_t *file)
{
	memset(cwd, 0, maxlen * sizeof(wchar_t));
	c_getcwd(cwd, maxlen);
	wchar_t *pos = cwd + wcslen(cwd);
	pos = wcs_append(pos, L"/");
	pos = wcs_append(pos, file);
	return cwd;
}

void SplitFileAbsPath(wchar_t *fullpath,
	wchar_t *dirname, int dirname_size,
	wchar_t* filename, int filename_size,
	wchar_t *basename, int basename_size,
	wchar_t *extname, int extname_size)
{
	memset(dirname, 0, dirname_size * sizeof(wchar_t));
	memset(filename, 0, filename_size * sizeof(wchar_t));
	memset(basename, 0, basename_size * sizeof(wchar_t));
	memset(extname, 0, extname_size * sizeof(wchar_t));

	int fullpath_len = wcslen(fullpath);
	int i = 0;
	int pos;
	wchar_t path_splitter1 = L'\\'; // not L"\\"
	wchar_t path_splitter2 = L'/';
	wchar_t dot_char = L'.';
	for (pos = fullpath_len - 1; pos >= 0; pos--)
	{
		if (fullpath[pos] == path_splitter1 || fullpath[pos] == path_splitter2)
		{
			break;
		}
		filename[i] = fullpath[pos];
		i++;
	}
	// copy dirname
	for (int j = 0; j < pos; j++)
	{
		dirname[j] = fullpath[j];
	}
	// swap filename
	int filename_len = wcslen(filename);
	wchar_t temp;
	for (pos = 0; pos < filename_len/2; pos++)
	{
		temp = filename[pos];
		filename[pos] = filename[filename_len-pos-1];
		filename[filename_len - pos - 1] = temp;
	}
	// split basename and extname, find the last dot
	for (pos = filename_len - 1; pos >= 0; pos--)
	{
		if (filename[pos] == dot_char)
		{
			break;
		}
	}
	// split basename and extname
	if (pos < 0)
	{
		memcpy(basename, filename, filename_len * sizeof(wchar_t));
	}
	else if (pos == 0)
	{
		memcpy(extname, filename, filename_len * sizeof(wchar_t));
	}
	else
	{
		memcpy(basename, filename, pos * sizeof(wchar_t));
		memcpy(extname, filename+pos, (filename_len - pos) * sizeof(wchar_t));
	}
}

int
wmain(int argc, wchar_t **argv)
{
	extern int Py_OptimizeFlag;
	extern int Py_NoSiteFlag;
	Py_OptimizeFlag = 2; //1 for -O, and 2 for -OO
	Py_NoSiteFlag = 1; //why need site module?

	/*Get the absolute path of the program*/
	//wchar_t *path = Py_GetProgramFullPath();

	wchar_t fullpath[500];
	GetProgramAbsPath(fullpath, 500, argv[0]);
	//wprintf(L"------%ls\n", path);

	wchar_t _dirname[500];
	wchar_t filename[500];
	wchar_t basename[200];
	wchar_t extname[100];
	SplitFileAbsPath(fullpath,
		_dirname, 500,
		filename, 500,
		basename, 200,
		extname, 100);

	wchar_t envname[200];
	wchar_t* _envname = envname;
	_envname = wcs_append(_envname, L"Env_");
	_envname = wcs_append(_envname, basename);
	//wprintf(L"------envname = %ls\n", envname);
	const wchar_t *env_path = _wgetenv(envname);
	/*wprintf(L"------%ls\n", _dirname);
	wprintf(L"------%ls\n", filename);
	wprintf(L"------%ls\n", basename);
	wprintf(L"------%ls\n", extname);
	wprintf(L"------%ls\n", env_path);*/

	wchar_t* dirname;
	if (env_path == NULL)
	{
		dirname = _dirname;
	}
	else
	{
		dirname = env_path;
	}
	//wprintf(L"------%ls\n", dirname);

	//Set the ProgramName
	Py_SetProgramName(filename); // full path of the program, needed by multiprocessing
								 // need combine with cwd to get full path

	/*Set PATH for dll search, It cannot be used for pythonXX.dll, 
	  because this dll is needed before the wmain executed*/
	const wchar_t *os_path = _wgetenv(L"PATH");
	wchar_t* path_env = malloc((wcslen(os_path) + 1024) * sizeof(wchar_t));
	wchar_t* pos = path_env;
	pos = wcs_append(pos, L"PATH=");
	pos = wcs_append(pos, dirname);
	pos = wcs_append(pos, L"/DLLs;");
	pos = wcs_append(pos, dirname);
	pos = wcs_append(pos, L"/packages/PySide2;");
	//pos = wcs_append(pos, L"C:/Anaconda3/Library/bin;"); //for dll debug
	pos = wcs_append(pos, os_path); //comment this, and import sqlite3 to test dll finder
	
	//wprintf(L"------%ls\n", path_env);
	int iRet = _wputenv(path_env);
	free(path_env);
	if (iRet < 0)
	{
		printf("set PATH error\n");
		return 1;
	}

	/*Set PATH for packages search, python.zip is included*/
	wchar_t libpath[1024];
	pos = libpath;
	pos = wcs_append(pos, dirname);
	pos = wcs_append(pos, L"/packages/;");
	pos = wcs_append(pos, dirname);
	pos = wcs_append(pos, L"/scripts/;");
	pos = wcs_append(pos, dirname);
	pos = wcs_append(pos, L"/packages/python.zip;");
	/*if (env_path != NULL)
	{
		pos = wcs_append(pos, _dirname);
		pos = wcs_append(pos, L";");
	}*/
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
