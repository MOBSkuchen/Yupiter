%include 'io64.inc'
section .data
v0 db "100"
section .bss
section .text
global CMAIN

end:
   ;popad
   xor rax, rbx
   ret

CMAIN:
   jmp end
   ret