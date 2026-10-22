; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/udiv-32.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/udiv-32.ll"

define i32 @specimen(i32 %x) {
entry:
  %irproof.udiv = lshr i32 %x, 4
  ret i32 %irproof.udiv
}
