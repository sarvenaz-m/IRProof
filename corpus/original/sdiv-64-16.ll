define i64 @specimen(i64 %x) {
entry:
  %q = sdiv i64 %x, 16
  ret i64 %q
}
