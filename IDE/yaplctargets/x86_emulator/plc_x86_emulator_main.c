/**
 * Win32 specific code
 **/

#include <stdio.h>
#include <sys/timeb.h>
#include <time.h>
#include <windows.h>
#include <locale.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <errno.h>

#include "initSoftPlc.h"
#include "interface_emulation.h"

size_t GetMsgInQueue(void* data);

void Set_Settings_MBRTU(int argc, char **argv);

long AtomicCompareExchange(long* atomicvar, long compared, long exchange)
{
    return InterlockedCompareExchange(atomicvar, exchange, compared);
}
CRITICAL_SECTION Atomic64CS;
long long AtomicCompareExchange64(long long* atomicvar, long long compared, long long exchange)
{
    long long res;
    EnterCriticalSection(&Atomic64CS);
    res=*atomicvar;
    if(*atomicvar == compared){
        *atomicvar = exchange;
    }
    LeaveCriticalSection(&Atomic64CS);
    return res;
}

struct _timeb timetmp;
void PLC_GetTime(IEC_TIME *CURRENT_TIME)
{
	_ftime(&timetmp);

	(*CURRENT_TIME).tv_sec = timetmp.time;
	(*CURRENT_TIME).tv_nsec = timetmp.millitm * 1000000;
}

void PLC_timer_notify()
{
    PLC_GetTime(&__CURRENT_TIME);
    __run();
}




HANDLE PLC_timer = NULL;
void PLC_SetTimer(unsigned long long next, unsigned long long period)
{
	LARGE_INTEGER liDueTime;
	/* arg 2 of SetWaitableTimer take 100 ns interval*/
	liDueTime.QuadPart =  next / (-100);

	if (!SetWaitableTimer(PLC_timer, &liDueTime, period<1000000?1:period/1000000, NULL, NULL, 0))
    {
        printf("SetWaitableTimer failed (%d)\n", GetLastError());
    }
}

__declspec(dllimport) void RTOS_TaskApp_EepromRes(void);

__declspec(dllimport) void RTOS_TaskApp_Eeprom(void);
/* Variable used to stop plcloop thread */
void PlcLoop()
{
    while(WaitForSingleObject(PLC_timer, INFINITE) == WAIT_OBJECT_0)
    {
        RTOS_TaskApp_EepromRes();
        PLC_timer_notify();
        RTOS_TaskApp_Eeprom();
    }
}

HANDLE TachoTimer = NULL;
void PLC_SetTachoTimer(unsigned long long next, unsigned long long period)
{
	LARGE_INTEGER liDueTime;
	/* arg 2 of SetWaitableTimer take 100 ns interval*/
	liDueTime.QuadPart =  next / (-100);

	if (!SetWaitableTimer(TachoTimer, &liDueTime, period<1000000?1:period/1000000, NULL, NULL, 0))
    {
        printf("SetWaitableTimer failed (%d)\n", GetLastError());
    }
}

void PlcTachoLoop()
{
    while(WaitForSingleObject(TachoTimer, INFINITE) == WAIT_OBJECT_0)
    {
        TahoTimerUpdate();
    }
}

HANDLE PLC_thread;
HANDLE PLC_Tacho_thread;
HANDLE debug_sem;
HANDLE debug_wait_sem;
HANDLE python_sem;

HANDLE python_wait_sem;
HANDLE MBRTU_Master_thread;

//extern HANDLE mbrtu_log_sem;
extern HANDLE RTOS_MTX_MbTables;


#define TACHO_PERIOD        500000000ULL        // 500ms
#define maxval(a,b) ((a>b)?a:b)

void InitPlc();

int startPLC(int argc,char **argv)
{
	unsigned long thread_id = 0;
	//unsigned long thread_mb_id = 0;
    //BOOL tmp;
    setlocale(LC_NUMERIC, "C");

    debug_sem = CreateSemaphore(
                            NULL,           // default security attributes
                            1,  			// initial count
                            1,  			// maximum count
                            NULL);          // unnamed semaphore
    if (debug_sem == NULL)
    {
        printf("startPLC CreateSemaphore debug_sem error: %d\n", GetLastError());
        return 1;
    }

    debug_wait_sem = CreateSemaphore(
                            NULL,           // default security attributes
                            0,  			// initial count
                            1,  			// maximum count
                            NULL);          // unnamed semaphore

    if (debug_wait_sem == NULL)
    {
        printf("startPLC CreateSemaphore debug_wait_sem error: %d\n", GetLastError());
        return 1;
    }

    python_sem = CreateSemaphore(
                            NULL,           // default security attributes
                            1,  			// initial count
                            1,  			// maximum count
                            NULL);          // unnamed semaphore

    if (python_sem == NULL)
    {
        printf("startPLC CreateSemaphore python_sem error: %d\n", GetLastError());
        return 1;
    }
    python_wait_sem = CreateSemaphore(
                            NULL,           // default security attributes
                            0,  			// initial count
                            1,  			// maximum count
                            NULL);          // unnamed semaphore


    if (python_wait_sem == NULL)
    {
        printf("startPLC CreateSemaphore python_wait_sem error: %d\n", GetLastError());
        return 1;
    }


    /* Create a waitable timer */
    timeBeginPeriod(1);
    PLC_timer = CreateWaitableTimer(NULL, FALSE, "WaitableTimer");
    if(NULL == PLC_timer)
    {
        printf("CreateWaitableTimer failed (%d)\n", GetLastError());
        return 1;
    }

    TachoTimer = CreateWaitableTimer(NULL, FALSE, "TachoTimer");
    if(NULL == TachoTimer)
    {
        printf("CreateWaitableTimer failed (%d)\n", GetLastError());
        return 1;
    }

    REG_Init();
    InitPlc();
    //Set_Settings_MBRTU(0, NULL);
    if ( open_connect_sql() == 0 )
    {
        InitEEPROM();
        //close_connect_sql();
    }
    if (init_eeprom_queue() == -1) exit(0);
    if( __init(argc,argv) == 0 )
    {
        PLC_SetTimer(common_ticktime__,common_ticktime__);
        PLC_thread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)PlcLoop, NULL, 0, &thread_id);
        PLC_SetTachoTimer(TACHO_PERIOD, TACHO_PERIOD);
        PLC_Tacho_thread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)PlcTachoLoop, NULL, 0, &thread_id);
    }
    else{
        return 1;
    }

    //close_connect_sql();
    return 0;
}

static unsigned long __debug_tick;

int TryEnterDebugSection(void)
{
    if(WaitForSingleObject(debug_sem, 0) == WAIT_OBJECT_0){
        /* Only enter if debug active */
        if(__DEBUG){
            return 1;
        }
        ReleaseSemaphore(debug_sem, 1, NULL);
    }
    return 0;
}

void LeaveDebugSection(void)
{
	ReleaseSemaphore(debug_sem, 1, NULL);
}

/*void MBRTU_RunMaster()
{

}*/




void Set_Settings_MBRTU(int argc, char **argv)
{
    SetMBRTU(argc, argv);
}


int stopPLC()
{
    CloseHandle(PLC_timer);
    CloseHandle(TachoTimer);
    WaitForSingleObject(PLC_thread, INFINITE);
    WaitForSingleObject(PLC_Tacho_thread, INFINITE);
    __cleanup();
    CloseHandle(debug_wait_sem);
    CloseHandle(debug_sem);
    CloseHandle(python_wait_sem);
    CloseHandle(python_sem);
    CloseHandle(PLC_thread);
    CloseHandle(PLC_Tacho_thread);
}

/* from plc_debugger.c */
int WaitDebugData(unsigned long *tick)
{
	DWORD res;
	res = WaitForSingleObject(debug_wait_sem, INFINITE);
    *tick = __debug_tick;
    /* Wait signal from PLC thread */
	return res != WAIT_OBJECT_0;
}

/* Called by PLC thread when debug_publish finished
 * This is supposed to unlock debugger thread in WaitDebugData*/
void InitiateDebugTransfer()
{
    /* remember tick */
    __debug_tick = __tick;
    /* signal debugger thread it can read data */
    ReleaseSemaphore(debug_wait_sem, 1, NULL);
}

int suspendDebug(int disable)
{
    /* Prevent PLC to enter debug code */
    WaitForSingleObject(debug_sem, INFINITE);
    __DEBUG = !disable;
    if(disable)
        ReleaseSemaphore(debug_sem, 1, NULL);
    return 0;
}

void resumeDebug()
{
	__DEBUG = 1;
    /* Let PLC enter debug code */
	ReleaseSemaphore(debug_sem, 1, NULL);
}

/* from plc_python.c */
int WaitPythonCommands(void)
{
    /* Wait signal from PLC thread */
	return WaitForSingleObject(python_wait_sem, INFINITE);
}

/* Called by PLC thread on each new python command*/
void UnBlockPythonCommands(void)
{
    /* signal debugger thread it can read data */
	ReleaseSemaphore(python_wait_sem, 1, NULL);
}

int TryLockPython(void)
{
	return WaitForSingleObject(python_sem, 0) == WAIT_OBJECT_0;
}

void UnLockPython(void)
{
	ReleaseSemaphore(python_sem, 1, NULL);
}

void LockPython(void)
{
	WaitForSingleObject(python_sem, INFINITE);
}

void InitRetain(void)
{
}

void CleanupRetain(void)
{
}

int CheckRetainBuffer(void)
{
	return 1;
}

void ValidateRetainBuffer(void)
{
}

void InValidateRetainBuffer(void)
{
}

void Retain(unsigned int offset, unsigned int count, void * p)
{
    /*
    unsigned int position;
    for(position=0; position<count; position++ ){
        printf("%d : 0x%2.2x\n", offset+position, ((char*)p)[position]);
    }
    */
}

void Remind(unsigned int offset, unsigned int count, void *p)
{
}

static void __attribute__((constructor))
beremiz_dll_init(void)
{
    InitializeCriticalSection(&Atomic64CS);

}

static void __attribute__((destructor))
beremiz_dll_destroy(void)
{
    DeleteCriticalSection(&Atomic64CS);
}

/**
 * Win32 specific code end
 **/