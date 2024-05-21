const path = require('path');

const filePath = path.resolve(__dirname, 'src', 'index.js');
const fileUrl = `file://${filePath}`;

console.log(fileUrl);