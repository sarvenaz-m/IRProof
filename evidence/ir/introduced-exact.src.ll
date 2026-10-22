; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/introduced-exact.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/introduced-exact.ll"

define i32 @specimen(i32 %x) {
entry:
  %q = udiv i32 %x, 8
  ret i32 %q
}
