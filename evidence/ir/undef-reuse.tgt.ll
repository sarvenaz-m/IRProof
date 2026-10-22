; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/undef-reuse.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/undef-reuse.ll"

define i8 @specimen(i8 %x) {
entry:
  %p = add i8 %x, %x
  ret i8 %p
}
