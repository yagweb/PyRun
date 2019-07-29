#include "Python.h"
#include <stdio.h>
#include <stdlib.h>
#include "common.h"


#ifdef NOCONSOLE

#include<windows.h>
#pragma comment( linker, "/subsystem:windows /ENTRY:wmainCRTStartup") // 设置入口地址

#endif


wchar_t* ReadPaths(wchar_t *pos, wchar_t *dirname, wchar_t *path_filename, size_t* left_size)
{
	WcharLine* lines = read_wfile(path_filename);
	WcharLine* current = lines;
	while (current != NULL)
	{
		if (IsAbsPath(current->Content) == 0)
		{
			pos = wcs_copyto(pos, dirname, left_size);
			if (pos == NULL)
			{
				break;
			}
			pos = wcs_copyto(pos, L"/", left_size);
			if (pos == NULL)
			{
				break;
			}
		}
		pos = wcs_copyto(pos, current->Content, left_size);
		if (pos == NULL)
		{
			break;
		}
		pos = wcs_copyto(pos, L";", left_size);
		if (pos == NULL)
		{
			break;
		}
		current = current->Next;
	}
	FreeWcharLines(lines);
	return pos;
}


wchar_t* ReadPath(wchar_t *path_filename)
{
	wchar_t* res = NULL;
	WcharLine* lines = read_wfile(path_filename);
	WcharLine* current = lines;
	while (current != NULL)
	{
		size_t size = (wcslen(current->Content)+1)*sizeof(wchar_t);
		res = malloc(size);
		wcs_copyto(res, current->Content, &size);
		break;
	}
	FreeWcharLines(lines);
	return res;
}


void WriteError(char* msg)
{
	FILE *fp;
	if ((fp = fopen("error.txt", "w")) == NULL)
	{
		printf("error file cannot open \n");
		exit(0);
	}
	else
	{
		printf(msg);
		fputs(msg, fp);
	}
	if (fclose(fp) != 0)
	{
		printf("file cannot be closed \n");
	}
}


#ifdef WINDOWS
int
wmain(int argc, wchar_t **argv)
{
	extern int Py_OptimizeFlag;
	extern int Py_NoSiteFlag;
	Py_OptimizeFlag = 2; //1 for -O, and 2 for -OO
	Py_NoSiteFlag = 1; //why need site module?
	size_t wchar_buf_size = 100000;
	wchar_t* wchar_buf = malloc(wchar_buf_size * sizeof(wchar_t));

	/*Get the absolute path of the program*/
	// Py_GetProgramFullPath() is not working currently

#ifdef _DEBUG
	wprintf(L">>argv[0] = %ls\n", argv[0]);
#endif

	const size_t fullpath_size = 1024;
	wchar_t fullpath[1024];
	size_t fullpath_left_size = fullpath_size;
	if (IsAbsPath(argv[0]))
	{
		wchar_t* state = wcs_copyto(fullpath, argv[0], &fullpath_left_size);
		if (state == NULL)
		{
			WriteError("the program path is too long\n");
			return 1;
		}
	}
	else
	{
		GetProgramAbsPath(fullpath, fullpath_size);
	}
#ifdef _DEBUG
	wprintf(L">> current exe path = %ls\n", fullpath);
#endif

	/* Parse the file*/
	wchar_t _dirname[1024];
	wchar_t filename[500];
	wchar_t basename[300];
	wchar_t extname[299];
	SplitFileAbsPath(fullpath,
		_dirname, 1024,
		filename, 500,
		basename, 300,
		extname, 299);
#ifdef _DEBUG
	wprintf(L">>current exe path items = %ls, %ls, %ls\n", _dirname, basename, extname);
#endif

	//Get Env_ to look modules and dlls, so the exe file only can be copied to any where.
	const size_t env_size = 300;
	wchar_t envname[300];
	size_t envname_left_size = env_size / sizeof(wchar_t);
	wchar_t* pos_envname = envname;
	pos_envname = wcs_copyto(pos_envname, L"Env_", &envname_left_size);
	pos_envname = wcs_copyto(pos_envname, basename, &envname_left_size);
#ifdef _DEBUG
	wprintf(L">> environment varialbe name = %ls\n", envname);
#endif
	wchar_t *env_path = _wgetenv(envname);
	size_t dirname_size = 1024;
	wchar_t* dirname = malloc(dirname_size*sizeof(wchar_t));
	if (env_path == NULL)
	{
		wcscpy(dirname, _dirname);
	}
	else
	{
		wcscpy(dirname, env_path);
		//free(env_path); // cannot free
	}
#ifdef _DEBUG
	wprintf(L">> Search dir = %ls\n", dirname);
#endif

	/* Read the real search dir from Env File in current working directory */
	wchar_t* envfile = wchar_buf;
	size_t envfile_size = wchar_buf_size;
	PathJoin(envfile, _dirname, L"Env_", envfile_size);
	int state = wcs_append(envfile, basename, envfile_size);
	if (state != 0)
	{
		WriteError("the path of the envfile is too long\n");
		return 2;
	}
	wchar_t* dirname_env = ReadPath(envfile);
	if (dirname_env != NULL)
	{
		wcscpy(dirname, dirname_env);
		free(dirname_env);
	}
#ifdef _DEBUG
	wprintf(L">> Search dir = %ls\n", dirname);
#endif

	/* Set the REAL ProgramName for Python
	   python sys.executable all comes from here
	   they are needed by multiprocessing, disutils etc.
	 */
	PathJoin(fullpath, dirname, filename, fullpath_size);
	Py_SetProgramName(fullpath);
	//Py_SetPythonHome(dirname);

	/*Set PATH for dll search, It cannot be used for pythonXX.dll,
	  because this dll is needed before the wmain executed
	*/
	wchar_t* path_env = wchar_buf;
	size_t path_env_left_size = wchar_buf_size;
	const wchar_t *os_path = _wgetenv(L"PATH");
	wchar_t* pos = path_env;
	pos = wcs_copyto(pos, L"PATH=", &path_env_left_size);
	pos = wcs_copyto(pos, dirname, &path_env_left_size);
	pos = wcs_copyto(pos, L";", &path_env_left_size);
	pos = wcs_copyto(pos, dirname, &path_env_left_size);
	pos = wcs_copyto(pos, L"/DLLs;", &path_env_left_size);

	/* Read PATH File to get user defined search pathes */
	int path_filename_length = 1024;
	wchar_t path_filename[1024];
	PathJoin(path_filename, dirname, L"PATH", fullpath_size);
 	pos = ReadPaths(pos, dirname, path_filename, &path_env_left_size);
	if (pos == NULL)
	{
		WriteError("too much lines in the PATH file\n");
		return 3;
	}

	PathJoin(path_filename, dirname, basename, fullpath_size);
	int state1 = wcs_append(path_filename, L".PATH", path_filename_length);
	if (state1 != 0)
	{
		WriteError("the X.PATH filename is too long\n");
		return 4;
	}
	pos = ReadPaths(pos, dirname, path_filename, &path_env_left_size);
	if (pos == NULL)
	{
		WriteError("too much lines in the X.PATH file\n");
		return 5;
	}

	pos = wcs_copyto(pos, os_path, &path_env_left_size); //comment this, and import sqlite3 to test dll finder
	if (pos == NULL)
	{
		WriteError("the OS PATH is too long\n");
		return 6;
	}
#ifdef _DEBUG
	wprintf(L">> Set PATH: %ls\n", path_env);
#endif

	int iRet = _wputenv(path_env);
	if (iRet < 0)
	{
		WriteError("set PATH error\n");
		return 7;
	}

	/*Set PATH for packages search, python.zip is included*/
	wchar_t* libpath = wchar_buf;
	size_t libpath_left_size = wchar_buf_size;
	pos = libpath;
	pos = wcs_copyto(pos, dirname, &libpath_left_size);
	pos = wcs_copyto(pos, L"/packages/python.zip;", &libpath_left_size);
	pos = wcs_copyto(pos, dirname, &libpath_left_size);
	pos = wcs_copyto(pos, L"/python.zip;", &libpath_left_size);
	pos = wcs_copyto(pos, dirname, &libpath_left_size);
	pos = wcs_copyto(pos, L"/scripts/;", &libpath_left_size);

	// Read .pth file
	PathJoin(path_filename, dirname, L".pth", fullpath_size);
	pos = ReadPaths(pos, dirname, path_filename, &libpath_left_size);
	if (pos == NULL)
	{
		WriteError("too much lines in the .pth file\n");
		return 8;
	}

	PathJoin(path_filename, dirname, basename, fullpath_size);
	int state2 = wcs_append(path_filename, L".pth", path_filename_length);
	if (state2 != 0)
	{
		WriteError(".pth file name length is too long\n");
		return 9;
	}
	pos = ReadPaths(pos, dirname, path_filename, &libpath_left_size);
	if (pos == NULL)
	{
		WriteError("too much lines in the X.pth file\n");
		return 10;
	}
#ifdef _DEBUG
	wprintf(L">> sys.path = %ls\n", libpath);
#endif

	/* Initialize Python */
	if (libpath[wcslen(libpath)-1] == L';')
	{
		libpath[wcslen(libpath)-1] = L'\0';
	}
	Py_SetPath(libpath);
	free(dirname);
	free(wchar_buf);
	Py_Initialize();
	PySys_SetArgv(argc, argv); //Set sys.argv

	// Now, run! sys.executable, can be used to the the exe path.
	/*PyRun_SimpleString("import hook\n"
		"hook.run()\n"
	);*/
	PyGILState_STATE gstate = PyGILState_Ensure();
	PyObject* hook = PyImport_ImportModule("hook");
	if (hook == NULL)
	{
		PyGILState_Release(gstate);
		Py_Finalize();
		return 100;
	}
	PyObject* run = PyObject_GetAttrString(hook, "run");
	if (run == NULL)
	{
		PyGILState_Release(gstate);
		Py_Finalize();
		return 101;
	}
	PyObject* run_result = PyObject_CallFunction(run, "");
	if (run_result == NULL)
	{
		PyGILState_Release(gstate);
		Py_Finalize();
		return 102;
	}
	int value = PyObject_IsTrue(run_result);
	Py_DECREF(hook);
	Py_DECREF(run);
	Py_DECREF(run_result);
	PyGILState_Release(gstate);
	Py_Finalize();
	if (value == 0)
	{
		return 103;
	}
	else
	{
		return 0;
	}
}
#else
// Linux char* is utf8 encoded.
int
main(int argc, char **argv)
{

}
#endif

