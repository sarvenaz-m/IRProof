; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/upstream/upstream-freeze-undef.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/upstream/upstream-freeze-undef.ll"

define i32 @specimen() {
  %v = freeze i32 undef
  ret i32 %v
}
