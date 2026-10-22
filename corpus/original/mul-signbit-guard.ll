define i8 @specimen(i8 %x) {
entry:
  %p = mul nsw i8 %x, -128
  ret i8 %p
}
