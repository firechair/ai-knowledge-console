# Security Best Practices

## Credentials Management

### For Public Repositories

**NEVER commit**:
- `.env` files with real credentials
- API keys or OAuth secrets
- User tokens or session data

**Safe to commit**:
- `.env.example` (template with no real values)
- Documentation about how to get credentials
- Code that loads from environment variables

### .gitignore

Ensure your `.gitignore` includes:
```
.env
.env.local
*.key
*.pem
```

### For This Project

This repository is **safe to make public** because:
1. `.env.example` contains only templates (no real credentials)
2. `.env` is in `.gitignore`
3. All credentials loaded from environment variables
4. OAuth tokens stored in-memory (not persisted)

### Credential Rotation

If you accidentally commit credentials:
1. **Immediately** rotate/revoke them in the provider console
2. Use `git filter-branch` or BFG Repo-Cleaner to remove from history
3. Force push to remote

### Production Security

For production deployment:
1. **Use secret management**: AWS Secrets Manager, HashiCorp Vault, etc.
2. **Encrypt tokens**: Encrypt OAuth tokens at rest in database
3. **Implement sessions**: Replace `user_id=default_user` with real user sessions
4. **Use HTTPS**: Always use TLS in production
5. **Rate limiting**: Enable rate limiting in production
6. **Audit logs**: Log all OAuth authorizations

### OAuth Security

- State tokens prevent CSRF attacks
- Refresh tokens allow long-term access without re-auth
- Scopes limit what the app can access
- Users can revoke access anytime from their account settings
