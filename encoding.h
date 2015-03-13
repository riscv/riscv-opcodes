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
#define VM_SV43  5

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
#define PTE_V    0x001 // Entry is a page Table descriptor
#define PTE_T    0x002 // Entry is a page Table, not a terminal node
#define PTE_G    0x004 // Global
#define PTE_UR   0x008 // User Write permission
#define PTE_UW   0x010 // User Read permission
#define PTE_UX   0x020 // User eXecute permission
#define PTE_SR   0x040 // Supervisor Read permission
#define PTE_SW   0x080 // Supervisor Write permission
#define PTE_SX   0x100 // Supervisor eXecute permission
#define PTE_R    0x200 // Referenced
#define PTE_D    0x400 // Dirty
#define PTE_PERM (PTE_SR | PTE_SW | PTE_SX | PTE_UR | PTE_UW | PTE_UX)

#ifdef __riscv

#ifdef __riscv64
# define MSTATUS_UA MSTATUS64_UA
# define MSTATUS_SA MSTATUS64_SA
# define MSTATUS_HA MSTATUS64_HA
# define MSTATUS_SD MSTATUS64_SD
# define SSTATUS_SD SSTATUS64_SD
# define RISCV_PGLEVELS 3
# define RISCV_PGSHIFT 13
#else
# define MSTATUS_SD MSTATUS32_SD
# define SSTATUS_SD SSTATUS32_SD
# define RISCV_PGLEVELS 2
# define RISCV_PGSHIFT 12
#endif
#define RISCV_PGLEVEL_BITS 10
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
