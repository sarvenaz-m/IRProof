; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-naive-shift.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-naive-shift.ll"

define i32 @specimen(i32 %x) {
entry:
  %q = sdiv i32 %x, 2
  ret i32 %q
}
