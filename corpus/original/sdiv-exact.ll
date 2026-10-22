define i32 @specimen(i32 %x) {
entry:
  %q = sdiv exact i32 %x, 4
  ret i32 %q
}
