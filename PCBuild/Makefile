# usage： make RELEASE=1.
#     0 for debug, 1 for release.

GCC=gcc
BITS=32
# args
OUTDIR=../bin
OBJDIR=../obj
#path for searching include file
PythonSrc=../../Python-3.6.4
HeaderLib=-I../PyRun/ -I$(PythonSrc)/PC -I$(PythonSrc)/Include
CFLAGS=-Wall -m$(BITS) -D WIN32 -D MINGW
LFLAGS=-m$(BITS)
RELEASE=0

ifeq ($(RELEASE),0)
    CFLAGS += -g
else
    CFLAGS += -static -O3 -DNDEBUG
    LFLAGS += -static
endif

#VPATH and vpath, used by make，not by compiler/linker
vpath %.c ../PyRun
vpath %.o $(OBJDIR)

#SubTargets = $(patsubst %.c,%.o,$(notdir $(wildcard ../PyRun/*.c)))

.PHONY : all pyrun_exe clean

##############################################
all : $(OUTDIR) $(OBJDIR) pyrun_exe

$(OUTDIR) :
	cd ..&&mkdir bin
	@echo Create output folder.
$(OBJDIR) :
	cd ..&&mkdir obj
	@echo Create output folder.

pyrun_exe:main.c
#	$(GCC) $(CFLAGS) -shared $(Pages_Components_All) -o $(OUTDIR)/$@
	$(GCC) $(CFLAGS) -static-libgcc -static-libstdc++ $^ -L$(OUTDIR) $(HeaderLib) -o $(OUTDIR)/PyRun.exe

%.o:%.c
	$(GCC) $(CFLAGS) -c $^ -o $(OBJDIR)/$@ $(HeaderLib)
###############################################

clean :
#	rm -f $(OBJS) $(TARGETS) $(addsuffix .exe,$(TARGETS))
	@echo off
	@echo %CD%
#	rd /s /q $(OUTDIR_OS)
	cd $(OUTDIR)&rmdir /s /q
	cd $(OBJDIR)&rmdir /s /q
	@echo clean completed

#dependencies
