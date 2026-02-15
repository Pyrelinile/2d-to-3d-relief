# Slicer guides

## Generic workflow
1. Slice model with intended layer height.
2. Add pause/change commands at layer numbers from `swap_plan.txt`.
3. Resume print after swap and purge.

## Command style mapping
- `m600`: filament change on firmware that supports it.
- `m0`: generic pause.
- `m25`: pause SD print.
- `none`: no command snippet generated.
