; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-exact.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/sdiv-exact.ll"

define i32 @specimen(i32 %x) {
entry:
  %irproof.sdiv.exact = ashr exact i32 %x, 2
  ret i32 %irproof.sdiv.exact
}
