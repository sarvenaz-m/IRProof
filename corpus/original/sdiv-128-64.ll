define i128 @specimen(i128 %x) {
entry:
  %q = sdiv i128 %x, 64
  ret i128 %q
}
