#include "common.h"
#include <stdlib.h> //putenv()
#include <string.h>
#ifdef WINDOWS
#include <direct.h> // for c_getcwd
#include <windows.h>
#else
#include <limits.h>
#include <unistd.h> //readlink()
#endif

// left_size is the buffer size / sizeof(wchar_t)
wchar_t* wcs_copyto(wchar_t* pos, const wchar_t* content, size_t* left_size)
{
	if(content == NULL)
	{
		return pos;
	}
	size_t length = wcslen(content);
	if (*left_size < length + 1)
	{
		return NULL;
	}
	wcscpy(pos, content);
	pos += length;
	*left_size -= length;
	return pos;
}

// left_size is the buffer size / sizeof(wchar_t)
int wcs_append(wchar_t* pos, const wchar_t* content, size_t total_size)
{
	size_t length = wcslen(content);
	wchar_t* end_pos = pos + wcslen(pos);
	if (total_size < length + wcslen(pos) + 1)
	{
		return 1;
	}
	wcscpy(end_pos, content);
	return 0;
}


#ifndef WINDOWS

// 将char类型转化为wchar13 // locale: 环境变量的值，mbstowcs依赖此值来判断src的编码方式
wchar_t* _to_wchar(const char* src){
  if (src == NULL) {
      return NULL;
  }
  //得到转化为需要的宽字符大小
  int w_size = mbstowcs(NULL, src, 0) + 1;
  //w_size=0说明mbstowcs返回值为-1。即在运行过程中遇到了非法字符(很有可能使locale没有设置正确)
  if (w_size == 0) {
	  printf("to wchar_t failed. maybe setlocale is needed.");
      return NULL;
  }
  wchar_t* buffer = malloc(w_size*sizeof(wchar_t));
  int ret = mbstowcs(buffer, src, strlen(src)+1);
  if (ret <= 0){
      free(buffer);
	  return NULL;
  }
  return buffer;
}

// 将char类型转化为wchar13 // locale: 环境变量的值，mbstowcs依赖此值来判断src的编码方式
int to_wchar(const char* src, wchar_t* dest, size_t maxlen){
  wchar_t* buffer = _to_wchar(src);
  if (buffer == NULL){
	  return -1;
  }
  size_t dest_len = wcslen(buffer);
  if(dest_len >= maxlen)
  {
	  printf("to wchar_t failed. dest buffer too small.");
      return -1;
  }
  wcscpy(dest, buffer);
  free(buffer);
  return dest_len;
}

//通过链接文件名获取被目标文件绝对路径
//为了防止buffer不够大，包装一下readlink()
char* _readlink(const char *filename)
{
    int size = 200;
    char *buffer = NULL;

    while(1)
    {
        buffer = (char *)realloc(buffer, size);
        //readlink()返回的路径名并没有以'\0'结尾
        int nchars = readlink(filename, buffer, size - 1);
        if (nchars < 0)
        {
            free(buffer);
			buffer = NULL;
			return buffer;
        }
        if (nchars <= size - 1) 
	    {
            buffer[nchars] = '\0';        //让路径名以'\0'结尾
            return buffer;
        }
        size *= 2;    //buffer空间不足，扩大为2倍
    }
}

 
FILE* _wfopen(const wchar_t* filename, const wchar_t* mode)
{
    char fn[MAX_PATH];
    char m[MAX_PATH];
    wcstombs(fn, filename, MAX_PATH);
    wcstombs(m, mode, MAX_PATH);
    return fopen(fn, m);
}

wchar_t* _wgetenv(const wchar_t* name)
{
    char _name[MAX_PATH];
    wcstombs(_name, name, MAX_PATH);
	char* _env = getenv(_name); // _env is a pointer, cannot be free
	wchar_t* env = _to_wchar(_env);
    return env;
}

int _wputenv(const wchar_t* value)
{
	int length = wcslen(value)*sizeof(wchar_t) + 1;
    char* _value = malloc(length);
    wcstombs(_value, value, length);
	int state = putenv(_value);
	free(_value);
	return state;
}

void _wgetcwd(wchar_t *cwd,
	int maxlen)
{
    size_t _maxlen = maxlen*sizeof(wchar_t);
	char* src = malloc(_maxlen);
	char* state = getcwd(src, _maxlen);
    if(state == NULL)
	{
		printf("getcwd failed.");
	    free(src);
		exit(0);
	}
    int res = to_wchar(src, cwd, maxlen);
	if(res == -1)
	{
		exit(0);
	}
	free(src);
}

#endif

int GetProgramAbsPath(wchar_t *cwd, size_t maxlen)
{
#ifdef WINDOWS
	int res = (int)GetModuleFileNameW(
		NULL,
		cwd,
		maxlen
	);
	return res;
#else
	char* buffer = _readlink("/proc/self/exe");
	if(buffer == NULL)
	{
		printf("read /proc/self/exe failed.");
		exit(0);
	}
    int res = to_wchar(buffer, cwd, maxlen);
	if(res == -1)
	{
		exit(0);
	}
	// free(buffer); // cannot free!
	return 0;
#endif
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
	size_t filename_len = wcslen(filename);
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
	size_t len = wcslen(path);
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

wchar_t* PathJoin(wchar_t *dest, wchar_t* path1, wchar_t* path2, size_t dest_size)
{
	size_t left_size = dest_size;
	if (IsAbsPath(path2) == 1)
	{
		return wcs_copyto(dest, path2, &left_size);
	}

	wchar_t *pos = dest;
	pos = wcs_copyto(pos, path1, &left_size);
	size_t path1_len = wcslen(path1);
	if (path1[path1_len - 1] != L'/' && path1[path1_len - 1] != L'/')
	{
		pos = wcs_copyto(pos, L"/", &left_size);
		if (pos == NULL)
		{
			return NULL;
		}
	}
	pos = wcs_copyto(pos, path2, &left_size);
	return pos;
}

//maxminum bytes in each line
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

WcharLine* read_wfile(const wchar_t *path)
{
	FILE  *fp = _wfopen(path, L"r");
	if (fp == NULL)
	{
		return NULL;
	}
	WcharLine* first = NULL;
	WcharLine* last = NULL;
	WcharLine* current = NULL;
	wchar_t strLine[MAX_LINE]; // buffer for read
	wchar_t* temp = NULL;
	while (!feof(fp)) // loop read until end
	{
		temp = fgetws(strLine, MAX_LINE, fp); //read line fp pointed to the buffer
		size_t len = wcslen(strLine);
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
	fclose(fp); //close file
	return first;
}


wchar_t* ReadPaths(wchar_t *pos, const wchar_t *delimiter, wchar_t *dirname, const wchar_t *path_filename, size_t* left_size)
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
		pos = wcs_copyto(pos, delimiter, left_size);
		if (pos == NULL)
		{
			break;
		}
		current = current->Next;
	}
	FreeWcharLines(lines);
	return pos;
}


wchar_t* ReadPath(const wchar_t *path_filename)
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