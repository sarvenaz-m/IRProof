; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/udiv-8.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/udiv-8.ll"

define i8 @specimen(i8 %x) {
entry:
  %irproof.udiv = lshr i8 %x, 3
  ret i8 %irproof.udiv
}
