; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/urem-8.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/urem-8.ll"

define i8 @specimen(i8 %x) {
entry:
  %irproof.urem = and i8 %x, 15
  ret i8 %irproof.urem
}
