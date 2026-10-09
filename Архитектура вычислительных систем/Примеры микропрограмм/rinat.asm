.radix 16
.model tiny
.stack 100
dat segment
flags db 00
dat ends
cod segment
assume cs:cod, ds:dat, es:dat
 strt:
      mov ax,dat
      mov ds,ax
      mov es,ax
      mov bx,offset flags
 fon: test[bx],01h
      jnz proc0 
 f1:  test[bx],02h 
      jnz proc1
 f2:  test[bx],04h
      jnz proc2
 f3:  test[bx],08h
      jnz proc3 
      jmp fon   
 proc0: and[bx],0feh
        jmp f1
 proc1: and[bx],0fdh
        jmp f2
 proc2: and[bx],0fbh
        jmp f3
 proc3: and[bx],0f7h
        jmp fon 
 cod ends
end strt 