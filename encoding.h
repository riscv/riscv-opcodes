// See LICENSE for license details.

#ifndef RISCV_CSR_ENCODING_H
#define RISCV_CSR_ENCODING_H

#define SR_S     0x00000001
#define SR_PS    0x00000002
#define SR_EI    0x00000004
#define SR_PEI   0x00000008
#define SR_EF    0x00000010
#define SR_U64   0x00000020
#define SR_S64   0x00000040
#define SR_VM    0x00000080
#define SR_EA    0x00000100
#define SR_IM    0x00FF0000
#define SR_IP    0xFF000000
#define SR_ZERO  ~(SR_S|SR_PS|SR_EI|SR_PEI|SR_EF|SR_U64|SR_S64|SR_VM|SR_EA|SR_IM|SR_IP)
#define SR_IM_SHIFT 16
#define SR_IP_SHIFT 24

#define IRQ_COP   2
#define IRQ_IPI   5
#define IRQ_HOST  6
#define IRQ_TIMER 7

#define IMPL_SPIKE  1
#define IMPL_ROCKET 2

#define CAUSE_MISALIGNED_FETCH 0
#define CAUSE_FAULT_FETCH 1
#define CAUSE_ILLEGAL_INSTRUCTION 2
#define CAUSE_PRIVILEGED_INSTRUCTION 3
#define CAUSE_FP_DISABLED 4
#define CAUSE_SYSCALL 6
#define CAUSE_BREAKPOINT 7
#define CAUSE_MISALIGNED_LOAD 8
#define CAUSE_MISALIGNED_STORE 9
#define CAUSE_FAULT_LOAD 10
#define CAUSE_FAULT_STORE 11
#define CAUSE_ACCELERATOR_DISABLED 12

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
#define PTE_PERM (PTE_SR | PTE_SW | PTE_SX | PTE_UR | PTE_UW | PTE_UX)

#ifdef __riscv

#ifdef __riscv64
# define RISCV_PGLEVELS 3
# define RISCV_PGSHIFT 13
#else
# define RISCV_PGLEVELS 2
# define RISCV_PGSHIFT 12
#endif
#define RISCV_PGLEVEL_BITS 10
#define RISCV_PGSIZE (1 << RISCV_PGSHIFT)

#ifndef __ASSEMBLER__

#define read_csr(reg) ({ long __tmp; \
  asm volatile ("csrr %0, " #reg : "=r"(__tmp)); \
  __tmp; })

#define write_csr(reg, val) \
  asm volatile ("csrw " #reg ", %0" :: "r"(val))

#define swap_csr(reg, val) ({ long __tmp; \
  asm volatile ("csrrw %0, " #reg ", %1" : "=r"(__tmp) : "r"(val)); \
  __tmp; })

#define set_csr(reg, bit) ({ long __tmp; \
  if (__builtin_constant_p(bit) && (bit) < 32) \
    asm volatile ("csrrs %0, " #reg ", %1" : "=r"(__tmp) : "i"(bit)); \
  else \
    asm volatile ("csrrs %0, " #reg ", %1" : "=r"(__tmp) : "r"(bit)); \
  __tmp; })

#define clear_csr(reg, bit) ({ long __tmp; \
  if (__builtin_constant_p(bit) && (bit) < 32) \
    asm volatile ("csrrc %0, " #reg ", %1" : "=r"(__tmp) : "i"(bit)); \
  else \
    asm volatile ("csrrc %0, " #reg ", %1" : "=r"(__tmp) : "r"(bit)); \
  __tmp; })

#define rdcycle() ({ unsigned long __tmp; \
  asm volatile ("rdcycle %0" : "=r"(__tmp)); \
  __tmp; })

#endif

#endif

#endif
