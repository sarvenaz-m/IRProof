define i32 @specimen(i32 %x) {
entry:
  %a = add nsw i32 %x, 0
  %b = and i32 %a, -1
  %c = xor i32 %b, 0
  ret i32 %c
}
