#ifndef IT_FB_BLOCK__
#define IT_FB_BLOCK__
/** F(B) C-code
 */
#include "iec_types_all.h"
#include "plc_abi.h"
#include "POUS.h"

//@TODO + define APP_* from LOCATED_VARIABLES_HIDDEN (by used libraries)

#define LIB_APP_DI
#define LIB_APP_DO
#define LIB_APP_AO
#define LIB_APP_DT
#define LIB_APP_PT
#define LIB_APP_AI
#define LIB_APP_EEPROM
#define LIB_APP_FLR
#define LIB_APP_MBRTU_MASTER
#define LIB_APP_SYS
#define LIB_APP_STEP_MOTOR

/** DI
 */

#ifdef LIB_APP_DI

plc_loc_dsc_t *PlcApp_TestLocVar(const uint8_t ZoneIn, const uint8_t TypeSzIn, const uint16_t GroupIn, const int32_t A00In, const int32_t A01In, const int32_t A02In);

void run_fast_func(uint8_t ch_num);

/** @brief  DIMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DIMode(DIMODE *DataIn);

/** @brief  DIStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DIStatus(DISTATUS *DataIn);

/** @brief  DIVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DIVal(DIVAL *DataIn);

/** @brief  DICntRst.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DICntRst(DICNTRST *DataIn);

//----------------------------------------------------------------------------------------------------------
/** @brief  DICntT.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DICntT(BOOL *Ex, BYTE *DIn, WORD *Ov, BOOL *OisSet, BYTE *Ok)
void App_DICntT(DICNTT *DataIn);


/** @brief  DISetCfgCntT.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DISetCfgCntT(BOOL *Ex, BYTE *DIn, WORD *Sp, BOOL *EnCmpMd, BYTE *Ok)
void App_DISetCfgCntT(DISETCFGCNTT *DataIn);

/** @brief  DIStateCfgCntT.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DIStateCfgCntT(BYTE *DIn, WORD *OSp, BOOL *OEnCmpMd, BYTE *Ok)
void App_DIStateCfgCntT(DISTATECFGCNTT *DataIn);

//--------------------------------------------------------------------------------------------------------------

/** @brief  DICnt.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DICnt(BOOL *Ex, BYTE *DIn, DWORD *Ov, BOOL *OisSet, BYTE *Ok)
void App_DICnt(DICNT *DataIn);

/** @brief  DISetCfgCnt.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DISetCfgCnt(BOOL *Ex, BYTE *DIn, DWORD *Sp, BOOL *EnCmpMd, BYTE *Ok)
void App_DISetCfgCnt(DISETCFGCNT *DataIn);

/** @brief  DIStateCfgCnt.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DIStateCfgCnt(BYTE *DIn, DWORD *OSp, BOOL *OEnCmpMd, BYTE *Ok)
void App_DIStateCfgCnt(DISTATECFGCNT *DataIn);

//--------------------------------------------------------------------------------------------------------------

/** @brief  DIEnc.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DIEnc(BOOL *Ex, BYTE *DIn, DWORD *OvA, BOOL *OisSetA, DWORD *OvB, BOOL *OisSetB, WORD *OvT, BOOL *OisSetT, BYTE *Ok)
void App_DIEnc(DIENC *DataIn);

/** @brief  DISetCfgEnc.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DISetCfgEnc(BOOL *Ex, BYTE *DIn, DWORD *SpA, BOOL *EnCmpMdA, DWORD *SpB, BOOL *EnCmpMdB, WORD *SpT, BOOL *EnCmpMdT, BYTE *Ok)
void App_DISetCfgEnc(DISETCFGENC *DataIn);

/** @brief  DIStateCfgEnc.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
//void PlcApp_DIStateCfgEnc(BYTE *DIn, DWORD *OSpA, BOOL *OEnCmpMdA, DWORD *OSpB, BOOL *OEnCmpMdB, WORD *OSpT, BOOL *OEnCmpMdT, BYTE *Ok)
void App_DIStateCfgEnc(DISTATECFGENC *DataIn);

//-------------------------------------------------------------------------------------------------------------------------------------------------------

#endif // LIB_APP_DI



/** AI
 */

#ifdef LIB_APP_AI

/** @brief  AIMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AIMode(AIMODE *DataIn);

/** @brief  AIStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AIStatus(AISTATUS *DataIn);

/** @brief  AIVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AIVal(AIVAL *DataIn);

#endif // LIB_APP_AI



/** DT
 */

#ifdef LIB_APP_DT

/** @brief  DTMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTMode(DTMODE *DataIn);

/** @brief  DTStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTStatus(DTSTATUS *DataIn);

/** @brief  DTSetId.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTSetId(DTSETID *DataIn);

/** @brief  DTGetId.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTGetId(DTGETID *DataIn);

/** @brief  DTVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DTVal(DTVAL *DataIn);

#endif // LIB_APP_DT



/** PT
 */

#ifdef LIB_APP_PT

/** @brief  PTMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_PTMode(PTMODE *DataIn);

/** @brief  PTStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_PTStatus(PTSTATUS *DataIn);

/** @brief  PTVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_PTVal(PTVAL *DataIn);

#endif // LIB_APP_PT



/** DO
 */

#ifdef LIB_APP_DO

/** @brief  DOMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOMode(DOMODE *DataIn);

//void PlcApp_DOStatus(BYTE *DOn, BYTE *Om, BOOL *Oepwm, DWORD *Otpwm, REAL *Odpwm, BOOL *Oesf, BOOL *Ovsf, BYTE *Ok)


/** @brief  DOStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOStatus(DOSTATUS *DataIn);

/** @brief  DOVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOVal(DOVAL *DataIn);

/** @brief  DOFast.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOFast(DOFAST *DataIn);

/** @brief  DOPwm.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOPwm(DOPWM *DataIn);

/** @brief  DOSafe.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_DOSafe(DOSAFE *DataIn);

#endif // LIB_APP_DO



/** AO
 */

#ifdef LIB_APP_AO

/** @brief  AOMode.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOMode(AOMODE *DataIn);

/** @brief  AOStatus.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOStatus(AOSTATUS *DataIn);

/** @brief  AOVal.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOVal(AOVAL *DataIn);

/** @brief  AOFast.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOFast(AOFAST *DataIn);

/** @brief  AOSafe.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void App_AOSafe(AOSAFE *DataIn);
#endif // LIB_APP_AO



/** EEPROM
 */

#ifdef LIB_APP_EEPROM

/** @brief  Clear all memory.
 *  @param  ExIn - allow execution.
 *  @param  OkOut - pointer to result.
 *  @return None.
 */
void AppEe_Clr(BOOL ExIn, BOOL *OkOut);

/** @brief  Search item in global array PlcEe_Regs.
 *  @param  AddrIn - start address of memory,
 *  @param  TyIn - ID of data type.
 *  @return Index to array PlcEe_Regs or -1.
 */
int32_t AppEe_Search(DINT AddrIn, BYTE TyIn);

/** @brief  Read data.
 *  @param  DataIn - pointer to structure of arguments.
 *  @return None.
 */
void AppEe_Read(EEREADLREAL *DataIn);

/** @brief  Write data.
 *  @param  DataIn - pointer to structure of arguments.
 *  @return None.
 */
void AppEe_Write(EEWRITELREAL *DataIn);

#endif // LIB_APP_EEPROM



/** FLR
 */

#ifdef LIB_APP_FLR

/** @def PI
 */
#define APP_FLR_PI          (REAL)3.14159265358979

/** @def Quantity of terms
 */
#define APP_FLR_SZ          5

/** @def Input terms
 */
#define APP_FLR_IN_HI2      0   //very higher
#define APP_FLR_IN_HI       1   //high
#define APP_FLR_IN_NORM     2   //normal
#define APP_FLR_IN_LO       3   //low
#define APP_FLR_IN_LO2      4   //very lowest

/** @def Output terms
 */
#define APP_FLR_OUT_OP2     0   //fast open  (speed 2)
#define APP_FLR_OUT_OP1     1   //slow open  (speed 1)
#define APP_FLR_OUT_NONE    2   //nothing
#define APP_FLR_OUT_CL1     3   //slow close (speed 1)
#define APP_FLR_OUT_CL2     4   //fast close (speed 2)

/** @def Direction of output value increase
 */
#define APP_FLR_DIR_DOWN    (SINT)-1
#define APP_FLR_DIR_NONE    (SINT)0
#define APP_FLR_DIR_UP      (SINT)1

/** @def Min/Max
 */
#define APP_FLR_MIN         (REAL)-1.0
#define APP_FLR_MAX         (REAL)1.0

/** @def Inverse probability of normal state
 *  @note q = (1 - Actions[APP_FLR_IN_NORM])
 */
#define APP_FLR_Q_MIN       (REAL)0.0
#define APP_FLR_Q_MAX       (REAL)0.3

/** @def Sigma
 */
#define APP_FLR_SIGMA       (REAL)0.0

/** @def Step of accumulating value increase
 */
#define APP_FLR_DX          (REAL)0.01


#define HI_SPEED_DELTA       (REAL)1.05

/** @brief  Gaus-function.
 *  @param  C   - value of In, where Gaus-function is maximum (1.0).
 *  @param  S   - incremental step of Gaus-function.
 *  @param  In  - input value.
 *  @param  Out - result.
 *  @return Result.
 */
REAL AppFlr_GausFx(const REAL C, const REAL S, const REAL In);

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

REAL AppFlr_TriangleFx(const REAL A, const REAL B, const REAL C, const REAL In);  //����������� ������� �������������� (��� ������� ����������)


/** @brief  Get difference between value and setpoint in Term-format (-1 .. 1).
 *  @param  ErSrc  - source difference (error).
 *  @return None.
 */
REAL AppFlr_ErTerm(const REAL ErSrc);

/** @brief  Get output terms.
 *  @param  Sigma - Sigma-value.
 *  @param  Min - minimum.
 *  @param  Max - maximum.
 *  @param  In  - input value.
 *  @param  Out - pointer to array of output terms.
 *  @return None.
 */
void AppFlr_OutTerms(const REAL Sigma, const REAL Min, const REAL Max, const REAL In, REAL *Out);

//������� ������������� � ��������������� ������ ��������� �������
REAL AppFlr_AccProb (REAL Inp, REAL *A, REAL *B, REAL *C, REAL *InpVec);


/** @brief  Accumulate actions.
 *  @param  dX  - step of value increase.
 *  @param  Min - minimum.
 *  @param  Max - maximum.
 *  @param  Actions - pointer to array of actions.
 *  @return Value of control action.
 */
REAL AppFlr_AccActions(const REAL dX, const REAL Min, const REAL Max, REAL *Actions, REAL *OCm, REAL *Om);

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
void AppFlr_ProbNorm(const REAL V, const REAL Sp, const REAL Speed, const REAL ActNorm, REAL *Y);

/** @brief  Get direction of changing Y.
 *  @param  Y - Y-value.
 *  @return UpDown-value.
 */
SINT AppFlr_UpDown(const REAL Y);

/** @brief  Get time of changing Y.
 *  @param  Tm - time of main-cycle (msec).
 *  @param  Y - Y-value.
 *  @return UpDown-value.
 */
REAL AppFlr_dVTm(const REAL Tm, const REAL Y);

/** @brief  FuzzyLogic.
 *  @param  DataIn - FB-arguments.
 *  @return None.
 */
void AppFlr(FLR1 *DataIn);

#endif // LIB_APP_FLR



/** MBRTU MASTER
 */

#ifdef LIB_APP_MBRTU_MASTER

/** @brief  MbRtuReadBool.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadBool(MBRTUREADBOOL *DataIn);

/** @brief  MbRtuReadInt.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadInt(MBRTUREADINT *DataIn);

/** @brief  MbRtuReadDInt.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadDInt(MBRTUREADDINT *DataIn);

/** @brief  MbRtuReadWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadWord(MBRTUREADWORD *DataIn);

/** @brief  MbRtuReadDWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadDWord(MBRTUREADDWORD *DataIn);

/** @brief  MbRtuReadReal.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_ReadReal(MBRTUREADREAL *DataIn);

/** @brief  MbRtuWriteBool.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteBool(MBRTUWRITEBOOL *DataIn);

/** @brief  MbRtuWriteInt.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteInt(MBRTUWRITEINT *DataIn);

/** @brief  MbRtuWriteDInt.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteDInt(MBRTUWRITEDINT *DataIn);

/** @brief  MbRtuWriteWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteWord(MBRTUWRITEWORD *DataIn);

/** @brief  MbRtuWriteDWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteDWord(MBRTUWRITEDWORD *DataIn);

/** @brief  MbRtuWriteReal.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_WriteReal(MBRTUWRITEREAL *DataIn);


/** @brief  MbRtuWriteWord.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_SendDiagQuery(MBRTUDIAG *DataIn);

/** @brief  MbRtuSetTimeOutValue.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_SetTimeOutValue(MBRTUSETTIMEOUTVALUE *DataIn);

/** @brief  MbRtuGetTimeOutValue.
 *  @param  DataIn - data.
 *  @return None.
 */
void AppMbRtuMaster_GetTimeOutValue(MBRTUGETTIMEOUTVALUE *DataIn);

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
void AppSys_SoftReset(BOOL ExIn);

#endif // LIB_APP_SYS


#endif // IT_FB_BLOCK__


void WriteRegForTest();


#ifdef LIB_APP_STEP_MOTOR

void App_StepperMove(STEPMOTOR *DataIn);

void App_StepperStatus(STEPSTATUS *DataIn);

#endif //LIB_APP_STEP_MOTOR