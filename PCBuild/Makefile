# usage： make RELEASE=1.
#     0 for debug, 1 for release.

GCC=gcc
LibPATH=-L/home/ken/anaconda3/lib
HeaderPATH=-I../PyRun/ -I/home/ken/anaconda3/include/python3.7m
LFLAGS += -fno-lto make
ifeq ($(RELEASE),0)
    CFLAGS += -D _DEBUG
endif

include common.mk

#VPATH and vpath, used by make，not by compiler/linker
vpath %.c ../embedpy/source
vpath %.o $(OBJDIR)


main:console.o common.o
	$(GCC) $(LFLAGS) -pthread -static-libgcc -static-libstdc++ $(OBJDIR)/console.o $(OBJDIR)/common.o -L$(OUTDIR) $(LibPATH) -lpython3.7m -o $(OUTDIR)/console$(EXEExt)

%.o:%.c
	$(GCC) $(CFLAGS) -c $^ -o $(OBJDIR)/$@ $(HeaderPATH)
###############################################

