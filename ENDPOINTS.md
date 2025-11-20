# List of Endpoints

This document provides a checklist of all available API endpoints for the application. Each endpoint is listed with its
HTTP method and path.

### User Management

- [ ] `GET  /users`
- [ ] `POST /users`
- [ ] `GET /users/{id}`
- [ ] `PUT /users/{id}`
- [ ] `DELETE /users/{id}`
- [ ] `DELETE /users/{id}/hard`
- [ ] `PATCH /users/{id}/restore`

### Role Management

- [x] `GET  /roles`
- [x] `POST /roles`
- [x] `GET  /roles/{id}`
- [x] `PUT  /roles/{id}`
- [x] `DELETE /roles/{id}`
- [x] `DELETE /roles/{id}/force`
- [x] `PATCH /roles/{id}/restore`
- [x] `GET  /roles/{id}/permissions`
- [x] `POST /roles/{id}/permissions`
- [x] `DELETE /roles/{id}/permissions/{permissionId}`

### Permission Management

- [x] `GET  /permissions`
- [x] `POST /permissions`
- [x] `GET  /permissions/{id}`
- [x] `PUT  /permissions/{id}`
- [x] `DELETE /permissions/{id}`
- [x] `DELETE /permissions/{id}/force`
- [x] `PATCH /permissions/{id}/restore`

### Authentication

- [ ] `POST /auth/login`
- [ ] `POST /auth/login/social`
- [ ] `POST /auth/logout`
- [ ] `POST /auth/register`
- [ ] `POST /auth/verify`
- [ ] `POST /auth/resend-verification`
- [ ] `POST /auth/password/forgot`
- [ ] `POST /auth/password/reset`
- [ ] `POST /auth/refresh`
- [ ] `GET  /auth/me`

### Profile Management

- [ ] `GET  /profile`
- [ ] `PUT  /profile`
- [ ] `PUT  /profile/password`
- [ ] `PUT  /profile/avatar`

### Session Management

- [ ] `GET  /sessions`
- [ ] `GET  /sessions/{id}`
- [ ] `DELETE /sessions/{id}`
- [ ] `DELETE /sessions/all`

### Accounts

- [ ] `GET  /accounts`
- [ ] `POST /accounts/link`
- [ ] `DELETE /accounts/unlink/{provider}`

### TODO:

- Support magic links for login
- Implement two-factor authentication endpoints, including setup, verification, and recovery options
- Permission checking endpoints