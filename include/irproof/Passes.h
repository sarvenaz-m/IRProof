#pragma once
#include "llvm/IR/PassManager.h"

namespace irproof {
class StrengthReductionPass : public llvm::OptionalPassInfoMixin<StrengthReductionPass> {
public:
  llvm::PreservedAnalyses run(llvm::Function &, llvm::FunctionAnalysisManager &);
};
class AuditPass : public llvm::RequiredPassInfoMixin<AuditPass> {
public:
  llvm::PreservedAnalyses run(llvm::Module &, llvm::ModuleAnalysisManager &);
};
} // namespace irproof
