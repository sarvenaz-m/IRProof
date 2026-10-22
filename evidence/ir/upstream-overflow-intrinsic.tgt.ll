; ModuleID = '/workspace/scratch/55cc38c50f2f/IRProof/corpus/upstream/upstream-overflow-intrinsic.ll'
source_filename = "/workspace/scratch/55cc38c50f2f/IRProof/corpus/upstream/upstream-overflow-intrinsic.ll"

define void @specimen(i32 %a, i32 %b) {
  %mul = call { i32, i1 } @llvm.umul.with.overflow.i32(i32 %a, i32 %b)
  ret void
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare { i32, i1 } @llvm.umul.with.overflow.i32(i32, i32) #0

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
