import os, sys
from yaplctargets.toolchain_yaplc_stm32 import toolchain_yaplc_stm32
from yaplctargets.toolchain_yaplc_stm32 import plc_rt_dir as plc_rt_dir

DI_C_TEXT = """
uint32_t Condition_ProgramDI(const uint8_t ChNum, void* val, uint8_t mode){
	uint32_t program_run_mask = 0;
	uint32_t Value = *((uint32_t*)val);
	switch(ChNum)
	{
		%(set_bits_case)s
	}
	return program_run_mask;
}
"""

AI_C_TEXT = """
uint32_t Condition_ProgramAI(const uint8_t ChNum, void* val, uint8_t mode){
	uint32_t program_run_mask = 0;
	float Value = *((float*)val);
	switch(ChNum)
	{
		%(set_bits_case)s
	}
	return program_run_mask;
}
"""

PT_C_TEXT = """
uint32_t Condition_ProgramPT(const uint8_t ChNum, void* val, uint8_t mode){
	uint32_t program_run_mask = 0;
	float Value = *((float*)val);
	switch(ChNum)
	{
%(set_bits_case)s
	}
	return program_run_mask;
}
"""

DT_C_TEXT = """
uint32_t Condition_ProgramDT(const uint8_t ChNum, void* val, uint8_t mode){
	uint32_t program_run_mask = 0;
	float Value = *((float*)val);
	switch(ChNum)
	{
%(set_bits_case)s
	}
	return program_run_mask;
}
"""
DEFAULT_C_TEXT = """
uint32_t Condition_Program%(interface_name)s(const uint8_t ChNum, void* val, uint8_t mode){
	return 0;
}
"""


FAST_APP_DICT = {
	"DI": ({"c_text": DI_C_TEXT}, {"DI_NORMAL_MODE": 0, "DI_TACHOMETER_MODE": 1, "DI_COUNTER_MODE": 2}),
	"AI": ({"c_text": AI_C_TEXT}, {"AI_MODE": 3}),
	"DT": ({"c_text": DT_C_TEXT}, {"DT_MODE": 4}),
	"PT": ({"c_text": PT_C_TEXT}, {"PT_MODE": 5}),
}


def GetFastTaskData(interface):
	return FAST_APP_DICT.get(interface.upper(), None)


def GetDefaultFastTaskString(interface):
	return DEFAULT_C_TEXT % {"interface_name": interface.upper()}


def GetMode(mode, default_modes):
	if mode == "Normal":
		return default_modes["DI_NORMAL_MODE"]
	elif mode == "Counter":
		return default_modes["DI_COUNTER_MODE"]
	elif mode == "Tachometer":
		return default_modes["DI_TACHOMETER_MODE"]
	else:
		mode_keys = default_modes.keys()
		for key in mode_keys:
			return default_modes.get(key, "")


def GenerateFastApp(task_data_dict, default_interfaces):
	condition_func = ""
	for interface in task_data_dict.keys():
		condition = ""
		TaskData = GetFastTaskData(interface)
		if TaskData is None:
			condition_func += GetDefaultFastTaskString(interface)
			continue

		use_ch = []
		task_data_dict[interface].sort(key=lambda x: x["Source"])
		for taskInfos in task_data_dict[interface]:
			source = taskInfos.get("Source", "")
			task_cond = taskInfos.get("Condition", "")
			task_bit = taskInfos.get("Bit", "")
			task_mode = taskInfos.get("Mode", "")

			if source not in use_ch:
				if len(use_ch) != 0:
					condition += "\t\t\tbreak;\n"
				use_ch.append(source)
				condition += f"\t\tcase {source}:\n"
			mode = GetMode(task_mode, TaskData[1])
			condition += f"\t\t\tif( mode == {mode} ) SET_BIT(program_run_mask, (Value {task_cond}), {task_bit});\n"
		condition += "\t\t\tbreak;\n"

		condition_func += (TaskData[0]["c_text"]) % {"set_bits_case": condition}

	for def_interface in default_interfaces:
		condition_func += GetDefaultFastTaskString(def_interface)

	return condition_func

class plm2004_target(toolchain_yaplc_stm32):
	def __init__(self, CTRInstance):
		toolchain_yaplc_stm32.__init__(self, CTRInstance)

		self.dev_family = "STM32F2"
		self.load_addr = "0x08020000"
		self.runtime_addr = "0x08000184"
		self.linker_script = os.path.join(os.path.join(os.path.join(plc_rt_dir, "bsp"), "plm2004"), "target-app.ld")
		self.bsp_dir = os.path.join(os.path.join(plc_rt_dir, "bsp"), "plm2004")
		self.find_dirs = ["-I\"" + self.bsp_dir + "\""]

	def GenerateFastApp(self, task_data_dict, default_interfaces):
		return GenerateFastApp(task_data_dict, default_interfaces)

if __name__ == '__main__':
	test = plm2004_target()
	interfaces_list = ["AI", "Ai", "pt", "DI", "DD", "TSet"]
	for interface in interfaces_list:
		interface_data = test.GetFastTaskData(interface)
		if isinstance(interface_data, str):
			print(interface_data)
		elif isinstance(interface_data, tuple):
			print(interface_data[0]["c_text"])