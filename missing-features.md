# SAHASplit - Missing Features Tracker

> Last Updated: December 14, 2025

This document tracks missing features compared to Splitwise and other expense splitting apps.
Features are marked with their implementation status.

## Legend
- ✅ **Implemented** - Feature is complete
- 🚧 **In Progress** - Currently being implemented
- ❌ **Not Started** - Feature pending implementation

---

## 🔴 Account & User Features

### Profile Management
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Profile Picture Upload | ✅ Implemented | Users can upload/change their avatar | High |
| Change Password | ✅ Implemented | Password change functionality for non-OAuth users | High |
| Edit Profile Name | ✅ Implemented | Name editing in UI | Medium |
| Email Verification Status | ❌ Not Started | Indicator if email is verified | Low |
| Account Creation Date | ✅ Implemented | Display when account was created | Low |

### Notification Preferences
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Email Notification Settings | ✅ Implemented | Toggle for expense/reminder emails | High |
| Push Notification Settings | ✅ Implemented | Toggle for push notifications | High |
| Notification Frequency | ❌ Not Started | Daily/weekly digest options | Medium |
| Reminder Settings | ❌ Not Started | Set reminder frequency for debts | Medium |

### Privacy & Security
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Two-Factor Authentication (2FA) | ❌ Not Started | 2FA via authenticator app or SMS | Medium |
| Active Sessions Management | ❌ Not Started | View/logout of other devices | Medium |
| Login History | ❌ Not Started | Record of login attempts | Low |
| Privacy Settings | ❌ Not Started | Control who can see activity/add to groups | Low |
| Delete Account | ✅ Implemented | Permanent account deletion (GDPR compliance) | High |

### Friend Management
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Invite Friends via SMS | ❌ Not Started | SMS invitation option | Low |
| Friend Nicknames | ❌ Not Started | Custom display names for friends | Low |
| Block Users | ❌ Not Started | Block functionality | Medium |
| Friend Requests | ❌ Not Started | Approval system before adding | Low |

---

## 🔶 Expense Features

### Expense Enhancements
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Expense Notes/Comments | ✅ Implemented | Add notes to expenses | High |
| Recurring Expenses | ❌ Not Started | Auto-repeat expenses (weekly/monthly) | Medium |
| Receipt/Bill Upload | ❌ Not Started | Attach images to expenses | Medium |
| Expense Templates | ❌ Not Started | Save frequently used expenses | Low |
| Expense Duplication | ❌ Not Started | Copy existing expenses | Low |

### Expense History
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Expense Filtering | ❌ Not Started | Filter by date/amount/category/person | Medium |
| Expense Search | ❌ Not Started | Search expenses by name | Medium |
| Activity Log | ❌ Not Started | Timeline of all changes | Low |
| Expense Edit History | ❌ Not Started | Track who edited what | Low |

---

## 🔷 Group Features

### Group Management
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Group Image/Avatar | ❌ Not Started | Custom group pictures | Low |
| Group Categories | ❌ Not Started | Trip/Home/Couple/Other tags | Low |
| Simplify Debts | ❌ Not Started | Auto debt optimization algorithm | Medium |
| Group Archive/Restore | ❌ Not Started | Archive old groups | Medium |
| Group Totals/Analytics | ❌ Not Started | Spending breakdown per group | Medium |

---

## 🟢 Payment & Settlement Features

### Settlement Options
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Payment Integration | ❌ Not Started | Connect PayPal/Venmo/UPI | Low |
| Payment Reminders | ❌ Not Started | Send reminders to debtors | Medium |
| Settlement History | ❌ Not Started | Track past settlements | Low |
| Partial Settlements | ❌ Not Started | Pay part of a debt | Medium |

---

## 🟡 Reporting & Analytics

### Dashboard & Reports
| Feature | Status | Description | Priority |
|---------|--------|-------------|----------|
| Monthly Spending Report | ❌ Not Started | Category breakdown by month | Medium |
| Category Analytics | ❌ Not Started | Pie charts of spending | Medium |
| Balance Trends | ❌ Not Started | Historical balance graph | Low |
| Export Reports | ❌ Not Started | PDF/CSV reports | Low |

---

## Implementation Queue (Priority Order)

### Phase 1 - High Priority ✅ COMPLETED
1. ✅ Profile Picture Upload
2. ✅ Change Password
3. ✅ Notification Preferences (Email + Push toggles)
4. ✅ Delete Account
5. ✅ Expense Notes/Comments

### Phase 2 - Medium Priority
- ❌ Expense Filtering & Search
- ❌ Recurring Expenses
- ❌ Receipt/Bill Upload
- ❌ Payment Reminders
- ❌ Simplify Debts
- ❌ Group Archive/Restore

### Phase 3 - Low Priority
- ❌ 2FA
- ❌ Active Sessions
- ❌ Group Images
- ❌ Expense Templates
- ❌ Analytics & Reports

---

## Change Log

| Date | Feature | Status Change | Notes |
|------|---------|---------------|-------|
| 2024-12-14 | Document Created | - | Initial feature tracking |
| 2024-12-14 | Profile Picture Upload | ❌ → ✅ | Backend + Frontend implemented |
| 2024-12-14 | Change Password | ❌ → ✅ | Backend + Frontend implemented |
| 2024-12-14 | Edit Profile Name | ❌ → ✅ | Frontend UI added |
| 2024-12-14 | Account Creation Date | ❌ → ✅ | Model + UI updated |
| 2024-12-14 | Email Notification Settings | ❌ → ✅ | Preferences API + UI |
| 2024-12-14 | Push Notification Settings | ❌ → ✅ | Preferences API + UI |
| 2024-12-14 | Delete Account | ❌ → ✅ | Full GDPR-compliant deletion |
| 2024-12-14 | Expense Notes/Comments | ❌ → ✅ | CRUD endpoints + UI component |

---

## Files Modified/Created

### Backend (Python/FastAPI)
- `backend/app/api/routers/user.py` - Added profile picture, password change, notification prefs, account deletion endpoints
- `backend/app/api/routers/expense.py` - Added expense notes CRUD endpoints
- `backend/app/models/models.py` - Added `notification_preferences` and `created_at` to User model
- `backend/app/schemas/user.py` - Added schemas for new features
- `backend/alembic/versions/20251214_add_user_notification_prefs.py` - Database migration

### Frontend (Vue.js)
- `frontend/src/views/AccountView.vue` - Complete redesign with all new features
- `frontend/src/views/ExpenseDetailsView.vue` - Added expense notes section
- `frontend/src/components/ExpenseNotes.vue` - New component for expense notes
- `frontend/src/services/api.ts` - Added API methods for all new features
- `frontend/src/stores/auth.ts` - Updated User interface
