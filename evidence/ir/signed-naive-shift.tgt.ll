; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-naive-shift.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-naive-shift.ll"

define i32 @specimen(i32 %x) {
entry:
  %q = ashr i32 %x, 1
  ret i32 %q
}
