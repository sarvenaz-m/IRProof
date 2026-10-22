define i8 @src(i8 %x) {
entry:
  %p = mul i8 %x, 8
  ret i8 %p
}

define i8 @tgt(i8 %x) {
entry:
  %p = shl nsw i8 %x, 3
  ret i8 %p
}
