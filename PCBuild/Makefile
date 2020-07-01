# usage： make RELEASE=1.
#     0 for debug, 1 for release.

PyVer=36
GCC=gcc

include common.mk

ifeq ($(OS),Windows_NT)
    ifeq ($(PyVer), 36)
			  LibPATH=-LC:/Anaconda3
			  HeaderPATH=-I../PyRun/ -IC:/Anaconda3/include
    else ifeq ($(PyVer), 37)
		    LibPATH=-LC:/WPy64-3770/python-3.7.7.amd64
		    HeaderPATH=-I../PyRun/ -IC:/WPy64-3770/python-3.7.7.amd64/include
    else ifeq ($(PyVer), 38)
		    LibPATH=-L/home/ken/anaconda3/lib
		    HeaderPATH=-I../PyRun/ -I/home/ken/anaconda3/include
    endif
		Pythonlib = python$(PyVer)
    CFLAGS += -D WINDOWS -D MINGW
else
    LibPATH=-L/home/ken/anaconda3/lib
    HeaderPATH=-I../PyRun/ -I/home/ken/anaconda3/include/python3.7m
    LFLAGS += -fno-lto make
		Pythonlib = python3.7m
endif

ifeq ($(RELEASE),0)
    CFLAGS += -D _DEBUG
endif

#VPATH and vpath, used by make，not by compiler/linker
vpath %.c ../embedpy/source
vpath %.o $(OBJDIR)


main:console.o common.o
	$(GCC) $(LFLAGS) -pthread -static-libgcc -static-libstdc++ $(OBJDIR)/console.o $(OBJDIR)/common.o -L$(OUTDIR) $(LibPATH) -l$(Pythonlib) -o $(OUTDIR)/console$(PyVer)$(EXEExt)

%.o:%.c
	$(GCC) $(CFLAGS) -c $^ -o $(OBJDIR)/$@ $(HeaderPATH)
###############################################

