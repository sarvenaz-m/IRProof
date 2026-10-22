; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-minus-three.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-minus-three.ll"

define i32 @specimen() {
entry:
  %q = ashr i32 -3, 1
  ret i32 %q
}
