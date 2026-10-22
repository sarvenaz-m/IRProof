define i32 @specimen(i32 %x) {
entry:
  %positive = and i32 %x, 2147483647
  %q = sdiv i32 %positive, 8
  ret i32 %q
}
