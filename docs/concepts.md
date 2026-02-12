# Concepts

## Heightmaps
An image is converted to luminance and normalized to `[0,1]`, then mapped to thickness `[min_mm,max_mm]`.

## Bas-relief mesh
The tool builds a manifold-like closed mesh from a sampled top surface, flat bottom, and side walls.

## Swap strategies
- **bands**: luminance percentiles become global swap heights.
- **quantize**: fixed stratified swap levels suitable for posterized color planning.
- **tdblend**: approximate optical accumulation using an exponential attenuation model.

## TD limitations
`tdblend` is intentionally heuristic. Real prints depend on nozzle size, extrusion width, filament pigment and cooling.
