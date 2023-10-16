#ifndef INITSOFTPLC_H__
#define INITSOFTPLC_H__


#ifdef MATHLIBRARY_EXPORTS
#define MATHLIBRARY_API __declspec(dllexport)
#else
#define MATHLIBRARY_API __declspec(dllimport)
#endif

#include "inttypes.h"
#include "interface_emulation.h"

void InitPlc();

uint16_t REG_Init(void);

uint8_t open_connect_sql();

int InitEEPROM();

int init_eeprom_queue();



MATHLIBRARY_API void InitSoftPlc(void* _plc_app_funcs, void* _yaplc_app,
                 void *(*TestLocVarFuncTarget)(const uint8_t, const uint8_t, const uint16_t, const int32_t, const int32_t, const int32_t),
                 void* cp_func_target, interfaces_func_t* interfaces);

MATHLIBRARY_API void free_eeprom_queue();

MATHLIBRARY_API void modbus_close(void *ctx);

MATHLIBRARY_API void modbus_free(void *ctx);

MATHLIBRARY_API int SetMBRTU(int argc,char **argv);



#endif // INITSOFTPLC_H__

