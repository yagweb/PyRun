#include "common.h"
#include <stdlib.h>
#include<string.h>
#ifdef WINDOWS
#include <direct.h> // for c_getcwd
#else
#endif

wchar_t* wcs_copyto(wchar_t* pos, const wchar_t* content)
{
	wcscpy(pos, content);
	pos = pos + wcslen(content);
	return pos;
}

void wcs_append(wchar_t* pos, const wchar_t* content)
{
	wcscpy(pos + wcslen(pos), content);
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
	getcwd(
		buffer,
		maxlen
	);
#endif
}

wchar_t* GetProgramAbsPath(wchar_t *cwd,
	int maxlen, wchar_t *file)
{
	if (IsAbsPath(file)==1)
	{
		wcs_copyto(cwd, file);
		return cwd;
	}
	memset(cwd, 0, maxlen * sizeof(wchar_t));
	c_getcwd(cwd, maxlen);
	wchar_t *pos = cwd + wcslen(cwd);
	pos = wcs_copyto(pos, L"/");
	pos = wcs_copyto(pos, file);
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

	int fullpath_len = (int)wcslen(fullpath);
	int i = 0;
	int pos;
	for (pos = fullpath_len - 1; pos >= 0; pos--)
	{
		// not L"\\"
		if (fullpath[pos] == L'\\' || fullpath[pos] == L'/')
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
	for (pos = 0; pos < filename_len / 2; pos++)
	{
		temp = filename[pos];
		filename[pos] = filename[filename_len - pos - 1];
		filename[filename_len - pos - 1] = temp;
	}
	// split basename and extname, find the last dot
	for (pos = filename_len - 1; pos >= 0; pos--)
	{
		if (filename[pos] == L'.')
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
		memcpy(extname, filename + pos, (filename_len - pos) * sizeof(wchar_t));
	}
}

int IsAbsPath(wchar_t *path)
{
	int len = wcslen(path);
#ifdef WINDOWS
	if (len >= 2 && path[1] == L':')
	{
		return 1;
	}
	else
	{
		return 0;
	}
#else
	if (len >= 1 && path[0] == L'/')
	{
		return 1;
	}
	else
	{
		return 0;
	}
#endif
}

wchar_t* PathJoin(wchar_t *dest, wchar_t* path1, wchar_t* path2)
{
	if (IsAbsPath(path2) == 1)
	{
		wcs_copyto(dest, path2);
		return dest;
	}

	wchar_t *pos = dest;
	pos = wcs_copyto(pos, path1);
	int path1_len = wcslen(path1);
	if (path1[path1_len - 1] != L'/' && path1[path1_len - 1] != L'/')
	{
		pos = wcs_copyto(pos, L"/");
	}
	pos = wcs_copyto(pos, path2);
	return dest;
}

//ÿ������ֽ���
#define MAX_LINE 1024

WcharLine* NewWcharLine()
{
	WcharLine* line = (WcharLine*)malloc(sizeof(WcharLine)); // not sizeof sizeof(WcharLine*)
	line->Content = NULL;
	line->Next = NULL;
	return line;
}

void FreeWcharLine(WcharLine* line)
{
	if (line->Content != NULL)
	{
		free(line->Content);
	}
	free(line);
}

void FreeWcharLines(WcharLine* line)
{
	WcharLine* temp = NULL;
	WcharLine* current = line;
	while (current != NULL)
	{
		temp = current->Next;
		FreeWcharLine(current);
		current = temp;
	}
}

WcharLine* read_wfile(wchar_t *path)
{
	FILE  *fp = _wfopen(path, L"r");
	if (fp == NULL) //�ж��ļ��Ƿ���ڼ��ɶ�
	{
		return NULL;
	}
	WcharLine* first = NULL;
	WcharLine* last = NULL;
	WcharLine* current = NULL;
	wchar_t strLine[MAX_LINE]; //��ȡ������
	while (!feof(fp)) //ѭ����ȡÿһ�У�ֱ���ļ�β
	{
		fgetws(strLine, MAX_LINE, fp); //��fp��ָ����ļ�һ�����ݶ���strLine������
		int len = wcslen(strLine);
		if (len >= 2 && strLine[len - 2] == L'\r' && strLine[len - 1] == L'\n')
		{
			strLine[len - 2] = L'\0';
		}
		else if (len >= 1 && strLine[len - 1] == L'\n')
		{
			strLine[len - 1] = L'\0';
		}
		// trim blank at end.
		len = wcslen(strLine);
		while (len >= 1 && strLine[len - 1] == L' ')
		{
			strLine[len - 1] = L'\0';
			len = wcslen(strLine);
		}
		len = wcslen(strLine);
		if (len == 0)
		{
			continue;
		}
		// Save to List
		if (first == NULL)
		{
			first = NewWcharLine();
			current = first;
		}
		else
		{
			current = NewWcharLine();
			last->Next = current;
		}
		current->Content = malloc((len + 2) * sizeof(wchar_t));
		wcscpy(current->Content, strLine);
		last = current;
	}
	fclose(fp); //�ر��ļ�
	return first;
}