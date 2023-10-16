#ifndef INTERFACE_EMULATION_H_
#define INTERFACE_EMULATION_H_


#ifdef MATHLIBRARY_EXPORTS
#define MATHLIBRARY_API __declspec(dllexport)
#else
#define MATHLIBRARY_API __declspec(dllimport)
#endif

typedef struct
{
    uint8_t (*TaskDI_IRQ)(const uint8_t, uint32_t);
    uint8_t (*TaskAI_IRQ)(const uint8_t, float);
    uint8_t (*TaskPT_IRQ)(const uint8_t, float);
    uint8_t (*TaskDT_IRQ)(const uint8_t, float);
    uint32_t (*GetDO_Value)(const uint8_t, const uint8_t);
    float (*GetAO_Value)(const uint8_t, const uint8_t);
    size_t (*GetMsgInQueue)(void*);
    void (*freeMBRTU_msg)(void*);
    void (*CloseThreadMBRTU)(void);
    uint8_t (*MBRTUIsAlive)(void);
} interfaces_func_t;

uint8_t TaskDI_IRQ(const uint8_t ChNum, uint32_t value);

uint8_t TaskAI_IRQ(const uint8_t ChNum, float val);

uint8_t TaskPT_IRQ(const uint8_t ChNum, float val);

uint8_t TaskDT_IRQ(const uint8_t ChNum, float val);

uint32_t GetDO_Value(const uint8_t ChNum, const uint8_t status);

float GetAO_Value(const uint8_t ChNum, const uint8_t status);

MATHLIBRARY_API void TahoTimerUpdate();

#endif // INTERFACE_EMULATION_H_
