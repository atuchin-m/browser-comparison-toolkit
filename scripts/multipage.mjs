
import * as utils from './utils.mjs'

export async function test(context, commands) {
  await commands.wait.byTime(30 * 1000);
  for (const url of utils.getUrls(context)) {
    await commands.measure.start(url);
    await commands.navigate('about:blank');
    await commands.wait.byTime(5 * 1000);
  }
};
