; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/generated/divide.ll'
source_filename = "irproof.divide"

define i32 @specimen(i32 noundef %x) {
entry:
  %irproof.sign = ashr i32 %x, 31
  %irproof.bias = and i32 %irproof.sign, 7
  %irproof.adjusted = add i32 %x, %irproof.bias
  %irproof.sdiv = ashr i32 %irproof.adjusted, 3
  ret i32 %irproof.sdiv
}
