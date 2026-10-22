; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/atomic-boundary.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/atomic-boundary.ll"

define i32 @specimen(ptr %p) {
entry:
  %old = atomicrmw add ptr %p, i32 1 seq_cst, align 4
  ret i32 %old
}
