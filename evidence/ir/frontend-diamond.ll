; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/generated/diamond.ll'
source_filename = "irproof.diamond"

define i32 @specimen(i32 noundef %x) {
entry:
  %nonneg = icmp sge i32 %x, 0
  br i1 %nonneg, label %nonnegative, label %negative

nonnegative:                                      ; preds = %entry
  %irproof.sdiv.nonneg = lshr i32 %x, 3
  br label %merge

negative:                                         ; preds = %entry
  %irproof.sign = ashr i32 %x, 31
  %irproof.bias = and i32 %irproof.sign, 7
  %irproof.adjusted = add i32 %x, %irproof.bias
  %irproof.sdiv = ashr i32 %irproof.adjusted, 3
  br label %merge

merge:                                            ; preds = %negative, %nonnegative
  %quotient = phi i32 [ %irproof.sdiv.nonneg, %nonnegative ], [ %irproof.sdiv, %negative ]
  ret i32 %quotient
}
