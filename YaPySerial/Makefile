#------------------------------------------------------------------------------#
# This makefile was generated by 'cbp2make' tool rev.147                       #
# and edited manualy!!!
#------------------------------------------------------------------------------#

CROSS_COMPILE = x86_64-w64-mingw32

INC = 
CFLAGS = -Wall
RESINC = 
LIBDIR = 
LIB = 
LDFLAGS = 

INC_POSIX = $(INC)
CFLAGS_POSIX = $(CFLAGS) -g
RESINC_POSIX = $(RESINC)
RCFLAGS_POSIX = $(RCFLAGS)
LIBDIR_POSIX = $(LIBDIR)
LIB_POSIX = $(LIB)
LDFLAGS_POSIX = $(LDFLAGS)
OBJDIR_POSIX = obj/Debug
DEP_POSIX = 
OUT_POSIX = bin/libYaPySerial.so

INC_WIN = $(INC)
CFLAGS_WIN = $(CFLAGS) -g
RESINC_WIN = $(RESINC)
RCFLAGS_WIN = $(RCFLAGS)
LIBDIR_WIN = $(LIBDIR)
LIB_WIN = $(LIB)
LDFLAGS_WIN = $(LDFLAGS)
OBJDIR_WIN = obj/Debug
DEP_WIN = 
OUT_WIN = bin/libYaPySerial.dll

OBJ_POSIX = $(OBJDIR_POSIX)/src/serial_common_posix.o $(OBJDIR_POSIX)/src/serial_posix.o

OBJ_WIN = $(OBJDIR_WIN)/src/serial_common.o $(OBJDIR_WIN)/src/serial_w32.o

before_posix:
	$(eval CC  = gcc)
	$(eval CXX = g++)
	$(eval AR  = ar )
	$(eval LD  = g++)
	test -d bin || mkdir -p bin
	test -d $(OBJDIR_POSIX)/src || mkdir -p $(OBJDIR_POSIX)/src

after_posix: 

posix: before_posix out_posix after_posix

out_posix: before_posix $(OBJ_POSIX) $(DEP_POSIX)
	$(LD) -shared $(LIBDIR_POSIX) $(OBJ_POSIX)  -o $(OUT_POSIX) $(LDFLAGS_POSIX) $(LIB_POSIX)

$(OBJDIR_POSIX)/src/serial_common_posix.o: src/serial_common.c
	$(CC) $(CFLAGS_POSIX) $(INC_POSIX) -c src/serial_common.c -o $(OBJDIR_POSIX)/src/serial_common_posix.o

$(OBJDIR_POSIX)/src/serial_posix.o: src/serial_posix.c
	$(CC) $(CFLAGS_POSIX) $(INC_POSIX) -c src/serial_posix.c -o $(OBJDIR_POSIX)/src/serial_posix.o

clean_posix: 
	rm -f $(OBJ_POSIX) $(OUT_POSIX)
	rm -rf bin
	rm -rf $(OBJDIR_POSIX)/src

before_win:
	$(eval CC  = $(CROSS_COMPILE)-gcc)
	$(eval CXX = $(CROSS_COMPILE)-g++)
	$(eval AR  = $(CROSS_COMPILE)-ar )
	$(eval LD  = $(CROSS_COMPILE)-g++)
	test -d bin || mkdir -p bin
	test -d $(OBJDIR_WIN)/src || mkdir -p $(OBJDIR_WIN)/src

after_win: 

win: before_win out_win after_win

out_win: before_win $(OBJ_WIN) $(DEP_WIN)
	$(LD) -shared $(LIBDIR_WIN) $(OBJ_WIN)  -o $(OUT_WIN) $(LDFLAGS_WIN) $(LIB_WIN)

$(OBJDIR_WIN)/src/serial_common_w32.o: src/serial_common.c
	$(CC) $(CFLAGS_WIN) $(INC_WIN) -c src/serial_common.c -o $(OBJDIR_WIN)/src/serial_common_w32.o

$(OBJDIR_WIN)/src/serial_w32.o: src/serial_w32.c
	$(CC) $(CFLAGS_WIN) $(INC_WIN) -c src/serial_w32.c -o $(OBJDIR_WIN)/src/serial_w32.o

clean_win: 
	rm -f $(OBJ_WIN) $(OUT_WIN)
	rm -rf bin
	rm -rf $(OBJDIR_WIN)/src

all: posix win

clean: clean_posix clean_win

