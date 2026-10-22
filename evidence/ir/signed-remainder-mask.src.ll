; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-remainder-mask.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/signed-remainder-mask.ll"

define i8 @specimen(i8 %x) {
entry:
  %r = srem i8 %x, 8
  ret i8 %r
}
