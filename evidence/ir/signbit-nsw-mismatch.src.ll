; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signbit-nsw-mismatch.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signbit-nsw-mismatch.ll"

define i8 @specimen(i8 %x) {
entry:
  %p = mul nsw i8 %x, -128
  ret i8 %p
}
