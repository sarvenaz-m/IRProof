define i32 @specimen(i32 %x) {
entry:
  %p = mul nuw nsw i32 %x, 8
  ret i32 %p
}
