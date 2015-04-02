// See LICENSE for license details.

#ifndef RISCV_CSR_ENCODING_H
#define RISCV_CSR_ENCODING_H

#define MSTATUS_SSIP        0x00000002
#define MSTATUS_HSIP        0x00000004
#define MSTATUS_MSIP        0x00000008
#define MSTATUS_IE          0x00000010
#define MSTATUS_PRV         0x00000060
#define MSTATUS_IE1         0x00000080
#define MSTATUS_PRV1        0x00000300
#define MSTATUS_IE2         0x00000400
#define MSTATUS_PRV2        0x00001800
#define MSTATUS_IE3         0x00002000
#define MSTATUS_PRV3        0x0000C000
#define MSTATUS_MPRV        0x00030000
#define MSTATUS_VM          0x00780000
#define MSTATUS_STIE        0x01000000
#define MSTATUS_HTIE        0x02000000
#define MSTATUS_MTIE        0x04000000
#define MSTATUS_FS          0x18000000
#define MSTATUS_XS          0x60000000
#define MSTATUS32_SD        0x80000000
#define MSTATUS64_UA        0x0000000F00000000
#define MSTATUS64_SA        0x000000F000000000
#define MSTATUS64_HA        0x00000F0000000000
#define MSTATUS64_SD        0x8000000000000000

#define SSTATUS_SIP         0x00000002
#define SSTATUS_IE          0x00000010
#define SSTATUS_PIE         0x00000080
#define SSTATUS_PS          0x00000100
#define SSTATUS_UA          0x000F0000
#define SSTATUS_TIE         0x01000000
#define SSTATUS_TIP         0x04000000
#define SSTATUS_FS          0x18000000
#define SSTATUS_XS          0x60000000
#define SSTATUS32_SD        0x80000000
#define SSTATUS64_SD        0x8000000000000000

#define PRV_U 0
#define PRV_S 1
#define PRV_H 2
#define PRV_M 3

#define VM_MBARE 0
#define VM_MBB   1
#define VM_MBBID 2
#define VM_SV32  4
#define VM_SV39  5
#define VM_SV48  6

#define UA_RV32  0
#define UA_RV64  4
#define UA_RV128 8

#define IRQ_TIMER  0
#define IRQ_IPI    1
#define IRQ_HOST   2
#define IRQ_COP    3

#define IMPL_SPIKE  1
#define IMPL_ROCKET 2

// page table entry (PTE) fields
#define PTE_TYPE   0x007
#define PTE_PERM   0x018
#define PTE_G      0x020 // Global
#define PTE_R      0x040 // Referenced
#define PTE_D      0x080 // Dirty
#define PTE_SOFT   0x300 // Reserved for Software
#define RV64_PTE_PPN_SHIFT 26
#define RV32_PTE_PPN_SHIFT 10
#define PTE_TYPE_INVALID 0
#define PTE_TYPE_TABLE   1
#define PTE_TYPE_U       2
#define PTE_TYPE_S       3
#define PTE_TYPE_US      4
#define PTE_TYPE_US_SR   4
#define PTE_TYPE_US_SRW  5
#define PTE_TYPE_US_SRX  6
#define PTE_TYPE_US_SRWX 7

#define PROT_TO_PERM(PROT) ((((PROT) & PROT_EXEC) ? 2 : 0) | (((PROT) & PROT_WRITE) ? 1 : 0))
#define PTE_CREATE(PPN, PERM_U, PERM_S) \
  (((PPN) << PTE_PPN_SHIFT) | (PROT_TO_PERM(PERM_U) << 3) | \
   ((PERM_U) && (PERM_S) ? (PTE_TYPE_US | PROT_TO_PERM(PERM_S)) : \
   (PERM_S) ? (PTE_TYPE_S | (PROT_TO_PERM(PERM_S) << 3)) : \
   (PERM_U) ? PTE_TYPE_U : 0))

#define PTE_UR(PTE) ((0xF4F4F4F4U >> ((PTE) & 0x1f)) & 1)
#define PTE_UW(PTE) ((0xF400F400U >> ((PTE) & 0x1f)) & 1)
#define PTE_UX(PTE) ((0xF4F40000U >> ((PTE) & 0x1f)) & 1)
#define PTE_SR(PTE) ((0xF8F8F8F8U >> ((PTE) & 0x1f)) & 1)
#define PTE_SW(PTE) ((0xA8A0A8A0U >> ((PTE) & 0x1f)) & 1)
#define PTE_SX(PTE) ((0xC8C8C0C0U >> ((PTE) & 0x1f)) & 1)
#define PTE_CHECK_PERM(PTE, SUPERVISOR, WRITE, EXEC) \
  ((SUPERVISOR) ? ((WRITE) ? PTE_SW(PTE) : (EXEC) ? PTE_SX(PTE) : PTE_SR(PTE)) \
                : ((WRITE) ? PTE_UW(PTE) : (EXEC) ? PTE_UX(PTE) : PTE_UR(PTE)))

#ifdef __riscv

#ifdef __riscv64
# define MSTATUS_UA MSTATUS64_UA
# define MSTATUS_SA MSTATUS64_SA
# define MSTATUS_HA MSTATUS64_HA
# define MSTATUS_SD MSTATUS64_SD
# define SSTATUS_SD SSTATUS64_SD
# define RISCV_PGLEVEL_BITS 9
# define PTE_PPN_SHIFT RV64_PTE_PPN_SHIFT
#else
# define MSTATUS_SD MSTATUS32_SD
# define SSTATUS_SD SSTATUS32_SD
# define RISCV_PGLEVEL_BITS 10
# define PTE_PPN_SHIFT RV32_PTE_PPN_SHIFT
#endif
#define RISCV_PGSHIFT 12
#define RISCV_PGSIZE (1 << RISCV_PGSHIFT)

#ifndef __ASSEMBLER__

#ifdef __GNUC__

#define read_csr(reg) ({ unsigned long __tmp; \
  asm volatile ("csrr %0, " #reg : "=r"(__tmp)); \
  __tmp; })

#define write_csr(reg, val) \
  asm volatile ("csrw " #reg ", %0" :: "r"(val))

#define swap_csr(reg, val) ({ long __tmp; \
  asm volatile ("csrrw %0, " #reg ", %1" : "=r"(__tmp) : "r"(val)); \
  __tmp; })

#define set_csr(reg, bit) ({ unsigned long __tmp; \
  if (__builtin_constant_p(bit) && (bit) < 32) \
    asm volatile ("csrrs %0, " #reg ", %1" : "=r"(__tmp) : "i"(bit)); \
  else \
    asm volatile ("csrrs %0, " #reg ", %1" : "=r"(__tmp) : "r"(bit)); \
  __tmp; })

#define clear_csr(reg, bit) ({ unsigned long __tmp; \
  if (__builtin_constant_p(bit) && (bit) < 32) \
    asm volatile ("csrrc %0, " #reg ", %1" : "=r"(__tmp) : "i"(bit)); \
  else \
    asm volatile ("csrrc %0, " #reg ", %1" : "=r"(__tmp) : "r"(bit)); \
  __tmp; })

#define rdtime() read_csr(time)
#define rdcycle() read_csr(cycle)
#define rdinstret() read_csr(instret)

#endif

#endif

#endif

#endif
