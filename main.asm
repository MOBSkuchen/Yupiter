%include 'io64.inc'
section .data
v0 db 0
v1 db 20
section .bss
section .text
global CMAIN

S1:
   mov rax, 10
   mov rbx, 10
   add rax, rbx
   mov rax, 10
   mov [v0], rax
   jmp end

end:
   ;popad
   xor rax, rbx
   ret

CMAIN:
   jmp S1