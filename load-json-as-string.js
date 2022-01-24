module.exports.lifeCyclePolicy = (serverless) => {
    const fsPromises = require('fs').promises
    return fsPromises.readFile('default.lifecycle.policy.json', 'utf-8')
};