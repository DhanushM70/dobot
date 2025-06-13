import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('dist'));

// Store running processes
const runningProcesses = new Map();

// API endpoint to handle Dobot commands
app.post('/api/dobot/command', (req, res) => {
    const { command } = req.body;
    
    console.log(`Received command: ${command}`);
    
    let scriptPath = '';
    let processKey = '';
    
    switch(command) {
        case '2':
            scriptPath = 'demo-magician-python-64-master/color d&t/python teach_color.py.py';
            processKey = 'colorTeaching';
            break;
        case '3':
            scriptPath = 'demo-magician-python-64-master/color d&t/detectcolor.py';
            processKey = 'colorDetection';
            break;
        case '4':
            scriptPath = 'demo-magician-python-64-master/inverse/cube_detection_dobot.py';
            processKey = 'cubeDetection';
            break;
        case '5':
            scriptPath = 'demo-magician-python-64-master/inverse/cam_to_dobot_matrix.npy';
            processKey = 'homographyMatrix';
            break;
        case 'q':
            // Terminate all running processes
            runningProcesses.forEach((process, key) => {
                if (process && !process.killed) {
                    process.kill();
                    console.log(`Terminated process: ${key}`);
                }
            });
            runningProcesses.clear();
            return res.json({ status: 'success', message: 'All processes terminated' });
        default:
            return res.json({ status: 'error', message: 'Invalid command' });
    }
    
    try {
        // Kill existing process if running
        if (runningProcesses.has(processKey)) {
            const existingProcess = runningProcesses.get(processKey);
            if (existingProcess && !existingProcess.killed) {
                existingProcess.kill();
            }
        }
        
        // Start new process
        const pythonProcess = spawn('python', [scriptPath], {
            cwd: __dirname,
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        runningProcesses.set(processKey, pythonProcess);
        
        pythonProcess.stdout.on('data', (data) => {
            console.log(`${processKey} stdout: ${data}`);
        });
        
        pythonProcess.stderr.on('data', (data) => {
            console.error(`${processKey} stderr: ${data}`);
        });
        
        pythonProcess.on('close', (code) => {
            console.log(`${processKey} process exited with code ${code}`);
            runningProcesses.delete(processKey);
        });
        
        pythonProcess.on('error', (error) => {
            console.error(`Failed to start ${processKey}:`, error);
            runningProcesses.delete(processKey);
            return res.json({ status: 'error', message: `Failed to start process: ${error.message}` });
        });
        
        res.json({ status: 'success', message: `${processKey} started successfully` });
        
    } catch (error) {
        console.error('Error executing command:', error);
        res.json({ status: 'error', message: error.message });
    }
});

// Get system status
app.get('/api/dobot/status', (req, res) => {
    const activeProcesses = Array.from(runningProcesses.keys()).filter(key => {
        const process = runningProcesses.get(key);
        return process && !process.killed;
    });
    
    res.json({
        status: 'online',
        activeProcesses,
        totalProcesses: runningProcesses.size
    });
});

// Serve the main page
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`🚀 Dobot Web Controller running on http://localhost:${PORT}`);
    console.log(`📁 Python scripts directory: ${path.join(__dirname, 'demo-magician-python-64-master')}`);
});