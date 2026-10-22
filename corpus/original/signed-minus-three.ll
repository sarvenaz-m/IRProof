define i32 @src() {
entry:
  %q = sdiv i32 -3, 2
  ret i32 %q
}

define i32 @tgt() {
entry:
  %q = ashr i32 -3, 1
  ret i32 %q
}
