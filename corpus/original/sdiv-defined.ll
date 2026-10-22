define i32 @specimen(i32 noundef %x) {
entry:
  %q = sdiv i32 %x, 8
  ret i32 %q
}
