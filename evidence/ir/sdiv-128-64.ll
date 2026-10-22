; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-128-64.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-128-64.ll"

define i128 @specimen(i128 %x) {
entry:
  %irproof.x = freeze i128 %x
  %irproof.sign = ashr i128 %irproof.x, 127
  %irproof.bias = and i128 %irproof.sign, 63
  %irproof.adjusted = add i128 %irproof.x, %irproof.bias
  %irproof.sdiv = ashr i128 %irproof.adjusted, 6
  ret i128 %irproof.sdiv
}
