#include "irproof/Passes.h"
#include "llvm/ADT/SmallVector.h"
#include "llvm/Analysis/AssumptionCache.h"
#include "llvm/Analysis/DomConditionCache.h"
#include "llvm/Analysis/ValueTracking.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/Dominators.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/Module.h"
#include "llvm/Analysis/InstructionSimplify.h"
#include "llvm/IR/PatternMatch.h"

using namespace llvm;
using namespace llvm::PatternMatch;

namespace {
// Freeze once before a multi-use expansion: an undef operand may take a different
// value at each use. Sharing the frozen value preserves source refinement.
Value *singleValue(IRBuilder<> &B, Value *X, AssumptionCache &AC,
                   DominatorTree &DT, Instruction &At) {
  if (isGuaranteedNotToBeUndefOrPoison(X, &AC, &At, &DT)) return X;
  return B.CreateFreeze(X, "irproof.x");
}

Value *reduce(BinaryOperator &I, AssumptionCache &AC, DominatorTree &DT,
              DomConditionCache &DC) {
  if (!I.getType()->isIntegerTy()) return nullptr; // scalar integers only
  auto *C = dyn_cast<ConstantInt>(I.getOperand(1));
  Value *X = I.getOperand(0);
  if (!C && I.isCommutative()) {
    C = dyn_cast<ConstantInt>(I.getOperand(0));
    X = I.getOperand(1);
  }
  if (!C) return nullptr;
  const APInt &K = C->getValue();
  IRBuilder<> B(&I);
  B.SetCurrentDebugLocation(I.getDebugLoc());
  auto amount = [&](unsigned N) { return ConstantInt::get(I.getType(), N); };

  switch (I.getOpcode()) {
  case Instruction::Add:
  case Instruction::Sub:
  case Instruction::Or:
  case Instruction::Xor:
    if (K.isZero()) return X;
    break;
  case Instruction::And:
    if (K.isAllOnes()) return X;
    break;
  case Instruction::Mul:
    // The sign-bit constant is negative; nsw semantics differ from shl nsw.
    if (K.isPowerOf2() && !K.isNegative()) {
      if (K.isOne()) return X;
      return B.CreateShl(X, amount(K.logBase2()), "irproof.mul",
                         I.hasNoUnsignedWrap(), I.hasNoSignedWrap());
    }
    break;
  case Instruction::UDiv:
    if (K.isPowerOf2()) {
      if (K.isOne()) return X;
      return B.CreateLShr(X, amount(K.logBase2()), "irproof.udiv", I.isExact());
    }
    break;
  case Instruction::URem:
    if (K.isPowerOf2())
      return B.CreateAnd(X, ConstantInt::get(I.getType(), K - 1), "irproof.urem");
    break;
  case Instruction::SDiv:
    if (K.isPowerOf2() && !K.isNegative()) {
      if (K.isOne()) return X;
      unsigned Shift = K.logBase2();
      if (I.isExact())
        return B.CreateAShr(X, amount(Shift), "irproof.sdiv.exact", true);
      // Branch facts constrain stable values. Do not infer a sign from one use
      // of an undef operand and silently reuse it for a different choice.
      bool Defined = isGuaranteedNotToBeUndefOrPoison(X, &AC, &I, &DT);
      if (isKnownNonNegative(X, SimplifyQuery(I.getModule()->getDataLayout(),
                                            nullptr, &DT, &AC, &I, true, false,
                                            Defined ? &DC : nullptr)))
        return B.CreateLShr(X, amount(Shift), "irproof.sdiv.nonneg");
      X = singleValue(B, X, AC, DT, I);
      auto *Sign = B.CreateAShr(X, amount(K.getBitWidth() - 1), "irproof.sign");
      auto *Bias = B.CreateAnd(Sign, ConstantInt::get(I.getType(), K - 1), "irproof.bias");
      // No flags here: only transfer flags when their semantics match exactly.
      auto *Adjusted = B.CreateAdd(X, Bias, "irproof.adjusted");
      return B.CreateAShr(Adjusted, amount(Shift), "irproof.sdiv");
    }
    break;
  default: break;
  }
  return nullptr;
}
} // namespace

PreservedAnalyses irproof::StrengthReductionPass::run(Function &F,
                                                     FunctionAnalysisManager &AM) {
  auto &DT = AM.getResult<DominatorTreeAnalysis>(F);
  auto &AC = AM.getResult<AssumptionAnalysis>(F);
  DomConditionCache DC;
  for (BasicBlock &BB : F)
    if (auto *Br = dyn_cast<CondBrInst>(BB.getTerminator())) DC.registerBranch(Br);
  // Snapshot the original instructions. Inserted instructions are not revisited.
  SmallVector<BinaryOperator *, 32> Worklist;
  for (Instruction &I : instructions(F))
    if (auto *BO = dyn_cast<BinaryOperator>(&I)) Worklist.push_back(BO);
  bool Changed = false;
  for (auto *I : Worklist) {
    if (Value *V = reduce(*I, AC, DT, DC)) {
      I->replaceAllUsesWith(V);
      DC.removeValue(I);
      I->eraseFromParent();
      Changed = true;
    }
  }
  if (!Changed) return PreservedAnalyses::all();
  PreservedAnalyses PA;
  PA.preserveSet<CFGAnalyses>(); // Edges and blocks are never changed.
  return PA;
}
