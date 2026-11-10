/**
 * Minimal ZIP (deflate) writer. Avoids a python3 dependency so skill
 * download zips can be built on Windows, macOS, and Linux.
 */
import fs from 'node:fs';
import path from 'node:path';
import {deflateRawSync} from 'node:zlib';

const CRC_TABLE = new Uint32Array(256);
for (let i = 0; i < 256; i++) {
  let c = i;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  CRC_TABLE[i] = c >>> 0;
}

function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function dosDateTime(d = new Date()): {time: number; date: number} {
  const time =
    ((d.getHours() & 0x1f) << 11) | ((d.getMinutes() & 0x3f) << 5) | ((Math.floor(d.getSeconds() / 2) & 0x1f) << 0);
  const date = (((d.getFullYear() - 1980) & 0x7f) << 9) | ((d.getMonth() + 1) << 5) | (d.getDate() & 0x1f);
  return {time, date};
}

function u16(n: number): Buffer {
  const b = Buffer.alloc(2);
  b.writeUInt16LE(n, 0);
  return b;
}

function u32(n: number): Buffer {
  const b = Buffer.alloc(4);
  b.writeUInt32LE(n >>> 0, 0);
  return b;
}

export type ZipEntry = {name: string; data: Buffer};

export function collectDir(root: string, prefix = ''): ZipEntry[] {
  const out: ZipEntry[] = [];
  function walk(dir: string, relBase: string) {
    if (!fs.existsSync(dir)) return;
    for (const ent of fs.readdirSync(dir, {withFileTypes: true})) {
      if (ent.name === '.DS_Store' || ent.name === '.git') continue;
      const abs = path.join(dir, ent.name);
      const rel = relBase ? `${relBase}/${ent.name}` : ent.name;
      if (ent.isDirectory()) walk(abs, rel);
      else {
        const name = prefix ? `${prefix}/${rel}` : rel;
        out.push({name: name.replace(/\\/g, '/'), data: fs.readFileSync(abs)});
      }
    }
  }
  walk(root, '');
  return out;
}

export function writeZip(dest: string, entries: ZipEntry[]) {
  fs.mkdirSync(path.dirname(dest), {recursive: true});
  const {time, date} = dosDateTime();
  const locals: Buffer[] = [];
  const centrals: Buffer[] = [];
  let offset = 0;

  for (const entry of entries) {
    const nameBuf = Buffer.from(entry.name, 'utf8');
    const deflated = deflateRawSync(entry.data);
    const useDeflate = deflated.length < entry.data.length;
    const payload = useDeflate ? deflated : entry.data;
    const method = useDeflate ? 8 : 0;
    const crc = crc32(entry.data);
    const local = Buffer.concat([
      Buffer.from([0x50, 0x4b, 0x03, 0x04]),
      u16(20),
      u16(0),
      u16(method),
      u16(time),
      u16(date),
      u32(crc),
      u32(payload.length),
      u32(entry.data.length),
      u16(nameBuf.length),
      u16(0),
      nameBuf,
      payload,
    ]);
    locals.push(local);
    centrals.push(
      Buffer.concat([
        Buffer.from([0x50, 0x4b, 0x01, 0x02]),
        u16(20),
        u16(20),
        u16(0),
        u16(method),
        u16(time),
        u16(date),
        u32(crc),
        u32(payload.length),
        u32(entry.data.length),
        u16(nameBuf.length),
        u16(0),
        u16(0),
        u16(0),
        u16(0),
        u32(0),
        u32(offset),
        nameBuf,
      ]),
    );
    offset += local.length;
  }

  const central = Buffer.concat(centrals);
  const eocd = Buffer.concat([
    Buffer.from([0x50, 0x4b, 0x05, 0x06]),
    u16(0),
    u16(0),
    u16(entries.length),
    u16(entries.length),
    u32(central.length),
    u32(offset),
    u16(0),
  ]);
  fs.writeFileSync(dest, Buffer.concat([...locals, central, eocd]));
}
