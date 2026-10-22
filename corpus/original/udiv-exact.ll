define i32 @specimen(i32 %x) {
entry:
  %q = udiv exact i32 %x, 16
  ret i32 %q
}
