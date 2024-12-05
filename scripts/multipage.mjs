
import fs from 'fs';
const URLS = fs.readFileSync('./scenarios/new-set.txt').toString().split("\n");

export async function test(context, commands) {
  for (url of URLS) {
    if (url.startsWith('#') || url.startsWith('/'))
      continue;
    if (url == '') break;
    await commands.measure.start(url);
  }
};
