import os
from targets.toolchain_gcc import toolchain_gcc
from yaplctargets.plm2004 import GenerateFastApp
from targets.Win32 import Win32_target
from targets.Linux import Linux_target
import shutil

toolchain_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.join(os.path.join(toolchain_dir, ".."), "..")
plc_rt_dir = os.path.join(os.path.join(os.path.join(base_dir, ".."), "RTE"), "src")
matiec_lib_dir = os.path.join(os.path.join(os.path.join(os.path.join(base_dir, ".."), "matiec"), "lib"), "C")
if (os.name == 'posix' and not os.path.isfile(plc_rt_dir)):
    plc_rt_dir = os.environ["HOME"] + "/YAPLC/RTE/src"
    base_dir = os.environ["HOME"] + "/YAPLC"


class x86_emulator_target(toolchain_gcc):
    if os.name in ("nt", "ce"):
        dlopen_prefix = ""
        extension = ".dll"
    else:
        dlopen_prefix = "./"
        extension = ".so"
    def __init__(self, CTRInstance):
        if os.name in ("nt", "ce"):
            prefix_dir = os.path.join(os.path.join(os.path.join(base_dir, ".."), "TDM-GCC-64"), "bin")
            self.toolchain_prefix = prefix_dir + "\\x86_64-w64-mingw32-"
            self.extra_files = ('%(s)s\\extra_files') % {"s": toolchain_dir}
            self.cflags = ["-m64", ('-I"%(s)s"') % {"s": self.extra_files}, ]
            self.ldflags = ["-shared", "-lwinmm", "-m64", "-lSoftPlc"]
            Win32_target.__init__(self, CTRInstance)
        else:
            self.toolchain_prefix = ""
            self.cflags = ["-fPIC", "-m64"]
            self.ldflags = ["-shared", "-lrt"]
            Linux_target.__init__(self, CTRInstance)
        #toolchain_gcc.__init__(self, CTRInstance)

    def getPath(self):
        return toolchain_dir

    def getCompiler(self):
        """
        Returns compiler
        """
        return self.toolchain_prefix + "gcc"

    def getLinker(self):
        """
        Returns linker
        """
        return self.toolchain_prefix + "g++"

    def getBuilderCFLAGS(self):
        flags = ["-I\"" + plc_rt_dir + "\""]
        flags += self.cflags
        flags += ["-fmessage-length=0"]
        flags += ["-fno-builtin"]
        flags += ["-fno-strict-aliasing"]
        flags += ["-ffunction-sections"]
        flags += ["-fdata-sections"]
        try:
            self.bsp_dir = os.path.join(os.path.join(plc_rt_dir, "bsp"), self.CTRInstance.GetTarget().getcontent().getLocalTag())
            flags += ["-I\"" + self.bsp_dir + "\""]
        except:
            raise Exception(_("The selected device is not available for emulation"))
        return flags

    def getBuilderLDFLAGS(self):
        return self.ldflags

    def build(self):

        build_path = self.CTRInstance._getBuildPath()
        self.ldflags.append(('-Wl,--dll -L"%(s)s"') % {"s" : build_path + "\\extra_files"})
        shutil.copyfile(self.extra_files + "\\it_fb_block.c", build_path + '\\it_fb_block.c')
        shutil.copyfile(self.extra_files + "\\it_fb_block.h", build_path + '\\it_fb_block.h')
        shutil.copyfile(self.extra_files + "\\SoftPlc.dll", build_path + '\\extra_files\\SoftPlc.dll')
        shutil.copyfile(self.extra_files + "\\SoftPlc.lib", build_path + '\\extra_files\\SoftPlc.lib')
        shutil.copyfile(self.extra_files + "\\sqlite3.dll", build_path + '\\extra_files\\sqlite3.dll')
        #shutil.copyfile(self.extra_files + "\\sqlite3.lib", build_path + '\\extra_files\\sqlite3.lib')

        self.CTRInstance.LocationCFilesAndCFLAGS.append(('', [(build_path + '\\it_fb_block.c',
                               '"-I' + matiec_lib_dir + '" -Wno-unused-function'), ],
                         False))

        return super(x86_emulator_target, self).build()

    def GenerateFastApp(self, task_data_dict, default_interfaces):
        return GenerateFastApp(task_data_dict, default_interfaces)