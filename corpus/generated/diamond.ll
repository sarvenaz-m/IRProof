; ModuleID = 'irproof.diamond'
source_filename = "irproof.diamond"

define i32 @specimen(i32 noundef %x) {
entry:
  %nonneg = icmp sge i32 %x, 0
  br i1 %nonneg, label %nonnegative, label %negative

nonnegative:                                      ; preds = %entry
  %positive.q = sdiv i32 %x, 8
  br label %merge

negative:                                         ; preds = %entry
  %negative.q = sdiv i32 %x, 8
  br label %merge

merge:                                            ; preds = %negative, %nonnegative
  %quotient = phi i32 [ %positive.q, %nonnegative ], [ %negative.q, %negative ]
  ret i32 %quotient
}
