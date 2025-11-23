# AWS Cognito Integration Guide

## Overview

This project uses AWS Cognito User Pools for user authentication and management, while maintaining user data in our PostgreSQL database for application-specific information.

## Architecture

### Dual Storage Strategy

- **AWS Cognito**: Handles authentication, password policies, MFA, and user lifecycle
- **PostgreSQL Database**: Stores application-specific user data (username, email, predictions, leagues, etc.)

### Why This Approach?

1. **Security**: Cognito provides enterprise-grade authentication with built-in password policies, MFA, and security features
2. **Scalability**: Cognito handles authentication at scale without impacting our database
3. **Compliance**: Cognito helps with compliance requirements (SOC, HIPAA, etc.)
4. **Application Data**: We still need our database for predictions, leagues, rankings, etc.

## Configuration

### Environment Variables

```bash
# Enable/disable Cognito (default: False for local dev)
COGNITO_ENABLED=true

# AWS Cognito User Pool ID
COGNITO_USER_POOL_ID=eu-north-1_xxxxxxxxx

# Cognito App Client ID
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx

# AWS Region (should match your Cognito pool region)
AWS_REGION=eu-north-1
```

### Local Development

**Recommended Approach**: Keep `COGNITO_ENABLED=false` for local development.

**Why?**
- Faster development (no AWS calls)
- No AWS credentials needed locally
- Easier testing and debugging
- Consistent with TDD workflow

**When to Enable Locally?**
- Testing Cognito-specific features (MFA, password policies)
- Integration testing before deployment
- Debugging Cognito issues

### Production/Staging

Always enable Cognito in production and staging environments:
- Better security
- Password policy enforcement
- MFA support
- User management features

## How It Works

### Signup Flow

1. **Cognito Enabled**:
   - Create user in Cognito first
   - Get Cognito user ID (sub)
   - Create user in our database with `cognito_user_id`
   - Store password hash in DB for fallback/consistency
   - Cognito handles email verification (if configured)

2. **Cognito Disabled** (Local Dev):
   - Create user directly in database
   - Use our own email verification system
   - Standard password hashing with bcrypt

### Login Flow

1. **Cognito Enabled**:
   - Authenticate with Cognito
   - Get Cognito tokens (access_token, id_token, refresh_token)
   - Look up user in database by `cognito_user_id` or email
   - Return our JWT token for API authentication

2. **Cognito Disabled**:
   - Authenticate against database password hash
   - Return our JWT token

### Password Reset

1. **Cognito Enabled**: Uses Cognito's password reset flow
2. **Cognito Disabled**: Uses our custom token-based reset

## Database Schema

The `User` model includes:
- `cognito_user_id`: Stores Cognito user ID (sub) when Cognito is used
- `hashed_password`: Always stored for consistency and fallback
- `email_verified`: Synced with Cognito verification status

## Best Practices

### 1. Feature Flag Pattern

Always check `settings.COGNITO_ENABLED` before making Cognito calls:

```python
if settings.COGNITO_ENABLED:
    # Use Cognito
else:
    # Use local auth
```

### 2. Error Handling

Cognito errors are caught and converted to user-friendly messages:
- `UsernameExistsException` → "Email already registered"
- `InvalidPasswordException` → Password policy violation
- `NotAuthorizedException` → Invalid credentials

### 3. Graceful Degradation

If Cognito is unavailable or disabled, the system falls back to local authentication seamlessly.

### 4. User Sync

When enabling Cognito for existing users:
- Migrate existing users to Cognito
- Update `cognito_user_id` in database
- Keep `hashed_password` for backward compatibility

## Setting Up Cognito in AWS

### 1. Create User Pool

1. Go to AWS Console → Cognito → User Pools
2. Create a new User Pool
3. Configure:
   - **Sign-in options**: Email
   - **Password policy**: Strong (or custom)
   - **MFA**: Optional (recommended for production)
   - **Email verification**: Required

### 2. Create App Client

1. In your User Pool, go to "App integration"
2. Create a new App Client
3. Configure:
   - **Allowed OAuth flows**: Authorization code grant, Implicit grant
   - **Allowed OAuth scopes**: email, openid, profile
   - **Allowed callback URLs**: Your frontend URLs

### 3. Get Credentials

- **User Pool ID**: Found in User Pool settings
- **App Client ID**: Found in App Client settings

### 4. Configure Terraform (Optional)

Add Cognito resources to your Terraform configuration for Infrastructure as Code.

## Testing

### Local Testing (Cognito Disabled)

```bash
# Standard signup/login tests work as before
pytest backend/tests/test_auth_signup.py
pytest backend/tests/test_auth_login.py
```

### Cognito Testing

1. Set `COGNITO_ENABLED=true`
2. Configure Cognito credentials
3. Run integration tests against Cognito

## Migration Path

### Existing Users

If you have existing users before enabling Cognito:

1. Create a migration script to:
   - Create users in Cognito
   - Update `cognito_user_id` in database
   - Keep existing `hashed_password` for fallback

2. Run migration during maintenance window

### New Users

New users automatically use Cognito when enabled.

## Troubleshooting

### Common Issues

1. **"Cognito not configured" warnings**
   - Check `COGNITO_ENABLED` is set correctly
   - Verify `COGNITO_USER_POOL_ID` and `COGNITO_CLIENT_ID` are set

2. **Authentication failures**
   - Check AWS credentials
   - Verify User Pool ID and Client ID
   - Check region matches

3. **Password policy errors**
   - Cognito enforces password policies
   - Check User Pool password policy settings
   - Update frontend validation to match

## Security Considerations

1. **Never store Cognito credentials in code**
   - Use environment variables
   - Use AWS Secrets Manager in production

2. **Token Management**
   - Cognito tokens are short-lived
   - Use refresh tokens for long sessions
   - Store tokens securely (httpOnly cookies recommended)

3. **Password Storage**
   - We still store password hashes for consistency
   - Cognito handles actual password validation
   - Consider encrypting `hashed_password` if storing Cognito passwords

## Future Enhancements

- [ ] MFA support
- [ ] Social login (Google, Facebook) via Cognito
- [ ] User migration tools
- [ ] Cognito token refresh endpoint
- [ ] Admin user management via Cognito

