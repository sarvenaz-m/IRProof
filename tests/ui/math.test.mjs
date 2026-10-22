import test from 'node:test';
import assert from 'node:assert/strict';
import {parseInteger, roundingSample} from '../../demo/assets/math.mjs';

test('corrected results agree with integer division for every signed i8 input', () => {
  for (let x = -128; x < 128; ++x)
    for (const d of [2, 4, 8, 16, 64]) {
      const r = roundingSample(BigInt(x), d, 8);
      assert.equal(r.corrected, BigInt(x) / BigInt(d));
    }
});

test('negative odd inputs expose the naive arithmetic shift', () => {
  assert.deepEqual(roundingSample(-3n, 2, 32), {source:-1n, naive:-2n, corrected:-1n, bias:1n});
});

test('128-bit limits remain exact and values outside the signed range are rejected', () => {
  const limit = 1n << 127n;
  assert.equal(parseInteger(String(-limit),128), -limit);
  assert.equal(parseInteger(String(limit-1n),128), limit-1n);
  assert.throws(()=>parseInteger(String(limit),128), /signed 128-bit/);
  assert.equal(roundingSample(-limit,8,128).source, -(1n<<124n));
});

test('input rejects fractions and JavaScript-like expressions', () => {
  for(const s of ['1.5','2**8','NaN','1e6','<script>','']) assert.throws(()=>parseInteger(s,32));
});
