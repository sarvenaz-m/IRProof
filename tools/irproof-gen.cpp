#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Verifier.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/InitLLVM.h"
#include "llvm/Support/raw_ostream.h"
#include <memory>

using namespace llvm;
static cl::opt<std::string> Output("o", cl::desc("Output IR path"), cl::init("-"));
static cl::opt<std::string> Scenario("scenario", cl::desc("divide, diamond, or loop"), cl::init("diamond"));
static cl::opt<unsigned> Width("width", cl::desc("Integer width (8..128)"), cl::init(32));
static cl::opt<unsigned> Divisor("divisor", cl::desc("Positive power of two"), cl::init(8));

int main(int argc, char **argv) {
  InitLLVM X(argc, argv);
  cl::ParseCommandLineOptions(argc, argv, "IRProof structured IR generator\n");
  if (Width < 8 || Width > 128 || !Divisor || (Divisor & (Divisor - 1)) ||
      (Width < 32 && Divisor >= (1U << (Width - 1)))) {
    errs() << "Use width 8..128 and a positive, representable power-of-two divisor.\n";
    return 2;
  }
  if (Scenario != "divide" && Scenario != "diamond" && Scenario != "loop") {
    errs() << "Unknown scenario. Choose divide, diamond, or loop.\n";
    return 2;
  }
  LLVMContext C;
  Module M("irproof." + Scenario, C);
  IRBuilder<> B(C);
  auto *Ty = IntegerType::get(C, Width);
  auto *F = Function::Create(FunctionType::get(Ty, {Ty}, false),
                              Function::ExternalLinkage, "specimen", M);
  auto *Arg = F->getArg(0);
  Arg->setName("x");
  Arg->addAttr(Attribute::NoUndef);
  auto *Entry = BasicBlock::Create(C, "entry", F);
  B.SetInsertPoint(Entry);
  auto K = [&](uint64_t N) { return ConstantInt::get(Ty, N); };
  if (Scenario == "divide") {
    B.CreateRet(B.CreateSDiv(Arg, K(Divisor), "quotient"));
  } else if (Scenario == "diamond") {
    auto *Positive = BasicBlock::Create(C, "nonnegative", F);
    auto *Negative = BasicBlock::Create(C, "negative", F);
    auto *Merge = BasicBlock::Create(C, "merge", F);
    B.CreateCondBr(B.CreateICmpSGE(Arg, K(0), "nonneg"), Positive, Negative);
    B.SetInsertPoint(Positive);
    auto *P = B.CreateSDiv(Arg, K(Divisor), "positive.q");
    B.CreateBr(Merge);
    B.SetInsertPoint(Negative);
    auto *N = B.CreateSDiv(Arg, K(Divisor), "negative.q");
    B.CreateBr(Merge);
    B.SetInsertPoint(Merge);
    auto *Phi = B.CreatePHI(Ty, 2, "quotient");
    Phi->addIncoming(P, Positive);
    Phi->addIncoming(N, Negative);
    B.CreateRet(Phi);
  } else {
    auto *Header = BasicBlock::Create(C, "loop.header", F);
    auto *Body = BasicBlock::Create(C, "loop.body", F);
    auto *Exit = BasicBlock::Create(C, "exit", F);
    B.CreateBr(Header);
    B.SetInsertPoint(Header);
    auto *Index = B.CreatePHI(Ty, 2, "i");
    auto *Acc = B.CreatePHI(Ty, 2, "sum");
    Index->addIncoming(K(0), Entry);
    Acc->addIncoming(K(0), Entry);
    B.CreateCondBr(B.CreateICmpULT(Index, Arg, "continue"), Body, Exit);
    B.SetInsertPoint(Body);
    auto *Term = B.CreateUDiv(Index, K(Divisor), "term");
    auto *NextAcc = B.CreateAdd(Acc, Term, "next.sum");
    auto *NextIndex = B.CreateAdd(Index, K(1), "next.i");
    B.CreateBr(Header);
    Index->addIncoming(NextIndex, Body);
    Acc->addIncoming(NextAcc, Body);
    B.SetInsertPoint(Exit);
    B.CreateRet(Acc);
  }
  if (verifyModule(M, &errs())) return 1;
  std::error_code EC;
  raw_fd_ostream OS(Output, EC, sys::fs::OF_Text);
  if (EC) { errs() << EC.message() << '\n'; return 1; }
  M.print(OS, nullptr);
  return 0;
}
