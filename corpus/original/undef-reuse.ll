define i8 @src(i8 %x) {
entry:
  %p = mul i8 %x, 2
  ret i8 %p
}

define i8 @tgt(i8 %x) {
entry:
  %p = add i8 %x, %x
  ret i8 %p
}
