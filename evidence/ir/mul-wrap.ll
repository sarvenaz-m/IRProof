; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/mul-wrap.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/mul-wrap.ll"

define i32 @specimen(i32 %x) {
entry:
  %irproof.mul = shl i32 %x, 3
  ret i32 %irproof.mul
}
