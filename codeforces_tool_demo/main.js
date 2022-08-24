const express = require('express');
const child_process = require('child_process');
const fs = require('fs');
const WebSocket = require('ws');
const iconv = require('iconv-lite');
const websocketServer = WebSocket.WebSocketServer;
const cors = require('cors');

const wss = new websocketServer({ port: 3000 });
wss.on('connection', function connection(ws) {
    ws.on('message', function message(data) {
        data = JSON.parse(data);
        console.log(data);
        const child1 = child_process.spawn('python', ['-u', 'getStatus.py', data.action, data.contestId, data.apiKey, data.apiSecret]);
        child1.stdout.on('data', data => {
            console.log(iconv.decode(data, 'cp936'));
            ws.send(iconv.decode(data, 'cp936'));
        });
        child1.stdout.on('close', () => {
            fs.readFile(`./status/${data.contestId}.json`, (err, datastr) => {
                if (err) return console.log(err.message);
                let datastr2 = JSON.parse(datastr);
                if (datastr2.status == 'FAILED') {
                    ws.send(datastr2.comment);
                    return console.log('爬取失败');
                }
                else {
                    ws.send('爬取成功');
                    console.log('爬取成功');
                    const child2 = child_process.spawn('python', ['-u', 'prelogin.py', data.handle, data.password, data.contestId]);
                    child2.stdout.on('data', (data) => {
                        console.log(iconv.decode(data, 'cp936'));
                        ws.send(iconv.decode(data, 'cp936'));
                    });
                    child2.stdout.on('close', () => {
                        fs.readFile(`./status/${data.contestId}_source.json`, (err, message) => {
                            if (err) {
                                ws.send(err.message);
                                return console.log(err.message);
                            }
                            message = JSON.parse(message);
                            if (message.status == 'FAILED') {
                                ws.send(message.comment);
                                return console.log(message.comment);
                            }
                            else {
                                ws.send('预检登录成功');
                                ws.send(`总共${message.length}条提交`);
                                console.log(data.handle, data.password);
                                const child3 = child_process.spawn('python', ['-u', 'getSource.py', data.handle, data.password, data.contestId]);
                                child3.stdout.on('data', data => {
                                    console.log(iconv.decode(data, 'cp936'));
                                    ws.send(iconv.decode(data, 'cp936'));
                                });
                                child3.stdout.on('close', () => {
                                    ws.send('所有提交爬取完毕');
                                    const child4 = child_process.spawn('tar', ['-cf', `./TAR/${data.contestId}.tar`, `./code/${data.contestId}`]);
                                    child4.stdout.on('close', () => {
                                        ws.send(`<a href="/download/${data.contestId}.tar" target="_blank">导出代码压缩包</a>`);
                                    });
                                });
                            }
                        });
                    });

                }
            });
        });
    });
});
app = express();
app.use(cors());
app.use('/', express.static('./public'));

app.get('/download/:contestId', (req, res) => {
    res.setHeader("Access-Control-Allow-Origin", '*')
    res.setHeader('Access-Control-Allow-Headers', '*')
    res.download('./TAR/' + req.params.contestId);
})

app.listen('8888', () => {
    console.log('running at http://127.0.0.1:8888');
})
