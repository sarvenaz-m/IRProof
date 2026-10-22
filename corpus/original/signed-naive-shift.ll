define i32 @src(i32 %x) {
entry:
  %q = sdiv i32 %x, 2
  ret i32 %q
}

define i32 @tgt(i32 %x) {
entry:
  %q = ashr i32 %x, 1
  ret i32 %q
}
