/* @page plc_abi.h
 *       PLC ABI
 *       from YAPLC
 *       2020, lamsystems-it.ru
 */

#ifndef PLC_ABI_H_
#define PLC_ABI_H_

#include <stdbool.h>
#include <stdint.h>
#include <iec_types_all.h>


/** @def Located variables
 *       zones
 */
#define PLC_LT_I   (uint8_t)0   //Inputs
#define PLC_LT_M   (uint8_t)1   //Memory
#define PLC_LT_Q   (uint8_t)2   //Outputs


/** @def Located variables
 *       types
 */
#define PLC_LSZ_X  (uint8_t)0   //BOOL
#define PLC_LSZ_B  (uint8_t)1   //SINT, USINT, BYTE, STRING  (CHAR*)
#define PLC_LSZ_W  (uint8_t)2   //INT,  UINT,  WORD, WSTRING (WCHAR*)
#define PLC_LSZ_D  (uint8_t)3   //DINT, UDINT, REAL, DWORD
#define PLC_LSZ_L  (uint8_t)4   //LINT, ULINT, LREAL, LWORD


/** @def Located variables
 *       number bytes for types
 */
#define PLC_BSZ_X  (uint8_t)1
#define PLC_BSZ_B  (uint8_t)1
#define PLC_BSZ_W  (uint8_t)2
#define PLC_BSZ_D  (uint8_t)4
#define PLC_BSZ_L  (uint8_t)8


/** @typedef EEPROM-register
 */
typedef struct
{
    //@var Start address of data
    IEC_DINT  Addr;
    //@var Data type ID (see type.h)
    IEC_BYTE  Ty;
    //@var Read:  allow
    IEC_BOOL  Rex;
    //@var Read:  store of read data
    IEC_LREAL Rval;
    //@var Read:  result code
    IEC_BYTE  Rok;
    //@var Write: allow
    IEC_BOOL  Wex;
    //@var Write: value to write
    IEC_LREAL Wval;
    //@var Write: result code
    IEC_BYTE  Wok;

} plc_app_eereg_t;


/** @def MbRtu Master data classes
 */
#define PLC_APP_MBRTU_MASTER_R_BOOL              (uint8_t)0   //MbRtuReadBool
#define PLC_APP_MBRTU_MASTER_R_INT               (uint8_t)1   //MbRtuReadInt
#define PLC_APP_MBRTU_MASTER_R_DINT              (uint8_t)2   //MbRtuReadDInt
#define PLC_APP_MBRTU_MASTER_R_WORD              (uint8_t)3   //MbRtuReadWord
#define PLC_APP_MBRTU_MASTER_R_DWORD             (uint8_t)4   //MbRtuReadDWord
#define PLC_APP_MBRTU_MASTER_R_REAL              (uint8_t)5   //MbRtuReadReal
#define PLC_APP_MBRTU_MASTER_W_BOOL              (uint8_t)6   //MbRtuWriteBool
#define PLC_APP_MBRTU_MASTER_W_INT               (uint8_t)7   //MbRtuWriteInt
#define PLC_APP_MBRTU_MASTER_W_DINT              (uint8_t)8   //MbRtuWriteDInt
#define PLC_APP_MBRTU_MASTER_W_WORD              (uint8_t)9   //MbRtuWriteWord
#define PLC_APP_MBRTU_MASTER_W_DWORD             (uint8_t)10  //MbRtuWriteDWord
#define PLC_APP_MBRTU_MASTER_W_REAL              (uint8_t)11  //MbRtuWriteReal
#define PLC_APP_MBRTU_MASTER_WR_WORD             (uint8_t)12   //MbRtuWriteReadByte

/** @def MbRtu Master result codes
 */
#define PLC_APP_MBRTU_MASTER_OFF                 (uint8_t)0   //off
#define PLC_APP_MBRTU_MASTER_EXEC_WAIT           (uint8_t)1   //exec. wait
#define PLC_APP_MBRTU_MASTER_EXEC_QUEUE          (uint8_t)2   //exec. in queue
#define PLC_APP_MBRTU_MASTER_EXEC                (uint8_t)3   //exec.
#define PLC_APP_MBRTU_MASTER_EXEC_DONE           (uint8_t)4   //exec. done success
#define PLC_APP_MBRTU_MASTER_ERR_COM_NUM         (uint8_t)10  //error! incorrect number of COM-port
#define PLC_APP_MBRTU_MASTER_ERR_COM_MODE        (uint8_t)11  //error! incorrect mode of COM-port
#define PLC_APP_MBRTU_MASTER_ERR_FUNC            (uint8_t)12  //error! incorrect Func
#define PLC_APP_MBRTU_MASTER_ERR_NUM             (uint8_t)13  //error! incorrect Num (quantity of read/write registers)
#define PLC_APP_MBRTU_MASTER_ERR_NO_RESP         (uint8_t)14  //error! no response long-time

enum
{
 PLC_APP_MBRTU_MASTER_TOUT_OFF = 0,   //off
 PLC_APP_MBRTU_MASTER_TOUT_WAIT,   //exec. wait
 PLC_APP_MBRTU_MASTER_TOUT_DONE,   //exec. in queue
 PLC_APP_MBRTU_MASTER_TOUT_FAIL,   //exec. is fail exec
};

/** @def MbRtu Master exceptions prefix
 */
#define PLC_APP_MBRTU_MASTER_EXC_PREF            (uint8_t)20

/** @def Quantity of MbRtu Master registers
 */
#define PLC_APP_MBRTU_MASTER_REG_SZ    (uint8_t)16//8

/** @typedef MbRtu Master register settings
 */
typedef struct
{
    //@var Data class
    IEC_DWORD DataClass:4;
    //@var Number of Com-port
    IEC_DWORD Com:4;
    //@var Function code
    IEC_DWORD Func:5;
    //@var Quantity of registers
    IEC_DWORD Num:4;
    //@var Byte order
    IEC_DWORD ByteOrder:2;
    //@var Sub Function code
    IEC_DWORD SubFunc:5;

} plc_app_mbrtu_master_set_t;

/** @typedef MbRtu Master register
 */
typedef struct
{
    //@var Request settings
    plc_app_mbrtu_master_set_t Set;
    //@var ID of target device
    IEC_BYTE ID;
    //@var Address of start register
    IEC_WORD Addr1;
    //@var Result
    IEC_BYTE *Ok;
    //@var Values
    void *Regs[PLC_APP_MBRTU_MASTER_REG_SZ];

} plc_app_mbrtu_master_reg_t;


/** @typedef Functions
 */
typedef struct
{
    //DI
    void (*DIMode)(BOOL *, BYTE *, BYTE *, BYTE *);
    void (*DIStatus)(BYTE *, BYTE *, BYTE *);
    void (*DIVal)(BOOL *, BYTE *, BOOL *, BYTE *);
    void (*DICntRst)(BOOL *, BYTE *, BOOL *, BYTE *);
    //----------------------------------------------------------------------------------------------------------------------------------------
    //void (*DICntT)(BOOL *, BYTE *, WORD *, BOOL *, WORD *, BOOL *, BYTE *);
    //----------------------------------------------------------------------------------------------------------------------------------------
    void (*DICntT)(BOOL *, BYTE *, WORD *, BOOL *, BYTE *);
    void (*DISetCfgCntT)(BOOL *, BYTE *, WORD *, BOOL *, BYTE *);
    void (*DIStateCfgCntT)(BYTE *, WORD *, BOOL *, BYTE *);
    //----------------------------------------------------------------------------------------------------------------------------------------
    //void (*DICnt)(BOOL *, BYTE *, DWORD *, BOOL *, DWORD *, BOOL *, BYTE *);
    //----------------------------------------------------------------------------------------------------------------------------------------
    void (*DICnt)(BOOL *, BYTE *, DWORD *, BOOL *, BYTE *);
    void (*DISetCfgCnt)(BOOL *, BYTE *, DWORD *, BOOL *, BYTE *);
    void (*DIStateCfgCnt)(BYTE *, DWORD *, BOOL *, BYTE *);
    //-----------------------------------------------------------------------------------------------------------------------------------------
    //void (*DIEnc)(BOOL *, BYTE *, DWORD *, BOOL *, DWORD *, BOOL *, WORD *, BOOL *, DWORD *, BOOL *, DWORD *, BOOL *, WORD *, BOOL *, BYTE *);
    //----------------------------------------------------------------------------------------------------------------------------------------
    void (*DIEnc)(BOOL *, BYTE *, DWORD *, BOOL *, DWORD *, BOOL *, WORD *, BOOL *, BYTE *);
    void (*DISetCfgEnc)(BOOL *, BYTE *, DWORD *, BOOL *, DWORD *, BOOL *, WORD *, BOOL *, BYTE *);
    void (*DIStateCfgEnc)(BYTE *, DWORD *, BOOL *, DWORD *, BOOL *, WORD *, BOOL *, BYTE *);
    //-----------------------------------------------------------------------------------------------------------------------------------------

    //AI
    void (*AIMode)(BOOL *, BYTE *, BYTE *, BYTE *);
    void (*AIStatus)(BYTE *, BYTE *, BYTE *, BYTE *);
    void (*AIVal)(BOOL *, BYTE *, REAL *, BYTE *);

    //DT
    void (*DTMode)(BOOL *, BYTE *, BYTE *, BYTE *);
    void (*DTStatus)(BYTE *, BYTE *, BYTE *, BYTE *);
    void (*DTSetID)(BOOL *, BYTE *, LWORD *, BYTE *);
    void (*DTGetID)(BYTE *, LWORD *, BYTE *);
    void (*DTVal)(BOOL *, BYTE *, REAL *, BYTE *);

    //PT
    void (*PTMode)(BOOL *, BYTE *, BYTE *, BYTE *, BYTE *);
    void (*PTStatus)(BYTE *, BYTE *, BYTE *, BYTE *);
    void (*PTVal)(BOOL *, BYTE *, REAL *, BYTE *);

    //DO
    void (*DOMode)(BOOL *, BYTE *, BYTE *, BYTE *);
    void (*DOStatus)(BYTE *, BYTE *, BOOL *, DWORD *, REAL *, BOOL *, BOOL *, BYTE *);//(*DOStatus)(BYTE *, BYTE *, BYTE *);
    void (*DOVal)(BOOL *, BYTE *, BOOL *, BOOL *, BYTE *);
    void (*DOFast)(BOOL *, BYTE *, BOOL *, BOOL *, BYTE *);
    void (*DOPwm)(BOOL *, BOOL *, BYTE *, DWORD *, REAL *, BYTE *);//(*DOPwm)(BOOL *, BOOL *, BYTE *, DWORD *, REAL *, BOOL *, BYTE *);
    void (*DOSafe)(BOOL *, BOOL *, BYTE *, BOOL *, BYTE *);//(*DOSafe)(BOOL *, BOOL *, BYTE *, BOOL *, BOOL *, BOOL *, BYTE *);


    //AO
    void (*AOMode)(BOOL *, BYTE *, BYTE *, BYTE *);
    void (*AOStatus)(BYTE *, BYTE *, BOOL *, REAL *, BYTE *Ok);//(BYTE *, BYTE *, BYTE *);
    void (*AOVal)(BOOL *, BYTE *, REAL *, REAL *, BYTE *);
    void (*AOFast)(BOOL *, BYTE *, REAL *, REAL *, BYTE *);
    void (*AOSafe)(BOOL *, BOOL *, BYTE *, REAL *, BYTE *);//(BOOL *, BOOL *, BYTE *, REAL *, REAL *, BOOL *, BYTE *);

    //MBRTU MASTER
    void (*MbRtuMaster)(BOOL *, BOOL *, plc_app_mbrtu_master_reg_t *);
    void (*setTimeOutValueMbRtuMaster)(BOOL *, BOOL *, WORD *, BYTE *);
    void (*getTimeOutValueMbRtuMaster)(BOOL *, BOOL *, WORD *, BYTE *);

    //SYSTEM
    void (*SoftReset)(BOOL);

    //SYS
    void (*GetTime)(IEC_TIME *);

} plc_app_funcs_t;


/** @typedef Located variables
 *           description of variable
 */
typedef struct _plc_loc_dsc_t
{
    void *v_buf;                       //@var Pointer to variable value buffer
    uint8_t v_type;                    //@var Zone ID
    uint8_t v_size;                    //@var Data Type Size ID
    uint16_t a_size;                   //@var Size of arguments
    const uint32_t *a_data;            //@var Pointer to buffer of arguments
    uint16_t proto;                    //@var Group ID

} plc_loc_dsc_t;


typedef const plc_loc_dsc_t *plc_loc_tbl_t;
typedef void (*app_fp_t) (void);


/** @typedef APP-ABI
 */
typedef struct
{
    uint32_t *sstart;
    app_fp_t entry;

    //App startup interface
    //* pointers are set in target C-file (yaplctargets)
    //* values   are set in target-app.ld
    uint32_t *data_loadaddr;
    uint32_t *data_start;
    uint32_t *data_end;
    uint32_t *bss_end;
    app_fp_t *pa_start;
    app_fp_t *pa_end;
    app_fp_t *ia_start;
    app_fp_t *ia_end;
    app_fp_t *fia_start;
    app_fp_t *fia_end;

    //RTE Version control
    //Semantic versioning is used
    //* values are set in target C-file (yaplctargets)
    //* equivalent values in plc_app.h
    uint32_t rte_ver_major;
    uint32_t rte_ver_minor;
    uint32_t rte_ver_patch;

    //Hardware ID
    //* value is set in target C-file (yaplctargets)
    //* equivalent value in plc_app.h
    uint32_t hw_id;

    //IO manager data
    //* values are set in target C-file (yaplctargets)
    plc_loc_tbl_t *l_tab;      //Location table
    uint32_t *w_tab;           //Weigth table
    uint16_t  l_sz;            //Location table size

    //EEPROM registers
    plc_app_eereg_t *ee_regs;  //pointer to array of registers
    uint16_t  ee_sz;           //length of array

    //Functions
    plc_app_funcs_t *funcs;

    //Common ticktime
    unsigned long long *common_ticktime;

    //Control instance of PLC_ID (md5)
    //* value is set in target C-file (yaplctargets)
    const char *check_id;   //Must be placed to the end of .text

    //App interface (md5)
    //* value is set in target C-file (yaplctargets)
    const char *id;      //Must be placed near the start of .text

    //Functions
    //* functions are declared in target C-file (yaplctargets)
    //* pointers are set in target C-file (yaplctargets)

    int (*start)(int , char **);
    int (*stop)(void);
    void (*run)(void);

    void (*dbg_resume)(void);
    void (*dbg_suspend)(int);

    int  (*dbg_data_get)(unsigned long *, unsigned long *, void **);
    void (*dbg_data_free)(void);

    void (*dbg_vars_reset)(void);
    void (*dbg_var_register)(int, void *);

    uint32_t (*log_cnt_get)(uint8_t);
    uint32_t (*log_msg_get)(uint8_t, uint32_t, char*, uint32_t, uint32_t*, uint32_t*, uint32_t*);
    void     (*log_cnt_reset)(void);
    int      (*log_msg_post)(uint8_t, char*, uint32_t);

} plc_app_abi_t;


/** @typedef RTE-ABI
 */
typedef struct
{
    void (*get_time)(IEC_TIME *);
    void (*set_timer)(unsigned long long, unsigned long long);

    int  (*check_retain_buf)(void);
    void (*invalidate_retain_buf)(void); //Call before saving
    void (*validate_retain_buf)(void);   //Call after saving

    void (*retain)(unsigned int, unsigned int, void *);
    void (*remind)(unsigned int, unsigned int, void *);

} plc_rte_abi_t;


/** @var Pointer to ABI (application)
 *       real define in plc_app.c
 */
extern plc_app_abi_t *PLC_APP_CURR;


/** @def Macroses
 */
#define PLC_LOC_CONCAT(a, b)           a##b
#define PLC_LOC_TYPE(a)                PLC_LOC_CONCAT(PLC_LT_, a)
#define PLC_LOC_SIZE(a)                PLC_LOC_CONCAT(PLC_LSZ_, a)


/** @def Logging
 */
#define LOG_LEVELS                    4
#define LOG_CRITICAL                  0
#define LOG_WARNING                   1
#define LOG_INFO                      2
#define LOG_DEBUG                     3

#define PLC_APP_AO_OFF                 0  //Block Off
#define PLC_APP_AO_OK                  1  //OK
#define PLC_APP_AO_ERR_AON             2  //invalid channel number
#define PLC_APP_AO_ERR_M               3  //invalid mode
#define PLC_APP_AO_ERR_NOT_NORM        3  //the channel is not Normal
#define PLC_APP_AO_ERR_NOT_FAST        3  //the channel is not Fast
#define PLC_APP_AO_ERR_SAFE            4  //the channel was set in Safe-value


/** @def Result codes
 */
#define PLC_APP_DO_OFF                 0  //Block Off
#define PLC_APP_DO_OK                  1  //OK
#define PLC_APP_DO_ERR_DON             2  //invalid channel number
#define PLC_APP_DO_ERR_M               3  //invalid mode
#define PLC_APP_DO_ERR_NOT_NORM        3  //the channel is not Normal
#define PLC_APP_DO_ERR_NOT_FAST        3  //the channel is not Fast
#define PLC_APP_DO_ERR_NOT_PWM         3  //the channel is not PWM
#define PLC_APP_DO_ERR_SAFE            4  //the channel is Safe State

#define IS_OK_BLOCK_RES_OPR            PLC_APP_AO_OK 


#endif // PLC_ABI_H_
