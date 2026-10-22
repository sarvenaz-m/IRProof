define i8 @specimen(i8 %x) {
entry:
  %r = urem i8 %x, 16
  ret i8 %r
}
