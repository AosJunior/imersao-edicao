#!/usr/bin/env node
// Monta a pasta da imersão de edição de vídeo no computador do aluno.
//   npx github:AosJunior/imersao-edicao            cria (ou atualiza) a pasta edicao-imersao em Filmes / Vídeos
//   npx github:AosJunior/imersao-edicao <pasta>    cria em outro lugar
// Pode rodar de novo: atualiza as skills, a marca e o guia, e nunca mexe no que está em videos/.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const ORIGEM = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SEMPRE = ['.claude', '.imersao', 'marca', 'CLAUDE.md', 'COMECE-AQUI.txt', 'GUIA.html', 'GUIA.md', 'roteiro.txt'];
const SO_SE_FALTAR = ['videos'];

function destinoPadrao() {
  const casa = os.homedir();
  const nomes = process.platform === 'darwin' ? ['Movies'] : process.platform === 'win32' ? ['Videos', 'Vídeos'] : ['Vídeos', 'Videos'];
  for (const n of nomes) if (fs.existsSync(path.join(casa, n))) return path.join(casa, n, 'edicao-imersao');
  return path.join(casa, 'edicao-imersao');
}

const destino = path.resolve(process.argv[2] || destinoPadrao());
const jaExistia = fs.existsSync(path.join(destino, 'marca', 'estilo.md'));
const ignorar = (src) => !/(^|[\\/])(__pycache__|\.DS_Store|node_modules)$/.test(src) && !src.endsWith('.pyc');

try {
  fs.mkdirSync(destino, { recursive: true });
  for (const item of SEMPRE) {
    const de = path.join(ORIGEM, item);
    if (fs.existsSync(de)) fs.cpSync(de, path.join(destino, item), { recursive: true, force: true, filter: ignorar });
  }
  for (const item of SO_SE_FALTAR) {
    const de = path.join(ORIGEM, item);
    if (fs.existsSync(de)) fs.cpSync(de, path.join(destino, item), { recursive: true, force: false, errorOnExist: false, filter: ignorar });
  }
  fs.mkdirSync(path.join(destino, 'videos', 'meu-primeiro-video', 'brutos'), { recursive: true });
  fs.mkdirSync(path.join(destino, 'videos', 'meu-primeiro-video', 'sequencia'), { recursive: true });
} catch (e) {
  console.error('\nNão consegui montar a pasta em ' + destino + '.\n' + (e && e.message ? e.message : e));
  console.error('Escreva TRAVEI no chat da aula, com uma foto desta tela.');
  process.exit(1);
}

const skills = fs.readdirSync(path.join(destino, '.claude', 'skills')).filter((n) => fs.existsSync(path.join(destino, '.claude', 'skills', n, 'SKILL.md')));
console.log('\n' + (jaExistia ? 'Pasta da imersão atualizada.' : 'Pasta da imersão criada.'));
console.log('\n  ' + destino + '\n');
console.log('Dentro dela: as skills (' + skills.map((s) => '/' + s).join(', ') + '), a marca, o roteiro e o guia (GUIA.html).');
console.log('Os vídeos que já estavam em "videos" não foram tocados.\n');
console.log('Agora:');
console.log('  1. Abra o app do Claude e clique em Code.');
console.log('  2. Escolha a pasta edicao-imersao (o caminho está aqui em cima).');
console.log('  3. Mande: O que tem nesta pasta?\n');

if (!process.env.IMERSAO_NAO_ABRIR && !process.argv.includes('--nao-abrir')) {
  try {
    const [cmd, args] = process.platform === 'darwin' ? ['open', [destino]] : process.platform === 'win32' ? ['explorer', [destino]] : ['xdg-open', [destino]];
    spawn(cmd, args, { detached: true, stdio: 'ignore' }).on('error', () => {}).unref();
  } catch { /* abrir a pasta é só conforto */ }
}
