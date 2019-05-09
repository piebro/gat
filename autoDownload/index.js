const fs = require('fs');
const util = require('util');
const puppeteer = require('puppeteer')

const linksList = JSON.parse(process.argv[2])

main();

async function main(){
  let browser = await puppeteer.launch({
    args: [
      // Required for Docker version of Puppeteer
      '--no-sandbox',
      '--disable-setuid-sandbox',
      // This will write shared memory files into /tmp instead of /dev/shm,
      // because Docker’s default for /dev/shm is 64MB
      '--disable-dev-shm-usage'
    ]
  })
  const browserVersion = await browser.version()
  console.log(`Started ${browserVersion}`)

  for(let i in linksList){
    let link = linksList[i];
    let page = await browser.newPage()
    page.setViewport({width:1000, height:1000})
    await page.goto(link)
    //await page.screenshot({path: '/images/buddy-screenshot.png'});
    
    await download(page, () =>{
      page.keyboard.press('s')
    })
    await page.close()  
    console.log("saved: " + link)
  }
  await browser.close()
}

async function download(page, f) {
  await page._client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: "images",
  });
  await f();
  let filename;
  while (!filename || filename.endsWith('.crdownload')) {
    await new Promise(resolve => setTimeout(resolve, 100));
    [filename] = await util.promisify(fs.readdir)("images");
  }
  await page.waitFor(100)
  return filename;
}
