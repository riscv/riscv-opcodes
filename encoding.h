#ifndef RISCV_CSR_ENCODING_H
#define RISCV_CSR_ENCODING_H

#define MSTATUS_UIE         0x00000001
#define MSTATUS_SIE         0x00000002
#define MSTATUS_HIE         0x00000004
#define MSTATUS_MIE         0x00000008
#define MSTATUS_UPIE        0x00000010
#define MSTATUS_SPIE        0x00000020
#define MSTATUS_UBE         0x00000040
#define MSTATUS_MPIE        0x00000080
#define MSTATUS_SPP         0x00000100
#define MSTATUS_VS          0x00000600
#define MSTATUS_MPP         0x00001800
#define MSTATUS_FS          0x00006000
#define MSTATUS_XS          0x00018000
#define MSTATUS_MPRV        0x00020000
#define MSTATUS_SUM         0x00040000
#define MSTATUS_MXR         0x00080000
#define MSTATUS_TVM         0x00100000
#define MSTATUS_TW          0x00200000
#define MSTATUS_TSR         0x00400000
#define MSTATUS_SPELP       0x00800000
#define MSTATUS32_SD        0x80000000
#define MSTATUS_UXL         0x0000000300000000
#define MSTATUS_SXL         0x0000000C00000000
#define MSTATUS_SBE         0x0000001000000000
#define MSTATUS_MBE         0x0000002000000000
#define MSTATUS_GVA         0x0000004000000000
#define MSTATUS_MPV         0x0000008000000000
#define MSTATUS_MPELP       0x0000020000000000
#define MSTATUS64_SD        0x8000000000000000

#define MSTATUSH_SBE        0x00000010
#define MSTATUSH_MBE        0x00000020
#define MSTATUSH_GVA        0x00000040
#define MSTATUSH_MPV        0x00000080

#define SSTATUS_UIE         0x00000001
#define SSTATUS_SIE         0x00000002
#define SSTATUS_UPIE        0x00000010
#define SSTATUS_SPIE        0x00000020
#define SSTATUS_UBE         0x00000040
#define SSTATUS_SPP         0x00000100
#define SSTATUS_VS          0x00000600
#define SSTATUS_FS          0x00006000
#define SSTATUS_XS          0x00018000
#define SSTATUS_SUM         0x00040000
#define SSTATUS_MXR         0x00080000
#define SSTATUS_SPELP       0x00800000
#define SSTATUS32_SD        0x80000000
#define SSTATUS_UXL         0x0000000300000000
#define SSTATUS64_SD        0x8000000000000000

#define HSTATUS_VSXL        0x300000000
#define HSTATUS_VTSR        0x00400000
#define HSTATUS_VTW         0x00200000
#define HSTATUS_VTVM        0x00100000
#define HSTATUS_VGEIN       0x0003f000
#define HSTATUS_HU          0x00000200
#define HSTATUS_SPVP        0x00000100
#define HSTATUS_SPV         0x00000080
#define HSTATUS_GVA         0x00000040
#define HSTATUS_VSBE        0x00000020

#define USTATUS_UIE         0x00000001
#define USTATUS_UPIE        0x00000010

#define MNSTATUS_NMIE       0x00000008
#define MNSTATUS_MNPP       0x00001800
#define MNSTATUS_MNPV       0x00000080

#define DCSR_XDEBUGVER      (3U<<30)
#define DCSR_NDRESET        (1<<29)
#define DCSR_FULLRESET      (1<<28)
#define DCSR_PELP           (1<<18)
#define DCSR_EBREAKM        (1<<15)
#define DCSR_EBREAKH        (1<<14)
#define DCSR_EBREAKS        (1<<13)
#define DCSR_EBREAKU        (1<<12)
#define DCSR_STOPCYCLE      (1<<10)
#define DCSR_STOPTIME       (1<<9)
#define DCSR_CAUSE          (7<<6)
#define DCSR_DEBUGINT       (1<<5)
#define DCSR_HALT           (1<<3)
#define DCSR_STEP           (1<<2)
#define DCSR_PRV            (3<<0)

#define DCSR_CAUSE_NONE     0
#define DCSR_CAUSE_SWBP     1
#define DCSR_CAUSE_HWBP     2
#define DCSR_CAUSE_DEBUGINT 3
#define DCSR_CAUSE_STEP     4
#define DCSR_CAUSE_HALT     5
#define DCSR_CAUSE_GROUP    6

#define MCONTROL_TYPE(xlen)    (0xfULL<<((xlen)-4))
#define MCONTROL_DMODE(xlen)   (1ULL<<((xlen)-5))
#define MCONTROL_MASKMAX(xlen) (0x3fULL<<((xlen)-11))

#define MCONTROL_SELECT     (1<<19)
#define MCONTROL_TIMING     (1<<18)
#define MCONTROL_ACTION     (0x3f<<12)
#define MCONTROL_CHAIN      (1<<11)
#define MCONTROL_MATCH      (0xf<<7)
#define MCONTROL_M          (1<<6)
#define MCONTROL_H          (1<<5)
#define MCONTROL_S          (1<<4)
#define MCONTROL_U          (1<<3)
#define MCONTROL_EXECUTE    (1<<2)
#define MCONTROL_STORE      (1<<1)
#define MCONTROL_LOAD       (1<<0)

#define MCONTROL_TYPE_NONE      0
#define MCONTROL_TYPE_MATCH     2

#define MCONTROL_ACTION_DEBUG_EXCEPTION   0
#define MCONTROL_ACTION_DEBUG_MODE        1
#define MCONTROL_ACTION_TRACE_START       2
#define MCONTROL_ACTION_TRACE_STOP        3
#define MCONTROL_ACTION_TRACE_EMIT        4

#define MCONTROL_MATCH_EQUAL     0
#define MCONTROL_MATCH_NAPOT     1
#define MCONTROL_MATCH_GE        2
#define MCONTROL_MATCH_LT        3
#define MCONTROL_MATCH_MASK_LOW  4
#define MCONTROL_MATCH_MASK_HIGH 5

#define MIP_USIP            (1 << IRQ_U_SOFT)
#define MIP_SSIP            (1 << IRQ_S_SOFT)
#define MIP_VSSIP           (1 << IRQ_VS_SOFT)
#define MIP_MSIP            (1 << IRQ_M_SOFT)
#define MIP_UTIP            (1 << IRQ_U_TIMER)
#define MIP_STIP            (1 << IRQ_S_TIMER)
#define MIP_VSTIP           (1 << IRQ_VS_TIMER)
#define MIP_MTIP            (1 << IRQ_M_TIMER)
#define MIP_UEIP            (1 << IRQ_U_EXT)
#define MIP_SEIP            (1 << IRQ_S_EXT)
#define MIP_VSEIP           (1 << IRQ_VS_EXT)
#define MIP_MEIP            (1 << IRQ_M_EXT)
#define MIP_SGEIP           (1 << IRQ_S_GEXT)
#define MIP_LCOFIP          (1 << IRQ_LCOF)

#define MIP_S_MASK          (MIP_SSIP | MIP_STIP | MIP_SEIP)
#define MIP_VS_MASK         (MIP_VSSIP | MIP_VSTIP | MIP_VSEIP)
#define MIP_HS_MASK         (MIP_VS_MASK | MIP_SGEIP)

#define MIDELEG_FORCED_MASK MIP_HS_MASK

#define SIP_SSIP MIP_SSIP
#define SIP_STIP MIP_STIP

#define MENVCFG_FIOM  0x00000001
#define MENVCFG_LPE   0x00000004
#define MENVCFG_SSE   0x00000008
#define MENVCFG_CBIE  0x00000030
#define MENVCFG_CBCFE 0x00000040
#define MENVCFG_CBZE  0x00000080
#define MENVCFG_ADUE  0x2000000000000000
#define MENVCFG_PBMTE 0x4000000000000000
#define MENVCFG_STCE  0x8000000000000000

#define MENVCFGH_ADUE  0x20000000
#define MENVCFGH_PBMTE 0x40000000
#define MENVCFGH_STCE  0x80000000

#define MSTATEEN0_CS       0x00000001
#define MSTATEEN0_FCSR     0x00000002
#define MSTATEEN0_JVT      0x00000004
#define MSTATEEN0_HCONTEXT 0x0200000000000000
#define MSTATEEN0_CD       0x0100000000000000
#define MSTATEEN0_HENVCFG  0x4000000000000000
#define MSTATEEN_HSTATEEN  0x8000000000000000

#define MSTATEEN0H_HCONTEXT 0x02000000
#define MSTATEEN0H_HENVCFG  0x40000000
#define MSTATEENH_HSTATEEN  0x80000000

#define MHPMEVENT_VUINH 0x0400000000000000
#define MHPMEVENT_VSINH 0x0800000000000000
#define MHPMEVENT_UINH  0x1000000000000000
#define MHPMEVENT_SINH  0x2000000000000000
#define MHPMEVENT_MINH  0x4000000000000000
#define MHPMEVENT_OF    0x8000000000000000

#define MHPMEVENTH_VUINH 0x04000000
#define MHPMEVENTH_VSINH 0x08000000
#define MHPMEVENTH_UINH  0x10000000
#define MHPMEVENTH_SINH  0x20000000
#define MHPMEVENTH_MINH  0x40000000
#define MHPMEVENTH_OF    0x80000000

#define HENVCFG_FIOM  0x00000001
#define HENVCFG_LPE   0x00000004
#define HENVCFG_SSE   0x00000008
#define HENVCFG_CBIE  0x00000030
#define HENVCFG_CBCFE 0x00000040
#define HENVCFG_CBZE  0x00000080
#define HENVCFG_ADUE  0x2000000000000000
#define HENVCFG_PBMTE 0x4000000000000000
#define HENVCFG_STCE  0x8000000000000000

#define HENVCFGH_ADUE  0x20000000
#define HENVCFGH_PBMTE 0x40000000
#define HENVCFGH_STCE  0x80000000

#define SISELECT_SMCDELEG_START       0x40
#define SISELECT_SMCDELEG_UNUSED      0x41
#define SISELECT_SMCDELEG_INSTRET     0x42
#define SISELECT_SMCDELEG_INSTRETCFG  0x42
/*
 * ?iselect values for hpmcounters4..31 and hpmevent4..31
 * can easily computed, and were elided for brevity.
 */
#define SISELECT_SMCDELEG_HPMCOUNTER_3  0x43
#define SISELECT_SMCDELEG_HPMEVENT_3    0x43
#define SISELECT_SMCDELEG_END           0x5f

#define HSTATEEN0_CS       0x00000001
#define HSTATEEN0_FCSR     0x00000002
#define HSTATEEN0_JVT      0x00000004
#define HSTATEEN0_SCONTEXT 0x0200000000000000
#define HSTATEEN0_SENVCFG  0x4000000000000000
#define HSTATEEN_SSTATEEN  0x8000000000000000

#define HSTATEEN0H_SCONTEXT 0x02000000
#define HSTATEEN0H_SENVCFG  0x40000000
#define HSTATEENH_SSTATEEN  0x80000000

#define SENVCFG_FIOM  0x00000001
#define SENVCFG_LPE   0x00000004
#define SENVCFG_SSE   0x00000008
#define SENVCFG_CBIE  0x00000030
#define SENVCFG_CBCFE 0x00000040
#define SENVCFG_CBZE  0x00000080

#define SSTATEEN0_CS   0x00000001
#define SSTATEEN0_FCSR 0x00000002
#define SSTATEEN0_JVT  0x00000004

#define MSECCFG_MML    0x00000001
#define MSECCFG_MMWP   0x00000002
#define MSECCFG_RLB    0x00000004
#define MSECCFG_USEED  0x00000100
#define MSECCFG_SSEED  0x00000200
#define MSECCFG_MLPE   0x00000400

/* jvt fields */
#define JVT_MODE   0x3F
#define JVT_BASE   (~0x3F)

#define PRV_U 0
#define PRV_S 1
#define PRV_M 3

#define PRV_HS (PRV_S + 1)

#define SATP32_MODE 0x80000000
#define SATP32_ASID 0x7FC00000
#define SATP32_PPN  0x003FFFFF
#define SATP64_MODE 0xF000000000000000
#define SATP64_ASID 0x0FFFF00000000000
#define SATP64_PPN  0x00000FFFFFFFFFFF

#define SATP_MODE_OFF  0
#define SATP_MODE_SV32 1
#define SATP_MODE_SV39 8
#define SATP_MODE_SV48 9
#define SATP_MODE_SV57 10
#define SATP_MODE_SV64 11

#define HGATP32_MODE 0x80000000
#define HGATP32_VMID 0x1FC00000
#define HGATP32_PPN 0x003FFFFF

#define HGATP64_MODE 0xF000000000000000
#define HGATP64_VMID 0x03FFF00000000000
#define HGATP64_PPN 0x00000FFFFFFFFFFF

#define HGATP_MODE_OFF 0
#define HGATP_MODE_SV32X4 1
#define HGATP_MODE_SV39X4 8
#define HGATP_MODE_SV48X4 9
#define HGATP_MODE_SV57X4 10

#define PMP_R     0x01
#define PMP_W     0x02
#define PMP_X     0x04
#define PMP_A     0x18
#define PMP_L     0x80
#define PMP_SHIFT 2

#define PMP_TOR   0x08
#define PMP_NA4   0x10
#define PMP_NAPOT 0x18

#define IRQ_U_SOFT   0
#define IRQ_S_SOFT   1
#define IRQ_VS_SOFT  2
#define IRQ_M_SOFT   3
#define IRQ_U_TIMER  4
#define IRQ_S_TIMER  5
#define IRQ_VS_TIMER 6
#define IRQ_M_TIMER  7
#define IRQ_U_EXT    8
#define IRQ_S_EXT    9
#define IRQ_VS_EXT   10
#define IRQ_M_EXT    11
#define IRQ_S_GEXT   12
#define IRQ_COP      12
#define IRQ_LCOF     13

/* page table entry (PTE) fields */
#define PTE_V     0x001 /* Valid */
#define PTE_R     0x002 /* Read */
#define PTE_W     0x004 /* Write */
#define PTE_X     0x008 /* Execute */
#define PTE_U     0x010 /* User */
#define PTE_G     0x020 /* Global */
#define PTE_A     0x040 /* Accessed */
#define PTE_D     0x080 /* Dirty */
#define PTE_SOFT  0x300 /* Reserved for Software */
#define PTE_RSVD  0x1FC0000000000000 /* Reserved for future standard use */
#define PTE_PBMT  0x6000000000000000 /* Svpbmt: Page-based memory types */
#define PTE_N     0x8000000000000000 /* Svnapot: NAPOT translation contiguity */
#define PTE_ATTR  0xFFC0000000000000 /* All attributes and reserved bits */

#define PTE_PPN_SHIFT 10

#define PTE_TABLE(PTE) (((PTE) & (PTE_V | PTE_R | PTE_W | PTE_X)) == PTE_V)

#ifdef __riscv

#if __riscv_xlen == 64
# define MSTATUS_SD MSTATUS64_SD
# define SSTATUS_SD SSTATUS64_SD
# define RISCV_PGLEVEL_BITS 9
# define SATP_MODE SATP64_MODE
#else
# define MSTATUS_SD MSTATUS32_SD
# define SSTATUS_SD SSTATUS32_SD
# define RISCV_PGLEVEL_BITS 10
# define SATP_MODE SATP32_MODE
#endif
#define RISCV_PGSHIFT 12
#define RISCV_PGSIZE (1 << RISCV_PGSHIFT)

#ifndef __ASSEMBLER__

#ifdef __GNUC__

#define read_csr(reg) ({ unsigned long __tmp; \
  asm volatile ("csrr %0, " #reg : "=r"(__tmp)); \
  __tmp; })

#define write_csr(reg, val) ({ \
  asm volatile ("csrw " #reg ", %0" :: "rK"(val)); })

#define swap_csr(reg, val) ({ unsigned long __tmp; \
  asm volatile ("csrrw %0, " #reg ", %1" : "=r"(__tmp) : "rK"(val)); \
  __tmp; })

#define set_csr(reg, bit) ({ unsigned long __tmp; \
  asm volatile ("csrrs %0, " #reg ", %1" : "=r"(__tmp) : "rK"(bit)); \
  __tmp; })

#define clear_csr(reg, bit) ({ unsigned long __tmp; \
  asm volatile ("csrrc %0, " #reg ", %1" : "=r"(__tmp) : "rK"(bit)); \
  __tmp; })

#define rdtime() read_csr(time)
#define rdcycle() read_csr(cycle)
#define rdinstret() read_csr(instret)

#endif

#endif

#endif

#endif
