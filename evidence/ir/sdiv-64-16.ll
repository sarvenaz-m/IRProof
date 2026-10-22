; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-64-16.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-64-16.ll"

define i64 @specimen(i64 %x) {
entry:
  %irproof.x = freeze i64 %x
  %irproof.sign = ashr i64 %irproof.x, 63
  %irproof.bias = and i64 %irproof.sign, 15
  %irproof.adjusted = add i64 %irproof.x, %irproof.bias
  %irproof.sdiv = ashr i64 %irproof.adjusted, 4
  ret i64 %irproof.sdiv
}
