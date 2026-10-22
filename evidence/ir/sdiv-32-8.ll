; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-32-8.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-32-8.ll"

define i32 @specimen(i32 %x) {
entry:
  %irproof.x = freeze i32 %x
  %irproof.sign = ashr i32 %irproof.x, 31
  %irproof.bias = and i32 %irproof.sign, 7
  %irproof.adjusted = add i32 %irproof.x, %irproof.bias
  %irproof.sdiv = ashr i32 %irproof.adjusted, 3
  ret i32 %irproof.sdiv
}
