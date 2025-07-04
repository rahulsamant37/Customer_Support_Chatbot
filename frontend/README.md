# Customer Support Chatbot Frontend

A modern, responsive web interface for the Customer Support Chatbot API.

## Features

- 🎨 **Modern UI**: Clean and intuitive chat interface
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- ⚡ **Real-time Chat**: Instant messaging with typing indicators
- 🔄 **Status Monitoring**: Shows API connection status
- 💡 **Smart Suggestions**: Quick access to common queries
- 🎯 **Error Handling**: Graceful error handling and user feedback

## Quick Start

1. **Start the server**:
   ```bash
   python start_server.py
   ```

2. **Open your browser** and navigate to:
   - Chat Interface: `http://localhost:8000/chat`
   - API Documentation: `http://localhost:8000/docs`

## Frontend Structure

```
frontend/
├── index.html          # Main chat interface
└── README.md          # This file
```

## Usage

### Basic Chat
1. Type your message in the input field
2. Press Enter or click "Send"
3. Wait for the AI response

### Suggestion Chips
Click on any of the suggested queries to quickly start a conversation:
- "Budget laptops"
- "Good headphones" 
- "Budget smartphones"
- "Gaming accessories"

### Mobile Experience
The interface is fully responsive and optimized for mobile devices with:
- Touch-friendly buttons
- Optimized layouts
- Smooth scrolling

## Customization

### API Endpoint
To change the API endpoint, edit the `apiUrl` in `index.html`:
```javascript
this.apiUrl = 'http://your-api-url:port';
```

### Styling
The CSS is embedded in the HTML file for easy customization. Key areas:
- **Colors**: Modify the gradient values in the CSS variables
- **Layout**: Adjust the `.chat-container` dimensions
- **Typography**: Change font families and sizes

### Suggestions
Modify the suggestion chips by editing the HTML in the welcome message section.

## Browser Support

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## Troubleshooting

### Connection Issues
- Check if the API server is running on `http://localhost:8000`
- Verify CORS is enabled (already configured in main.py)
- Check browser console for error messages

### Display Issues
- Clear browser cache
- Check if JavaScript is enabled
- Ensure modern browser (ES6+ support required)

## Development

The frontend is a single HTML file with embedded CSS and JavaScript for simplicity. For production, consider:
- Separating CSS and JS into external files
- Implementing proper build process
- Adding additional error handling
- Implementing authentication if needed
