; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-minus-three.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-minus-three.ll"

define i32 @specimen() {
entry:
  %q = sdiv i32 -3, 2
  ret i32 %q
}
