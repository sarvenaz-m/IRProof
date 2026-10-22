define i32 @src(i32 %x) {
entry:
  %q = udiv i32 %x, 8
  ret i32 %q
}

define i32 @tgt(i32 %x) {
entry:
  %q = lshr exact i32 %x, 3
  ret i32 %q
}
