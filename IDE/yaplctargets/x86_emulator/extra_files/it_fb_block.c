#include "it_fb_block.h"
#include "plc_abi.h"
#include "stdio.h"
#include "initSoftPlc.h"
/* LOCATED_VARIABLES
 * global variables
 */

#define PLC_LOC_BUF(name)  PLC_LOC_CONCAT(name, _BUF)
#define PLC_LOC_ADDR(name) PLC_LOC_CONCAT(name, _ADDR)
#define PLC_LOC_DSC(name)  PLC_LOC_CONCAT(name, _LDSC)

#define __LOCATED_VAR( type, name, lt, lsz, io_proto, ... ) \
type PLC_LOC_BUF(name);                                     \
type * name = &(PLC_LOC_BUF(name));                         \
const uint32_t PLC_LOC_ADDR(name)[] = {__VA_ARGS__};        \
const plc_loc_dsc_t PLC_LOC_DSC(name) =                     \
    {                                                       \
     .v_buf  = (void *)&(PLC_LOC_BUF(name)),                \
     .v_type = PLC_LOC_TYPE(lt),                            \
     .v_size = PLC_LOC_SIZE(lsz),                           \
     .a_size = sizeof(PLC_LOC_ADDR(name))/sizeof(uint32_t), \
     .a_data = &(PLC_LOC_ADDR(name)[0]),                    \
     .proto  = io_proto                                     \
    };

#include "LOCATED_VARIABLES.h"
#include "LOCATED_VARIABLES_HIDDEN.h"
#undef __LOCATED_VAR


/** LOCATED VARIABLES
 */

#define __LOCATED_VAR(type, name, ...) &(PLC_LOC_DSC(name)),
plc_loc_tbl_t plc_loc_table[] =
{
#include "LOCATED_VARIABLES.h"
#include "LOCATED_VARIABLES_HIDDEN.h"
};
#undef __LOCATED_VAR

#define PLC_LOC_TBL_SIZE (sizeof(plc_loc_table)/sizeof(plc_loc_dsc_t *))
uint32_t plc_loc_weigth[PLC_LOC_TBL_SIZE];



/** LOCATED VARIABLES
 *  EEPROM-registers
 */

#define __LOCATED_VAR(AddrIn, TyIn, ... ) \
    {                                     \
     .Addr = AddrIn,                      \
     .Ty   = TyIn,                        \
     .Rex  = FALSE,                       \
     .Rval = 0.0,                         \
     .Rok  = FALSE,                       \
     .Wex  = FALSE,                       \
     .Wval = 0.0,                         \
     .Wok  = FALSE                        \
    },
plc_app_eereg_t PlcEe_Regs[] =
{
#include "LOCATED_VARIABLES_EEREG.h"
};
#undef __LOCATED_VAR

//const uint32_t PLC_EE_REGS_SIZE = (sizeof(PlcEe_Regs)/sizeof(plc_app_eereg_t));
#define PLC_EE_REGS_SIZE (sizeof(PlcEe_Regs)/sizeof(plc_app_eereg_t))

/** LOCATED FUNCTIONS
 */
plc_app_funcs_t PlcAppFuncs =
{
    .DIMode     = 0,
	.DIStatus   = 0,
    .DIVal      = 0,
	.DICntRst   = 0,
    .DICntT     = 0,
    .DICnt      = 0,
    .DIEnc      = 0,

    .AIMode     = 0,
	.AIStatus   = 0,
    .AIVal      = 0,

    .DTMode     = 0,
	.DTStatus   = 0,
    .DTSetID    = 0,
    .DTGetID    = 0,
    .DTVal      = 0,

    .PTMode     = 0,
	//.PTStatus   = 0,
    .PTVal      = 0,

    .DOMode     = 0,
	.DOStatus   = 0,
    .DOVal      = 0,
    .DOFast     = 0,
    .DOPwm      = 0,
    .DOSafe     = 0,

    .AOMode     = 0,
	.AOStatus   = 0,
    .AOVal      = 0,
    .AOFast     = 0,
    .AOSafe     = 0,

    .SoftReset  = 0,

    .GetTime    = 0
};

extern uint32_t Condition_ProgramDI(const uint8_t, void*, fast_task_event_t);
extern uint32_t Condition_ProgramAI(const uint8_t, void*, fast_task_event_t);
extern uint32_t Condition_ProgramPT(const uint8_t, void*, fast_task_event_t);
extern uint32_t Condition_ProgramDT(const uint8_t, void*, fast_task_event_t);


typedef struct cond_struct_t
{
    uint32_t (*CondDI)(const uint8_t, void*, fast_task_event_t);
    uint32_t (*CondAI)(const uint8_t, void*, fast_task_event_t);
    uint32_t (*CondPT)(const uint8_t, void*, fast_task_event_t);
    uint32_t (*CondDT)(const uint8_t, void*, fast_task_event_t);
}cond_struct_t;

cond_struct_t Cond ={
    .CondDI = Condition_ProgramDI,
    .CondAI = Condition_ProgramAI,
    .CondPT = Condition_ProgramPT,
    .CondDT = Condition_ProgramDT
};

fastApp_t FastApp = {
    .cond_str = &Cond
};

//CopyFunc_t CopyVarsApp;
uint16_t reg_Index[PLC_LOC_TBL_SIZE];
uint8_t (*CopyArrayMbToAppPtr[PLC_LOC_TBL_SIZE])(void*);
uint8_t (*CopyArrayAppToMbPtr[PLC_LOC_TBL_SIZE])(void*);


CopyFunc_t CopyVarsApp = {.CopyAppToMb = &CopyArrayAppToMbPtr[0],
                          .CopyMbToApp = &CopyArrayMbToAppPtr[0],
                          .RegInd = &reg_Index[0],
                          .Sz = 0
};

interfaces_func_t SoftPLC_Interfaces;

uint8_t TaskDI_IRQ(const uint8_t ChNum, uint32_t value)
{
    if(SoftPLC_Interfaces.TaskDI_IRQ)
    {
        return SoftPLC_Interfaces.TaskDI_IRQ(ChNum, value);
    }
    return (uint8_t)0;
}

uint8_t TaskAI_IRQ(const uint8_t ChNum, float value)
{
    if(SoftPLC_Interfaces.TaskAI_IRQ)
    {
        return SoftPLC_Interfaces.TaskAI_IRQ(ChNum, value);
    }
    return (uint8_t)0;
}

uint8_t TaskPT_IRQ(const uint8_t ChNum, float value)
{
    if(SoftPLC_Interfaces.TaskPT_IRQ)
    {
        return SoftPLC_Interfaces.TaskPT_IRQ(ChNum, value);
    }
    return (uint8_t)0;
}

uint8_t TaskDT_IRQ(const uint8_t ChNum, float value)
{
    if(SoftPLC_Interfaces.TaskDT_IRQ)
    {
        return SoftPLC_Interfaces.TaskDT_IRQ(ChNum, value);
    }
    return (uint8_t)0;
}

uint32_t GetDO_Value(const uint8_t ChNum, const uint8_t status)
{
    if(SoftPLC_Interfaces.GetDO_Value)
    {
        return SoftPLC_Interfaces.GetDO_Value(ChNum, status);
    }
    return (uint32_t)0;
}

float GetAO_Value(const uint8_t ChNum, const uint8_t status)
{
    if(SoftPLC_Interfaces.GetAO_Value)
    {
        return SoftPLC_Interfaces.GetAO_Value(ChNum, status);
    }
    return 0.;
}

size_t GetMsgInQueue(void *data){
    if (SoftPLC_Interfaces.GetMsgInQueue)
    {
        return SoftPLC_Interfaces.GetMsgInQueue(data);
    }
    return 0;
}

void freeMBRTU_msg(void* data){
    if (SoftPLC_Interfaces.freeMBRTU_msg)
    {
        SoftPLC_Interfaces.freeMBRTU_msg(data);
    }
}

void CloseThreadMBRTU()
{
    if(SoftPLC_Interfaces.CloseThreadMBRTU)
    {
        SoftPLC_Interfaces.CloseThreadMBRTU();
    }

}

uint8_t MBRTUIsAlive()
{
    uint8_t res = 0;
    if(SoftPLC_Interfaces.MBRTUIsAlive)
    {
        res = SoftPLC_Interfaces.MBRTUIsAlive();
    }
    return res;
}

plc_app_abi_t plc_yaplc_app =
{
    .rte_ver_major = 1,
    .rte_ver_minor = 0,
    .rte_ver_patch = 0,

    .hw_id = 2004,

    //Located Variables
    // IO manager interface
    .l_tab = &plc_loc_table[0],
    .w_tab = &plc_loc_weigth[0],
    .l_sz  = PLC_LOC_TBL_SIZE,
    .AppCopy = &CopyVarsApp,

    //EEPROM-registers
    .ee_regs = &PlcEe_Regs[0],
    .ee_sz   = PLC_EE_REGS_SIZE,

    //Located functions
    .funcs = &PlcAppFuncs,

    //Common ticktime
    .common_ticktime = &common_ticktime__,

    //App interface
    //.id   = plc_md5,

    /*.start = startPLC,
    .stop  = stopPLC,
    .run   = runPLC,
*/
    .FastApp        = &FastApp,
/*
    .dbg_resume    = resumeDebug,
    .dbg_suspend   = suspendDebug,

    .dbg_data_get  = GetDebugData,
    .dbg_data_free = FreeDebugData,

    .dbg_vars_reset   = ResetDebugVariables,
    .dbg_var_register = RegisterDebugVariable,

    .log_cnt_get   = GetLogCount,
    .log_msg_get   = GetLogMessage,
    .log_cnt_reset = ResetLogCount,
*/    .log_msg_post  = LogMessage
};

void InitPlc()
{
    InitSoftPlc((void*)&PlcAppFuncs, (void*)&plc_yaplc_app, (void*)PlcApp_TestLocVar, (void*)&CopyVarsApp, &SoftPLC_Interfaces);
}

plc_loc_dsc_t *PlcApp_TestLocVar(const uint8_t ZoneIn, const uint8_t TypeSzIn, const uint16_t GroupIn, const int32_t A00In, const int32_t A01In, const int32_t A02In)
{
    plc_loc_dsc_t *Res = 0;
    uint16_t iVar;
    if(plc_loc_table && PLC_LOC_TBL_SIZE > 0)
    {
        for(iVar=0; iVar<PLC_LOC_TBL_SIZE; iVar++)
        {
            if(plc_loc_table[iVar]->v_type == ZoneIn && plc_loc_table[iVar]->v_size == TypeSzIn && plc_loc_table[iVar]->proto == GroupIn && plc_loc_table[iVar]->v_buf)
            {
                if(A00In >= 0 && plc_loc_table[iVar]->a_size >= 1)
                {
                    if(plc_loc_table[iVar]->a_data[0] != (uint32_t)A00In) continue;
                }

                if(A01In >= 0 && plc_loc_table[iVar]->a_size >= 2)
                {
                    if(plc_loc_table[iVar]->a_data[1] != (uint32_t)A01In) continue;
                }

                if(A02In >= 0 && plc_loc_table[iVar]->a_size >= 3)
                {
                    if(plc_loc_table[iVar]->a_data[2] != (uint32_t)A02In) continue;
                }

                Res = (plc_loc_dsc_t *)plc_loc_table[iVar];
                break;
            }
        }
    }
    return (Res);
}


/** F(B) C-code
 */

//@TODO + define APP_* from LOCATED_VARIABLES_HIDDEN (by used libraries)

/** DI
 */

#ifdef LIB_APP_DI

/** @brief  DIMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DIMode(DIMODE *DataIn)
{
    if(DataIn && PlcAppFuncs.DIMode)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE DIn = __GET_VAR(DataIn->DIN);
        BYTE M   = __GET_VAR(DataIn->M);
        BYTE Ok  = 0;

        PlcAppFuncs.DIMode(&Ex, &DIn, &M, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DIStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DIStatus(DISTATUS *DataIn)
{
    if(DataIn && PlcAppFuncs.DIStatus)
    {
        BYTE  DIn = __GET_VAR(DataIn->DIN);
        BYTE Om   = 0;
        BYTE Ok   = 0;
		BOOL En = __GET_VAR(DataIn->EN);

        PlcAppFuncs.DIStatus(&DIn, &Om, &Ok);

        __SET_VAR(DataIn->, OM,, Om);
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DIVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DIVal(DIVAL *DataIn)
{
    if(DataIn && PlcAppFuncs.DIVal)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE DIn = __GET_VAR(DataIn->DIN);
        BOOL Ov  = 0;
        BYTE Ok  = 0;

        PlcAppFuncs.DIVal(&Ex, &DIn, &Ov, &Ok);

        if(Ex)
		{
        __SET_VAR(DataIn->, OV,, Ov);
		}

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DICntRst.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DICntRst(DICNTRST *DataIn)
{
    if(DataIn && PlcAppFuncs.DICntRst)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE DIn = __GET_VAR(DataIn->DIN);
        BOOL Rst = __GET_VAR(DataIn->RST);
        BYTE Ok  = 0;

        PlcAppFuncs.DICntRst(&Ex, &DIn, &Rst, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}


//----------------------------------------------------------------------------------------------------------
/** @brief  DICntT.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DICntT(BOOL *Ex, BYTE *DIn, WORD *Ov, BOOL *OisSet, BYTE *Ok)
void App_DICntT(DICNTT *DataIn)
{
    if(DataIn && PlcAppFuncs.DICntT)
    {
        BOOL Ex    = __GET_VAR(DataIn->EX);
        BYTE DIn   = __GET_VAR(DataIn->DIN);
        WORD Ov    = 0;
        BOOL OisSet  = 0;
        BYTE Ok    = 0;

        PlcAppFuncs.DICntT(&Ex, &DIn, &Ov, &OisSet, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OV,, Ov);
         __SET_VAR(DataIn->, OISSET,, OisSet);
		}
        __SET_VAR(DataIn->, OK,, Ok);
    }
}


/** @brief  DISetCfgCntT.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DISetCfgCntT(BOOL *Ex, BYTE *DIn, WORD *Sp, BOOL *EnCmpMd, BYTE *Ok)
void App_DISetCfgCntT(DISETCFGCNTT *DataIn)
{
    if(DataIn && PlcAppFuncs.DISetCfgCntT)
    {
        BOOL Ex    = __GET_VAR(DataIn->EX);
        BYTE DIn   = __GET_VAR(DataIn->DIN);
		WORD Sp   = __GET_VAR(DataIn->SP);
		BOOL EnCmpMd   = __GET_VAR(DataIn->ENCMPMD);
        BYTE Ok    = 0;

        PlcAppFuncs.DISetCfgCntT(&Ex, &DIn, &Sp, &EnCmpMd, &Ok);

       __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DIStateCfgCntT.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DIStateCfgCntT(BYTE *DIn, WORD *OSp, BOOL *OEnCmpMd, BYTE *Ok)
void App_DIStateCfgCntT(DISTATECFGCNTT *DataIn)
{
    if(DataIn && PlcAppFuncs.DIStateCfgCntT)
    {
        BYTE DIn   = __GET_VAR(DataIn->DIN);
        WORD OSp    = 0;
        BOOL OEnCmpMd  = 0;
        BYTE Ok    = 0;

        PlcAppFuncs.DIStateCfgCntT(&DIn, &OSp, &OEnCmpMd, &Ok);

        __SET_VAR(DataIn->, OSP,, OSp);
        __SET_VAR(DataIn->, OENCMPMD,, OEnCmpMd);
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

//--------------------------------------------------------------------------------------------------------------

/** @brief  DICnt.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DICnt(BOOL *Ex, BYTE *DIn, DWORD *Ov, BOOL *OisSet, BYTE *Ok)
void App_DICnt(DICNT *DataIn)
{
    if(DataIn && PlcAppFuncs.DICnt)
    {
        BOOL Ex    = __GET_VAR(DataIn->EX);
        BYTE DIn   = __GET_VAR(DataIn->DIN);
        DWORD Ov   = 0;
        BOOL OisSet  = 0;
        BYTE Ok    = 0;

        PlcAppFuncs.DICnt(&Ex, &DIn, &Ov, &OisSet, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OV,, Ov);
         __SET_VAR(DataIn->, OISSET,, OisSet);
		}
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DISetCfgCnt.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DISetCfgCnt(BOOL *Ex, BYTE *DIn, DWORD *Sp, BOOL *EnCmpMd, BYTE *Ok)
void App_DISetCfgCnt(DISETCFGCNT *DataIn)
{
    if(DataIn && PlcAppFuncs.DISetCfgCnt)
    {
        BOOL Ex    = __GET_VAR(DataIn->EX);
        BYTE DIn   = __GET_VAR(DataIn->DIN);
		DWORD Sp   = __GET_VAR(DataIn->SP);
		BOOL EnCmpMd   = __GET_VAR(DataIn->ENCMPMD);
        BYTE Ok    = 0;

        PlcAppFuncs.DISetCfgCnt(&Ex, &DIn,  &Sp, &EnCmpMd, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DIStateCfgCnt.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DIStateCfgCnt(BYTE *DIn, DWORD *OSp, BOOL *OEnCmpMd, BYTE *Ok)
void App_DIStateCfgCnt(DISTATECFGCNT *DataIn)
{
    if(DataIn && PlcAppFuncs.DIStateCfgCnt)
    {
        BYTE DIn   = __GET_VAR(DataIn->DIN);
        DWORD OSp    = 0;
        BOOL OEnCmpMd  = 0;
        BYTE Ok    = 0;

        PlcAppFuncs.DIStateCfgCnt(&DIn, &OSp, &OEnCmpMd, &Ok);

        __SET_VAR(DataIn->, OSP,, OSp);
        __SET_VAR(DataIn->, OENCMPMD,, OEnCmpMd);
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

//--------------------------------------------------------------------------------------------------------------

/** @brief  DIEnc.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DIEnc(BOOL *Ex, BYTE *DIn, DWORD *OvA, BOOL *OisSetA, DWORD *OvB, BOOL *OisSetB, WORD *OvT, BOOL *OisSetT, BYTE *Ok)
void App_DIEnc(DIENC *DataIn)
{
    if(DataIn && PlcAppFuncs.DIEnc)
    {
        BOOL  Ex     = __GET_VAR(DataIn->EX);
        BYTE  DIn    = __GET_VAR(DataIn->DIN);
        DWORD OvA     = 0;
        BOOL  OisSetA  = 0;
        DWORD OvB     = 0;
        BOOL  OisSetB  = 0;
        WORD  OvT     = 0;
        BOOL  OisSetT  = 0;
        BYTE  Ok     = 0;

        PlcAppFuncs.DIEnc(&Ex, &DIn, &OvA, &OisSetA, &OvB, &OisSetB, &OvT, &OisSetT, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OVA,, OvA);
         __SET_VAR(DataIn->, OISSETA,, OisSetA);
         __SET_VAR(DataIn->, OVB,, OvB);
         __SET_VAR(DataIn->, OISSETB,, OisSetB);
         __SET_VAR(DataIn->, OVT,, OvT);
         __SET_VAR(DataIn->, OISSETT,, OisSetT);
		}

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DISetCfgEnc.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DISetCfgEnc(BOOL *Ex, BYTE *DIn, DWORD *SpA, BOOL *EnCmpMdA, DWORD *SpB, BOOL *EnCmpMdB, WORD *SpT, BOOL *EnCmpMdT, BYTE *Ok)
void App_DISetCfgEnc(DISETCFGENC *DataIn)
{
    if(DataIn && PlcAppFuncs.DISetCfgEnc)
    {
        BOOL  Ex     = __GET_VAR(DataIn->EX);
        BYTE  DIn    = __GET_VAR(DataIn->DIN);
		DWORD SpA   = __GET_VAR(DataIn->SPA);
		BOOL EnCmpMdA   = __GET_VAR(DataIn->ENCMPMDA);
		DWORD SpB   = __GET_VAR(DataIn->SPB);
		BOOL EnCmpMdB   = __GET_VAR(DataIn->ENCMPMDB);
		WORD SpT   = __GET_VAR(DataIn->SPT);
		BOOL EnCmpMdT   = __GET_VAR(DataIn->ENCMPMDT);
		BYTE SpMultiplier = __GET_VAR(DataIn->SPMULTIPLIER);

        BYTE  Ok     = 0;

        PlcAppFuncs.DISetCfgEnc(&Ex, &DIn, &SpA, &EnCmpMdA, &SpB, &EnCmpMdB, &SpT, &EnCmpMdT, &SpMultiplier, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DIStateCfgEnc.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DIStateCfgEnc(BYTE *DIn, DWORD *OSpA, BOOL *OEnCmpMdA, DWORD *OSpB, BOOL *OEnCmpMdB, WORD *OSpT, BOOL *OEnCmpMdT, BYTE *Ok)
void App_DIStateCfgEnc(DISTATECFGENC *DataIn)
{
    if(DataIn && PlcAppFuncs.DIStateCfgEnc)
    {
        BYTE  DIn    = __GET_VAR(DataIn->DIN);
        DWORD OSpA     = 0;
        BOOL  OEnCmpMdA  = 0;
        DWORD OSpB     = 0;
        BOOL  OEnCmpMdB  = 0;
        WORD  OSpT     = 0;
        BOOL  OEnCmpMdT  = 0;
        BYTE  SpMultiplier = 1;

        BYTE  Ok     = 0;

        PlcAppFuncs.DIStateCfgEnc(&DIn, &OSpA, &OEnCmpMdA, &OSpB, &OEnCmpMdB, &OSpT, &OEnCmpMdT, &SpMultiplier, &Ok);
        //PlcAppFuncs.DIStateCfgEnc(&DIn, &OSpA, &OEnCmpMdA, &OSpB, &OEnCmpMdB, &OSpT, &OEnCmpMdT, &Ok);

        __SET_VAR(DataIn->, OSPA,, OSpA);
        __SET_VAR(DataIn->, OENCMPMDA,, OEnCmpMdA);
        __SET_VAR(DataIn->, OSPB,, OSpB);
        __SET_VAR(DataIn->, OENCMPMDB,, OEnCmpMdB);
        __SET_VAR(DataIn->, OSPT,, OSpT);
        __SET_VAR(DataIn->, OENCMPMDT,, OEnCmpMdT);
        __SET_VAR(DataIn->, SPMULTIPLIER,, SpMultiplier);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

//-------------------------------------------------------------------------------------------------------------------------------------------------------

#endif // LIB_APP_DI



/** AI
 */

#ifdef LIB_APP_AI

/** @brief  AIMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AIMode(AIMODE *DataIn)
{
    if(DataIn && PlcAppFuncs.AIMode)
    {
        BOOL  Ex  = __GET_VAR(DataIn->EX);
        BYTE  AIn = __GET_VAR(DataIn->AIN);
        BYTE  M   = __GET_VAR(DataIn->M);

        BYTE Ok   = 0;

        PlcAppFuncs.AIMode(&Ex, &AIn, &M, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  AIStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AIStatus(AISTATUS *DataIn)
{
    if(DataIn && PlcAppFuncs.AIStatus)
    {
        BYTE  AIn = __GET_VAR(DataIn->AIN);
        BYTE Om   = 0;
        BYTE Os   = 0;
        BYTE Ok   = 0;
		BOOL En = __GET_VAR(DataIn->EN);

        PlcAppFuncs.AIStatus(&AIn, &Om, &Os, &Ok);

        __SET_VAR(DataIn->, OM,, Om);
        __SET_VAR(DataIn->, OS,, Os);
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  AIVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AIVal(AIVAL *DataIn)
{
    if(DataIn && PlcAppFuncs.AIVal)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE AIn = __GET_VAR(DataIn->AIN);
        REAL Ov  = 0.0;
        BYTE Ok  = 0;

        PlcAppFuncs.AIVal(&Ex, &AIn, &Ov, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OV,, Ov);
		}

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

#endif // LIB_APP_AI



/** DT
 */

#ifdef LIB_APP_DT

/** @brief  DTMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTMode(DTMODE *DataIn)
{
    if(DataIn && PlcAppFuncs.DTMode)
    {
        BOOL  Ex  = __GET_VAR(DataIn->EX);
        BYTE  DTn = __GET_VAR(DataIn->DTN);
        BYTE  M   = __GET_VAR(DataIn->M);
        BYTE Ok   = 0;

        PlcAppFuncs.DTMode(&Ex, &DTn, &M, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DTStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTStatus(DTSTATUS *DataIn)
{
    if(DataIn && PlcAppFuncs.DTStatus)
    {
        BYTE  DTn = __GET_VAR(DataIn->DTN);
        BYTE Om   = 0;
        BYTE Os   = 0;
        BYTE Ok   = 0;
		BOOL En = __GET_VAR(DataIn->EN);

        PlcAppFuncs.DTStatus(&DTn, &Om, &Os, &Ok);

        __SET_VAR(DataIn->, OM,, Om);
        __SET_VAR(DataIn->, OS,, Os);
        __SET_VAR(DataIn->, OK,, Ok);
    }
}


/** @brief  DTSetId.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTSetId(DTSETID *DataIn)
{
    if(DataIn && PlcAppFuncs.DTSetID)
    {
        BOOL  Ex  = __GET_VAR(DataIn->EX);
        BYTE  DTn = __GET_VAR(DataIn->DTN);
        LWORD ID  = __GET_VAR(DataIn->ID);
        BYTE  Ok  = 0;

        PlcAppFuncs.DTSetID(&Ex, &DTn, &ID, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DTGetId.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTGetId(DTGETID *DataIn)
{
    if(DataIn && PlcAppFuncs.DTGetID)
    {
        BYTE  DTn = __GET_VAR(DataIn->DTN);
        LWORD OID = 0;
        BYTE  Ok  = 0;

        PlcAppFuncs.DTGetID(&DTn, &OID, &Ok);

        __SET_VAR(DataIn->, OID,, OID);
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DTVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTVal(DTVAL *DataIn)
{
    if(DataIn && PlcAppFuncs.DTVal)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE DTn = __GET_VAR(DataIn->DTN);
        REAL Ov  = 0.0;
        BYTE Ok  = 0;

        PlcAppFuncs.DTVal(&Ex, &DTn, &Ov, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OV,, Ov);
		}
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

#endif // LIB_APP_DT



/** PT
 */

#ifdef LIB_APP_PT

/** @brief  PTMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_PTMode(PTMODE *DataIn)
{
    if(DataIn && PlcAppFuncs.PTMode)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE PTn = __GET_VAR(DataIn->PTN);
        BYTE M   = __GET_VAR(DataIn->M);
        BYTE STy = __GET_VAR(DataIn->STY);
        BYTE Ok  = 0;

        PlcAppFuncs.PTMode(&Ex, &PTn, &M, &STy, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  PTStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_PTStatus(PTSTATUS *DataIn)
{
    if(DataIn && PlcAppFuncs.PTStatus)
    {
        BYTE  PTn = __GET_VAR(DataIn->PTN);
        BYTE Om   = 0;
        BYTE Os   = 0;
        BYTE Ok   = 0;
		BOOL En = __GET_VAR(DataIn->EN);

        PlcAppFuncs.PTStatus(&PTn, &Om, &Os, &Ok);

        __SET_VAR(DataIn->, OM,, Om);
        __SET_VAR(DataIn->, OS,, Os);
        __SET_VAR(DataIn->, OK,, Ok);
    }
}


/** @brief  PTVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_PTVal(PTVAL *DataIn)
{
    if(DataIn && PlcAppFuncs.PTVal)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE PTn = __GET_VAR(DataIn->PTN);
        REAL Ov  = 0.0;
        BYTE Ok  = 0;

        PlcAppFuncs.PTVal(&Ex, &PTn, &Ov, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OV,, Ov);
		}
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

#endif // LIB_APP_PT



/** DO
 */

#ifdef LIB_APP_DO

/** @brief  DOMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOMode(DOMODE *DataIn)
{
    if(DataIn && PlcAppFuncs.DOMode)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE DOn = __GET_VAR(DataIn->DON);
        BYTE M   = __GET_VAR(DataIn->M);
        BYTE Ok  = 0;

        PlcAppFuncs.DOMode(&Ex, &DOn, &M, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

//void PlcApp_DOStatus(BYTE *DOn, BYTE *Om, BOOL *Oepwm, DWORD *Otpwm, REAL *Odpwm, BOOL *Oesf, BOOL *Ovsf, BYTE *Ok)


/** @brief  DOStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOStatus(DOSTATUS *DataIn)
{
    if(DataIn && PlcAppFuncs.DOStatus)
    {
        BYTE  DOn = __GET_VAR(DataIn->DON);
        BYTE Om   = 0;
        BOOL Oepwm   = 0;
		DWORD Otpwm   = 0;
		REAL  Odpwm   = 0;
		BOOL Oesf   = 0;
		BOOL Ovsf   = 0;
        BYTE Ok   = 0;
		BOOL En = __GET_VAR(DataIn->EN);

        PlcAppFuncs.DOStatus(&DOn, &Om, &Oepwm, &Otpwm, &Odpwm, &Oesf, &Ovsf, &Ok);

        __SET_VAR(DataIn->, OM,, Om);
        __SET_VAR(DataIn->, OEPWM,, Oepwm);
		__SET_VAR(DataIn->, OTPWM,, Otpwm);
		__SET_VAR(DataIn->, ODPWM,, Odpwm);

		__SET_VAR(DataIn->, OESF,, Oesf);
		__SET_VAR(DataIn->, OVSF,, Ovsf);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DOVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOVal(DOVAL *DataIn)
{
    if(DataIn && PlcAppFuncs.DOVal)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE DOn = __GET_VAR(DataIn->DON);
        BOOL V   = __GET_VAR(DataIn->V);
        BOOL Ov  = 0;
        BYTE Ok  = 0;

        PlcAppFuncs.DOVal(&Ex, &DOn, &V, &Ov, &Ok);

        if(Ex)
		{
        __SET_VAR(DataIn->, OV,, Ov);
		}
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DOFast.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOFast(DOFAST *DataIn)
{
    if(DataIn && PlcAppFuncs.DOFast)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE DOn = __GET_VAR(DataIn->DON);
        BOOL V   = __GET_VAR(DataIn->V);
        BOOL Ov  = 0;
        BYTE Ok  = 0;

        PlcAppFuncs.DOFast(&Ex, &DOn, &V, &Ov, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OV,, Ov);
		}
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DOPwm.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOPwm(DOPWM *DataIn)
{
    if(DataIn && PlcAppFuncs.DOPwm)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BOOL En  = __GET_VAR(DataIn->ENPWM);
        BYTE DOn = __GET_VAR(DataIn->DON);
        DWORD Tm = __GET_VAR(DataIn->TM);
        REAL  D  = __GET_VAR(DataIn->DU);
        BYTE Ok  = 0;

        PlcAppFuncs.DOPwm(&Ex, &En, &DOn, &Tm, &D, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  DOSafe.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOSafe(DOSAFE *DataIn)
{
    if(DataIn && PlcAppFuncs.DOSafe)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BOOL En  = __GET_VAR(DataIn->ENSF);
        BYTE DOn = __GET_VAR(DataIn->DON);
        BOOL V   = __GET_VAR(DataIn->V);
        BYTE Ok  = 0;

        PlcAppFuncs.DOSafe(&Ex, &En, &DOn, &V, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

#endif // LIB_APP_DO



/** AO
 */

#ifdef LIB_APP_AO

/** @brief  AOMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOMode(AOMODE *DataIn)
{
    if(DataIn && PlcAppFuncs.AOMode)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE AOn = __GET_VAR(DataIn->AON);
        BYTE M   = __GET_VAR(DataIn->M);
        BYTE Ok  = 0;

        PlcAppFuncs.AOMode(&Ex, &AOn, &M, &Ok);
        __SET_VAR(DataIn->, OK,, Ok);
        printf("Ex: %u, AOn: %u, M: %u, Ok: %u\n", Ex, AOn, M, Ok);
    }else printf("Error!!!\n");
}

/** @brief  AOStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOStatus(AOSTATUS *DataIn)
{
    if(DataIn && PlcAppFuncs.AOStatus)
    {
        BYTE  AOn = __GET_VAR(DataIn->AON);
        BYTE Om   = 0;
		BOOL Oesf   = 0;
		REAL Ovsf   = 0;
        BYTE Ok   = 0;
		BOOL En = __GET_VAR(DataIn->EN);

        PlcAppFuncs.AOStatus(&AOn, &Om, &Oesf, &Ovsf, &Ok);

        __SET_VAR(DataIn->, OM,, Om);

		__SET_VAR(DataIn->, OESF,, Oesf);
		__SET_VAR(DataIn->, OVSF,, Ovsf);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  AOVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOVal(AOVAL *DataIn)
{
    if(DataIn && PlcAppFuncs.AOVal)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE AOn = __GET_VAR(DataIn->AON);
        REAL V   = __GET_VAR(DataIn->V);
        REAL Ov  = 0.0;
        BYTE Ok  = 0;

        PlcAppFuncs.AOVal(&Ex, &AOn, &V, &Ov, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OV,, Ov);
		}
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  AOFast.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOFast(AOFAST *DataIn)
{
    if(DataIn && PlcAppFuncs.AOFast)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BYTE AOn = __GET_VAR(DataIn->AON);
        REAL V   = __GET_VAR(DataIn->V);
        REAL Ov  = 0.0;
        BYTE Ok  = 0;

        PlcAppFuncs.AOFast(&Ex, &AOn, &V, &Ov, &Ok);

		if(Ex)
		{
         __SET_VAR(DataIn->, OV,, Ov);
		}
        __SET_VAR(DataIn->, OK,, Ok);
    }
}

/** @brief  AOSafe.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOSafe(AOSAFE *DataIn)
{
    if(DataIn && PlcAppFuncs.AOSafe)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BOOL En  = __GET_VAR(DataIn->ENSF);
        BYTE AOn = __GET_VAR(DataIn->AON);
        REAL V   = __GET_VAR(DataIn->V);
        BYTE Ok  = 0;

        PlcAppFuncs.AOSafe(&Ex, &En, &AOn, &V, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
    }
}

#endif // LIB_APP_AO



/** EEPROM
 */

#ifdef LIB_APP_EEPROM

/** @brief  Clear all memory.
 *  @param  ExIn - allow execution.
 *  @param  OkOut - pointer to result.
 *  @return None.
 */
void AppEe_Clr(BOOL ExIn, BOOL *OkOut)
{
    if(OkOut)
    {
        *__QX4_1_1 = ExIn;
        *OkOut = __IX4_1_5_BUF;
    }
}

/** @brief  Search item in global array PlcEe_Regs.
 *  @param  AddrIn - start address of memory,
 *  @param  TyIn - ID of data type.
 *  @return Index to array PlcEe_Regs or -1.
 */
int32_t AppEe_Search(DINT AddrIn, BYTE TyIn)
{
    int32_t i=0;
    for(i=0; i<(int32_t)(PLC_EE_REGS_SIZE); i++)
    {
        if(PlcEe_Regs[i].Addr == AddrIn && PlcEe_Regs[i].Ty == TyIn) return (i);
    }
    return ((int32_t)(-1));
}

/** @brief  Read data.
 *  @param  DataIn - pointer to structure of arguments.
 *  @return None.
 */
void AppEe_Read(EEREADLREAL *DataIn)
{
    if(DataIn)
    {
        EEREGLREAL TEMP = __GET_VAR(DataIn->REG);
        int32_t IDx     = AppEe_Search(TEMP.ADDR, TEMP.TY);

        if(IDx > -1)
        {
            PlcEe_Regs[IDx].Rex = __GET_VAR(DataIn->EX);

            __SET_VAR(DataIn->, OVAL,, PlcEe_Regs[IDx].Rval);
            __SET_VAR(DataIn->, OK,, PlcEe_Regs[IDx].Rok);
        }
    }
}

/** @brief  Write data.
 *  @param  DataIn - pointer to structure of arguments.
 *  @return None.
 */
void AppEe_Write(EEWRITELREAL *DataIn)
{
    if(DataIn)
    {
        EEREGLREAL TEMP = __GET_VAR(DataIn->REG);
        int32_t IDx     = AppEe_Search(TEMP.ADDR, TEMP.TY);

        if(IDx > -1)
        {
            PlcEe_Regs[IDx].Wex  = __GET_VAR(DataIn->EX);
            PlcEe_Regs[IDx].Wval = __GET_VAR(DataIn->VAL);

            __SET_VAR(DataIn->, OK,, PlcEe_Regs[IDx].Wok);
        }
    }
}

#endif // LIB_APP_EEPROM



/** FLR
 */

#ifdef LIB_APP_FLR

/** @brief  Gaus-function.
 *  @param  C   - value of In, where Gaus-function is maximum (1.0).
 *  @param  S   - incremental step of Gaus-function.
 *  @param  In  - input value.
 *  @param  Out - result.
 *  @return Result.
 */
REAL AppFlr_GausFx(const REAL C, const REAL S, const REAL In)
{
    if(S) return (exp(((-1.0)*(0.5*powf((In-C), 2.0)))/(powf(S, 2.0))));
    return (0.0);
}

/** @brief  Triangle-function.
 *  @param  A   - A-argument.
 *  @param  B   - B-argument.
 *  @param  C   - C-argument.
 *  @param  In  - input value.
 *  @return Result.
 */
//REAL AppFlr_TriangleFx(const REAL A, const REAL B, const REAL C, const REAL In)
//{
//    if(In > A && In < C) return ((In < B) ? (In-A)/(B-A) : (C-In)/(C-B));
//    return (0.0);
//}

REAL AppFlr_TriangleFx(const REAL A, const REAL B, const REAL C, const REAL In)  //Треугольная функция принадлежности (для входных параметров)
 {
	REAL RetVal = 0.0;

	if ((In > A) && (In < C))
	{
		if (In < B) RetVal = (In - A)/(B - A);
		if (In >= B) RetVal = (C - In)/(C - B);
	}
	return RetVal;
}


/** @brief  Get difference between value and setpoint in Term-format (-1 .. 1).
 *  @param  ErSrc  - source difference (error).
 *  @return None.
 */
REAL AppFlr_ErTerm(const REAL ErSrc)
{
    //trigonometric function
    REAL Er = (270.0-ErSrc);
    if(Er < 180.0) Er = 180.0;  //to min
    if(Er > 360.0) Er = 360.0;  //to max
    Er = Er*(APP_FLR_PI/180.0); //to radian
    Er = cos(Er)*2.0;
    return (Er);
}

/** @brief  Get output terms.
 *  @param  Sigma - Sigma-value.
 *  @param  Min - minimum.
 *  @param  Max - maximum.
 *  @param  In  - input value.
 *  @param  Out - pointer to array of output terms.
 *  @return None.
 */
void AppFlr_OutTerms(const REAL Sigma, const REAL Min, const REAL Max, const REAL In, REAL *Out)
{
    if(Out)
    {
        REAL S = ((Sigma != 0.0) ? Sigma : (Max-Min)/((REAL)(2*APP_FLR_SZ)));
        REAL C;
        BYTE i;

        for(i=0; i<APP_FLR_SZ; i++)
        {
            if(In < Min)
            {
                //fast open
                Out[i] = ((i == APP_FLR_OUT_OP2) ? APP_FLR_MAX : 0.0);
            }
            else if(In > Max)
            {
                //fast close
                Out[i] = ((i == APP_FLR_OUT_CL2) ? APP_FLR_MAX : 0.0);
            }
            else
            {
                C = Min+((((REAL)i)*(Max-Min))/((REAL)(APP_FLR_SZ-1)));
                Out[i] = AppFlr_GausFx(C, S, In);
            }
        }
    }
}


//Функция дефазификации и аккамулирования термов выходного вектора
REAL AppFlr_AccProb (REAL Inp, REAL *A, REAL *B, REAL *C, REAL *InpVec)
{
	BYTE i;
	REAL Max, Acc;

	Max = InpVec[0] * AppFlr_TriangleFx (A[0], B[0], C[0], Inp);
	for (i = 1; i < APP_FLR_SZ; i++)
	{
		Acc = InpVec[i] * AppFlr_TriangleFx (A[i], B[i], C[i], Inp);
		if (Acc > Max)
			Max = Acc;
	}
	return Max;
}


/** @brief  Accumulate actions.
 *  @param  dX  - step of value increase.
 *  @param  Min - minimum.
 *  @param  Max - maximum.
 *  @param  Actions - pointer to array of actions.
 *  @return Value of control action.
 */
REAL AppFlr_AccActions(const REAL dX, const REAL Min, const REAL Max, REAL *Actions, REAL *OCm, REAL *Om)
{
    if(Actions && dX)
    {
        /** @var Arguments of Triangle-function
         */
        REAL A[APP_FLR_SZ] = {-1.0, -0.7, -0.25, 0.4, 0.8};
        REAL B[APP_FLR_SZ] = {-0.9, -0.5,  0.0,  0.5, 0.9};
        REAL C[APP_FLR_SZ] = {-0.8, -0.3,  0.25, 0.7, 1.0};

        REAL Val, Acc;
        REAL L  = 0.0;
        REAL R  = 0.0;
        REAL cm = 0.0;
        REAL m  = 0.000000001;
        BYTE i;

	    L = AppFlr_AccProb (-1,  A,  B, C, Actions);
	    for (Val=Min; Val<=Max; Val+=dX)
	    {
         R = AppFlr_AccProb (Val, A,  B, C, Actions);
         cm	= cm + dX *(((Val*L) + (Val+dX)*R)/2);
	     m = m + ((L + R)/2.0) * dX;
	     L = R;
	    }

        if(OCm) *OCm = cm;
        if(Om)  *Om  = m;

        if(m != 0.0) return (cm/m);
    }

    return (0.0);
}


//REAL AppFlr_AccActions(const REAL dX, const REAL Min, const REAL Max, REAL *Actions, REAL *OCm, REAL *Om)
//{
//    if(Actions && dX)
//    {
//        /** @var Arguments of Triangle-function
//         */
//        REAL A[APP_FLR_SZ] = {-1.0, -0.7, -0.25, 0.4, 0.8};
//        REAL B[APP_FLR_SZ] = {-0.9, -0.5,  0.0,  0.5, 0.9};
//        REAL C[APP_FLR_SZ] = {-0.8, -0.3,  0.25, 0.7, 1.0};
//
//        REAL Val, Acc;
//        REAL L  = 0.0;
//        REAL R  = 0.0;
//        REAL cm = 0.0;
//        REAL m  = 0.000000001;
//        BYTE i;
//
//        for(Val=Min; Val<=Max; Val+=dX)
//        {
//            //accumulate value
//            for(i=0; i<APP_FLR_SZ; i++)
//            {
//                Acc = Actions[i]*AppFlr_TriangleFx(A[i], B[i], C[i], Val);
//                if(!i || Acc > R) R = Acc;
//            }
//
//            cm = cm	+ (dX*(((Val*L)+(Val+dX)*R)/2.0));
//            m  = m	+ (((L+R)/2.0)*dX);
//            L  = R;
//        }
//
//        if(OCm) *OCm = cm;
//        if(Om)  *Om  = m;
//
//        if(m != 0.0) return (cm/m);
//    }
//
//    return (0.0);
//}

/** @brief  Probability of normal state.
 *  @param  V       - current value.
 *  @param  Sp      - setpont.
 *  @param  Speed   - speed of changing V at time TmCy.
 *  @param  ActNorm - value of normal action.
 *  @param  Y       - Y-value.
 *  @return None.
 */
void AppFlr_ProbNorm(const REAL V, const REAL Sp, const REAL Speed, const REAL ActNorm, REAL *Y)
{
    if(Y)
    {
        /** @var Inverse probability of normal state
         */
        //REAL q = (1.0-ActNorm);
        //if(q > APP_FLR_Q_MIN && q < APP_FLR_Q_MAX)
        //{
        //    if((V < Sp && Speed > 0.0) || (V > Sp && Speed < 0.0))
        //    {
        //        *Y *= (-1.0);
        //    }
        //}
		//-------------------------------------------------------------------------------------


		//===========================================================================================================================
		REAL q = fabs((LREAL)(1.0-ActNorm));
		//if(V < Sp)
		//{
			if(((V < Sp) && (Speed > 0)) || ((V > Sp) && (Speed < 0)))//и если значение входного параметра увеличивается
			{
				if((q > 0.0) && (q < 0.1) && (fabs((LREAL)Speed) > HI_SPEED_DELTA)) // и вероятность от состояния "Не изменять" выше 0.7
				{
		         //Xcm *= -1;// Меняем направление приращения управляющего воздействия на противоположное
		         //------------ Модифицировно 2020 ------
					if(*Y <= 0)
						*Y += 1;
					else
						*Y -= 1;

					*Y /= 2.5;
				//--------------------------------------
				}
			}
		//}
        //==========================================================================================================================
/*        if(V < Sp)
		{
		 *Y = 0.5;
		}
		else
         *Y = -0.5; */
        //==========================================================================================================================

		//if(V > Sp)// Если текущее значение входного параметра больше заданного
		//{
		//	if(Speed < 0)//и если значение входного параметра уменьшается
		//	{
		//		if((q > 0.0) && (q < 0.1)) // и вероятность от состояния "Не изменять" выше 0.7
		//		{
		//			//Xcm *= -1;// Меняем направление приращения управляющего воздействия на противоположное
		//			//------------ Модифицировно 2020 ------
		//			if(*Y <= 0)
		//				*Y += 1;
		//			else
		//				*Y -= 1;
		//
		//			*Y /= 2.5;
		//			//--------------------------------------
		//		}
		//	}
		//}
    }
}

/** @brief  Get direction of changing Y.
 *  @param  Y - Y-value.
 *  @return UpDown-value.
 */
SINT AppFlr_UpDown(const REAL Y)
{
    if(Y < 0.0) return (APP_FLR_DIR_DOWN);
    if(Y > 0.0) return (APP_FLR_DIR_UP);
    return (APP_FLR_DIR_NONE);
}

/** @brief  Get time of changing Y.
 *  @param  Tm - time of main-cycle (msec).
 *  @param  Y - Y-value.
 *  @return UpDown-value.
 */
REAL AppFlr_dVTm(const REAL Tm, const REAL Y)
{
    if(Tm)
    {
        REAL Yabs = (REAL)fabs((LREAL)Y);
        return ((Tm-(Yabs*Tm)));
    }
    return (0.0);
}

/** @brief  FuzzyLogic.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void AppFlr(FLR1 *DataIn)
{
    if(DataIn)
    {
        //get FB-data
        REAL V      = __GET_VAR(DataIn->V);
        REAL Vprev  = __GET_VAR(DataIn->VPREV);
        REAL Sp     = __GET_VAR(DataIn->SP);
        REAL ErSrc  = __GET_VAR(DataIn->ER);
        REAL Tm     = __GET_VAR(DataIn->TM);
		BOOL OrdInp = __GET_VAR(DataIn->ORDINP);

        /** @var Debug
         */
        REAL Ocm, Om;

        /** @var Speed of changing source value
         */

		//(REAL)fabs((LREAL)Y);

        REAL Speed = 0.0;//(V-Vprev);

		if(V > Vprev)
		 Speed = V/Vprev;
	    else
		 Speed = Vprev/V * (-1);

        /** @var Difference between value and setpoint (Term-format)
         */

		if(OrdInp)
			ErSrc /= 1.111;
		else
			ErSrc /= 0.1111;

        REAL Er = AppFlr_ErTerm(ErSrc);

        /** @var Output terms
         */
        REAL Outputs[APP_FLR_SZ];
        //init. output terms
        AppFlr_OutTerms(APP_FLR_SIGMA, APP_FLR_MIN, APP_FLR_MAX, Er, Outputs);

        /** @var Actions
         */
        REAL Actions[APP_FLR_SZ];
        //rules
        Actions[APP_FLR_IN_HI2]  = Outputs[APP_FLR_OUT_CL2];
        Actions[APP_FLR_IN_HI]   = Outputs[APP_FLR_OUT_CL1];
        Actions[APP_FLR_IN_NORM] = Outputs[APP_FLR_OUT_NONE];
        Actions[APP_FLR_IN_LO]   = Outputs[APP_FLR_OUT_OP1];
        Actions[APP_FLR_IN_LO2]  = Outputs[APP_FLR_OUT_OP2];
        //accumulate actions
        REAL Y = AppFlr_AccActions(APP_FLR_DX, APP_FLR_MIN, APP_FLR_MAX, Actions, &Ocm, &Om);
        //probability of normal action
        AppFlr_ProbNorm(V, Sp, Speed, Actions[APP_FLR_IN_NORM], &Y);

        /** @var Direction of changing Y
         */
        SINT UpDown = AppFlr_UpDown(Y);

        /** @var Time of changing Y (msec)
         */
        REAL TmDv = AppFlr_dVTm(Tm, Y);

        //set FB-data
        __SET_VAR(DataIn->, VPREV,, V);
        __SET_VAR(DataIn->, TMDV,, TmDv);
        __SET_VAR(DataIn->, UPDOWN,, UpDown);
        //__SET_VAR(DataIn->, DEB_SPEED,, Speed);
        //__SET_VAR(DataIn->, DEB_Y0,, Y0);
        //__SET_VAR(DataIn->, DEB_ER,, Er);
        //__SET_VAR(DataIn->, DEB_CM,, Ocm);
        //__SET_VAR(DataIn->, DEB_M,, Om);
    }
}

#endif // LIB_APP_FLR



/** MBRTU MASTER
 */

#ifdef LIB_APP_MBRTU_MASTER

/** @brief  MbRtuReadBool.
 *  @param  DataIn - data.
 *  @return None.
 */
 #include <stdio.h>
void AppMbRtuMaster_ReadBool(MBRTUREADBOOL *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_R_BOOL;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->O1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->O2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->O3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->O4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->O5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->O6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->O7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->O8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuReadInt.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadInt(MBRTUREADINT *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_R_INT;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->O1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->O2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->O3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->O4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->O5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->O6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->O7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->O8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuReadDInt.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadDInt(MBRTUREADDINT *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_R_DINT;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->O1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->O2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->O3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->O4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->O5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->O6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->O7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->O8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuReadWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadWord(MBRTUREADWORD *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_R_WORD;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->O1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->O2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->O3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->O4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->O5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->O6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->O7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->O8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

       // __SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuReadDWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadDWord(MBRTUREADDWORD *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_R_DWORD;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->O1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->O2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->O3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->O4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->O5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->O6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->O7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->O8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

       // __SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuReadReal.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadReal(MBRTUREADREAL *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_R_REAL;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->O1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->O2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->O3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->O4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->O5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->O6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->O7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->O8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuWriteBool.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteBool(MBRTUWRITEBOOL *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_W_BOOL;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->I1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->I2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->I3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->I4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->I5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->I6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->I7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->I8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuWriteInt.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteInt(MBRTUWRITEINT *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_W_INT;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->I1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->I2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->I3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->I4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->I5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->I6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->I7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->I8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

       // __SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuWriteDInt.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteDInt(MBRTUWRITEDINT *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_W_DINT;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->I1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->I2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->I3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->I4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->I5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->I6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->I7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->I8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuWriteWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteWord(MBRTUWRITEWORD *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_W_WORD;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->I1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->I2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->I3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->I4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->I5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->I6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->I7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->I8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuWriteDWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteDWord(MBRTUWRITEDWORD *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_W_DWORD;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->I1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->I2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->I3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->I4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->I5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->I6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->I7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->I8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}

/** @brief  MbRtuWriteReal.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteReal(MBRTUWRITEREAL *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_W_REAL;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      = __GET_VAR(DataIn->FUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Addr1         = __GET_VAR(DataIn->ADDR1);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->I1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->I2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->I3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->I4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->I5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->I6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->I7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->I8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }

        //__SET_VAR(DataIn->, EXPREV,, Ex);
    }
}


/** @brief  MbRtuWriteWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_SendDiagQuery(MBRTUDIAG *DataIn)
{
    if(DataIn && PlcAppFuncs.MbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
            BYTE Ok = __GET_VAR(DataIn->OK);
            if(!(Ok == PLC_APP_MBRTU_MASTER_EXEC_QUEUE || Ok == PLC_APP_MBRTU_MASTER_EXEC))
            {
                BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
				BOOL mode = __GET_VAR(DataIn->MODE);
                plc_app_mbrtu_master_reg_t Reg;

                Reg.Set.DataClass = PLC_APP_MBRTU_MASTER_WR_WORD;
                Reg.Set.Com       = __GET_VAR(DataIn->COM);
                Reg.Set.Func      =   0x08;//MBRTU_FUNC_08;//__GET_VAR(DataIn->SUBFUNC);
				Reg.Set.SubFunc   = __GET_VAR(DataIn->SUBFUNC);
                Reg.Set.Num       = __GET_VAR(DataIn->NUM);
                Reg.Set.ByteOrder = 0;// __GET_VAR(DataIn->BO);
                Reg.ID            = __GET_VAR(DataIn->ID);
                Reg.Ok            = __GET_VAR_REF(DataIn->OK);
                Reg.Regs[0]       = (void *)__GET_VAR_REF(DataIn->I1);
                Reg.Regs[1]       = (void *)__GET_VAR_REF(DataIn->I2);
                Reg.Regs[2]       = (void *)__GET_VAR_REF(DataIn->I3);
                Reg.Regs[3]       = (void *)__GET_VAR_REF(DataIn->I4);
                Reg.Regs[4]       = (void *)__GET_VAR_REF(DataIn->I5);
                Reg.Regs[5]       = (void *)__GET_VAR_REF(DataIn->I6);
                Reg.Regs[6]       = (void *)__GET_VAR_REF(DataIn->I7);
                Reg.Regs[7]       = (void *)__GET_VAR_REF(DataIn->I8);

                Reg.Regs[8]       = (void *)__GET_VAR_REF(DataIn->OUTDATA);
                //Reg.Regs[9]       = (void *)__GET_VAR_REF(DataIn->O2);
                //Reg.Regs[10]      = (void *)__GET_VAR_REF(DataIn->O3);
                //Reg.Regs[11]      = (void *)__GET_VAR_REF(DataIn->O4);
                //Reg.Regs[12]      = (void *)__GET_VAR_REF(DataIn->O5);
                //Reg.Regs[13]      = (void *)__GET_VAR_REF(DataIn->O6);
                //Reg.Regs[14]      = (void *)__GET_VAR_REF(DataIn->O7);
                //Reg.Regs[15]      = (void *)__GET_VAR_REF(DataIn->O8);

                PlcAppFuncs.MbRtuMaster(&Ex, &ExPrev, &Reg);

				if(!mode)
				{
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 0))
				 {
                   __SET_VAR(DataIn->, EXPREV,, 1);
				 }
				 if((*(Reg.Ok) >= PLC_APP_MBRTU_MASTER_EXEC_DONE) && (ExPrev == 1))
				 {
				  __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_EXEC_WAIT);
				  __SET_VAR(DataIn->, EXPREV,, 0);
				 }
				}
            }
        }
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }
   //
   //     //__SET_VAR(DataIn->, EXPREV,, Ex);

    }
}

/** @brief  MbRtuSetTimeOutValue.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_SetTimeOutValue(MBRTUSETTIMEOUTVALUE *DataIn)
{
    if(DataIn && PlcAppFuncs.setTimeOutValueMbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
         BYTE Ok = __GET_VAR(DataIn->OK);
		 if(Ok <= PLC_APP_MBRTU_MASTER_TOUT_WAIT)
		 {
		  BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
		  WORD Val    = __GET_VAR(DataIn->VALUE);
		  BYTE *Ok    = __GET_VAR_REF(DataIn->OK);

		  if(ExPrev == 0)
		   PlcAppFuncs.setTimeOutValueMbRtuMaster(&Ex, &ExPrev, &Val, Ok);

		  if((*Ok >= PLC_APP_MBRTU_MASTER_TOUT_DONE) && (ExPrev == 0))
		  {
            __SET_VAR(DataIn->, EXPREV,, 1);
		  }
		 }
		}
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_TOUT_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }
	}
}

/** @brief  MbRtuGetTimeOutValue.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_GetTimeOutValue(MBRTUGETTIMEOUTVALUE *DataIn)
{
    if(DataIn && PlcAppFuncs.getTimeOutValueMbRtuMaster)
    {
        BOOL Ex = __GET_VAR(DataIn->EX);

        if(Ex)
        {
         BYTE Ok = __GET_VAR(DataIn->OK);
		 if(Ok <= PLC_APP_MBRTU_MASTER_TOUT_WAIT)
		 {
		  BOOL ExPrev = __GET_VAR(DataIn->EXPREV);
		  WORD *Val   = __GET_VAR_REF(DataIn->VALUE);
		  BYTE *Ok    = __GET_VAR_REF(DataIn->OK);

		  if(ExPrev == 0)
		   PlcAppFuncs.getTimeOutValueMbRtuMaster(&Ex, &ExPrev, Val, Ok);

		  if((*Ok >= PLC_APP_MBRTU_MASTER_TOUT_DONE) && (ExPrev == 0))
		  {
            __SET_VAR(DataIn->, EXPREV,, 1);
		  }
		 }
		}
        else
        {
            __SET_VAR(DataIn->, OK,, PLC_APP_MBRTU_MASTER_TOUT_OFF);
			__SET_VAR(DataIn->, EXPREV,, 0);
        }
	}
}

#endif // LIB_APP_MBRTU_MASTER



/** SYSTEM
 */

#ifdef LIB_APP_SYS

/** @brief  Software reset.
 *  @param Ex - allow to execution:
 *  @arg     = false - not allow
 *  @arg     = true  - allow
 *  @return None.
 */
void AppSys_SoftReset(BOOL ExIn)
{
    if(PlcAppFuncs.SoftReset)
    {
        PlcAppFuncs.SoftReset(ExIn);
    }
}

#endif // LIB_APP_SYS

#ifdef LIB_APP_STEP_MOTOR

/** @brief  DOPwm.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_StepperMove(STEPMOTOR *DataIn)
{
    if(DataIn && PlcAppFuncs.StepMove)
    {
        BOOL Ex  = __GET_VAR(DataIn->EX);
        BOOL Rst  = __GET_VAR(DataIn->RST);
        BYTE Stop = __GET_VAR(DataIn->STOP);
        BYTE DOnStep = __GET_VAR(DataIn->DONSTEP);
		BYTE DOnDir  = __GET_VAR(DataIn->DONDIR);
		WORD StartSpeed = __GET_VAR(DataIn->STARTSPEED);
        WORD Speed   = __GET_VAR(DataIn->SPEED);
		WORD AcN 	 = __GET_VAR(DataIn->ACN);
		WORD DecN	 = __GET_VAR(DataIn->DECN);
		DWORD Steps  = __GET_VAR(DataIn->STEPS);
		BOOL Dir     = __GET_VAR(DataIn->DIR);
		WORD ChDirDelay = __GET_VAR(DataIn->DIR_DELAY);
		WORD StepRPM = __GET_VAR(DataIn->STEPRPM);
		WORD DivStep = __GET_VAR(DataIn->DIVSTEP);
		//AcN *= DivStep * StepRPM;
		//DecN *= DivStep * StepRPM;
        BYTE Ok  = 0;
        BYTE State = 0;
		BYTE Err = 0;
        PlcAppFuncs.StepMove(&Ex, &Rst, &Stop, &DOnStep, &DOnDir, &StartSpeed, &Speed, &AcN, &DecN, &Steps, &Dir, &ChDirDelay, &StepRPM, &DivStep, &Ok, &State, &Err);

        __SET_VAR(DataIn->, OK,, Ok);
		__SET_VAR(DataIn->, STATE,, State);
		__SET_VAR(DataIn->, ERR,, Err);
    }
}

void App_StepperStatus(STEPSTATUS *DataIn)
{
    if(DataIn && PlcAppFuncs.StepStatus)
    {
        BYTE DOnStep = __GET_VAR(DataIn->DONSTEP);
		BYTE DOnDir  = __GET_VAR(DataIn->DONDIR);
        BYTE Ok  = 0;
        BYTE State = 0;
        PlcAppFuncs.StepStatus(&DOnStep, &DOnDir, &State, &Ok);

        __SET_VAR(DataIn->, OK,, Ok);
		__SET_VAR(DataIn->, STATE,, State);
    }
}

#endif //LIB_APP_STEP_MOTOR