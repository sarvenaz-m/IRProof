; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-16-4.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-16-4.ll"

define i16 @specimen(i16 %x) {
entry:
  %irproof.x = freeze i16 %x
  %irproof.sign = ashr i16 %irproof.x, 15
  %irproof.bias = and i16 %irproof.sign, 3
  %irproof.adjusted = add i16 %irproof.x, %irproof.bias
  %irproof.sdiv = ashr i16 %irproof.adjusted, 2
  ret i16 %irproof.sdiv
}
