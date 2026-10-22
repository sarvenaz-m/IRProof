; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/introduced-overflow.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/introduced-overflow.ll"

define i8 @specimen(i8 %x) {
entry:
  %p = mul i8 %x, 8
  ret i8 %p
}
