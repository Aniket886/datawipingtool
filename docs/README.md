# DataWipe Pro - Web Interface

This is the web interface for the DataWipe Pro data wiping tool. The website provides information about the tool, features, and includes a web-based demonstration of data wiping concepts.

## Features

- **Modern Responsive Design**: Mobile-friendly interface with dark theme
- **Interactive Web Tool**: Browser-based file wiping simulation for educational purposes
- **Feature Showcase**: Comprehensive overview of desktop application capabilities
- **Download Links**: Direct links to download the desktop application
- **Developer Information**: About section with social links and contact info

## Structure

```
docs/
├── index.html          # Main webpage
├── assets/
│   ├── style.css      # Responsive CSS styling
│   └── script.js      # Interactive JavaScript
├── _config.yml        # GitHub Pages configuration
└── README.md          # This file
```

## Web Tool Disclaimer

The web-based data wiping tool is for **educational and demonstration purposes only**. It simulates the data wiping process to show how the desktop application works, but does not perform actual secure data erasure.

For real secure data wiping, please use the desktop application with appropriate administrative privileges.

## GitHub Pages Deployment

This website is automatically deployed to GitHub Pages from the `docs/` folder. Any changes to files in this directory will be reflected on the live website.

**Live URL**: https://aniket886.github.io/datawipingtool/

## Local Development

To run this website locally:

1. Clone the repository
2. Navigate to the `docs/` folder
3. Serve the files using any web server:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   
   # Using Jekyll (if you have it installed)
   jekyll serve
   ```
4. Open `http://localhost:8000` in your browser

## Browser Compatibility

The website is compatible with:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Performance

The website is optimized for:
- Fast loading times
- Mobile responsiveness
- Accessibility (WCAG 2.1 AA)
- SEO optimization

## Contributing

To contribute to the web interface:

1. Fork the repository
2. Make changes to files in the `docs/` folder
3. Test locally
4. Submit a pull request

## License

This web interface is part of the DataWipe Pro project and is licensed under the MIT License.
