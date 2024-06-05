
const fs = require('fs');
const URLS = fs.readFileSync('./scenarios/new-set.txt').toString().split("\n");

async function perfTest(context, commands) {
  for (url of URLS) {
    if (url == '') break;
    await commands.measure.start(url);
    await commands.wait.byTime(1500)
  }
};

module.exports = {
  test: perfTest
};
