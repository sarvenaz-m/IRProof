export function parseInteger(text, width) {
  if (!/^-?\d{1,50}$/.test(text.trim())) throw new Error('Enter a whole number.');
  const x = BigInt(text);
  const lo = -(1n << BigInt(width - 1)), hi = (1n << BigInt(width - 1)) - 1n;
  if (x < lo || x > hi) throw new Error(`Use a signed ${width}-bit value (${lo} to ${hi}).`);
  return x;
}
export function roundingSample(x, divisor, width) {
  const d = BigInt(divisor), n = Math.log2(Number(divisor));
  if (!Number.isInteger(n) || d < 2n) throw new Error('Choose a positive power of two.');
  const shift = BigInt(n), sign = x >> BigInt(width - 1);
  return {source: x / d, naive: x >> shift,
          corrected: (x + (sign & (d - 1n))) >> shift,
          bias: sign & (d - 1n)};
}
export function plotRounding(divisor, width) {
  const points = Array.from({length: 33}, (_, i) => ({x: i - 16, ...roundingSample(BigInt(i - 16), divisor, width)}));
  const sx = x => 30 + (x + 16) * 12.5;
  const sy = y => 76 - Number(y) * 5;
  const path = field => points.map((p, i) => `${i ? 'L' : 'M'}${sx(p.x)},${sy(p[field])}`).join(' ');
  return `<svg class="round-plot" viewBox="0 0 460 155" role="img" aria-label="Division and arithmetic shift for inputs minus sixteen to sixteen"><path class="plot-grid" d="M30 26H430M30 76H430M30 126H430M230 16V136"/><path class="plot-naive" d="${path('naive')}"/><path class="plot-source" d="${path('source')}"/><text x="30" y="150">−16</text><text x="225" y="150">0</text><text x="420" y="150">16</text><text x="10" y="80">0</text></svg>`;
}
