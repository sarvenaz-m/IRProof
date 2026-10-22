define i8 @src(i8 %x) {
entry:
  %r = srem i8 %x, 8
  ret i8 %r
}

define i8 @tgt(i8 %x) {
entry:
  %r = and i8 %x, 7
  ret i8 %r
}
