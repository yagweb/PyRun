#ifndef COMMON_H_
#define COMMON_H_

#include <stdio.h>

wchar_t* wcs_copyto(wchar_t* pos, const wchar_t* content);

void wcs_append(wchar_t* pos, const wchar_t* content);

void c_getcwd(wchar_t *buffer, int maxlen);

wchar_t* GetProgramAbsPath(wchar_t *cwd,
	int maxlen, wchar_t *file);

void SplitFileAbsPath(wchar_t *fullpath,
	wchar_t *dirname, int dirname_size,
	wchar_t* filename, int filename_size,
	wchar_t *basename, int basename_size,
	wchar_t *extname, int extname_size);

int IsAbsPath(wchar_t *path);

wchar_t* PathJoin(wchar_t *dest, wchar_t* path1, wchar_t* path2);

typedef struct _WcharLine WcharLine;

struct _WcharLine
{
	wchar_t* Content;
	WcharLine* Next;
};

WcharLine* NewWcharLine();

void FreeWcharLine(WcharLine* line);

void FreeWcharLines(WcharLine* line);

WcharLine* read_wfile(wchar_t *path);

#endif