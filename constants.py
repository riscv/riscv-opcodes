import re


isa_regex = \
re.compile("^RV(32|64|128)[IE]+[ABCDEFGHJKLMNPQSTUVX]*(Zicsr|Zifencei|Zihintpause|Zam|Ztso|Zkne|Zknd|Zknh|Zkse|Zksh|Zkg|Zkb|Zkr|Zks|Zkn|Zba|Zbc|Zbb|Zbp|Zbr|Zbm|Zbs|Zbe|Zbf|Zbt|Zmmul|Zbpbo){,1}(_Zicsr){,1}(_Zifencei){,1}(_Zihintpause){,1}(_Zmmul){,1}(_Zam){,1}(_Zba){,1}(_Zbb){,1}(_Zbc){,1}(_Zbe){,1}(_Zbf){,1}(_Zbm){,1}(_Zbp){,1}(_Zbpbo){,1}(_Zbr){,1}(_Zbs){,1}(_Zbt){,1}(_Zkb){,1}(_Zkg){,1}(_Zkr){,1}(_Zks){,1}(_Zkn){,1}(_Zknd){,1}(_Zkne){,1}(_Zknh){,1}(_Zkse){,1}(_Zksh){,1}(_Ztso){,1}$")

# regex to find <msb>..<lsb>=<val> patterns in instruction
fixed_ranges = re.compile(
    '\s*(?P<msb>\d+.?)\.\.(?P<lsb>\d+.?)\s*=\s*(?P<val>\d[\w]*)[\s$]*', re.M)

# regex to find <lsb>=<val> patterns in instructions
#single_fixed = re.compile('\s+(?P<lsb>\d+)=(?P<value>[\w\d]*)[\s$]*', re.M)
single_fixed = re.compile('(?:^|[\s])(?P<lsb>\d+)=(?P<value>[\w]*)((?=\s|$))', re.M)

# regex to find the overloading condition variable
var_regex = re.compile('(?P<var>[a-zA-Z][\w\d]*)\s*=\s*.*?[\s$]*', re.M)

# regex for pseudo op instructions returns the dependent filename, dependent
# instruction, the pseudo op name and the encoding string
pseudo_regex = re.compile(
    '^\$pseudo_op\s+(?P<filename>rv[\d]*_[\w].*)::\s*(?P<orig_inst>.*?)\s+(?P<pseudo_inst>.*?)\s+(?P<overload>.*)$'
, re.M)

imported_regex = re.compile('^\s*\$import\s*(?P<extension>.*)\s*::\s*(?P<instruction>.*)', re.M)

#
# Trap cause codes
causes = [
  (0x00, 'misaligned fetch'),
  (0x01, 'fetch access'),
  (0x02, 'illegal instruction'),
  (0x03, 'breakpoint'),
  (0x04, 'misaligned load'),
  (0x05, 'load access'),
  (0x06, 'misaligned store'),
  (0x07, 'store access'),
  (0x08, 'user_ecall'),
  (0x09, 'supervisor_ecall'),
  (0x0A, 'virtual_supervisor_ecall'),
  (0x0B, 'machine_ecall'),
  (0x0C, 'fetch page fault'),
  (0x0D, 'load page fault'),
  (0x0F, 'store page fault'),
  (0x14, 'fetch guest page fault'),
  (0x15, 'load guest page fault'),
  (0x16, 'virtual instruction'),
  (0x17, 'store guest page fault'),
]

csrs = [
  # Standard User R/W
  (0x001, 'fflags'),
  (0x002, 'frm'),
  (0x003, 'fcsr'),
  (0x008, 'vstart'),
  (0x009, 'vxsat'),
  (0x00A, 'vxrm'),
  (0x00F, 'vcsr'),
  (0x015, 'seed'), # Zkr

  # Standard User RO
  (0xC00, 'cycle'),
  (0xC01, 'time'),
  (0xC02, 'instret'),
  (0xC03, 'hpmcounter3'),
  (0xC04, 'hpmcounter4'),
  (0xC05, 'hpmcounter5'),
  (0xC06, 'hpmcounter6'),
  (0xC07, 'hpmcounter7'),
  (0xC08, 'hpmcounter8'),
  (0xC09, 'hpmcounter9'),
  (0xC0A, 'hpmcounter10'),
  (0xC0B, 'hpmcounter11'),
  (0xC0C, 'hpmcounter12'),
  (0xC0D, 'hpmcounter13'),
  (0xC0E, 'hpmcounter14'),
  (0xC0F, 'hpmcounter15'),
  (0xC10, 'hpmcounter16'),
  (0xC11, 'hpmcounter17'),
  (0xC12, 'hpmcounter18'),
  (0xC13, 'hpmcounter19'),
  (0xC14, 'hpmcounter20'),
  (0xC15, 'hpmcounter21'),
  (0xC16, 'hpmcounter22'),
  (0xC17, 'hpmcounter23'),
  (0xC18, 'hpmcounter24'),
  (0xC19, 'hpmcounter25'),
  (0xC1A, 'hpmcounter26'),
  (0xC1B, 'hpmcounter27'),
  (0xC1C, 'hpmcounter28'),
  (0xC1D, 'hpmcounter29'),
  (0xC1E, 'hpmcounter30'),
  (0xC1F, 'hpmcounter31'),
  (0xC20, 'vl'),
  (0xC21, 'vtype'),
  (0xC22, 'vlenb'),

  # Standard Supervisor R/W
  (0x100, 'sstatus'),
  (0x102, 'sedeleg'),
  (0x103, 'sideleg'),
  (0x104, 'sie'),
  (0x105, 'stvec'),
  (0x106, 'scounteren'),
  (0x10A, 'senvcfg'),
  (0x10C, 'sstateen0'), # Smstateen
  (0x10D, 'sstateen1'), # Smstateen
  (0x10E, 'sstateen2'), # Smstateen
  (0x10F, 'sstateen3'), # Smstateen
  (0x140, 'sscratch'),
  (0x141, 'sepc'),
  (0x142, 'scause'),
  (0x143, 'stval'),
  (0x144, 'sip'),
  (0x14D, 'stimecmp'), # Sstc
  (0x180, 'satp'),
  (0x5A8, 'scontext'),

  # Standard Hypervisor R/w
  (0x200, 'vsstatus'),
  (0x204, 'vsie'),
  (0x205, 'vstvec'),
  (0x240, 'vsscratch'),
  (0x241, 'vsepc'),
  (0x242, 'vscause'),
  (0x243, 'vstval'),
  (0x244, 'vsip'),
  (0x24D, 'vstimecmp'), # Sstc
  (0x280, 'vsatp'),
  (0x600, 'hstatus'),
  (0x602, 'hedeleg'),
  (0x603, 'hideleg'),
  (0x604, 'hie'),
  (0x605, 'htimedelta'),
  (0x606, 'hcounteren'),
  (0x607, 'hgeie'),
  (0x60A, 'henvcfg'),
  (0x60C, 'hstateen0'), # Smstateen
  (0x60D, 'hstateen1'), # Smstateen
  (0x60E, 'hstateen2'), # Smstateen
  (0x60F, 'hstateen3'), # Smstateen
  (0x643, 'htval'),
  (0x644, 'hip'),
  (0x645, 'hvip'),
  (0x64A, 'htinst'),
  (0x680, 'hgatp'),
  (0x6A8, 'hcontext'),
  (0xE12, 'hgeip'),

  # Standard Supervisor RO
  (0xDA0, 'scountovf'), # Sscofpmf

  # Tentative CSR assignment for CLIC
  (0x007, 'utvt'),
  (0x045, 'unxti'),
  (0x046, 'uintstatus'),
  (0x048, 'uscratchcsw'),
  (0x049, 'uscratchcswl'),
  (0x107, 'stvt'),
  (0x145, 'snxti'),
  (0x146, 'sintstatus'),
  (0x148, 'sscratchcsw'),
  (0x149, 'sscratchcswl'),
  (0x307, 'mtvt'),
  (0x345, 'mnxti'),
  (0x346, 'mintstatus'),
  (0x348, 'mscratchcsw'),
  (0x349, 'mscratchcswl'),

  # Standard Machine R/W
  (0x300, 'mstatus'),
  (0x301, 'misa'),
  (0x302, 'medeleg'),
  (0x303, 'mideleg'),
  (0x304, 'mie'),
  (0x305, 'mtvec'),
  (0x306, 'mcounteren'),
  (0x30a, 'menvcfg'),
  (0x30C, 'mstateen0'), # Smstateen
  (0x30D, 'mstateen1'), # Smstateen
  (0x30E, 'mstateen2'), # Smstateen
  (0x30F, 'mstateen3'), # Smstateen
  (0x320, 'mcountinhibit'),
  (0x340, 'mscratch'),
  (0x341, 'mepc'),
  (0x342, 'mcause'),
  (0x343, 'mtval'),
  (0x344, 'mip'),
  (0x34a, 'mtinst'),
  (0x34b, 'mtval2'),
  (0x3a0, 'pmpcfg0'),
  (0x3a1, 'pmpcfg1'),
  (0x3a2, 'pmpcfg2'),
  (0x3a3, 'pmpcfg3'),
  (0x3a4, 'pmpcfg4'),
  (0x3a5, 'pmpcfg5'),
  (0x3a6, 'pmpcfg6'),
  (0x3a7, 'pmpcfg7'),
  (0x3a8, 'pmpcfg8'),
  (0x3a9, 'pmpcfg9'),
  (0x3aa, 'pmpcfg10'),
  (0x3ab, 'pmpcfg11'),
  (0x3ac, 'pmpcfg12'),
  (0x3ad, 'pmpcfg13'),
  (0x3ae, 'pmpcfg14'),
  (0x3af, 'pmpcfg15'),
  (0x3b0, 'pmpaddr0'),
  (0x3b1, 'pmpaddr1'),
  (0x3b2, 'pmpaddr2'),
  (0x3b3, 'pmpaddr3'),
  (0x3b4, 'pmpaddr4'),
  (0x3b5, 'pmpaddr5'),
  (0x3b6, 'pmpaddr6'),
  (0x3b7, 'pmpaddr7'),
  (0x3b8, 'pmpaddr8'),
  (0x3b9, 'pmpaddr9'),
  (0x3ba, 'pmpaddr10'),
  (0x3bb, 'pmpaddr11'),
  (0x3bc, 'pmpaddr12'),
  (0x3bd, 'pmpaddr13'),
  (0x3be, 'pmpaddr14'),
  (0x3bf, 'pmpaddr15'),
  (0x3c0, 'pmpaddr16'),
  (0x3c1, 'pmpaddr17'),
  (0x3c2, 'pmpaddr18'),
  (0x3c3, 'pmpaddr19'),
  (0x3c4, 'pmpaddr20'),
  (0x3c5, 'pmpaddr21'),
  (0x3c6, 'pmpaddr22'),
  (0x3c7, 'pmpaddr23'),
  (0x3c8, 'pmpaddr24'),
  (0x3c9, 'pmpaddr25'),
  (0x3ca, 'pmpaddr26'),
  (0x3cb, 'pmpaddr27'),
  (0x3cc, 'pmpaddr28'),
  (0x3cd, 'pmpaddr29'),
  (0x3ce, 'pmpaddr30'),
  (0x3cf, 'pmpaddr31'),
  (0x3d0, 'pmpaddr32'),
  (0x3d1, 'pmpaddr33'),
  (0x3d2, 'pmpaddr34'),
  (0x3d3, 'pmpaddr35'),
  (0x3d4, 'pmpaddr36'),
  (0x3d5, 'pmpaddr37'),
  (0x3d6, 'pmpaddr38'),
  (0x3d7, 'pmpaddr39'),
  (0x3d8, 'pmpaddr40'),
  (0x3d9, 'pmpaddr41'),
  (0x3da, 'pmpaddr42'),
  (0x3db, 'pmpaddr43'),
  (0x3dc, 'pmpaddr44'),
  (0x3dd, 'pmpaddr45'),
  (0x3de, 'pmpaddr46'),
  (0x3df, 'pmpaddr47'),
  (0x3e0, 'pmpaddr48'),
  (0x3e1, 'pmpaddr49'),
  (0x3e2, 'pmpaddr50'),
  (0x3e3, 'pmpaddr51'),
  (0x3e4, 'pmpaddr52'),
  (0x3e5, 'pmpaddr53'),
  (0x3e6, 'pmpaddr54'),
  (0x3e7, 'pmpaddr55'),
  (0x3e8, 'pmpaddr56'),
  (0x3e9, 'pmpaddr57'),
  (0x3ea, 'pmpaddr58'),
  (0x3eb, 'pmpaddr59'),
  (0x3ec, 'pmpaddr60'),
  (0x3ed, 'pmpaddr61'),
  (0x3ee, 'pmpaddr62'),
  (0x3ef, 'pmpaddr63'),
  (0x747, 'mseccfg'),
  (0x7a0, 'tselect'),
  (0x7a1, 'tdata1'),
  (0x7a2, 'tdata2'),
  (0x7a3, 'tdata3'),
  (0x7a4, 'tinfo'),
  (0x7a5, 'tcontrol'),
  (0x7a8, 'mcontext'),
  (0x7aa, 'mscontext'),
  (0x7b0, 'dcsr'),
  (0x7b1, 'dpc'),
  (0x7b2, 'dscratch0'),
  (0x7b3, 'dscratch1'),
  (0xB00, 'mcycle'),
  (0xB02, 'minstret'),
  (0xB03, 'mhpmcounter3'),
  (0xB04, 'mhpmcounter4'),
  (0xB05, 'mhpmcounter5'),
  (0xB06, 'mhpmcounter6'),
  (0xB07, 'mhpmcounter7'),
  (0xB08, 'mhpmcounter8'),
  (0xB09, 'mhpmcounter9'),
  (0xB0A, 'mhpmcounter10'),
  (0xB0B, 'mhpmcounter11'),
  (0xB0C, 'mhpmcounter12'),
  (0xB0D, 'mhpmcounter13'),
  (0xB0E, 'mhpmcounter14'),
  (0xB0F, 'mhpmcounter15'),
  (0xB10, 'mhpmcounter16'),
  (0xB11, 'mhpmcounter17'),
  (0xB12, 'mhpmcounter18'),
  (0xB13, 'mhpmcounter19'),
  (0xB14, 'mhpmcounter20'),
  (0xB15, 'mhpmcounter21'),
  (0xB16, 'mhpmcounter22'),
  (0xB17, 'mhpmcounter23'),
  (0xB18, 'mhpmcounter24'),
  (0xB19, 'mhpmcounter25'),
  (0xB1A, 'mhpmcounter26'),
  (0xB1B, 'mhpmcounter27'),
  (0xB1C, 'mhpmcounter28'),
  (0xB1D, 'mhpmcounter29'),
  (0xB1E, 'mhpmcounter30'),
  (0xB1F, 'mhpmcounter31'),
  (0x323, 'mhpmevent3'),
  (0x324, 'mhpmevent4'),
  (0x325, 'mhpmevent5'),
  (0x326, 'mhpmevent6'),
  (0x327, 'mhpmevent7'),
  (0x328, 'mhpmevent8'),
  (0x329, 'mhpmevent9'),
  (0x32A, 'mhpmevent10'),
  (0x32B, 'mhpmevent11'),
  (0x32C, 'mhpmevent12'),
  (0x32D, 'mhpmevent13'),
  (0x32E, 'mhpmevent14'),
  (0x32F, 'mhpmevent15'),
  (0x330, 'mhpmevent16'),
  (0x331, 'mhpmevent17'),
  (0x332, 'mhpmevent18'),
  (0x333, 'mhpmevent19'),
  (0x334, 'mhpmevent20'),
  (0x335, 'mhpmevent21'),
  (0x336, 'mhpmevent22'),
  (0x337, 'mhpmevent23'),
  (0x338, 'mhpmevent24'),
  (0x339, 'mhpmevent25'),
  (0x33A, 'mhpmevent26'),
  (0x33B, 'mhpmevent27'),
  (0x33C, 'mhpmevent28'),
  (0x33D, 'mhpmevent29'),
  (0x33E, 'mhpmevent30'),
  (0x33F, 'mhpmevent31'),

  # Standard Machine RO
  (0xF11, 'mvendorid'),
  (0xF12, 'marchid'),
  (0xF13, 'mimpid'),
  (0xF14, 'mhartid'),
  (0xF15, 'mconfigptr'),
]

csrs32 = [
  # Standard Supervisor R/W
  (0x15D, 'stimecmph'), # Sstc

  # Standard Hypervisor R/w
  (0x25D, 'vstimecmph'), # Sstc
  (0x615, 'htimedeltah'),
  (0x61A, 'henvcfgh'),
  (0x61C, 'hstateen0h'), # Smstateen
  (0x61D, 'hstateen1h'), # Smstateen
  (0x61E, 'hstateen2h'), # Smstateen
  (0x61F, 'hstateen3h'), # Smstateen

  # Standard User RO
  (0xC80, 'cycleh'),
  (0xC81, 'timeh'),
  (0xC82, 'instreth'),
  (0xC83, 'hpmcounter3h'),
  (0xC84, 'hpmcounter4h'),
  (0xC85, 'hpmcounter5h'),
  (0xC86, 'hpmcounter6h'),
  (0xC87, 'hpmcounter7h'),
  (0xC88, 'hpmcounter8h'),
  (0xC89, 'hpmcounter9h'),
  (0xC8A, 'hpmcounter10h'),
  (0xC8B, 'hpmcounter11h'),
  (0xC8C, 'hpmcounter12h'),
  (0xC8D, 'hpmcounter13h'),
  (0xC8E, 'hpmcounter14h'),
  (0xC8F, 'hpmcounter15h'),
  (0xC90, 'hpmcounter16h'),
  (0xC91, 'hpmcounter17h'),
  (0xC92, 'hpmcounter18h'),
  (0xC93, 'hpmcounter19h'),
  (0xC94, 'hpmcounter20h'),
  (0xC95, 'hpmcounter21h'),
  (0xC96, 'hpmcounter22h'),
  (0xC97, 'hpmcounter23h'),
  (0xC98, 'hpmcounter24h'),
  (0xC99, 'hpmcounter25h'),
  (0xC9A, 'hpmcounter26h'),
  (0xC9B, 'hpmcounter27h'),
  (0xC9C, 'hpmcounter28h'),
  (0xC9D, 'hpmcounter29h'),
  (0xC9E, 'hpmcounter30h'),
  (0xC9F, 'hpmcounter31h'),

  # Standard Machine RW
  (0x310, 'mstatush'),
  (0x31A, 'menvcfgh'),
  (0x31C, 'mstateen0h'), # Smstateen
  (0x31D, 'mstateen1h'), # Smstateen
  (0x31E, 'mstateen2h'), # Smstateen
  (0x31F, 'mstateen3h'), # Smstateen
  (0x723, 'mhpmevent3h'),  # Sscofpmf
  (0x724, 'mhpmevent4h'),  # Sscofpmf
  (0x725, 'mhpmevent5h'),  # Sscofpmf
  (0x726, 'mhpmevent6h'),  # Sscofpmf
  (0x727, 'mhpmevent7h'),  # Sscofpmf
  (0x728, 'mhpmevent8h'),  # Sscofpmf
  (0x729, 'mhpmevent9h'),  # Sscofpmf
  (0x72A, 'mhpmevent10h'), # Sscofpmf
  (0x72B, 'mhpmevent11h'), # Sscofpmf
  (0x72C, 'mhpmevent12h'), # Sscofpmf
  (0x72D, 'mhpmevent13h'), # Sscofpmf
  (0x72E, 'mhpmevent14h'), # Sscofpmf
  (0x72F, 'mhpmevent15h'), # Sscofpmf
  (0x730, 'mhpmevent16h'), # Sscofpmf
  (0x731, 'mhpmevent17h'), # Sscofpmf
  (0x732, 'mhpmevent18h'), # Sscofpmf
  (0x733, 'mhpmevent19h'), # Sscofpmf
  (0x734, 'mhpmevent20h'), # Sscofpmf
  (0x735, 'mhpmevent21h'), # Sscofpmf
  (0x736, 'mhpmevent22h'), # Sscofpmf
  (0x737, 'mhpmevent23h'), # Sscofpmf
  (0x738, 'mhpmevent24h'), # Sscofpmf
  (0x739, 'mhpmevent25h'), # Sscofpmf
  (0x73A, 'mhpmevent26h'), # Sscofpmf
  (0x73B, 'mhpmevent27h'), # Sscofpmf
  (0x73C, 'mhpmevent28h'), # Sscofpmf
  (0x73D, 'mhpmevent29h'), # Sscofpmf
  (0x73E, 'mhpmevent30h'), # Sscofpmf
  (0x73F, 'mhpmevent31h'), # Sscofpmf
  (0x757, 'mseccfgh'),
  (0xB80, 'mcycleh'),
  (0xB82, 'minstreth'),
  (0xB83, 'mhpmcounter3h'),
  (0xB84, 'mhpmcounter4h'),
  (0xB85, 'mhpmcounter5h'),
  (0xB86, 'mhpmcounter6h'),
  (0xB87, 'mhpmcounter7h'),
  (0xB88, 'mhpmcounter8h'),
  (0xB89, 'mhpmcounter9h'),
  (0xB8A, 'mhpmcounter10h'),
  (0xB8B, 'mhpmcounter11h'),
  (0xB8C, 'mhpmcounter12h'),
  (0xB8D, 'mhpmcounter13h'),
  (0xB8E, 'mhpmcounter14h'),
  (0xB8F, 'mhpmcounter15h'),
  (0xB90, 'mhpmcounter16h'),
  (0xB91, 'mhpmcounter17h'),
  (0xB92, 'mhpmcounter18h'),
  (0xB93, 'mhpmcounter19h'),
  (0xB94, 'mhpmcounter20h'),
  (0xB95, 'mhpmcounter21h'),
  (0xB96, 'mhpmcounter22h'),
  (0xB97, 'mhpmcounter23h'),
  (0xB98, 'mhpmcounter24h'),
  (0xB99, 'mhpmcounter25h'),
  (0xB9A, 'mhpmcounter26h'),
  (0xB9B, 'mhpmcounter27h'),
  (0xB9C, 'mhpmcounter28h'),
  (0xB9D, 'mhpmcounter29h'),
  (0xB9E, 'mhpmcounter30h'),
  (0xB9F, 'mhpmcounter31h'),
]

# look up table of position of various arguments that are used by the
# instructions in the encoding files.
arg_lut = {}
arg_lut['rd'] = (11, 7)
arg_lut['rt'] = (19, 15)  # source+dest register address. Overlaps rs1.
arg_lut['rs1'] = (19, 15)
arg_lut['rs2'] = (24, 20)
arg_lut['rs3'] = (31, 27)
arg_lut['aqrl'] = (26, 25)
arg_lut['aq'] = (26, 26)
arg_lut['rl'] = (25, 25)
arg_lut['fm'] = (31, 28)
arg_lut['pred'] = (27, 24)
arg_lut['succ'] = (23, 20)
arg_lut['rm'] = (14, 12)
arg_lut['funct3'] = (14, 12)
arg_lut['funct2'] = (26, 25)
arg_lut['imm20'] = (31, 12)
arg_lut['jimm20'] = (31, 12)
arg_lut['imm12'] = (31, 20)
arg_lut['csr'] = (31, 20)
arg_lut['imm12hi'] = (31, 25)
arg_lut['bimm12hi'] = (31, 25)
arg_lut['imm12lo'] = (11, 7)
arg_lut['bimm12lo'] = (11, 7)
arg_lut['zimm'] = (19, 15)
arg_lut['shamt'] = (26, 20)
arg_lut['shamtw'] = (24, 20)
arg_lut['shamtw4'] = (23, 20)
arg_lut['shamtd'] = (25, 20)
arg_lut['bs'] = (31, 30)  # byte select for RV32K AES
arg_lut['rnum'] = (23, 20)  # round constant for RV64 AES
arg_lut['rc'] = (29, 25)
arg_lut['imm2'] = (21, 20)
arg_lut['imm3'] = (22, 20)
arg_lut['imm4'] = (23, 20)
arg_lut['imm5'] = (24, 20)
arg_lut['imm6'] = (25, 20)
arg_lut['zimm'] = (19, 15)
arg_lut['opcode'] = (6,0)
arg_lut['funct7'] = (31,25)

# for vectors
arg_lut['vd'] = (11, 7)
arg_lut['vs3'] = (11, 7)
arg_lut['vs1'] = (19, 15)
arg_lut['vs2'] = (24, 20)
arg_lut['vm'] = (25, 25)
arg_lut['wd'] = (26, 26)
arg_lut['amoop'] = (31, 27)
arg_lut['nf'] = (31, 29)
arg_lut['simm5'] = (19, 15)
arg_lut['zimm10'] = (29, 20)
arg_lut['zimm11'] = (30, 20)


#compressed immediates and fields
arg_lut['c_nzuimm10'] = (12,5)
arg_lut['c_uimm7lo'] = (6,5)
arg_lut['c_uimm7hi'] = (12,10)
arg_lut['c_uimm8lo'] = (6,5)
arg_lut['c_uimm8hi'] = (12,10)
arg_lut['c_uimm9lo'] = (6,5)
arg_lut['c_uimm9hi'] = (12,10)
arg_lut['c_nzimm6lo'] = (6,2)
arg_lut['c_nzimm6hi'] = (12,12)
arg_lut['c_imm6lo'] = (6,2)
arg_lut['c_imm6hi'] = (12,12)
arg_lut['c_nzimm10hi'] = (12,12)
arg_lut['c_nzimm10lo'] = (6,2)
arg_lut['c_nzimm18hi'] = (12,12)
arg_lut['c_nzimm18lo'] = (6,2)
arg_lut['c_imm12'] = (12,2)
arg_lut['c_bimm9lo'] = (6,2)
arg_lut['c_bimm9hi'] = (12,10)
arg_lut['c_nzuimm5'] = (6,2)
arg_lut['c_nzuimm6lo'] = (6,2)
arg_lut['c_nzuimm6hi'] = (12, 12)
arg_lut['c_uimm8splo'] = (6,2)
arg_lut['c_uimm8sphi'] = (12, 12)
arg_lut['c_uimm8sp_s'] = (12,7)
arg_lut['c_uimm10splo'] = (6,2)
arg_lut['c_uimm10sphi'] = (12, 12)
arg_lut['c_uimm9splo'] = (6,2)
arg_lut['c_uimm9sphi'] = (12, 12)
arg_lut['c_uimm10sp_s'] = (12,7)
arg_lut['c_uimm9sp_s'] = (12,7)

arg_lut['rs1_p'] = (9,7)
arg_lut['rs2_p'] = (4,2)
arg_lut['rd_p'] = (4,2)
arg_lut['rd_rs1_n0'] = (11,7)
arg_lut['rd_rs1_p'] = (9,7)
arg_lut['rd_rs1'] = (11,7)
arg_lut['rd_n2'] = (11,7)
arg_lut['rd_n0'] = (11,7)
arg_lut['rs1_n0'] = (11,7)
arg_lut['c_rs2_n0'] = (6,2)
arg_lut['c_rs1_n0'] = (11,7)
arg_lut['c_rs2'] = (6,2)

# dictionary containing the mapping of the argument to the what the fields in
# the latex table should be
latex_mapping = {}
latex_mapping['imm12'] = 'imm[11:0]'
latex_mapping['rs1'] = 'rs1'
latex_mapping['rs2'] = 'rs2'
latex_mapping['rd'] = 'rd'
latex_mapping['imm20'] = 'imm[31:12]'
latex_mapping['bimm12hi'] = 'imm[12$\\vert$10:5]'
latex_mapping['bimm12lo'] = 'imm[4:1$\\vert$11]'
latex_mapping['imm12hi'] = 'imm[11:5]'
latex_mapping['imm12lo'] = 'imm[4:0]'
latex_mapping['jimm20'] = 'imm[20$\\vert$10:1$\\vert$11$\\vert$19:12]'
latex_mapping['zimm'] = 'uimm'
latex_mapping['shamtw'] = 'shamt'
latex_mapping['shamtd'] = 'shamt'
latex_mapping['rd_p'] = "rd\\,$'$"
latex_mapping['rs1_p'] = "rs1\\,$'$"
latex_mapping['rs2_p'] = "rs2\\,$'$"
latex_mapping['rd_rs1_n0'] = 'rd/rs$\\neq$0'
latex_mapping['rd_rs1_p'] = "rs1\\,$'$/rs2\\,$'$"
latex_mapping['c_rs2'] = 'rs2'
latex_mapping['c_rs2_n0'] = 'rs2$\\neq$0'
latex_mapping['rd_n0'] = 'rd$\\neq$0'
latex_mapping['rs1_n0'] = 'rs1$\\neq$0'
latex_mapping['c_rs1_n0'] = 'rs1$\\neq$0'
latex_mapping['rd_rs1'] = 'rd/rs1'
latex_mapping['c_nzuimm10'] = "nzuimm[5:4$\\vert$9:6$\\vert$2$\\vert$3]"
latex_mapping['c_uimm7lo'] = 'uimm[2$\\vert$6]'
latex_mapping['c_uimm7hi'] = 'uimm[5:3]'
latex_mapping['c_uimm8lo'] = 'uimm[7:6]'
latex_mapping['c_uimm8hi'] = 'uimm[5:3]'
latex_mapping['c_uimm9lo'] = 'uimm[7:6]'
latex_mapping['c_uimm9hi'] = 'uimm[5:4$\\vert$8]'
latex_mapping['c_nzimm6lo'] = 'nzimm[4:0]'
latex_mapping['c_nzimm6hi'] = 'nzimm[5]'
latex_mapping['c_imm6lo'] = 'imm[4:0]'
latex_mapping['c_imm6hi'] = 'imm[5]'
latex_mapping['c_nzimm10hi'] = 'nzimm[9]'
latex_mapping['c_nzimm10lo'] = 'nzimm[4$\\vert$6$\\vert$8:7$\\vert$5]'
latex_mapping['c_nzimm18hi'] = 'nzimm[17]'
latex_mapping['c_nzimm18lo'] = 'nzimm[16:12]'
latex_mapping['c_imm12'] = 'imm[11$\\vert$4$\\vert$9:8$\\vert$10$\\vert$6$\\vert$7$\\vert$3:1$\\vert$5]'
latex_mapping['c_bimm9lo'] = 'imm[7:6$\\vert$2:1$\\vert$5]'
latex_mapping['c_bimm9hi'] = 'imm[8$\\vert$4:3]'
latex_mapping['c_nzuimm5'] = 'nzuimm[4:0]'
latex_mapping['c_nzuimm6lo'] = 'nzuimm[4:0]'
latex_mapping['c_nzuimm6hi'] = 'nzuimm[5]'
latex_mapping['c_uimm8splo'] = 'uimm[4:2$\\vert$7:6]'
latex_mapping['c_uimm8sphi'] = 'uimm[5]'
latex_mapping['c_uimm8sp_s'] = 'uimm[5:2$\\vert$7:6]'
latex_mapping['c_uimm10splo'] = 'uimm[4$\\vert$9:6]'
latex_mapping['c_uimm10sphi'] = 'uimm[5]'
latex_mapping['c_uimm9splo'] = 'uimm[4:3$\\vert$8:6]'
latex_mapping['c_uimm9sphi'] = 'uimm[5]'
latex_mapping['c_uimm10sp_s'] = 'uimm[5:4$\\vert$9:6]'
latex_mapping['c_uimm9sp_s'] = 'uimm[5:3$\\vert$8:6]'

# created a dummy instruction-dictionary like dictionary for all the instruction
# types so that the same logic can be used to create their tables
latex_inst_type = {}
latex_inst_type['R-type'] = {}
latex_inst_type['R-type']['variable_fields'] = ['opcode', 'rd', 'funct3', \
        'rs1', 'rs2', 'funct7']
latex_inst_type['R4-type'] = {}
latex_inst_type['R4-type']['variable_fields'] = ['opcode', 'rd', 'funct3', \
        'rs1', 'rs2', 'funct2', 'rs3']
latex_inst_type['I-type'] = {}
latex_inst_type['I-type']['variable_fields'] = ['opcode', 'rd', 'funct3', \
        'rs1', 'imm12']
latex_inst_type['S-type'] = {}
latex_inst_type['S-type']['variable_fields'] = ['opcode', 'imm12lo', 'funct3', \
        'rs1', 'rs2', 'imm12hi']
latex_inst_type['B-type'] = {}
latex_inst_type['B-type']['variable_fields'] = ['opcode', 'bimm12lo', 'funct3', \
        'rs1', 'rs2', 'bimm12hi']
latex_inst_type['U-type'] = {}
latex_inst_type['U-type']['variable_fields'] = ['opcode', 'rd', 'imm20']
latex_inst_type['J-type'] = {}
latex_inst_type['J-type']['variable_fields'] = ['opcode', 'rd', 'jimm20']
latex_fixed_fields = []
latex_fixed_fields.append((31,25))
latex_fixed_fields.append((24,20))
latex_fixed_fields.append((19,15))
latex_fixed_fields.append((14,12))
latex_fixed_fields.append((11,7))
latex_fixed_fields.append((6,0))
