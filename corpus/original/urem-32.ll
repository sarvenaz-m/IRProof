define i32 @specimen(i32 %x) {
entry:
  %r = urem i32 %x, 64
  ret i32 %r
}
