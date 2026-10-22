; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-8-2.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-8-2.ll"

define i8 @specimen(i8 %x) {
entry:
  %irproof.x = freeze i8 %x
  %irproof.sign = ashr i8 %irproof.x, 7
  %irproof.bias = and i8 %irproof.sign, 1
  %irproof.adjusted = add i8 %irproof.x, %irproof.bias
  %irproof.sdiv = ashr i8 %irproof.adjusted, 1
  ret i8 %irproof.sdiv
}
