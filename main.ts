#!/usr/bin/env node
// Validation entrypoint for news-image-20261122.
//
// Copies the pre-rendered entry.png (drawn by render.py) into the
// grader's output directory, after proving the file is exactly what
// the competition gate requires: a real PNG, at most 1 MiB, exactly
// 1024x1024, 8-bit truecolour RGB, every chunk CRC-valid, IEND last,
// nothing after it. The copy is re-read and its sha256 compared with
// the source, so a truncated or corrupted write fails loudly.
//
// The source image is resolved relative to THIS script file
// (import.meta.url), never relative to the caller's working
// directory: the grader runs `node /bot/main.ts` from anywhere.
// Output goes to $MAKEFUN_OUTPUT_DIR, default /output.
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const LIMIT = 1048576;
const here = dirname(fileURLToPath(import.meta.url));
const SRC = join(here, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR || "/output";

function fail(msg) {
  console.error(`validation failed: ${msg}`);
  process.exit(1);
}

// CRC-32 (IEEE 802.3, polynomial 0xEDB88320, reflected). Node's stdlib
// has no CRC32 helper, so the table is built at startup and the
// checksum runs over each chunk's type + data bytes, as the PNG spec
// defines it.
const CRC_TABLE = (() => {
  const table = new Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(data) {
  let crc = 0xffffffff;
  for (const byte of data) {
    crc = CRC_TABLE[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

// Walk the chunk stream past the 8-byte signature. Each chunk is a
// 4-byte big-endian length, a 4-byte type, data, and a 4-byte CRC over
// type + data. Returns the chunk count; fails on a bad CRC, a chunk
// that overruns the file, a missing IEND, or trailing bytes after it.
function walkChunks(buf) {
  let offset = 8;
  let count = 0;
  let sawIEND = false;
  while (offset < buf.length) {
    if (offset + 12 > buf.length) {
      fail("truncated PNG chunk header");
    }
    const len = buf.readUInt32BE(offset);
    const type = buf.toString("ascii", offset + 4, offset + 8);
    if (offset + 12 + len > buf.length) {
      fail(`chunk ${type} overruns end of file`);
    }
    const stored = buf.readUInt32BE(offset + 8 + len);
    const computed = crc32(buf.subarray(offset + 4, offset + 8 + len));
    if (stored !== computed) {
      fail(`chunk ${type} CRC mismatch`);
    }
    offset += 12 + len;
    count++;
    if (type === "IEND") {
      sawIEND = true;
      break;
    }
  }
  if (!sawIEND) {
    fail("missing IEND chunk");
  }
  if (offset !== buf.length) {
    fail(`trailing bytes after IEND (${buf.length - offset} bytes)`);
  }
  return count;
}

const buf = (() => {
  try {
    return readFileSync(SRC);
  } catch {
    fail(`cannot read ${SRC}`);
  }
})();

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (buf.length < 33 || !buf.subarray(0, 8).equals(PNG_MAGIC)) {
  fail("not a PNG (bad magic bytes)");
}
if (buf.length > LIMIT) {
  fail(`size ${buf.length} exceeds ${LIMIT} bytes`);
}
// IHDR must be the first chunk: 13 bytes of data starting at offset 16.
if (buf.toString("ascii", 12, 16) !== "IHDR") {
  fail("first chunk is not IHDR");
}
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  fail(`IHDR dimensions ${width}x${height}, expected exactly 1024x1024`);
}
// PNG colour model sanity: bit depth 8, colour type 2 (truecolour RGB).
const bitDepth = buf[24];
const colourType = buf[25];
if (bitDepth !== 8 || colourType !== 2) {
  fail(`unexpected PNG format: bit depth ${bitDepth}, colour type ${colourType}`);
}
// Full chunk walk: every chunk's CRC, IEND last, nothing after it.
const chunkCount = walkChunks(buf);

mkdirSync(OUT_DIR, { recursive: true });
const outPath = join(OUT_DIR, "entry.png");
writeFileSync(outPath, buf);

// Verify the written copy is byte-identical to the validated source.
const written = readFileSync(outPath);
const digest = createHash("sha256").update(buf).digest("hex");
const writtenDigest = createHash("sha256").update(written).digest("hex");
if (writtenDigest !== digest) {
  fail(`written copy digest mismatch: ${writtenDigest} != ${digest}`);
}

console.log(`ok: ${outPath} ${width}x${height} ${buf.length} bytes ${chunkCount} chunks sha256=${digest}`);
