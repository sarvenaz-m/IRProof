#include "irproof/Passes.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Plugins/PassPlugin.h"

extern "C" LLVM_ATTRIBUTE_WEAK llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return {LLVM_PLUGIN_API_VERSION, "IRProof", "1.0.0",
          [](llvm::PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](llvm::StringRef Name, llvm::FunctionPassManager &FPM,
                   llvm::ArrayRef<llvm::PassBuilder::PipelineElement>) {
                  if (Name != "irproof-strength") return false;
                  FPM.addPass(irproof::StrengthReductionPass());
                  return true;
                });
            PB.registerPipelineParsingCallback(
                [](llvm::StringRef Name, llvm::ModulePassManager &MPM,
                   llvm::ArrayRef<llvm::PassBuilder::PipelineElement>) {
                  if (Name == "irproof-audit") {
                    MPM.addPass(irproof::AuditPass());
                    return true;
                  }
                  if (Name == "irproof-pipeline") {
                    llvm::FunctionPassManager FPM;
                    FPM.addPass(irproof::StrengthReductionPass());
                    MPM.addPass(llvm::createModuleToFunctionPassAdaptor(std::move(FPM)));
                    return true;
                  }
                  return false;
                });
          }};
}
