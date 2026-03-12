# OnlySq AI Chat Interface

A beautiful Material You styled web interface for the OnlySq AI API, featuring model selection, real-time chat, and a modern design.

## Features

- 🎨 **Material You Design**: Modern, cohesive interface following Google's Material Design 3 guidelines
- 🤖 **Multiple AI Models**: Access to all available OnlySq AI models including GPT-4o, Claude, Gemini, and more
- 💬 **Real-time Chat**: Interactive chat interface with smooth animations
- 🔧 **Easy Setup**: Simple Node.js server with proxy endpoints
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- 🚀 **Local Hosting**: Run locally on any port you choose

## Quick Start

### Prerequisites

- Node.js (version 14 or higher)
- npm (comes with Node.js)

### Installation

1. **Clone or download** this project to your local machine

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the server**:
   ```bash
   npm start
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:3000
   ```

### Development Mode

For development with auto-restart:
```bash
npm run dev
```

## Project Structure

```
ONLYSQ_CHAT/
├── index.html          # Main web interface
├── server.js           # Node.js server with API proxy
├── package.json        # Project dependencies and scripts
└── README.md          # This file
```

## API Endpoints

The server provides proxy endpoints to avoid CORS issues:

- `GET /api/models` - Fetch available AI models
- `POST /api/chat/completions` - Send chat messages to AI models

## Configuration

### Changing the Port

Edit `server.js` and modify the `PORT` variable:
```javascript
const PORT = process.env.PORT || 3000; // Change 3000 to your preferred port
```

### API Key

The application comes pre-configured with your API key:
- **API Key**: `sq-zq8kT2BEKhxFdapFvtGBvlX8EB1PjbOa`
- **Base URL**: `https://api.onlysq.ru/ai/openai`

You can change these in the frontend JavaScript if needed.

## Available Models

The interface automatically loads all available models from the OnlySq API, including:

- **Text Models**: GPT-4o, Claude, Gemini, Llama, Qwen, and more
- **Image Models**: Flux, GPT Image, and others
- **Specialized Models**: Reasoning models, coding models, and search-optimized models

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Server Won't Start
- Ensure Node.js is installed: `node --version`
- Check port availability: `netstat -an | grep 3000`

### Models Not Loading
- Check internet connection
- Verify API key is correct
- Check browser console for errors

### CORS Issues
The server includes CORS middleware to handle cross-origin requests automatically.

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues or questions:
1. Check the browser console for error messages
2. Verify your API key is valid
3. Ensure the OnlySq API is accessible from your location

## API Documentation

For more information about the OnlySq API, visit:
[OnlySq API Documentation](https://api.onlysq.ru/docs)