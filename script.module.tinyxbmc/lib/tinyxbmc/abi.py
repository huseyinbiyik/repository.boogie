'''
Created on Nov 1, 2021

@author: boogie
'''
import platform
import xbmc
import struct


elf_machines = {2: "sparc", 3: "x86", 8: "mips", 20: "ppc", 21: "ppc64", 22: "s390",
                40: "arm", 42: "superh", 50: "ia64", 62: "amd64", 183: "aarch64", 243: "riscv"}


def detect_os():
    system = platform.system().lower()
    if "windows" in system or xbmc.getCondVisibility('system.platform.windows'):
        return "windows"
    if "linux" in system or xbmc.getCondVisibility('system.platform.linux'):
        if xbmc.getCondVisibility('system.platform.android'):
            return "android"
        return "linux"


def getelfabi():
    def readbyte(offset, decoder="B", size=1):
        f.seek(offset)
        return struct.unpack(decoder, f.read(size))[0]
    mflags_d = {}
    with open("/proc/self/exe", "rb") as f:
        is64 = readbyte(0x4) == 2
        oseabi = readbyte(0x7)
        eabiver = readbyte(0x8)
        machine = elf_machines.get(readbyte(0x12, "H", 2))
        if is64:
            f.seek(0x30)
        else:
            f.seek(0x24)
        mflags = f.read(4)
    if machine in ["arm", "arm64"]:
        first, mid, abi = struct.unpack("HBB", mflags)
        mflags_d["ABI"] = abi
        mflags_d["HRD"] = first >> 10 & 1
        mflags_d["SFT"] = first >> 9 & 1
    toolchains = []
    if machine == "x86":
        toolchains.append("i386")
    elif machine == "amd64":
        if is64:
            toolchains.append("amd64")
            toolchains.append("i386")
        else:
            toolchains.append("i386")
    elif machine in ["arm", "aarch64"]:
        if is64:
            toolchains.append("aarch64")
        elif mflags_d["HARD"]:
            toolchains.append("armhf")
            toolchains.append("armel")
        else:
            toolchains.append("armel")
    return toolchains, machine, is64, mflags
