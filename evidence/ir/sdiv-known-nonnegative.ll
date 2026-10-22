; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-known-nonnegative.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-known-nonnegative.ll"

define i32 @specimen(i32 %x) {
entry:
  %positive = and i32 %x, 2147483647
  %irproof.sdiv.nonneg = lshr i32 %positive, 3
  ret i32 %irproof.sdiv.nonneg
}
