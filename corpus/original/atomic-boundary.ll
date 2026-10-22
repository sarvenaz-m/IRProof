define i32 @src(ptr %p) {
entry:
  %old = atomicrmw add ptr %p, i32 1 seq_cst
  ret i32 %old
}

define i32 @tgt(ptr %p) {
entry:
  %old = atomicrmw add ptr %p, i32 1 seq_cst
  ret i32 %old
}
