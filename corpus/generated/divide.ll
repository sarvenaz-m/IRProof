; ModuleID = 'irproof.divide'
source_filename = "irproof.divide"

define i32 @specimen(i32 noundef %x) {
entry:
  %quotient = sdiv i32 %x, 8
  ret i32 %quotient
}
