import os, sys
from yaplctargets.toolchain_yaplc_stm32 import toolchain_yaplc_stm32
from yaplctargets.toolchain_yaplc_stm32 import plc_rt_dir as plc_rt_dir

class yaplc_target(toolchain_yaplc_stm32):
    def __init__(self, CTRInstance):
        
        toolchain_yaplc_stm32.__init__(self, CTRInstance)
        
        self.dev_family       = "STM32F4"
        self.load_addr        = "0x08008000"
        self.runtime_addr     = "0x080001ac"
        self.base_flags       = ["-mthumb", "-mcpu=cortex-m4", "-mfpu=fpv4-sp-d16", "-mfloat-abi=hard", "-g3", "-DARM_MATH_CM4", "-D__FPU_USED"]
        self.linker_script    = os.path.join(os.path.join(os.path.join(plc_rt_dir, "bsp"), "nuc-227-dev"), "stm32f4disco-app.ld")
