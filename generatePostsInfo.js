'use strict'
import * as fs from "node:fs";

const generatePostsInfoFile = function (dirPath) {
  fs.readdir(dirPath, function (err, files) {
    if (err) {
      console.log('Error getting directory information.');
    } else {
      const posts = [];
      files.forEach(function (file, index) {
        let fileName = file.split('_')[1].replace(/--/g, ' ').replace(/-/g, ' ').replace(/ \w+.html/g, '');
        posts.push({
          id: index + 1,
          date: file.split('_')[0],
          title: fileName,
          fileName: file
        });
      });
      fs.writeFileSync('./src/assets/posts.info.json', JSON.stringify(posts));
    }
  });
}
generatePostsInfoFile('./src/assets/posts');
