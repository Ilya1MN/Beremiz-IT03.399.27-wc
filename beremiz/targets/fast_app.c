#include "plc_abi.h"

extern void (*FastPrograms_Ptr[32])();
extern fastApp_t FastApp;

// SetBit
//* mask - uint32_t value
//* bit - TRUE..FALSE
//* bit_number - Task priority for pointer fast func (0x01) run FastApp[1]()
#define SET_BIT(mask,bit,bit_number) ( mask |= bit << bit_number )

enum
{
    DI0 = 0,
    DI1,
    DI2,
    DI3,
    DI4,
    DI5,
    DI6,
    DI7
};

enum
{
    AI0 = 0,
    AI1
};

enum
{
    PT0 = 0,
    PT1,
    PT2,
    PT3
};

enum
{
    DT0 = 0,
    DT1,
    DT2,
    DT3,
    DT4,
    DT5,
    DT6,
    DT7,
    DT8,
    DT9
};

%(fast_func_declaring)s

void __FAST_TASKS_Init__IT()
{
%(fast_func_init_call)s
}


%(fast_func_run_call)s



%(condition_space)s

extern plc_app_abi_t plc_yaplc_app;

#define ADD_FAST_FUNC(FUNC) (FastApp.FastPrograms_Ptr[Sz++] = FUNC)
void AppFastInit()
{
    uint8_t Sz = 0;
    __FAST_TASKS_Init__IT();
%(func_prt_space)s
    /*
    ADD_FAST_FUNC(FASTTOGGLEDO_body_run__);
    FastApp.FastPrograms_Ptr[Sz++] = FASTTOGGLEDO_body_run__;
    */
    FastApp.SzFastFunc = Sz+1;
    plc_yaplc_app.FastApp = &FastApp;
}