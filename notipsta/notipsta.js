const express = require('express');
const { exec } = require("child_process");
const fs = require('fs');

const PORT = process.env.NOTIPSTA_PORT || 5001;
const INTERVAL = process.env.NOTIPSTA_WATCH_INTERVAL || 10000;
const APPS = 'tippecanoe,tile-join,pullUpdatedSTVs.sh'.split(',').join('\\|')
const FILE = '/data/PREV_RUN';
const COMMAND = '/scripts/pullUpdatedSTVs.sh';
const UPDATES = '/scripts/selectUpdatedSTVs.sh';

// sed 's%^\s*\(.*\)\s\s%\1,%'
const psFilter = 'grep -v grep | sed -e "s%\\s*root\\s*%,%g" -e "s%^\\s*%%"';

const psCommand = `ps -eo etime,user,pid,user,args | grep "\\(${APPS}\\)" | ${psFilter}`;
const app = express();
const status = {
    last: 0, running: false, duration: 0, updates: []
}

function runCommand(toExecute, success) {
  exec(toExecute, (error, stdout, stderr) => {
    if (error) {
      console.log('Error', error);
      console.log('StdErr', stderr);
    }
    success(stdout);
  });
}

function updateStatus() {
  if (!status.running) {
    runCommand(`${UPDATES} ${status.last}`, (stdout) => {
      status.updates = stdout.split(/\s/).filter((f) => f).map(Number);
    })
  }
  if (FILE) {
    runCommand(`cat ${FILE} 2>/dev/null|| echo -n 0`, (stdout) => {
      status.last = Number(stdout);
    });
  }
  runCommand(psCommand, (stdout) => {
    status.running = Boolean(stdout);
    if (status.running) {
      const arr = stdout.split('\n');
      const time = arr.map((c) => {
        if (c === '') return 0;
        const [s, m, h] = c.split(',')[0].split(':').reverse().map(Number)
        let t = m * 60 + s;
        if (h) t += 3600 * h;
        return t;
      });
      status.duration = Math.max(...time);
    }
    setTimeout(updateStatus, INTERVAL)
  });
}

async function startProcess(force) {
  const toRun = force ? `${COMMAND} force` : COMMAND;
  exec(toRun, (error, stdout, stderr) => {
    if (error) {
      console.log('Error', error);
      console.log('Stderr', stderr);
    }
    console.log(stdout);
  });
}

const printableDate = () => {
  const d = new Date();
  const date = [d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()];
  const time = [d.getUTCHours(), d.getUTCMinutes()];
  date[1] += 1;
  if (date[1] < 10) date[1] = `0${date[1]}`
  if (time[1] < 10) time[1] = `0${time[1]}`
  return `${date.join('-')} ${time.join(':')}`;
}

function update (req, res, force = false) {
  const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
  const fromPrev = Math.round(Number(new Date())/1000) - status.last;
  console.log(`${ip} ${printableDate()} ${req.method} PREV_RUN was ${fromPrev}s ago ${JSON.stringify(status)}`);
  if (status.running) {
      res.status(208).send(status);
  } else {
    status.running = true;
    status.duration = 0;
    startProcess(force);
    res.send(status);
  }
};


// GET to retrieve current status.
app.get('/', (req, res) => res.send(status));
// PUT to rebuild from scratch.
app.put('/', (req, res) => update(req, res, true));
// PATCH to perform an update for mbtiles
app.patch('/', (req, res) => update(req, res, false));


app.listen(PORT, function () {
  updateStatus();
  console.log([
    'Notipsta: Notification for tippecanoe status',
    `\tListening ${PORT}`,
    `\tRunning checks every ${INTERVAL}ms`,
    `\tFlagged processes: "\(${APPS}\)"`,
    `\tTimestamp file ${FILE}`,
    `\tUpdate command ${COMMAND}`,
    String(new Date())
  ].join('\n'));
});