; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/introduced-overflow.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/introduced-overflow.ll"

define i8 @specimen(i8 %x) {
entry:
  %p = shl nsw i8 %x, 3
  ret i8 %p
}
