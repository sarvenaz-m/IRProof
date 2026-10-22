; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/mul-nuw.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/original/mul-nuw.ll"

define i32 @specimen(i32 %x) {
entry:
  %irproof.mul = shl nuw i32 %x, 3
  ret i32 %irproof.mul
}
