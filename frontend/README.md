# SplitPro Vue.js Frontend

This is the Vue.js frontend for SplitPro, a complete rewrite from the Next.js/React implementation.

## 🚀 Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000

### Docker

```bash
# From the backend directory, run docker-compose
cd ../backend
docker-compose up frontend
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/        # Vue components
│   │   ├── Layout/        # Layout components
│   │   ├── Expense/       # Expense-related components
│   │   └── ...
│   ├── views/             # Page views
│   │   ├── auth/          # Authentication pages
│   │   ├── HomeView.vue
│   │   ├── BalancesView.vue
│   │   └── ...
│   ├── stores/            # Pinia stores
│   │   ├── auth.ts
│   │   ├── expense.ts
│   │   ├── balance.ts
│   │   └── group.ts
│   ├── services/          # API services
│   │   └── api.ts
│   ├── lib/               # Utilities
│   │   ├── currency.ts
│   │   ├── category.ts
│   │   └── utils.ts
│   ├── utils/             # Helper functions
│   │   └── numbers.ts     # BigInt financial calculations
│   ├── router/            # Vue Router
│   └── main.ts            # App entry point
├── public/                # Static assets
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

## 🔑 Key Features

### Financial Precision
All amounts use **integer cents** (e.g., $12.50 = 1250) to avoid floating-point errors:

```typescript
import { formatCurrency, parseCurrencyInput } from '@/utils/numbers'

// Display: 1250 cents → "$12.50"
formatCurrency(1250, 'USD')

// Parse: "$12.50" → 1250 cents
parseCurrencyInput("12.50")
```

### State Management (Pinia)
- `useAuthStore()` - User authentication & session
- `useExpenseStore()` - Expense CRUD operations
- `useBalanceStore()` - Friend/group balances
- `useGroupStore()` - Group management

### API Integration
All backend endpoints are mapped in `src/services/api.ts`:

```typescript
import { apiClient } from '@/services/api'

// Create expense
await apiClient.createExpense({
  name: "Dinner",
  amount: 5000, // $50.00 in cents
  currency: "USD",
  // ...
})
```

## 🎨 UI Components

Built with:
- **Tailwind CSS** - Utility-first styling
- **Lucide Icons** - Icon library
- **Vue Sonner** - Toast notifications
- **date-fns** - Date formatting

## 📡 API Endpoints

The frontend connects to the Python/FastAPI backend at `/api`:

- **Auth**: `/api/auth/login`, `/api/auth/register`, `/api/auth/magic-link`
- **Expenses**: `/api/expenses`, `/api/expenses/{id}`
- **Groups**: `/api/groups`, `/api/groups/{id}`
- **Users**: `/api/users/me`, `/api/users/friends`
- **Balances**: `/api/expenses/balances/all`

## 🔒 Authentication

JWT-based authentication:
1. Login → Receive access token
2. Token stored in localStorage
3. Axios interceptor adds `Authorization: Bearer {token}` to requests
4. 401 responses trigger automatic logout

## 📱 PWA Support

Progressive Web App features via Vite PWA plugin:
- Offline support
- Install to home screen
- Service worker caching

## 🌐 i18n (Internationalization)

Multi-language support with vue-i18n (to be expanded):
- English (default)
- Spanish, French, German (planned)

## 🧪 Development

### Environment Variables

Create `.env.local`:

```
VITE_API_URL=http://localhost:8000
```

### Type Checking

```bash
npm run type-check
```

### Build for Production

```bash
npm run build
npm run preview
```

## 🐳 Docker Production Build

```dockerfile
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

## 📝 Migration from Next.js

This Vue.js frontend replaces the original Next.js implementation with:

| Next.js | Vue.js |
|---------|--------|
| tRPC | REST API (FastAPI) |
| Zustand | Pinia |
| Next.js Router | Vue Router |
| React Components | Vue SFCs |
| next-i18next | vue-i18n |
| SWR | Axios + Pinia |

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## 📄 License

Same as parent project - see [LICENSE](../LICENSE)

