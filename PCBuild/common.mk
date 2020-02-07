# This is a shell of makefile for cross platforms for small projects
# For Windows developments, it can be run in sys2 mingw64
# For big project, CMake is recommended.
# Usage:
#       include this file, and implement the target "main"
# Author Ken Wenguang Yang (yagweb)

BITS=64
RELEASE=1
CLEAN=0
MSYS2=0

ifeq ($(OS),Windows_NT)
    ifeq ($(BITS), 64)
        BITS_NAME=Min64
    else
        BITS_NAME=Min32
    endif
else
    ifeq ($(BITS), 64)
        BITS_NAME=Lin64
    else
        BITS_NAME=Lin32
    endif
endif

ifeq ($(RELEASE),0)
    Type_Name=Debug
else
    Type_Name=Release
endif

ifeq ($(CLEAN),0)
    CLEAN_TARGET=
else
    CLEAN_TARGET=clean
endif

mkfile_path :=$(abspath $(lastword $(MAKEFILE_LIST)))#获取当前正在执行的makefile的绝对路径
ROOT_PATH :=$(strip $(patsubst %/, %, $(dir $(mkfile_path))))#
SOURCE_ROOT_PATH :=$(ROOT_PATH)#
#$(info $(ROOT_PATH))
OUTDIR=$(abspath $(ROOT_PATH)/../bin/$(BITS_NAME))
OBJDIR=$(abspath $(ROOT_PATH)/../obj/$(BITS_NAME)/$(Type_Name))
ifeq ($(RELEASE),0)
    OUTDIR:=$(OUTDIR)/Debug
endif

# += operator will add a blank operator
ifeq ($(OS),Windows_NT)
    ifeq ($(MSYS2),1)
        LINUX=1
    else
        LINUX=0
    endif
    DLLPre=
    DLLExt=.dll
    LIBExt=.lib
    EXEExt=.dll

    CFLAGS=-Wall -m$(BITS) -D WIN32 -D MINGW
    LFLAGS=-Wall -m$(BITS)
else
    LINUX=1
    DLLPre=lib
    DLLExt=.so
    LIBExt=.a
    EXEExt=

    CFLAGS=-Wall -m$(BITS) -fPIC
    LFLAGS=-Wall -m$(BITS) -fPIC
endif

ifeq ($(LINUX),0)
    DirNotExists=@if NOT exist $(1) $(2)
    MKDIR=if NOT exist $(1) mkdir $(1)
    CLEAR=if exist $(1) rmdir /s /q $(1)
    COPY=if exist $(1) xcopy /f /Y $(1) $(2)
else
    DirNotExists=@if [ ! -d $(1) ]; then $(2); fi
    define MKDIR
        if [ ! -d $(1) ]; then mkdir $(1); fi
    endef
    CLEAR=if [ -d $(1) ]; then cd $(1)&&rm -f *.*; fi
    COPY=if [ -f $(1) ]; then cp -f $(1) $(2); fi
endif

ifeq ($(RELEASE),0)
    # debug
    CFLAGS += -g
else
    # release
    CFLAGS += -static -O3 -DNDEBUG
    # LFLAGS += -static
endif

.PHONY : all

all :  $(CLEAN_TARGET) OUTDIR OBJDIR main

# shell commands must put under the first target and sentence starts with TAB
exit:
	@exit 1

OUTDIR :#创建输出文件夹的伪目标
	$(call MKDIR, "$(dir $(patsubst %/, %, $(dir $(OUTDIR))))")
	$(call MKDIR, "$(dir $(OUTDIR))")
	$(call MKDIR, "$(OUTDIR)")
	@echo Create folder $(OUTDIR)

OBJDIR :#创建输出文件夹的伪目标
	$(call MKDIR, "$(dir $(dir $(OBJDIR)))")
	$(call MKDIR, "$(dir $(OBJDIR))")
	$(call MKDIR, "$(OBJDIR)")
	@echo Create folder $(OBJDIR)

clean :
	@echo off
	@echo remove $(OBJDIR)
#	$(call CLEAR, "$(OUTDIR)")
	$(call CLEAR, "$(OBJDIR)")
	@echo clean completed