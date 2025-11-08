# Calendar Integration Security

## Overview

The calendar integration feature allows users to connect external calendars (Apple, Google, Outlook) to Kairos. This document outlines security considerations and best practices.

## Current Implementation

### Password Storage

⚠️ **Current State**: Passwords are stored in plain text in the database.

🔒 **Recommended**: Implement encryption for stored passwords using one of the following approaches:

1. **Symmetric Encryption** (Quick implementation):
   - Use `cryptography.fernet` for symmetric encryption
   - Store encryption key in environment variable
   - Encrypt passwords before storing, decrypt when using

2. **Secrets Management** (Production recommended):
   - Use a secrets management service (AWS Secrets Manager, HashiCorp Vault)
   - Store only references to secrets in the database
   - Retrieve actual passwords only when needed

### Authentication

- Apple Calendar uses app-specific passwords (good practice)
- Users should never use their main Apple ID password
- Each integration should have its own credentials

## Security Best Practices

### For Users

1. **Use App-Specific Passwords**:
   - Never share your main account password
   - Generate dedicated app-specific passwords for Kairos
   - Revoke app-specific passwords when no longer needed

2. **Limit Calendar Access**:
   - Only connect calendars that you need to sync
   - Review connected integrations regularly
   - Remove unused integrations

3. **Monitor Sync Activity**:
   - Check the last sync timestamp regularly
   - Verify that synced events are correct
   - Report any suspicious activity

### For Developers

1. **Implement Password Encryption**:
   ```python
   from cryptography.fernet import Fernet
   
   # Generate and store key securely
   key = Fernet.generate_key()
   cipher = Fernet(key)
   
   # Encrypt before storing
   encrypted_password = cipher.encrypt(password.encode())
   
   # Decrypt when using
   decrypted_password = cipher.decrypt(encrypted_password).decode()
   ```

2. **Add Rate Limiting**:
   - Limit sync requests per user/integration
   - Prevent brute force attacks on credentials
   - Implement exponential backoff for failed syncs

3. **Audit Logging**:
   - Log all integration creation/deletion events
   - Log sync activities (success/failure)
   - Monitor for unusual patterns

4. **Secure API Endpoints**:
   - Require authentication for all integration endpoints
   - Validate user ownership of integrations
   - Use HTTPS only for all API calls

## Future Enhancements

### OAuth Integration

For Google and Outlook calendars, implement OAuth 2.0 flow:
- More secure than password storage
- No need to handle user passwords
- Token-based access with refresh capability
- Easier revocation by users

### Multi-Factor Authentication

Consider adding MFA for:
- Creating new integrations
- Syncing calendars
- Deleting integrations

## Compliance

### Data Protection

- **GDPR**: Users should be able to export and delete their integration data
- **Data Retention**: Passwords should be deleted immediately when integration is removed
- **Data Minimization**: Only store necessary information

### CalDAV Protocol

- CalDAV is an open protocol based on WebDAV
- Uses standard HTTP authentication
- Supports SSL/TLS for secure connections
- Compatible with iCloud, Google Calendar, and other providers

## Implementation Checklist

- [x] Basic password storage (plain text)
- [ ] Implement password encryption
- [ ] Add rate limiting for sync operations
- [ ] Implement audit logging
- [ ] Add OAuth support for Google/Outlook
- [ ] Add integration health monitoring
- [ ] Implement automatic password rotation
- [ ] Add webhook support for real-time sync

## References

- [CalDAV Specification](https://datatracker.ietf.org/doc/html/rfc4791)
- [Apple CalDAV Documentation](https://developer.apple.com/documentation/calendar)
- [OAuth 2.0 Best Practices](https://oauth.net/2/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
