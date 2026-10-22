define i64 @specimen(i64 %x) {
entry:
  %q = udiv i64 %x, 9223372036854775808
  ret i64 %q
}
