; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/urem-32.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/urem-32.ll"

define i32 @specimen(i32 %x) {
entry:
  %irproof.urem = and i32 %x, 63
  ret i32 %irproof.urem
}
