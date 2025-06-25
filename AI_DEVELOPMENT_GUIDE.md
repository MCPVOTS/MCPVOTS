# AI Development Guidelines for MCPVots

## Repository Access for Claude Opus 4

This repository is configured to support AI-driven development with Claude Opus 4. The following guidelines ensure smooth collaboration and automated updates.

## Branch Strategy

### Main Branches
- `main`: Production-ready code
- `develop`: Integration branch for features
- `ai-updates/*`: AI-generated feature branches
- `hotfix/*`: Critical bug fixes

### AI Branch Naming Convention
```
ai-updates/YYYY-MM-DD-feature-description
ai-updates/enhancement-component-name
ai-updates/bugfix-issue-number
```

## Automated Workflows

### 1. AI Commit Workflow
```bash
# AI commits should include proper metadata
git commit -m "feat: Add new MCP server integration

- Enhanced server discovery
- Improved error handling
- Added comprehensive tests

Co-authored-by: Claude Opus 4 <opus4@anthropic.com>
AI-Generated: true
Change-Type: enhancement"
```

### 2. Pull Request Creation
- AI can create PRs automatically
- All PRs include automated testing
- Code review is optional for minor changes
- Major changes require human review

### 3. Deployment Pipeline
```yaml
# Triggered on main branch updates
- Build and test
- Security scan
- Deploy to staging
- Run integration tests
- Deploy to production (if tests pass)
- Monitor and alert
```

## AI Permissions

### Allowed Actions
- ✅ Create feature branches
- ✅ Commit code changes
- ✅ Create pull requests
- ✅ Update documentation
- ✅ Run tests and builds
- ✅ Deploy to staging
- ✅ Monitor system health

### Restricted Actions
- ❌ Direct push to main
- ❌ Delete branches
- ❌ Modify security settings
- ❌ Access production secrets
- ❌ Override required checks

## Quality Gates

### Automated Checks
1. **Code Quality**
   - ESLint/TSLint compliance
   - Prettier formatting
   - TypeScript type checking
   - Security vulnerability scan

2. **Testing**
   - Unit tests (>80% coverage)
   - Integration tests
   - E2E tests
   - Accessibility tests

3. **Performance**
   - Bundle size analysis
   - Lighthouse scores
   - Load testing
   - Memory leak detection

### Manual Review Triggers
- Security-related changes
- Infrastructure modifications
- Breaking API changes
- Major architectural updates

## Integration Points

### GitHub API Integration
```typescript
// Example API calls AI can make
const github = new Octokit({
  auth: process.env.GITHUB_TOKEN
});

// Create pull request
await github.rest.pulls.create({
  owner: 'kabrony',
  repo: 'MCPVots',
  title: 'AI Enhancement: Advanced MCP Integration',
  head: 'ai-updates/mcp-enhancement',
  base: 'main',
  body: generatePRDescription()
});
```

### MCP Server Integration
```typescript
// AI can update MCP configurations
const mcpConfig = {
  servers: [
    {
      name: "ai-assistant",
      command: "claude-opus-4",
      args: ["--repository", "MCPVots"],
      capabilities: ["code-generation", "testing", "documentation"]
    }
  ]
};
```

## Monitoring and Rollback

### Health Checks
- Application performance metrics
- Error rate monitoring
- User experience tracking
- Security incident detection

### Automated Rollback
- Triggered by error thresholds
- Automatic revert to last known good state
- Notification to development team
- Post-incident analysis

## Security Considerations

### Secrets Management
- GitHub tokens stored securely
- Environment variables encrypted
- No secrets in code
- Regular token rotation

### Access Control
- AI actions logged and audited
- Rate limiting on API calls
- Sandbox environment for testing
- Production access restrictions

## Communication Protocols

### Status Updates
```json
{
  "timestamp": "2025-06-24T12:00:00Z",
  "actor": "Claude Opus 4",
  "action": "pull_request_created",
  "details": {
    "pr_number": 123,
    "branch": "ai-updates/mcp-enhancement",
    "files_changed": 15,
    "lines_added": 342,
    "lines_removed": 28
  },
  "status": "success"
}
```

### Notification Channels
- GitHub notifications
- Email alerts
- Slack/Discord webhooks
- Dashboard updates

## Emergency Procedures

### Issue Escalation
1. AI detects critical issue
2. Automatic rollback initiated
3. Human team notified immediately
4. Incident response team activated
5. Post-mortem scheduled

### Manual Override
- Emergency stop button available
- Human can pause AI operations
- Manual deployment controls
- Override all automated processes

## Getting Started for AI

### Initial Setup
```bash
# Clone repository
git clone https://github.com/kabrony/MCPVots.git
cd MCPVots

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Configure AI credentials

# Start development server
npm run dev
```

### Common AI Tasks
```bash
# Create new feature branch
git checkout -b ai-updates/$(date +%Y-%m-%d)-new-feature

# Run tests
npm test

# Build application
npm run build

# Deploy to staging
npm run deploy:staging

# Create pull request
gh pr create --title "AI Enhancement" --body "$(cat PR_TEMPLATE.md)"
```

## Best Practices

### Code Quality
- Follow existing code style
- Add comprehensive tests
- Update documentation
- Include error handling

### Git Practices
- Atomic commits
- Descriptive commit messages
- Proper branch naming
- Clean commit history

### Testing Strategy
- Test-driven development
- Comprehensive coverage
- Integration testing
- Performance testing

### Documentation
- Update README files
- API documentation
- Architecture diagrams
- Change logs

## Support and Contact

For AI-related issues or questions:
- Create GitHub issue with `ai-support` label
- Tag `@kabrony` for urgent matters
- Check AI operations dashboard
- Review automated logs

---

**Note**: This document is automatically updated by AI systems. Last updated: 2025-06-24
