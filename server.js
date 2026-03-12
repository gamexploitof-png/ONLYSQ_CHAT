const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Proxy endpoint for OnlySq API models
app.get('/api/models', async (req, res) => {
    try {
        const response = await fetch('https://api.onlysq.ru/ai/models', {
            headers: {
                'Authorization': 'Bearer sq-zq8kT2BEKhxFdapFvtGBvlX8EB1PjbOa'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error fetching models:', error);
        res.status(500).json({ error: 'Failed to fetch models' });
    }
});

// Proxy endpoint for OnlySq API chat completions
app.post('/api/chat/completions', async (req, res) => {
    try {
        const { model, messages, max_tokens, temperature } = req.body;
        
        const response = await fetch('https://api.onlysq.ru/ai/openai/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer sq-zq8kT2BEKhxFdapFvtGBvlX8EB1PjbOa',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model,
                messages,
                max_tokens,
                temperature
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error with chat completion:', error);
        res.status(500).json({ error: 'Failed to process chat completion' });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Your OnlySq AI Chat Interface is ready!`);
    console.log(`Open your browser and navigate to http://localhost:${PORT}`);
});

module.exports = app;