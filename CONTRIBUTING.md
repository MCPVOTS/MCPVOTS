# Contributing to MCPVots

First off, thank you for considering contributing to MCPVots! 🎉

The following is a set of guidelines for contributing to MCPVots. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Pledge

- **Be Respectful**: Treat everyone with respect and kindness
- **Be Inclusive**: Welcome newcomers and help them learn
- **Be Collaborative**: Work together towards common goals
- **Be Professional**: Maintain professional communication

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues as you might find that the problem has already been reported.

**Bug Report Template:**
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Windows 11, macOS 13, Ubuntu 20.04]
- Browser: [e.g. Chrome 118, Firefox 119, Safari 17]
- Node.js Version: [e.g. 18.17.0]
- MCPVots Version: [e.g. 1.0.0]
```

### ✨ Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Clear title** and description
- **Use case** for the enhancement
- **Benefits** to users
- **Implementation ideas** (optional)

### 🔧 Code Contributions

1. **Fork** the repository
2. **Create** a feature branch from `develop`
3. **Make** your changes
4. **Test** your changes thoroughly
5. **Submit** a pull request

## Development Setup

### Prerequisites

- Node.js 18.0.0 or higher
- Python 3.11 or higher
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/MCPVots.git
cd MCPVots

# Install dependencies
npm install

# Start development environment
npm run dev

# In another terminal, start backend services
npm run services:start
```

### Available Scripts

```bash
# Development
npm run dev                    # Start development server
npm run build                  # Build for production
npm run preview               # Preview production build

# Testing
npm test                      # Run all tests
npm run test:coverage         # Run tests with coverage
npm run test:watch           # Run tests in watch mode
npm run test:e2e             # Run end-to-end tests

# Code Quality
npm run lint                  # Run ESLint
npm run lint:fix             # Fix ESLint issues
npm run type-check           # TypeScript type checking
npm run format               # Format code with Prettier

# Advanced
npm run ecosystem:build       # Build entire ecosystem
npm run ecosystem:monitor     # Start monitoring dashboard
npm run analyze              # Bundle size analysis
```

## Pull Request Process

### Before Submitting

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Follow code style guidelines**
5. **Update CHANGELOG.md** if applicable

### PR Title Format

Use conventional commit format:
```
feat(mcp): add new server monitoring feature
fix(ui): resolve theme switching bug
docs(readme): update installation instructions
```

### PR Description Template

```markdown
## Summary
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Cross-browser testing (if UI changes)

## Screenshots (if applicable)
Add screenshots or videos demonstrating the changes

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## Style Guidelines

### JavaScript/TypeScript

- **ESLint**: Follow the project's ESLint configuration
- **Prettier**: Use Prettier for code formatting
- **TypeScript**: Use TypeScript for new code when possible
- **Comments**: Write clear, concise comments for complex logic

```javascript
// ✅ Good
/**
 * Establishes connection to MCP server with retry logic
 * @param {string} serverUrl - WebSocket URL of the MCP server
 * @param {number} maxRetries - Maximum number of connection attempts
 * @returns {Promise<WebSocket>} Connected WebSocket instance
 */
async function connectToMCPServer(serverUrl, maxRetries = 3) {
  // Implementation details...
}

// ❌ Avoid
function connect(url, retries) {
  // Missing documentation and unclear parameter names
}
```

### CSS/Styling

- **Tailwind CSS**: Use Tailwind utilities for styling
- **Dark Theme**: Ensure all new components support dark theme
- **Accessibility**: Follow WCAG 2.1 AA guidelines
- **Responsive**: Design for mobile-first approach

```css
/* ✅ Good - Uses semantic classes and dark theme support */
.server-status-card {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-md p-4;
  @apply border border-gray-200 dark:border-gray-700;
  @apply hover:shadow-lg transition-shadow duration-200;
}

/* ❌ Avoid - Hard-coded colors without dark theme support */
.card {
  background: #ffffff;
  border: 1px solid #e5e5e5;
}
```

### Git Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Feature
feat(mcp): add real-time server monitoring

# Bug fix
fix(theme): resolve dark mode toggle state persistence

# Documentation
docs(contributing): update development setup instructions

# Refactor
refactor(components): simplify server status component logic

# Test
test(integration): add WebSocket connection tests
```

### File Organization

```
src/
├── components/          # React components
│   ├── common/         # Reusable components
│   ├── mcp/           # MCP-specific components
│   └── theme/         # Theme-related components
├── contexts/           # React contexts
├── hooks/             # Custom React hooks
├── services/          # Business logic and API calls
├── types/             # TypeScript type definitions
├── utils/             # Utility functions
└── styles/            # Global styles and themes
```

## Testing Guidelines

### Unit Tests

- **Coverage**: Aim for >80% code coverage
- **Test Names**: Use descriptive test names
- **Arrange-Act-Assert**: Follow AAA pattern

```javascript
// ✅ Good
describe('MCPServerService', () => {
  it('should retry connection when initial attempt fails', async () => {
    // Arrange
    const mockServer = createMockServer();
    const service = new MCPServerService();
    
    // Act
    const result = await service.connect(mockServer.url);
    
    // Assert
    expect(result.isConnected).toBe(true);
    expect(mockServer.connectionAttempts).toBe(2);
  });
});
```

### Integration Tests

- **Real Scenarios**: Test actual user workflows
- **Error Handling**: Test error conditions
- **Performance**: Include performance assertions

## Documentation

### Code Documentation

- **JSDoc**: Use JSDoc for function documentation
- **README**: Keep README.md up to date
- **Examples**: Provide usage examples

### Architecture Documentation

- **Mermaid Diagrams**: Use Mermaid for architecture diagrams
- **Decision Records**: Document architectural decisions
- **API Documentation**: Keep API docs current

## Community

### Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs and request features
- **Discord**: [Join our Discord community](DISCORD_LINK_TO_BE_CONFIGURED)

### Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **CHANGELOG.md**: Release notes
- **GitHub**: Contributor graph

## Advanced Contribution Areas

### 🤖 AI Integration

Help improve our AI capabilities:
- Trilogy AGI enhancements
- Model Context Protocol optimizations
- Intelligent monitoring features

### 🔧 Infrastructure

Contribute to infrastructure:
- Docker containerization
- CI/CD pipeline improvements
- Deployment automation

### 🎨 Design & UX

Enhance user experience:
- UI/UX improvements
- Accessibility enhancements
- Mobile optimization

### 📊 Analytics & Monitoring

Improve observability:
- Performance monitoring
- Error tracking
- Usage analytics

---

## Thank You! 🙏

Every contribution, no matter how small, makes MCPVots better for everyone. We appreciate your time and effort!

**Happy Coding!** 🚀
