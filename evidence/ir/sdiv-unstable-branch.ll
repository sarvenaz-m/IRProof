; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-unstable-branch.ll'
source_filename = "irproof.diamond"

define i32 @specimen(i32 %x) {
entry:
  %nonneg = icmp sge i32 %x, 0
  br i1 %nonneg, label %nonnegative, label %negative

nonnegative:                                      ; preds = %entry
  %irproof.x = freeze i32 %x
  %irproof.sign = ashr i32 %irproof.x, 31
  %irproof.bias = and i32 %irproof.sign, 7
  %irproof.adjusted = add i32 %irproof.x, %irproof.bias
  %irproof.sdiv = ashr i32 %irproof.adjusted, 3
  br label %merge

negative:                                         ; preds = %entry
  %irproof.x1 = freeze i32 %x
  %irproof.sign2 = ashr i32 %irproof.x1, 31
  %irproof.bias3 = and i32 %irproof.sign2, 7
  %irproof.adjusted4 = add i32 %irproof.x1, %irproof.bias3
  %irproof.sdiv5 = ashr i32 %irproof.adjusted4, 3
  br label %merge

merge:                                            ; preds = %negative, %nonnegative
  %quotient = phi i32 [ %irproof.sdiv, %nonnegative ], [ %irproof.sdiv5, %negative ]
  ret i32 %quotient
}
