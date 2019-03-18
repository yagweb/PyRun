#include "Python.h"
#include <stdlib.h>
#include "common.h"

wchar_t* ReadPaths(wchar_t *pos, wchar_t *dirname, wchar_t *path_filename)
{
	WcharLine* lines = read_wfile(path_filename);
	WcharLine* current = lines;
	while (current != NULL)
	{
		if (IsAbsPath(current->Content) == 0)
		{
			pos = wcs_copyto(pos, dirname);
			pos = wcs_copyto(pos, L"/");
		}
		pos = wcs_copyto(pos, current->Content);
		pos = wcs_copyto(pos, L";");
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
		res = malloc((wcslen(current->Content)+1)*sizeof(wchar_t));
		wcs_copyto(res, current->Content);
		break;
	}
	FreeWcharLines(lines);
	return res;
}


#ifdef WINDOWS
int
wmain(int argc, wchar_t **argv)
{
	extern int Py_OptimizeFlag;
	extern int Py_NoSiteFlag;
	Py_OptimizeFlag = 2; //1 for -O, and 2 for -OO
	Py_NoSiteFlag = 1; //why need site module?

	/*Get the absolute path of the program*/
	//wchar_t *path = Py_GetProgramFullPath();
	//wprintf(L"------%ls\n", argv[0]);

	wchar_t fullpath[500];
	if (IsAbsPath(argv[0]))
	{
		wcs_copyto(fullpath, argv[0]);
	}
	else
	{
		GetProgramAbsPath(fullpath, 500);
	}
	//wprintf(L"------%ls\n", fullpath);

	wchar_t _dirname[500];

	wchar_t filename[500];
	wchar_t basename[200];
	wchar_t extname[100];
	SplitFileAbsPath(fullpath,
		_dirname, 500,
		filename, 500,
		basename, 200,
		extname, 100);

	//wprintf(L"------%ls, %ls, %ls\n", dirname, basename, extname);

	//Get Env_, so the exe sole can be copied to any where.
	wchar_t envname[200];
	wchar_t* _envname = envname;
	_envname = wcs_copyto(_envname, L"Env_");
	_envname = wcs_copyto(_envname, basename);
	//wprintf(L"------envname = %ls\n", envname);
	wchar_t *env_path = _wgetenv(envname);

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

	//Read Env File
	wchar_t envfile[100];
	PathJoin(envfile, _dirname, L"Env_");
	wcs_append(envfile, basename);
	wchar_t* dirname_env = ReadPath(envfile);
	if (dirname_env != NULL)
	{
		dirname = dirname_env;
		//
		//free(dirname_env);
	}

	//Set the ProgramName
	// sys.executable all comes from here
	// they are needed by multiprocessing, disutils etc.
	PathJoin(fullpath, dirname, filename);
	Py_SetProgramName(fullpath);
	//Py_SetPythonHome(dirname);

	/*Set PATH for dll search, It cannot be used for pythonXX.dll,
	  because this dll is needed before the wmain executed*/
	const wchar_t *os_path = _wgetenv(L"PATH");
	wchar_t* path_env = malloc((wcslen(os_path) + 1024) * sizeof(wchar_t));
	wchar_t* pos = path_env;
	pos = wcs_copyto(pos, L"PATH=");
	pos = wcs_copyto(pos, dirname);
	pos = wcs_copyto(pos, L";");
	pos = wcs_copyto(pos, dirname);
	pos = wcs_copyto(pos, L"/DLLs;");

	//Read PATH File
	wchar_t path_filename[500];
	PathJoin(path_filename, dirname, L"PATH");
	pos = ReadPaths(pos, dirname, path_filename);

	PathJoin(path_filename, dirname, basename);
	wcs_append(path_filename, L".PATH");
	pos = ReadPaths(pos, dirname, path_filename);

	pos = wcs_copyto(pos, os_path); //comment this, and import sqlite3 to test dll finder

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
	pos = wcs_copyto(pos, dirname);
	pos = wcs_copyto(pos, L"/packages/;");
	pos = wcs_copyto(pos, dirname);
	pos = wcs_copyto(pos, L"/scripts/;");
	pos = wcs_copyto(pos, dirname);
	pos = wcs_copyto(pos, L"/packages/python.zip;");

	// Read .pth file
	PathJoin(path_filename, dirname, L".pth");
	pos = ReadPaths(pos, dirname, path_filename);

	PathJoin(path_filename, dirname, basename);
	wcs_append(path_filename, L".pth");
	pos = ReadPaths(pos, dirname, path_filename);

	//wprintf(L"------%ls\n", libpath);

	Py_SetPath(libpath); // Cannot be removed
	Py_Initialize();
	PySys_SetArgv(argc, argv); //Set sys.argv

	// Now, run! sys.executable, can be used to the the exe path.
	PyRun_SimpleString("import hook\n"
		"hook.run()\n"
	);

	Py_Finalize();
	return 0;
}
#else
// Linux char* is utf8 encoded.
int
main(int argc, char **argv)
{

}
#endif

