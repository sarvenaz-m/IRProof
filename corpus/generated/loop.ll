; ModuleID = 'irproof.loop'
source_filename = "irproof.loop"

define i32 @specimen(i32 noundef %x) {
entry:
  br label %loop.header

loop.header:                                      ; preds = %loop.body, %entry
  %i = phi i32 [ 0, %entry ], [ %next.i, %loop.body ]
  %sum = phi i32 [ 0, %entry ], [ %next.sum, %loop.body ]
  %continue = icmp ult i32 %i, %x
  br i1 %continue, label %loop.body, label %exit

loop.body:                                        ; preds = %loop.header
  %term = udiv i32 %i, 8
  %next.sum = add i32 %sum, %term
  %next.i = add i32 %i, 1
  br label %loop.header

exit:                                             ; preds = %loop.header
  ret i32 %sum
}
