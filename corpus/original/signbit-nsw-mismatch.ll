define i8 @src(i8 %x) {
entry:
  %p = mul nsw i8 %x, -128
  ret i8 %p
}

define i8 @tgt(i8 %x) {
entry:
  %p = shl nsw i8 %x, 7
  ret i8 %p
}
