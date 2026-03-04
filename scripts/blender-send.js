/**
 * Sends Python code to the running Blender MCP socket server on port 9876.
 * Usage: node scripts/blender-send.js <python-file.py>
 */
const net = require('net');
const fs = require('fs');
const path = require('path');

const BLENDER_HOST = 'localhost';
const BLENDER_PORT = 9876;

const pyFile = process.argv[2];
if (!pyFile) {
    console.error('Usage: node scripts/blender-send.js <python-file.py>');
    process.exit(1);
}

const code = fs.readFileSync(path.resolve(pyFile), 'utf-8');
const command = JSON.stringify({
    type: 'execute_code',
    params: { code }
});

const client = new net.Socket();
let responseData = '';

client.connect(BLENDER_PORT, BLENDER_HOST, () => {
    console.log(`Connected to Blender MCP on ${BLENDER_HOST}:${BLENDER_PORT}`);
    console.log(`Sending ${code.length} bytes of Python code...`);
    client.write(command);
});

client.on('data', (data) => {
    responseData += data.toString();
    try {
        const response = JSON.parse(responseData);
        console.log('\n--- Blender Response ---');
        if (response.status === 'success') {
            console.log('✓ Success');
            if (response.result && response.result.result) {
                console.log(response.result.result);
            }
        } else {
            console.log('✗ Error:', response.message || JSON.stringify(response));
        }
        client.destroy();
    } catch (e) {
        // Incomplete JSON, wait for more data
    }
});

client.on('close', () => {
    console.log('Connection closed');
});

client.on('error', (err) => {
    console.error('Connection error:', err.message);
    console.error('Make sure Blender is open and BlenderMCP is connected (port 9876)');
    process.exit(1);
});
