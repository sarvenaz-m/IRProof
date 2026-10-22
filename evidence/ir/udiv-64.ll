; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/udiv-64.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/udiv-64.ll"

define i64 @specimen(i64 %x) {
entry:
  %irproof.udiv = lshr i64 %x, 63
  ret i64 %irproof.udiv
}
