; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/undef-reuse.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/undef-reuse.ll"

define i8 @specimen(i8 %x) {
entry:
  %p = mul i8 %x, 2
  ret i8 %p
}
