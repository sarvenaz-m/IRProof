#include "irproof/Passes.h"
#include "llvm/ADT/DenseMap.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/IR/CFG.h"
#include "llvm/IR/Dominators.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/FormatVariadic.h"
#include "llvm/Support/JSON.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;
namespace {
std::string operand(const Value &V) {
  std::string S;
  raw_string_ostream OS(S);
  V.printAsOperand(OS, false);
  return S;
}
json::Object inspect(Function &F, FunctionAnalysisManager &AM) {
  auto &DT = AM.getResult<DominatorTreeAnalysis>(F);
  auto &LI = AM.getResult<LoopAnalysis>(F);
  DenseMap<const BasicBlock *, std::string> BlockIDs;
  DenseMap<const Instruction *, std::string> IDs;
  unsigned BN = 0;
  for (auto &BB : F) {
    BlockIDs[&BB] = "b" + std::to_string(BN++);
    unsigned IN = 0;
    for (auto &I : BB) IDs[&I] = BlockIDs[&BB] + ".i" + std::to_string(IN++);
  }
  json::Array Blocks, CFG, Dataflow;
  unsigned Total = 0, SignedDivides = 0, Flagged = 0;
  for (auto &BB : F) {
    json::Array Insts;
    for (auto &I : BB) {
      std::string Text;
      raw_string_ostream OS(Text);
      I.print(OS);
      json::Array Flags;
      if (auto *BO = dyn_cast<BinaryOperator>(&I)) {
        if (BO->hasNoSignedWrap()) Flags.push_back("nsw");
        if (BO->hasNoUnsignedWrap()) Flags.push_back("nuw");
        if (BO->isExact()) Flags.push_back("exact");
        if (!Flags.empty()) ++Flagged;
      }
      if (I.getOpcode() == Instruction::SDiv) ++SignedDivides;
      for (unsigned N = 0; N < I.getNumOperands(); ++N)
        if (auto *Def = dyn_cast<Instruction>(I.getOperand(N)))
          Dataflow.push_back(json::Object{{"from", IDs[Def]}, {"to", IDs[&I]},
                                          {"operand", static_cast<int64_t>(N)}});
      Insts.push_back(json::Object{{"id", IDs[&I]}, {"opcode", I.getOpcodeName()},
                                   {"text", Text}, {"uses", static_cast<int64_t>(I.getNumUses())},
                                   {"flags", std::move(Flags)}});
      ++Total;
    }
    auto *DN = DT.getNode(&BB);
    std::string IDom;
    if (DN && DN->getIDom()) IDom = BlockIDs[DN->getIDom()->getBlock()];
    Blocks.push_back(json::Object{{"id", BlockIDs[&BB]}, {"label", operand(BB)},
                                  {"reachable", DT.isReachableFromEntry(&BB)},
                                  {"loopDepth", static_cast<int64_t>(LI.getLoopDepth(&BB))},
                                  {"immediateDominator", IDom}, {"instructions", std::move(Insts)}});
    unsigned EdgeN = 0;
    for (auto *S : successors(&BB)) {
      std::string Label;
      if (isa<CondBrInst>(BB.getTerminator()))
        Label = EdgeN == 0 ? "true" : "false";
      CFG.push_back(json::Object{{"from", BlockIDs[&BB]}, {"to", BlockIDs[S]},
                                 {"label", Label}, {"backedge", DT.dominates(S, &BB)}});
      ++EdgeN;
    }
  }
  return json::Object{{"name", F.getName().str()}, {"instructions", Total},
                       {"signedDivides", SignedDivides}, {"flaggedInstructions", Flagged},
                       {"blocks", std::move(Blocks)}, {"cfg", std::move(CFG)},
                       {"dataflow", std::move(Dataflow)}};
}
} // namespace

PreservedAnalyses irproof::AuditPass::run(Module &M, ModuleAnalysisManager &AM) {
  auto &FAM = AM.getResult<FunctionAnalysisManagerModuleProxy>(M).getManager();
  json::Array Functions;
  for (auto &F : M) if (!F.isDeclaration()) Functions.push_back(inspect(F, FAM));
  json::Value Report(json::Object{{"schemaVersion", 1}, {"module", M.getModuleIdentifier()},
                                  {"functions", std::move(Functions)}});
  outs() << formatv("{0:2}\n", Report);
  return PreservedAnalyses::all();
}
